import asyncio
import json as _json
import httpx
from ..api.providers import PROVIDERS
from ..api.client import MAX_RETRIES, TIMEOUT, parse_response, parse_ollama_response
from ..utils.logger import get_logger, log_request, log_response, log_error

logger = get_logger("chat_service")

SYSTEM_PROMPT = (
    "You are a helpful assistant. Always reply in 5 lines or less. "
    "Be concise and direct. No long explanations, no bullet points, no headers."
)

SYSTEM_MESSAGE = {"role": "system", "content": SYSTEM_PROMPT}

# Conversation history in OpenAI format (role/content dicts).
# Gemini messages are converted on the fly before each request.
chat_history: list[dict] = [SYSTEM_MESSAGE]


def reset_history() -> None:
    """Clear the conversation history."""
    global chat_history
    chat_history = [SYSTEM_MESSAGE]
    logger.info("Chat history cleared")


def get_history() -> list[dict]:
    return chat_history


# ── body builders ─────────────────────────────────────────────────────────────

def _build_groq_body(model: str, history: list[dict]) -> dict:
    """OpenAI-compatible body (used by groq)."""
    return {"model": model, "messages": history}


def _build_ollama_body(model: str, history: list[dict]) -> dict:
    """Ollama /api/chat body — stream disabled so we get a single JSON object."""
    return {"model": model, "messages": history, "stream": False}


def _build_gemini_body(history: list[dict]) -> dict:
    """
    Gemini REST body.

    * system message  → systemInstruction
    * user/assistant  → contents with role 'user' / 'model'
    """
    system_parts: list[str] = []
    contents: list[dict] = []

    for msg in history:
        role = msg["role"]
        text = msg["content"]

        if role == "system":
            system_parts.append(text)
        elif role == "user":
            contents.append({"role": "user", "parts": [{"text": text}]})
        elif role == "assistant":
            contents.append({"role": "model", "parts": [{"text": text}]})

    body: dict = {"contents": contents}
    if system_parts:
        body["systemInstruction"] = {
            "parts": [{"text": "\n".join(system_parts)}]
        }
    return body


def _build_body(provider: str, model: str, history: list[dict]) -> dict:
    if provider == "gemini":
        return _build_gemini_body(history)
    if provider == "ollama":
        return _build_ollama_body(model, history)
    return _build_groq_body(model, history)


# ── main chat function ────────────────────────────────────────────────────────

async def chat(provider: str, model: str, user_message: str) -> str:
    """
    Send a message and maintain full conversation history.
    Supports groq (OpenAI format) and gemini (REST format).
    """
    if not chat_history:
        chat_history.append(SYSTEM_MESSAGE)

    chat_history.append({"role": "user", "content": user_message})
    logger.info(f"User: {user_message}")
    log_request(
        logger, provider, model, user_message,
        conversation_turn=sum(1 for m in chat_history if m["role"] == "user"),
    )

    if provider not in PROVIDERS:
        logger.error(f"Unknown provider: {provider}")
        log_error(logger, "invalid_provider", provider, "Provider not in supported list")
        return "error: unknown provider"

    url     = PROVIDERS[provider]["url"]
    headers = PROVIDERS[provider]["headers"]
    body    = _build_body(provider, model, chat_history)

    reply = "error: all retries failed"

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info(f"Attempt {attempt}/{MAX_RETRIES} — sending to {provider}")
            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                response = await client.post(url, headers=headers, json=body)
                response.raise_for_status()
                if provider == "ollama":
                    reply = parse_ollama_response(response.text)
                else:
                    data  = response.json()
                    reply = parse_response(provider, data)
                log_response(logger, provider, model, reply, "success",
                             attempt=attempt, is_chat=True)
                break
        except httpx.HTTPStatusError as e:
            status = e.response.status_code
            logger.error(f"HTTP error on attempt {attempt}/{MAX_RETRIES}: {status}")
            logger.error(f"Response body: {e.response.text}")
            log_error(logger, "http_error", provider, f"HTTP {status}", attempt=attempt)

            if status == 429:
                # Try to honour the retryDelay hint from the API
                retry_delay = 5.0
                try:
                    err_body = _json.loads(e.response.text)
                    for detail in err_body.get("error", {}).get("details", []):
                        if "retryDelay" in detail:
                            raw = detail["retryDelay"]           # e.g. "4s"
                            retry_delay = float(raw.rstrip("s")) + 1.0
                            break
                except Exception:
                    pass

                # If the daily quota is zero there's no point retrying
                try:
                    violations = err_body.get("error", {}).get("details", [])
                    for v in violations:
                        for quota in v.get("violations", []):
                            if "PerDay" in quota.get("quotaId", ""):
                                logger.error("Daily quota exhausted — skipping remaining retries.")
                                reply = "error: Gemini daily quota exhausted. Try again tomorrow or switch to groq."
                                chat_history.append({"role": "assistant", "content": reply})
                                return reply
                except Exception:
                    pass

                if attempt < MAX_RETRIES:
                    logger.info(f"Rate limited — waiting {retry_delay:.1f}s before retry...")
                    await asyncio.sleep(retry_delay)

        except Exception as e:
            logger.error(f"Unexpected error on attempt {attempt}/{MAX_RETRIES}: {type(e).__name__}: {e}")
            log_error(logger, type(e).__name__, provider, str(e), attempt=attempt)

    chat_history.append({"role": "assistant", "content": reply})
    return reply