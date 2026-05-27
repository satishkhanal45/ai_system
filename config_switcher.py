from utils.logger import get_logger

logger = get_logger("config_switcher")

# default provider config
current_config = {
    "provider": "groq",
    "model"   : "llama-3.3-70b-versatile",
}

def switch_provider(provider: str, model: str):
    """switch provider and model at runtime"""
    current_config["provider"] = provider
    current_config["model"]    = model
    logger.info(f"Switched to provider: {provider}, model: {model}")

def get_current_config() -> dict:
    """returns the currently active provider config"""
    return current_config