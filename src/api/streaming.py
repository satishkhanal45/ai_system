# Async streaming client

import httpx
import time
import json
from ..utils.logger import get_logger, log_request, log_error

logger = get_logger("streaming")

TIMEOUT = 60
MAX_RETRIES = 3

def build_stream_body(provider: str, model: str, prompt: str) -> dict:
    if provider == "groq" or provider == "ollama":
        return {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": True,
        }
    elif provider == "gemini":
        return {
            "contents": [{"parts": [{"text": prompt}]}]
        }

async def stream_response(url: str, headers: dict, body: dict, provider: str):
    """
    Streams tokens from the LLM provider one by one.
    Yields each token as it arrives.
    Also tracks time-to-first-token and total latency.
    """
    start_time = time.time()
    first_token_time = None
    token_count = 0

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info(f"Attempt {attempt}/{MAX_RETRIES} — starting stream from {provider}")

            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                async with client.stream("POST", url, headers=headers, json=body) as response:
                    response.raise_for_status()

                    async for line in response.aiter_lines():

                        # groq and ollama send lines like: data: {...}
                        if provider in ("groq", "ollama"):
                            if not line.startswith("data:"):
                                continue

                            chunk = line[len("data:"):].strip()

                            if chunk == "[DONE]":
                                break

                            try:
                                data = json.loads(chunk)
                                delta = data["choices"][0]["delta"]
                                if "content" not in delta:
                                    continue
                                token = delta["content"]
                            except Exception:
                                continue

                        # gemini streams differently — full json each time
                        elif provider == "gemini":
                            try:
                                data = json.loads(line)
                                token = data["candidates"][0]["content"]["parts"][0]["text"]
                            except Exception:
                                continue

                        if token:
                            token_count += 1
                            # record time to first token
                            if first_token_time is None:
                                first_token_time = time.time()
                                ttft = first_token_time - start_time
                                logger.info(f"Time to first token: {ttft:.3f}s")

                            yield token

            # if stream completed successfully, log total latency and stop retrying
            total_time = time.time() - start_time
            logger.info(f"Stream complete. Total latency: {total_time:.3f}s, tokens: {token_count}")
            return

        except httpx.TimeoutException:
            logger.warning(f"Timeout on attempt {attempt}/{MAX_RETRIES}")
            log_error(logger, "stream_timeout", provider, f"Stream request timed out after {TIMEOUT}s", attempt=attempt)

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error on attempt {attempt}/{MAX_RETRIES}: {e.response.status_code}")
            logger.error(f"Response body: {e.response.text}")
            log_error(logger, "stream_http_error", provider, f"HTTP {e.response.status_code}", attempt=attempt)

        except Exception as e:
            logger.error(f"Unexpected error on attempt {attempt}/{MAX_RETRIES}: {type(e).__name__}: {e}")
            log_error(logger, type(e).__name__, provider, f"Stream error: {str(e)}", attempt=attempt)

    logger.error("All retries failed for streaming")
    log_error(logger, "stream_max_retries_exceeded", provider, "All stream retries failed")
