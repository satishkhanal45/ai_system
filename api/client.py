#async httpx client with retries and timeouts


import httpx
from utils.logger import get_logger

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
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info(f"Attempt {attempt} — sending request to {provider}")
            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                response = await client.post(url, headers=headers, json=body)
                response.raise_for_status()
                data = response.json()
                return parse_response(provider, data)

        except httpx.TimeoutException:
            logger.warning(f"Timeout on attempt {attempt} for {provider}")

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error on attempt {attempt}: {e.response.status_code}")
            logger.error(f"Response body: {e.response.text}")
            
        except Exception as e:
            logger.error(f"Unexpected error on attempt {attempt}: {e}")

    return "error: all retries failed"