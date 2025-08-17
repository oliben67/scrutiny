import logging
from pathlib import Path

from scrutiny.config import _configs

_main_logger = logging.getLogger()

log_file = _configs.get("logging", {}).get("log_file", "logs/scrutiny.log")
logFormatter = logging.Formatter(_configs["logging"]["log_format"])

# Ensure log_file is within a safe directory (e.g., under ./logs)
safe_log_dir = Path("logs").resolve()
log_file_path = Path(log_file).resolve()
if not str(log_file_path).startswith(str(safe_log_dir)):
    raise ValueError("Unsafe log_file path detected: {}".format(log_file_path))

# Create parent directory securely if it does not exist
log_file_path.parent.mkdir(parents=True, exist_ok=True)
log_level = str(_configs.get("logging", {}).get("log_level", "INFO")).upper()
_main_logger.setLevel(log_level)
fileHandler = logging.FileHandler(str(log_file_path))
fileHandler.setFormatter(logFormatter)
_main_logger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
_main_logger.addHandler(consoleHandler)

_main_logger.setLevel(_configs["logging"]["log_level"].upper())

logger = _main_logger.getChild("scrutiny")
