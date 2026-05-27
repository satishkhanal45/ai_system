#calls LLM and enforces structured output


from utils.schemas import LLMRequest, LLMResponse
from utils.validators import validate_llm_output
from services.llm_service import call_llm
from utils.logger import get_logger

logger = get_logger("structured_service")

# this prompt instructs the LLM to reply in strict JSON format
STRUCTURED_PROMPT = """
Analyze the following text and reply ONLY with a JSON object.
No explanation, no markdown, just raw JSON.

The JSON must follow this exact structure:
{{
  "summary": "one sentence summary",
  "keywords": ["keyword1", "keyword2", "keyword3"],
  "sentiment": "positive" or "negative" or "neutral"
}}

Text to analyze:
{user_text}
"""

async def get_structured_output(provider: str, model: str, user_text: str):
    prompt = STRUCTURED_PROMPT.format(user_text=user_text)

    request = LLMRequest(
        provider=provider,
        model=model,
        prompt=prompt
    )

    logger.info(f"Sending structured output request to {provider}")
    response: LLMResponse = await call_llm(request)

    if response.status == "error":
        logger.error("LLM call failed, cannot validate output")
        return None

    logger.info("Validating LLM output against schema")
    result = validate_llm_output(response.content)

    return result