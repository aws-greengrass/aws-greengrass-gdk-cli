from gdk.common.config.GDKProject import GDKProject


class InitConfiguration(GDKProject):
    def __init__(self, _args) -> None:
        super().__init__()
        self._args = _args
        self.otf_version = self._get_otf_version()

    def _get_otf_version(self):
        _version_arg = self._args.get("otf_version", None)
        if _version_arg:
            return _version_arg.strip()
        else:
            return self.test_config.otf_version
