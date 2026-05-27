import logging
import json
from utils.config import LOG_LEVEL, APP_NAME

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)

    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(handler)

    return logger

def log_structured(logger: logging.Logger, event: str, data: dict):
    """logs a structured JSON event for observability"""
    payload = {"event": event, **data}
    logger.info(json.dumps(payload))