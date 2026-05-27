import time
from utils.logger import log_structured, get_logger

logger = get_logger("tracer")

def count_tokens(text: str) -> int:
    """simple token count — splits by space"""
    return len(text.split())

def trace_request(provider: str, model: str, prompt: str, response: str, start_time: float):
    """traces the full lifecycle: prompt → response → latency → tokens"""
    latency = round(time.time() - start_time, 3)
    prompt_tokens = count_tokens(prompt)
    response_tokens = count_tokens(response)

    log_structured(logger, "request_trace", {
        "provider"       : provider,
        "model"          : model,
        "prompt"         : prompt,
        "response"       : response,
        "latency_sec"    : latency,
        "prompt_tokens"  : prompt_tokens,
        "response_tokens": response_tokens,
        "total_tokens"   : prompt_tokens + response_tokens,
    })