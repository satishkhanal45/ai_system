import time
from utils.schemas import LLMRequest
from utils.tracer import trace_request
from services.llm_service import call_llm
from utils.logger import get_logger

logger = get_logger("debug_service")

async def run_with_trace(provider: str, model: str, prompt: str):
    """normal request with full tracing"""
    request = LLMRequest(provider=provider, model=model, prompt=prompt)

    logger.info(f"Sending request to {provider}")
    start_time = time.time()

    response = await call_llm(request)

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

    request = LLMRequest(
        provider=provider,
        model="invalid-model-xyz",   # this will cause a 400 error
        prompt=prompt
    )

    start_time = time.time()
    response = await call_llm(request)

    logger.error(f"Simulated failure result: {response.status}")
    logger.error(f"Simulated failure response: {response.content}")

    trace_request(
        provider=provider,
        model="invalid-model-xyz",
        prompt=prompt,
        response=response.content,
        start_time=start_time
    )

    return response