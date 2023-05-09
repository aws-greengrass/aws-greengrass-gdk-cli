class TestConfiguration:
    def __init__(self, test_config):
        self.test_build_system = "maven"
        self.otf_version = "1.1.0-SNAPSHOT"  # TODO: Default value should be the latest version of otf testing standalone jar.
        self.otf_tag = "Sample"
        self.nucleus_version = "LATEST"  # TODO: Default value should be the latest version of Nucleus.
        self.otf_options = {}

        self._set_test_config(test_config)

    def _set_test_config(self, test_config):
        self._set_build_config(test_config.get("build", {}))
        self._set_otf_config(test_config)

    def _set_build_config(self, test_build_config):
        self.test_build_system = test_build_config.get("build_system", self.test_build_system)

    def _set_otf_config(self, test_config):
        self.otf_version = test_config.get("otf_version", self.otf_version)
        self._set_otf_options(test_config.get("otf_options", {}))

    def _set_otf_options(self, otf_options):
        self.otf_options = otf_options
        self.otf_tag = otf_options.get("tags", self.otf_tag)
        self.nucleus_version = otf_options.get("ggc.version", self.nucleus_version)
