from abc import ABC, abstractmethod
from typing import List


class GDKBuildSystem(ABC):
    """
    Class for GDK build system
    """

    @property
    @abstractmethod
    def build_command(self) -> List[str]:
        """
        Build command for the build system
        """

    @property
    @abstractmethod
    def build_folder(self) -> List[str]:
        """
        Build folder created after running the build command
        """

    @property
    @abstractmethod
    def build_system_identifier(self) -> List[str]:
        """
        List of files used to identify the build system
        """

    @abstractmethod
    def build(self, **kwargs) -> None:
        """
        Build the project
        """
