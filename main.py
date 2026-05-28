import asyncio
import time
from colorama import Fore, Style
from utils.config import APP_NAME
from utils.logger import get_logger
from utils.schemas import LLMRequest
from utils.cli import (
    print_menu, print_user, print_assistant, print_success,
    print_error, print_info, print_section, print_response, input_prompt
)
from services.llm_service import call_llm
from services.stream_service import stream_llm
from services.structured_service import get_structured_output
from services.debug_service import run_with_trace, simulate_failure
from services.chat_service import chat, reset_history, get_history
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
║  6. Chat with Memory                         ║
║  0. Exit                                     ║
╚══════════════════════════════════════════════╝
"""

async def run_task1():
    print_section("T1 — System Architecture + Project Scaffold")
    print_response("Project structure", "ai_system/api, services, utils")
    print_response("Config loaded from", ".env")
    print_response("Logging", "structured via utils/logger.py")
    print_response("Module boundaries", "api/  services/  utils/")
    print_info("T1 is the scaffold — no API call needed.")
    print_info("All other tasks are built on top of this structure.")

async def run_task2():
    print_section("T2 — Multi-Provider Async API Layer")
    prompt = "What is artificial intelligence in one sentence?"
    providers = [
        ("groq", "llama-3.3-70b-versatile"),
        ("groq", "llama-3.1-8b-instant"),
    ]
    for provider, model in providers:
        request = LLMRequest(provider=provider, model=model, prompt=prompt)
        print_info(f"Sending to {provider} / {model} ...")
        response = await call_llm(request)
        if response.status == "success":
            print_success(f"{provider} / {model}")
        else:
            print_error(f"{provider} / {model} failed")
        print_response("Response", response.content)

async def run_task3():
    print_section("T3 — Streaming + Async Execution System")
    request = LLMRequest(
        provider="groq",
        model="llama-3.3-70b-versatile",
        prompt="Explain what an API is in simple terms."
    )
    print(Fore.MAGENTA + "\n  --- Stream Start ---" + Style.RESET_ALL)
    async for token in stream_llm(request):
        print(Fore.YELLOW + token + Style.RESET_ALL, end="", flush=True)
    print(Fore.MAGENTA + "\n  --- Stream End ---" + Style.RESET_ALL)

async def run_task4():
    print_section("T4 — Structured Data + Validation Layer")
    import json
    user_text = "I just got a promotion at work and I couldn't be happier!"
    print_response("Input text", user_text)
    result = await get_structured_output(
        provider="groq",
        model="llama-3.3-70b-versatile",
        user_text=user_text
    )
    if result:
        print_success("Validation passed")
        print_response("Summary  ", result.summary)
        print_response("Keywords ", str(result.keywords))
        print_response("Sentiment", result.sentiment)
        print(Fore.CYAN + "\n  --- JSON Output ---" + Style.RESET_ALL)
        print(json.dumps(result.model_dump(), indent=2))
    else:
        print_error("Failed to get structured output")

async def run_task5():
    print_section("T5 — Observability + Debugging System")
    prompt = "What is machine learning in one sentence?"

    print_info("[1/3] Request Tracing")
    config = get_current_config()
    response = await run_with_trace(config["provider"], config["model"], prompt)
    print_response("Response", response.content)

    print_info("[2/3] Simulating API Failure")
    await simulate_failure(config["provider"], config["model"], prompt)
    print_error("Failure simulation complete — check logs above.")

    print_info("[3/3] Runtime Provider Switch + Concurrent Requests")
    switch_provider("groq", "llama-3.1-8b-instant")
    config = get_current_config()
    print_success(f"Switched to: {config['provider']} / {config['model']}")

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

    print_response("Sequential", f"{seq_time}s")
    print_response("Concurrent", f"{con_time}s")
    print_success(f"Async was {round(seq_time / con_time, 1)}x faster")

async def run_chat():
    print_section("Chat with Memory")
    print_info("Type your message and press Enter.")
    print_info("Type 'history' to see full conversation.")
    print_info("Type 'reset' to clear memory.")
    print_info("Type 'exit' to return to menu.")

    provider = "groq"
    model    = "llama-3.3-70b-versatile"

    while True:
        user_input = input(Fore.GREEN + "\n  You: " + Style.RESET_ALL).strip()

        if user_input.lower() == "exit":
            break

        elif user_input.lower() == "reset":
            reset_history()
            print_success("Memory cleared.")

        elif user_input.lower() == "history":
            print_section("Chat History")
            for msg in get_history():
                if msg["role"] == "system":
                    continue
                if msg["role"] == "user":
                    print(Fore.GREEN + f"  You      : " + Style.RESET_ALL + msg["content"])
                else:
                    print(Fore.YELLOW + f"  Assistant: " + Style.RESET_ALL + msg["content"])

        elif user_input:
            reply = await chat(provider, model, user_input)
            print_assistant(reply)

TASKS = {
    "1": run_task1,
    "2": run_task2,
    "3": run_task3,
    "4": run_task4,
    "5": run_task5,
    "6": run_chat,
}

async def main():
    while True:
        print_menu(MENU)
        choice = input(Fore.CYAN + "  Select task (0-6): " + Style.RESET_ALL).strip()

        if choice == "0":
            print_success("Goodbye!")
            break
        elif choice in TASKS:
            await TASKS[choice]()
            input(Fore.CYAN + "\n  Press Enter to return to menu..." + Style.RESET_ALL)
        else:
            print_error("Invalid choice. Enter 0-6.")

if __name__ == "__main__":
    asyncio.run(main())