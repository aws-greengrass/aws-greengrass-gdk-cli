import gdk.common.configuration as configuration
from gdk.common.config.TestConfiguration import TestConfiguration


class GDKConfiguration:
    def __init__(self):
        self._config = configuration.get_configuration()
        self._component = self._config.get("component")
        self._test = self._config.get("test", {})

        self.component_name = next(iter(self._component))
        self.component_config = self._component.get(self.component_name)
        self.test_config = TestConfiguration(self._test)
