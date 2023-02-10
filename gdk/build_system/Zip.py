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
    def __init__(self):
        pass

    def __str__(self):
        return "zip"

    def build(self):
        self._build_system_zip()

    def _build_system_zip(self):
        try:
            zip_build = next(iter(self._get_build_folder_by_build_system()))  # Only one zip-build folder in the set
            artifacts_zip_build = Path(zip_build).joinpath(utils.current_directory.name).resolve()
            utils.clean_dir(zip_build)
            logging.debug("Copying over component files to the '{}' folder.".format(artifacts_zip_build.name))
            shutil.copytree(utils.current_directory, artifacts_zip_build, ignore=self._ignore_files_during_zip)

            # Get build file name without extension. This will be used as name of the archive.
            archive_file = utils.current_directory.name
            logging.debug(
                "Creating an archive named '{}.zip' in '{}' folder with the files in '{}' folder.".format(
                    archive_file, zip_build.name, artifacts_zip_build.name
                )
            )
            archive_file_name = Path(zip_build).joinpath(archive_file).resolve()
            shutil.make_archive(archive_file_name, "zip", root_dir=artifacts_zip_build)
            logging.debug("Archive complete.")

        except Exception as e:
            raise Exception("""Failed to zip the component in default build mode.\n{}""".format(e))

    def _ignore_files_during_zip(self, path, names):
        """
        Creates a list of files or directories to ignore while copying a directory.

        Helper function to create custom list of files/directories to ignore. Here, we exclude,
        1. project config file -> gdk-config.json
        2. greengrass-build directory
        3. recipe file
        4. tests folder
        5. node_modules
        6. hidden files

        Parameters
        ----------
            path,names

        Returns
        -------
            ignore_list(list): List of files or directories to ignore during zip.
        """
        # TODO: Identify individual files in recipe that are not same as zip and exclude them during zip.

        ignore_list = [
            consts.cli_project_config_file,
            consts.greengrass_build_dir,
            self.project_config["component_recipe_file"].name,
            "test*",
            ".*",
            "node_modules",
        ]
        return ignore_list
