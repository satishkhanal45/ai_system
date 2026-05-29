import time
from ..utils.schemas import LLMRequest
from ..utils.tracer import trace_request
from .llm_service import call_llm
from ..utils.logger import get_logger, log_request, log_response, log_error

logger = get_logger("debug_service")

async def run_with_trace(provider: str, model: str, prompt: str):
    """normal request with full tracing"""
    request = LLMRequest(provider=provider, model=model, prompt=prompt)

    logger.info(f"Sending request to {provider} with tracing enabled")
    log_request(logger, provider, model, prompt, tracing=True)
    
    start_time = time.time()

    response = await call_llm(request)
    elapsed_time = time.time() - start_time

    if response.status == "success":
        log_response(logger, provider, model, response.content, response.status, elapsed_time=f"{elapsed_time:.2f}s", tracing=True)
    else:
        log_error(logger, "traced_request_error", provider, response.content, elapsed_time=f"{elapsed_time:.2f}s")

    trace_request(
        provider=provider,
        model=model,
        prompt=prompt,
        response=response.content,
        start_time=start_time
    )

    return response

async def simulate_failure(provider: str, model: str, prompt: str):
    """simulates API failure by using a bad model name"""
    logger.info("Simulating API failure with bad model name")
    log_request(logger, provider, "invalid-model-xyz", prompt, simulation=True)

    request = LLMRequest(
        provider=provider,
        model="invalid-model-xyz",   # this will cause a 400 error
        prompt=prompt
    )

    start_time = time.time()
    response = await call_llm(request)
    elapsed_time = time.time() - start_time

    logger.error(f"Simulated failure result: {response.status}")
    logger.error(f"Simulated failure response: {response.content}")
    log_error(logger, "simulated_failure", provider, response.content, elapsed_time=f"{elapsed_time:.2f}s")

    trace_request(
        provider=provider,
        model="invalid-model-xyz",
        prompt=prompt,
        response=response.content,
        start_time=start_time
    )

    return response
