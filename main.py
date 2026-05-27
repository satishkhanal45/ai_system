import asyncio
from utils.config import APP_NAME
from utils.logger import get_logger
from utils.schemas import LLMRequest
from services.llm_service import call_llm

logger = get_logger(APP_NAME)

async def main():
    logger.info(f"Starting {APP_NAME}")

    request = LLMRequest(
        provider="groq",
        model="llama-3.3-70b-versatile",
        prompt="Say hello in one sentence."
    )

    response = await call_llm(request)
    logger.info(f"Provider : {response.provider}")
    logger.info(f"Status   : {response.status}")
    logger.info(f"Response : {response.content}")

if __name__ == "__main__":
    asyncio.run(main())