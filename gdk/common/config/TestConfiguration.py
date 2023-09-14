class TestConfiguration:
    def __init__(self, test_config):
        self.test_build_system = "maven"
        self.gtf_version = "1.1.0"  # TODO: Default value should be the latest version of gtf testing standalone jar.
        self.gtf_options = {}

        self._set_test_config(test_config)

    def _set_test_config(self, test_config):
        self._set_build_config(test_config.get("build", {}))
        self._set_gtf_config(test_config)

    def _set_build_config(self, test_build_config):
        self.test_build_system = test_build_config.get("build_system", self.test_build_system)

    def _set_gtf_config(self, test_config):
        self.gtf_version = (test_config.get("gtf_version")
                            if "gtf_version" in test_config
                            else test_config.get("otf_version", self.gtf_version))
        self.gtf_options = (test_config.get("gtf_options")
                            if "gtf_options" in test_config
                            else test_config.get("otf_options", {}))
