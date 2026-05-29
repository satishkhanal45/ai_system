#!/usr/bin/env python
"""
Simple test script to demonstrate the logging system
"""
import asyncio
import sys
from src.utils.logger import get_logger, log_request, log_response, log_error, log_structured
from src.utils.schemas import LLMRequest

logger = get_logger("test_logger")

async def test_logging():
    """Test basic logging functionality"""
    
    logger.info("=" * 60)
    logger.info("Starting logging system test")
    logger.info("=" * 60)
    
    # Test 1: Simple logging
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    
    # Test 2: Request logging
    logger.info("\n--- Test 1: Logging API Request ---")
    log_request(
        logger,
        provider="groq",
        model="llama-3.3-70b-versatile",
        prompt="What is artificial intelligence?",
        url="https://api.groq.com/openai/v1/chat/completions"
    )
    
    # Test 3: Response logging
    logger.info("\n--- Test 2: Logging API Response ---")
    log_response(
        logger,
        provider="groq",
        model="llama-3.3-70b-versatile",
        response="Artificial intelligence is the simulation of human intelligence...",
        status="success",
        elapsed_time="0.85s",
        attempt=1,
        status_code=200
    )
    
    # Test 4: Error logging
    logger.info("\n--- Test 3: Logging Error ---")
    log_error(
        logger,
        error_type="http_error",
        provider="groq",
        message="HTTP 429 - Rate Limited",
        attempt=3,
        status_code=429
    )
    
    # Test 5: Structured logging
    logger.info("\n--- Test 4: Structured Event Logging ---")
    log_structured(logger, "chat_initiated", {
        "user_id": "user_123",
        "provider": "groq",
        "model": "llama-3.3-70b-versatile",
        "conversation_turn": 1
    })
    
    # Test 6: Another error for error.log
    logger.info("\n--- Test 5: Another Error Example ---")
    log_error(
        logger,
        error_type="timeout",
        provider="gemini",
        message="Request timed out after 30 seconds",
        attempt=2
    )
    
    logger.info("\n" + "=" * 60)
    logger.info("Logging test complete!")
    logger.info("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_logging())
    print("\n✅ Logs have been written to:")
    print("   - logs/app.log (all logs)")
    print("   - logs/error.log (errors only)")
    print("   - logs/requests.log (requests only)")
