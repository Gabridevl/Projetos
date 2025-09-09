import json
import logging
import os
from typing import Any, Dict


_LOGGER_CONFIGURED = False


def _project_root() -> str:
    return os.path.dirname(__file__) if os.path.isdir(__file__) else os.path.dirname(os.path.abspath(__file__))


def _default_config_path() -> str:
    return os.path.join(os.path.dirname(_project_root()), "data", "config.json")


def configure_logging(level: int = logging.INFO) -> None:
    global _LOGGER_CONFIGURED
    if _LOGGER_CONFIGURED:
        return
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    _LOGGER_CONFIGURED = True


def log_info(message: str) -> None:
    if not _LOGGER_CONFIGURED:
        configure_logging()
    logging.info(message)


def log_error(message: str) -> None:
    if not _LOGGER_CONFIGURED:
        configure_logging()
    logging.error(message)


def load_config(path: str | None = None) -> Dict[str, Any]:
    config_path = path or _default_config_path()
    if not os.path.isabs(config_path):
        # Resolve relative to project root
        base = os.path.dirname(_project_root())
        config_path = os.path.join(base, config_path)
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        log_error(f"Config file not found: {config_path}")
        return {}
    except Exception as exc:
        log_error(f"Failed to load config: {exc}")
        return {}


