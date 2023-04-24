import json
import logging
import os
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)


class ConfigKey(Enum):
    INSTALLED = 'installed'


class Singleton(type):
    """
    Metaclass makes a class a singleton.
    """

    def __init__(cls, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls.__instance = None

    def __call__(cls, *args, **kwargs):
        """
        Called every time a new instance of a class is being implemented.
        """
        force_create = kwargs.get('force_create', False)

        if not cls.__instance or force_create is True:
            cls.__instance = super().__call__(*args, **kwargs)

        return cls.__instance


GDK_RUNTIME_CONFIG_DIR = "__GDK_RUNTIME_CONFIG_PATH"


class RuntimeConfig(metaclass=Singleton):
    """
    Wrapper around a dict that persists values used by the application by flushing them to
    disk.
    """
    DEFAULT_CONFIG_FILE_NAME = 'runtime.json'

    def __init__(self, *args, **kwargs):
        self._config = dict()
        self._config_path = None
        self._load_config()

    def set(self, key: ConfigKey, value: str):
        self._config[key] = value
        self._flush()

    def get(self, key: ConfigKey):
        return self._config.get(key, None)

    @property
    def config_dir(self) -> Path:
        if os.getenv(GDK_RUNTIME_CONFIG_DIR):
            return Path(os.getenv(GDK_RUNTIME_CONFIG_DIR))

        return Path(os.path.expanduser('~/.gdk'))

    @property
    def config_path(self) -> Path:
        if not self._config_path:
            self._config_path = Path(self.config_dir, self.DEFAULT_CONFIG_FILE_NAME)

        return self._config_path

    @config_path.setter
    def config_path(self, config_path: Path) -> None:
        self._config_path = config_path

    def _load_config(self):
        """
        Load the configuration from disk
        """
        if not self.config_path.exists():
            return

        config_keys = [k.value for k in ConfigKey]

        try:
            content = self.config_path.read_text()
            json_content = json.loads(content)
            self._config = {ConfigKey(k): v for (k, v) in json_content.items() if k in config_keys}
        except (OSError, ValueError) as ex:
            logger.debug("Failed to load config to file %s", self.config_path, exc_info=ex)

    def _flush(self):
        """
        Flush the config to disk.
        """
        try:
            conf = {k.value: v for (k, v) in self._config.items()}
            config_str = json.dumps(conf)
            if not self.config_dir.exists():
                os.makedirs(self.config_dir, mode=0o700, exist_ok=True)
            self.config_path.write_text(config_str)
        except (OSError, ValueError) as ex:
            logger.debug("Failed to flush config to file %s", self.config_path, exc_info=ex)
