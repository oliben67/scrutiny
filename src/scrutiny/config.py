import os

_configs = {
    "logging": {
        "log_file": os.environ.get("SCRUTINY_LOG_FILE", "logs/divide.log"),
        "log_level": "DEBUG",
        "log_format": "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",
    },
    "parameters": {
        "name": "parametrize",
    },
}
