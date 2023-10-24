import glob
import os
import shutil
import logging
from pathlib import Path

import gdk.common.utils as utils
import gdk.common.consts as consts
from gdk.build_system.GDKBuildSystem import GDKBuildSystem
from gdk.commands.component.config.ComponentBuildConfiguration import ComponentBuildConfiguration


class Zip(GDKBuildSystem):
    """
    Builds the component as a zip file.

    Copies over necessary files by excluding certain files to a build folder identied for zip build system
    (supported_component_builds.json has the build folder info).
    This build folder is zipped completely as a component zip artifact.
    Raises an exception if there's an error in the process of zippings.
    """

    @property
    def build_command(self):
        return []

    @property
    def build_system_identifier(self):
        return ["gdk-config.json"]

    @property
    def build_folder(self):
        return ["zip-build"]

    def build(self, **kwargs):
        try:
            project_config: ComponentBuildConfiguration = kwargs.get("project_config")
            # Only one zip-build folder in the set
            zip_build = utils.get_current_directory().joinpath(*self.build_folder).resolve()
            artifacts_zip_build = Path(zip_build).joinpath(utils.get_current_directory().name).resolve()
            utils.clean_dir(zip_build)
            logging.debug("Copying over component files to the '{}' folder.".format(artifacts_zip_build.name))
            root_directory_path = utils.get_current_directory()

            unwanted_paths = self.generate_ignore_list_from_globs(root_directory_path,
                                                                  self.get_ignored_file_patterns(project_config))
            self.smart_excludes_warning(project_config)

            def ignore_with_glob_support(dir, names):
                ignore_set = set()
                for name in names:
                    full_pathname = Path(dir) / name
                    if str(full_pathname) in unwanted_paths or f"{str(full_pathname)}{os.path.sep}" in unwanted_paths:
                        ignore_set.add(name)
                return ignore_set

            shutil.copytree(
                root_directory_path,
                artifacts_zip_build,
                ignore=ignore_with_glob_support,
            )

            # Get build file name without extension. This will be used as name of the archive.
            archive_file = utils.get_current_directory().name
            zip_name_setting = project_config.build_options.get("zip_name", None)
            if zip_name_setting is not None:
                if len(zip_name_setting):
                    archive_file = zip_name_setting
                else:
                    archive_file = project_config.component_name
            logging.debug(
                "Creating an archive named '{}.zip' in '{}' folder with the files in '{}' folder.".format(
                    archive_file, zip_build.name, artifacts_zip_build.name
                )
            )
            archive_file_name = Path(zip_build).joinpath(archive_file).resolve()
            shutil.make_archive(archive_file_name, "zip", root_dir=artifacts_zip_build)
            logging.debug("Archive complete.")

        except Exception:
            logging.error("Failed to zip the component in default build mode.")
            raise

    def get_ignored_file_patterns(self, project_config: ComponentBuildConfiguration) -> list:
        """
        Creates a list of files or directory patterns to ignore while copying a directory.

        When no `exclude` option is present on the build configuration, it excludes:
        1. project config file -> gdk-config.json
        2. greengrass-build directory
        3. recipe file
        4. tests folder
        5. node_modules
        6. hidden files

        Otherwise it excludes:
        1. project config file -> gdk-config.json
        2. greengrass-build directory
        3. recipe file
        4. Any pattern defined on the exclude pattern array
        """
        options = project_config.build_options

        ignore_list = [
            consts.cli_project_config_file,
            consts.greengrass_build_dir,
            project_config.recipe_file.name,
        ]

        if not options:
            ignore_list.extend(
                [
                    "**/test*",
                    "**/.*",
                    "**/node_modules",
                ]
            )
        else:
            ignore_list.extend(options.get("excludes", []))

        return ignore_list

    def generate_ignore_list_from_globs(self, root_directory, globs):
        ignored_pathnames = set()
        for pattern in globs:
            # glob.glob has a root_dir parameter, but only for python 3.10+, so we prepend the root dir to the glob pattern
            glob_pattern_whole = f"{root_directory}{os.path.sep}{pattern}"
            ignored_pathnames = ignored_pathnames | set(glob.glob(glob_pattern_whole, recursive=True))
        return ignored_pathnames

    def smart_excludes_warning(self, project_config: ComponentBuildConfiguration):
        """
        Smart warning to warn user of excludes behavior change, if it is detected that a custom excludes is provided
        and none of the patterns attempt to match any directories. This warning can be ignored by setting the
        environment variable GDK_EXCLUDES_WARN_IGNORE to true. This is added in the 1.5.0 release and can be removed
        at some point in the future.
        """
        warning_string = ("Build option \'excludes\' found in config and none of the provided patterns " +
                          "include directory matching. In GDK version 1.5.0, patterns for exclusions in zip builds " +
                          "were changed to use the glob format, so patterns with no specified directory pattern will " +
                          "only match at the root level of the project. If this is intentional, you can ignore this " +
                          "warning, but to achieve the old behavior excluding from each subdirectory, append \'**/\' " +
                          "to each pattern as such: ")
        warning_string_2 = (". To ignore this warning in the future, set the GDK_EXCLUDES_WARN_IGNORE environment " +
                            "variable to true.")
        GDK_EXCLUDES_ENV_KEY = "GDK_EXCLUDES_WARN_IGNORE"
        build_options = project_config.build_options
        excludes_list = build_options.get("excludes", [])
        if not excludes_list or os.environ.get(GDK_EXCLUDES_ENV_KEY, "False").lower() == "true":
            return
        elif all(pattern.find("/") == -1 for pattern in excludes_list):
            # We check if we issue the warning by seeing if there are any slashes in any items in the provided excludes
            # configuration. If there are any slashes, we assume that the project is created using GDK 1.5.0+ and does
            # not need the warning.
            suggestion_list = [f"**/{old_pattern}" for old_pattern in excludes_list]
            suggestion_list_str = str(suggestion_list).replace("'", '"')
            logging.warning(f"{warning_string}{suggestion_list_str}{warning_string_2}")
        else:
            return
