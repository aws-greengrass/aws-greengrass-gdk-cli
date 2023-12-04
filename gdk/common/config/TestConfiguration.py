import logging

from gdk.common.GithubUtils import GithubUtils
from gdk.common.consts import GTF_REPO_OWNER, GTF_REPO_NAME


class TestConfiguration:
    def __init__(self, test_config):
        self.test_build_system = "maven"
        self.gtf_version = "1.2.0"  # Default value for when Github API call fails
        self.gtf_options = {}

        self._set_test_config(test_config)

    def _set_test_config(self, test_config):
        self._set_build_config(test_config.get("build", {}))
        self._set_gtf_config(test_config)

    def _set_build_config(self, test_build_config):
        self.test_build_system = test_build_config.get("build_system", self.test_build_system)

    def _set_gtf_config(self, test_config):
        github_utils = GithubUtils()
        try:
            latest_gtf_version = github_utils.get_latest_release_name(GTF_REPO_OWNER, GTF_REPO_NAME)
            self.gtf_version = latest_gtf_version
            logging.info("Discovered %s as latest GTF release name.", self.gtf_version)
        except Exception as e:
            logging.info("Unable to get the latest GTF release name. Using %s as the default value.", self.gtf_version)
            logging.debug("Exception information for GTF release name API call: %s", str(e))
        self.gtf_version = (test_config.get("gtf_version")
                            if "gtf_version" in test_config
                            else test_config.get("otf_version", self.gtf_version))
        self.gtf_options = (test_config.get("gtf_options")
                            if "gtf_options" in test_config
                            else test_config.get("otf_options", {}))
