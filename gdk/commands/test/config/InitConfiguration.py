import semver
from gdk.common.config.GDKProject import GDKProject
import logging
import requests
from packaging.version import Version


class InitConfiguration(GDKProject):
    def __init__(self, _args) -> None:
        super().__init__()
        self._args = _args
        self._gtf_releases_url = "https://github.com/aws-greengrass/aws-greengrass-testing/releases"
        self.gtf_version = self._get_gtf_version()

    def _get_gtf_version(self):
        _version_arg = self._args.get("gtf_version", None)
        if _version_arg is None:
            _version_arg = self._args.get("otf_version", None)
        if _version_arg:
            logging.info("Using the GTF version provided in the command %s", _version_arg)
            return self._validated_gtf_version(_version_arg)
        logging.info("Using the GTF version provided in the GDK test config %s", self.test_config.gtf_version)
        return self._validated_gtf_version(self.test_config.gtf_version)

    def _validated_gtf_version(self, version) -> str:
        _version = version.strip()

        if not _version:
            raise ValueError(
                "GTF version cannot be empty. Please specify a valid GTF version in the GDK config or in the command argument."
            )

        if not semver.Version.is_valid(_version):
            raise ValueError(
                f"GTF version {_version} is not a valid semver. Please specify a valid GTF version in the GDK config or in"
                " the command argument."
            )

        if not self._gtf_version_exists(_version):
            raise ValueError(
                f"The specified Greengrass Test Framework (GTF) version '{_version}' does not exist. Please"
                f" provide a valid GTF version from the releases here: {self._gtf_releases_url}"
            )

        try:
            if (Version(_version) < Version(self.test_config.latest_gtf_version) and
                    not self.test_config.upgrade_suggestion_already_provided):
                logging.info(
                    f"The current latest version of GTF is {self.test_config.latest_gtf_version}. Please consider "
                    "using the latest version."
                )
        except Exception as e:
            logging.debug("Not providing GTF update suggestion due to caught version error: %s", str(e))

        return _version

    def _gtf_version_exists(self, _version) -> bool:
        _testing_jar_url = "https://github.com/aws-greengrass/aws-greengrass-testing/releases/tag/v" + _version
        head_response = requests.head(_testing_jar_url, timeout=10)
        return head_response.status_code == 200
