import subprocess as sp

from gdk.build_system.GDKBuildSystem import GDKBuildSystem


class Gradle(GDKBuildSystem):
    @property
    def build_command(self):
        return ["gradle", "clean", "build"]

    @property
    def build_folder(self):
        return ["build", "libs"]

    @property
    def build_system_identifier(self):
        return ["build.gradle", "build.gradle.kts"]

    def build(self):
        sp.run(self.build_command, check=True)
