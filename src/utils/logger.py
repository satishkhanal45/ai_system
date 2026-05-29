import logging
import json
import os
from logging.handlers import RotatingFileHandler
from .config import LOG_LEVEL, APP_NAME

# Create logs directory if it doesn't exist
LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

# Log file paths
LOG_FILE = os.path.join(LOGS_DIR, "app.log")
ERROR_LOG_FILE = os.path.join(LOGS_DIR, "error.log")
REQUEST_LOG_FILE = os.path.join(LOGS_DIR, "requests.log")

# Standard formatter
STANDARD_FORMATTER = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Detailed formatter with extra info
DETAILED_FORMATTER = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def get_logger(name: str) -> logging.Logger:
    """
    Get or create a logger with both console and file handlers.
    
    Args:
        name: Logger name (typically __name__)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)
    
    # Skip if handlers already added
    if logger.handlers:
        return logger
    
    # Console handler (stdout)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(LOG_LEVEL)
    console_handler.setFormatter(STANDARD_FORMATTER)
    
    # File handler with rotation (main app log)
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(LOG_LEVEL)
    file_handler.setFormatter(DETAILED_FORMATTER)
    
    # Error file handler with rotation (errors only)
    error_handler = RotatingFileHandler(
        ERROR_LOG_FILE,
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(DETAILED_FORMATTER)
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)
    
    return logger

def log_request(logger: logging.Logger, provider: str, model: str, prompt: str, **kwargs):
    """Log API request details"""
    request_data = {
        "event": "api_request",
        "provider": provider,
        "model": model,
        "prompt_length": len(prompt),
        **kwargs
    }
    logger.info(f"REQUEST: {json.dumps(request_data)}")
    _log_to_request_file(request_data)

def log_response(logger: logging.Logger, provider: str, model: str, response: str, status: str, **kwargs):
    """Log API response details"""
    response_data = {
        "event": "api_response",
        "provider": provider,
        "model": model,
        "response_length": len(response),
        "status": status,
        **kwargs
    }
    logger.info(f"RESPONSE: {json.dumps(response_data)}")

def log_error(logger: logging.Logger, error_type: str, provider: str = None, message: str = None, **kwargs):
    """Log error details"""
    error_data = {
        "event": "error",
        "error_type": error_type,
        "provider": provider,
        "message": message,
        **kwargs
    }
    logger.error(f"ERROR: {json.dumps(error_data)}")

def log_structured(logger: logging.Logger, event: str, data: dict):
    """Logs a structured JSON event for observability"""
    payload = {"event": event, **data}
    logger.info(json.dumps(payload))

def _log_to_request_file(request_data: dict):
    """Write request to dedicated request log file"""
    request_logger = logging.getLogger("requests")
    request_logger.setLevel(LOG_LEVEL)
    
    if not request_logger.handlers:
        request_handler = RotatingFileHandler(
            REQUEST_LOG_FILE,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        request_handler.setFormatter(STANDARD_FORMATTER)
        request_logger.addHandler(request_handler)
    
    request_logger.info(json.dumps(request_data))
