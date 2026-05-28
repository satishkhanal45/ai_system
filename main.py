import asyncio
import time
from utils.config import APP_NAME
from utils.logger import get_logger
from utils.schemas import LLMRequest
from services.llm_service import call_llm
from services.stream_service import stream_llm
from services.structured_service import get_structured_output
from services.debug_service import run_with_trace, simulate_failure
from config_switcher import switch_provider, get_current_config

logger = get_logger(APP_NAME)

MENU = """
╔══════════════════════════════════════════════╗
║         AI System — Week 1 Task Runner       ║
╠══════════════════════════════════════════════╣
║  1. System Architecture + Project Scaffold   ║
║  2. Multi-Provider Async API Layer           ║
║  3. Streaming + Async Execution System       ║
║  4. Structured Data + Validation Layer       ║
║  5. Observability + Debugging System         ║
║  0. Exit                                     ║
╚══════════════════════════════════════════════╝
"""

async def run_task1():
    print("\n[T1] System Architecture + Project Scaffold")
    print("  Project structure  : ai_system/api, services, utils")
    print("  Config loaded from : .env")
    print("  Logging            : structured via utils/logger.py")
    print("  Module boundaries  : api/ services/ utils/")
    print("  All other tasks are built on top of this structure.")

async def run_task2():
    print("\n[T2] Multi-Provider Async API Layer")
    prompt = "What is artificial intelligence in one sentence?"
    providers = [
        ("groq",  "llama-3.3-70b-versatile"),
        ("groq",  "llama-3.1-8b-instant"),
    ]
    for provider, model in providers:
        request = LLMRequest(provider=provider, model=model, prompt=prompt)
        print(f"\n  Sending to {provider} / {model} ...")
        response = await call_llm(request)
        print(f"  Status   : {response.status}")
        print(f"  Response : {response.content}")

async def run_task3():
    print("\n[T3] Streaming + Async Execution System")
    request = LLMRequest(
        provider="groq",
        model="llama-3.3-70b-versatile",
        prompt="Explain what an API is in simple terms."
    )
    print("\n  --- Stream Start ---")
    async for token in stream_llm(request):
        print(token, end="", flush=True)
    print("\n  --- Stream End ---")

async def run_task4():
    print("\n[T4] Structured Data + Validation Layer")
    import json
    from services.structured_service import get_structured_output
    user_text = "I just got a promotion at work and I couldn't be happier!"
    print(f"  Input text: {user_text}")
    result = await get_structured_output(
        provider="groq",
        model="llama-3.3-70b-versatile",
        user_text=user_text
    )
    if result:
        print("\n  --- Structured Output ---")
        print(f"  Summary   : {result.summary}")
        print(f"  Keywords  : {result.keywords}")
        print(f"  Sentiment : {result.sentiment}")
        print("\n  --- JSON Output ---")
        print(json.dumps(result.model_dump(), indent=2))
    else:
        print("  Failed to get structured output")

async def run_task5():
    print("\n[T5] Observability + Debugging System")
    prompt = "What is machine learning in one sentence?"

    print("\n  [1/3] Request Tracing")
    config = get_current_config()
    response = await run_with_trace(config["provider"], config["model"], prompt)
    print(f"  Response : {response.content}")

    print("\n  [2/3] Simulating API Failure")
    await simulate_failure(config["provider"], config["model"], prompt)
    print("  Failure simulation complete — check logs above.")

    print("\n  [3/3] Runtime Provider Switch + Concurrent Requests")
    switch_provider("groq", "llama-3.1-8b-instant")
    config = get_current_config()
    print(f"  Switched to: {config['provider']} / {config['model']}")

    requests = [
        LLMRequest(provider="groq", model="llama-3.3-70b-versatile", prompt="What is AI?"),
        LLMRequest(provider="groq", model="llama-3.3-70b-versatile", prompt="What is ML?"),
        LLMRequest(provider="groq", model="llama-3.3-70b-versatile", prompt="What is DL?"),
    ]

    seq_start = time.time()
    for req in requests:
        await call_llm(req)
    seq_time = round(time.time() - seq_start, 3)

    con_start = time.time()
    await asyncio.gather(*[call_llm(req) for req in requests])
    con_time = round(time.time() - con_start, 3)

    print(f"  Sequential : {seq_time}s")
    print(f"  Concurrent : {con_time}s")
    print(f"  Async was {round(seq_time / con_time, 1)}x faster")

TASKS = {
    "1": run_task1,
    "2": run_task2,
    "3": run_task3,
    "4": run_task4,
    "5": run_task5,
}

async def main():
    while True:
        print(MENU)
        choice = input("  Select task (0-5): ").strip()

        if choice == "exit" or choice == "0":
            print("\n  Goodbye!\n")
            break
        elif choice in TASKS:
            await TASKS[choice]()
            input("\n  Press Enter to return to menu...")
        else:
            print("\n  Invalid choice. Enter 0-5.")

if __name__ == "__main__":
    asyncio.run(main())