from gdk.build_system.GDKBuildSystem import GDKBuildSystem
from gdk.build_system.Gradle import Gradle
from gdk.build_system.GradleWrapper import GradleWrapper
from gdk.build_system.Maven import Maven


class UATBuildSystem:
    """
    Delegates build tasks to the appropriate build system
    """

    @classmethod
    def get(self, system_type: str) -> GDKBuildSystem:
        system = system_type.strip().lower()
        if not system or system == "":
            raise Exception("Build system not specified")

        if system == "maven":
            return Maven()
        elif system == "gradle":
            return Gradle()
        elif system == "gradlew":
            return GradleWrapper()
        else:
            raise Exception(f"Build system type '{system_type}' is not supported")
