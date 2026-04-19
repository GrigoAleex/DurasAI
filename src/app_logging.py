import logging
from datetime import datetime
from pathlib import Path

_LOG_PATH: Path | None = None


def configure_logging() -> Path:
    global _LOG_PATH

    if _LOG_PATH is not None:
        return _LOG_PATH

    logs_dir = Path(__file__).resolve().parent.parent / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    log_path = logs_dir / f"{timestamp}.log"

    formatter = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    root_logger.addHandler(stream_handler)
    root_logger.addHandler(file_handler)

    _LOG_PATH = log_path
    logging.getLogger(__name__).info("Logging initialized: %s", log_path)
    return _LOG_PATH
