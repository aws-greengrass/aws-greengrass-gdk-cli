import fnmatch
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

            def ignore_patterns_in_root(path, names):
                if str(path) == str(root_directory_path):
                    return {
                        name
                        for pattern in self.get_ignored_file_patterns(project_config)
                        for name in fnmatch.filter(names, pattern)
                    }
                return set()

            shutil.copytree(
                root_directory_path,
                artifacts_zip_build,
                ignore=ignore_patterns_in_root,
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

        Otherwise it exclues:
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
                    "test*",
                    ".*",
                    "node_modules",
                ]
            )
        else:
            ignore_list.extend(options.get("excludes", []))

        return ignore_list
