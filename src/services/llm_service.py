#calls the client, returns unified response

from ..api.client import async_post, build_body
from ..api.providers import PROVIDERS
from ..utils.schemas import LLMRequest, LLMResponse
from ..utils.logger import get_logger, log_response, log_error

logger = get_logger("llm_service")

async def call_llm(request: LLMRequest) -> LLMResponse:
    provider = request.provider

    if provider not in PROVIDERS:
        logger.error(f"Unknown provider: {provider}")
        log_error(logger, "invalid_provider", provider, f"Provider not in supported list")
        return LLMResponse(
            provider=provider,
            model=request.model,
            content="error: unknown provider",
            status="error"
        )

    url = PROVIDERS[provider]["url"]
    headers = PROVIDERS[provider]["headers"]
    body = build_body(provider, request.model, request.prompt)

    content = await async_post(url, headers, body, provider, request.model)

    status = "error" if content.startswith("error") else "success"
    
    # Log the final response status
    if status == "success":
        log_response(logger, provider, request.model, content, status)
    else:
        log_error(logger, "api_error", provider, content)

    return LLMResponse(
        provider=provider,
        model=request.model,
        content=content,
        status=status
    )
