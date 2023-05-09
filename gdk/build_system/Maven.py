import platform
import subprocess as sp
from gdk.build_system.GDKBuildSystem import GDKBuildSystem


class Maven(GDKBuildSystem):
    @property
    def build_command(self):
        os_platform = platform.system()
        if os_platform == "Windows":
            return ["mvn.cmd", "package"]
        else:
            return ["mvn", "package"]

    @property
    def build_folder(self):
        return ["target"]

    @property
    def build_system_identifier(self):
        return ["pom.xml"]

    def build(self):
        sp.run(self.build_command, check=True)
