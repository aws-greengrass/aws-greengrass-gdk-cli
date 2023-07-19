import semver
from gdk.common.config.GDKProject import GDKProject
import logging


class InitConfiguration(GDKProject):
    def __init__(self, _args) -> None:
        super().__init__()
        self._args = _args
        self.otf_version = self._get_otf_version()

    def _get_otf_version(self):
        _version_arg = self._args.get("otf_version", None)
        if _version_arg:
            logging.info("Using the OTF version specified in the command argument: %s", _version_arg)
            return self._validated_otf_version(_version_arg)
        logging.info("Using the OTF version specified in the GDK test config %s", self.test_config.otf_version)
        return self._validated_otf_version(self.test_config.otf_version)

    def _validated_otf_version(self, version) -> str:
        _version = version.strip()

        if not _version:
            raise ValueError(
                "OTF version cannot be empty. Please specify a valid OTF version in the GDK config or in the command argument."
            )

        if not semver.Version.is_valid(_version):
            raise ValueError(
                f"OTF version {_version} is not a valid semver. Please specify a valid OTF version in the GDK config or in"
                " the command argument."
            )

        return _version
