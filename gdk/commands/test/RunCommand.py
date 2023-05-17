from gdk.commands.Command import Command
from gdk.common.config.GDKProject import GDKProject
from gdk.build_system.UATBuildSystem import UATBuildSystem


class RunCommand(Command):
    def __init__(self, command_args) -> None:
        super().__init__(command_args, "run")
        self._gdk_project = GDKProject()
        self._test_directory = self._gdk_project.gg_build_dir.joinpath("uat-features").resolve()
        self._test_build_system = self._gdk_project.test_config.test_build_system

    def run(self):
        """
        This method is called when customer runs the `gdk test run` command

        1. Check if the test module is built. Otherwise, raise an exception.
        2. TODO: If ggc.archive path is not configured, then download the latest nucleus archive from url
        3. TODO: Run the test module jar with configured options.
        """
        if not self._is_test_module_built():
            raise Exception(
                "UAT module is not built. Please build the test module using `gdk test build`command before running the tests."
            )

    def _is_test_module_built(self) -> bool:
        """
        Return true if the test module build folder exists
        """
        uat_build_system = UATBuildSystem.get(self._test_build_system)
        test_build_folder = self._test_directory.joinpath(*uat_build_system.build_folder).resolve()

        return test_build_folder.exists()
