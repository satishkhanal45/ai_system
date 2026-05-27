import asyncio
import time
from utils.config import APP_NAME
from utils.logger import get_logger
from utils.schemas import LLMRequest
from services.llm_service import call_llm
from services.debug_service import run_with_trace, simulate_failure
from config_switcher import switch_provider, get_current_config

logger = get_logger(APP_NAME)

async def main():
    logger.info(f"Starting {APP_NAME}")

    prompt = "What is machine learning in one sentence?"

    # --- test 1: normal request with tracing ---
    print("\n--- Test 1: Normal Request with Tracing ---")
    config = get_current_config()
    response = await run_with_trace(config["provider"], config["model"], prompt)
    print(f"Response: {response.content}\n")

    # --- test 2: simulate API failure ---
    print("--- Test 2: Simulated API Failure ---")
    await simulate_failure(config["provider"], config["model"], prompt)
    print()

    # --- test 3: runtime provider switch ---
    print("--- Test 3: Runtime Provider Switch ---")
    switch_provider("groq", "llama-3.1-8b-instant")
    config = get_current_config()
    logger.info(f"Now using: {config['provider']} / {config['model']}")
    response = await run_with_trace(config["provider"], config["model"], prompt)
    print(f"Response after switch: {response.content}\n")

    # --- test 4: multiple concurrent requests ---
    print("--- Test 4: Multiple Concurrent Requests ---")

    requests = [
        LLMRequest(provider="groq", model="llama-3.3-70b-versatile", prompt="What is AI?"),
        LLMRequest(provider="groq", model="llama-3.3-70b-versatile", prompt="What is ML?"),
        LLMRequest(provider="groq", model="llama-3.3-70b-versatile", prompt="What is DL?"),
    ]

    # sequential — one after another
    print("\n[Sequential]")
    seq_start = time.time()
    for req in requests:
        r = await call_llm(req)
        print(f"  {req.prompt} → {r.content[:60]}...")
    seq_time = round(time.time() - seq_start, 3)
    print(f"  Sequential total time: {seq_time}s")

    # concurrent — all at once
    print("\n[Concurrent]")
    con_start = time.time()
    results = await asyncio.gather(
        call_llm(requests[0]),
        call_llm(requests[1]),
        call_llm(requests[2]),
    )
    con_time = round(time.time() - con_start, 3)
    for req, r in zip(requests, results):
        print(f"  {req.prompt} → {r.content[:60]}...")
    print(f"  Concurrent total time: {con_time}s")

    print(f"\n  Sequential: {seq_time}s  vs  Concurrent: {con_time}s")
    print(f"  Async was {round(seq_time / con_time, 1)}x faster\n")

if __name__ == "__main__":
    asyncio.run(main())