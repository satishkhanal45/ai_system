from utils.schemas import LLMRequest
from api.client import async_post, build_body
from api.providers import PROVIDERS
from utils.logger import get_logger

logger = get_logger("chat_service")

SYSTEM_MESSAGE = {
    "role": "system",
    "content": "You are a helpful assistant. Always reply in 5 lines or less. Be concise and direct. No long explanations, no bullet points, no headers."
}

# this holds the conversation history
chat_history = [SYSTEM_MESSAGE]

def reset_history():
    """clears the conversation history"""
    global chat_history
    chat_history = [SYSTEM_MESSAGE]
    logger.info("Chat history cleared")

def get_history():
    return chat_history

async def chat(provider: str, model: str, user_message: str) -> str:
    """
    Sends a message and keeps track of the full conversation history.
    Each call appends to chat_history so the LLM remembers context.
    """

    # initialize with system message if empty
    if not chat_history:
        chat_history.append(SYSTEM_MESSAGE)

    # add user message to history
    chat_history.append({"role": "user", "content": user_message})
    logger.info(f"User: {user_message}")

    if provider not in PROVIDERS:
        logger.error(f"Unknown provider: {provider}")
        return "error: unknown provider"

    url = PROVIDERS[provider]["url"]
    headers = PROVIDERS[provider]["headers"]

    # build body using full history instead of single prompt
    body = {
        "model": model,
        "messages": chat_history,
    }

    # reuse existing async_post from client.py
    from api.client import MAX_RETRIES, TIMEOUT, parse_response
    import httpx

    reply = "error: all retries failed"

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info(f"Attempt {attempt} — sending to {provider}")
            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                response = await client.post(url, headers=headers, json=body)
                response.raise_for_status()
                data = response.json()
                reply = parse_response(provider, data)
                break
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error on attempt {attempt}: {e.response.status_code}")
            logger.error(f"Response body: {e.response.text}")
        except Exception as e:
            logger.error(f"Unexpected error on attempt {attempt}: {e}")

    # add assistant reply to history
    chat_history.append({"role": "assistant", "content": reply})

    return reply