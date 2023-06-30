from gdk.common.config.GDKProject import GDKProject


class ComponentBuildConfiguration(GDKProject):
    def __init__(self, _args) -> None:
        super().__init__()
        self._args = _args
        self.build_config = self.component_config.get("build", {})
        self.build_system = self.build_config.get("build_system", "")
        self.build_options = self.build_config.get("options", {})
        self.component_version = self.component_config.get("version", "NEXT_PATCH")
        self.publisher = self.component_config.get("author", "")
        self.region = self._get_region()

    def _get_region(self):
        _publish_config = self.component_config.get("publish", {})
        _region = _publish_config.get("region", "")
        return _region
