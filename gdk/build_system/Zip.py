import shutil
import logging
from pathlib import Path

import gdk.common.utils as utils
import gdk.common.consts as consts


class Zip:
    """
    Builds the component as a zip file.

    Copies over necessary files by excluding certain files to a build folder identied for zip build system
    (supported_component_builds.json has the build folder info).
    This build folder is zipped completely as a component zip artifact.
    Raises an exception if there's an error in the process of zippings.
    """

    def __init__(self, project_config, build_folders):
        self.build_folders = build_folders
        self.project_config = project_config

    def __str__(self):
        return "zip"

    def _get_build_options(self) -> dict:
        return self.project_config["component_build_config"].get("options", dict())

    def build(self):
        try:
            # Only one zip-build folder in the set
            zip_build = next(iter(self.build_folders))
            artifacts_zip_build = Path(zip_build).joinpath(
                utils.current_directory.name).resolve()
            utils.clean_dir(zip_build)
            logging.debug("Copying over component files to the '{}' folder.".format(
                artifacts_zip_build.name))
            shutil.copytree(utils.current_directory, artifacts_zip_build,
                            ignore=shutil.ignore_patterns(*self.get_ignored_file_patterns()))

            # Get build file name without extension. This will be used as name of the archive.
            archive_file = self.project_config["component_name"]
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

    def get_ignored_file_patterns(self) -> list:
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
        options = self._get_build_options()

        ignore_list = [
            consts.cli_project_config_file,
            consts.greengrass_build_dir,
            self.project_config["component_recipe_file"].name,
        ]

        if not options:
            ignore_list.extend([
                "test*",
                ".*",
                "node_modules",
            ])
        else:
            ignore_list.extend(options.get("excludes", []))

        return ignore_list
