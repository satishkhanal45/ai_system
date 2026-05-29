#streaming pipeline  


from ..api.streaming import stream_response, build_stream_body
from ..api.providers import PROVIDERS
from ..utils.schemas import LLMRequest
from ..utils.logger import get_logger, log_request, log_error

logger = get_logger("stream_service")

async def stream_llm(request: LLMRequest):
    """
    Receives an LLMRequest, sets up the stream,
    and yields tokens one by one to the caller.
    """
    provider = request.provider

    if provider not in PROVIDERS:
        logger.error(f"Unknown provider: {provider}")
        log_error(logger, "invalid_provider", provider, f"Provider not in supported list")
        return

    url = PROVIDERS[provider]["url"]
    headers = PROVIDERS[provider]["headers"]
    body = build_stream_body(provider, request.model, request.prompt)

    logger.info(f"Starting stream pipeline for provider: {provider}, model: {request.model}")
    log_request(logger, provider, request.model, request.prompt, stream=True)

    try:
        async for token in stream_response(url, headers, body, provider):
            yield token
    except Exception as e:
        logger.error(f"Stream error: {type(e).__name__}: {e}")
        log_error(logger, type(e).__name__, provider, f"Stream failed: {str(e)}")
