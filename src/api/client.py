#async httpx client with retries and timeouts


import httpx
import time
from .providers import PROVIDERS
from ..utils.logger import get_logger, log_request, log_response, log_error

logger = get_logger("client")

TIMEOUT = 30       # seconds
MAX_RETRIES = 3

def build_body(provider: str, model: str, prompt: str) -> dict:
    if provider == "groq" or provider == "ollama":
        return {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
        }
    elif provider == "gemini":
        return {
            "contents": [{"parts": [{"text": prompt}]}]
        }

def parse_response(provider: str, data: dict) -> str:
    if provider == "groq" or provider == "ollama":
        return data["choices"][0]["message"]["content"]
    elif provider == "gemini":
        return data["candidates"][0]["content"]["parts"][0]["text"]

async def async_post(url: str, headers: dict, body: dict, provider: str, model: str) -> str:
    prompt = body.get("messages", [{}])[0].get("content", "") if "messages" in body else body.get("contents", [{}])[0].get("parts", [{}])[0].get("text", "")
    
    # Log the request
    log_request(logger, provider, model, prompt, url=url, attempt=1)
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            start_time = time.time()
            logger.info(f"Attempt {attempt}/{MAX_RETRIES} — sending request to {provider} (model: {model})")
            
            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                response = await client.post(url, headers=headers, json=body)
                elapsed_time = time.time() - start_time
                
                response.raise_for_status()
                data = response.json()
                content = parse_response(provider, data)
                
                # Log successful response
                log_response(
                    logger, 
                    provider, 
                    model, 
                    content, 
                    "success",
                    attempt=attempt,
                    elapsed_time=f"{elapsed_time:.2f}s",
                    status_code=response.status_code
                )
                return content

        except httpx.TimeoutException:
            logger.warning(f"Timeout on attempt {attempt}/{MAX_RETRIES} for {provider}")
            log_error(logger, "timeout", provider, f"Request timed out after {TIMEOUT}s", attempt=attempt)

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error on attempt {attempt}/{MAX_RETRIES}: {e.response.status_code}")
            logger.error(f"Response body: {e.response.text}")
            log_error(
                logger, 
                "http_error", 
                provider, 
                f"HTTP {e.response.status_code}",
                attempt=attempt,
                status_code=e.response.status_code
            )
            
        except Exception as e:
            logger.error(f"Unexpected error on attempt {attempt}/{MAX_RETRIES}: {type(e).__name__}: {e}")
            log_error(
                logger, 
                type(e).__name__, 
                provider, 
                str(e),
                attempt=attempt
            )

    error_message = "error: all retries failed"
    log_error(logger, "max_retries_exceeded", provider, error_message)
    return error_message
