import subprocess as sp
from gdk.build_system.GDKBuildSystem import GDKBuildSystem
import platform


class GradleWrapper(GDKBuildSystem):
    @property
    def build_command(self):
        os_platform = platform.system()
        if os_platform == "Windows":
            return ["./gradlew.bat", "build"]
        else:
            return ["./gradlew", "build"]

    @property
    def build_folder(self):
        return ["build", "libs"]

    @property
    def build_system_identifier(self):
        return ["build.gradle", "build.gradle.kts"]

    def build(self):
        sp.run(self.build_command, check=True)
