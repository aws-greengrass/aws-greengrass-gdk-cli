import subprocess as sp

from gdk.build_system.GDKBuildSystem import GDKBuildSystem
import logging


class Gradle(GDKBuildSystem):
    @property
    def build_command(self):
        return ["gradle", "build"]

    @property
    def build_folder(self):
        return ["build", "libs"]

    @property
    def build_system_identifier(self):
        return ["build.gradle", "build.gradle.kts"]

    def build(self, **kwargs):
        path = kwargs.get("path")
        logging.info("Running the build command '%s'", " ".join(self.build_command))
        sp.run(self.build_command, check=True, cwd=path)
