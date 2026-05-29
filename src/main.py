import asyncio
import argparse
import sys
import time
from colorama import Fore, Style
from .utils.config import APP_NAME
from .utils.logger import get_logger
from .utils.schemas import LLMRequest
from .utils.cli import (
    print_menu, print_user, print_assistant, print_success,
    print_error, print_info, print_section, print_response, input_prompt
)
from .services.llm_service import call_llm
from .services.stream_service import stream_llm
from .services.structured_service import get_structured_output
from .services.debug_service import run_with_trace, simulate_failure
from .services.chat_service import chat, reset_history, get_history
from .config_switcher import switch_provider, get_current_config

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
    user_prompt = input(Fore.GREEN + "\n  Enter your prompt: " + Style.RESET_ALL).strip()
    if not user_prompt:
        print_error("No prompt entered.")
        return
    request = LLMRequest(
        provider="groq",
        model="llama-3.3-70b-versatile",
        prompt=user_prompt
    )
    print(Fore.MAGENTA + "\n  --- Stream Start ---" + Style.RESET_ALL)
    async for token in stream_llm(request):
        print(Fore.YELLOW + token + Style.RESET_ALL, end="", flush=True)
        await asyncio.sleep(0.02)
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

# ── provider / model catalogue ────────────────────────────────────────────────
PROVIDER_MODELS = {
    "groq": {
        "default": "llama-3.3-70b-versatile",
        "thinking": None,           # Groq has no native thinking mode
        "models": [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
        ],
    },
    "gemini": {
        "default": "gemini-2.5-flash-preview-05-20",
        "thinking": "gemini-2.5-flash-preview-05-20",
        "models": [
            "gemini-2.5-flash-preview-05-20",
            "gemini-2.0-flash",
            "gemini-1.5-pro",
        ],
    },
    "ollama": {
        "default": "llama3.2",
        "thinking": None,
        "models": [
            "llama3.2",
            "llama3.2:1b",
            "phi3",
            "mistral",
        ],
    },
}

THINKING_LEVELS = ["low", "medium", "high"]

# ── argparse helper ───────────────────────────────────────────────────────────
def build_chat_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="chat",
        description="Chat with Memory — option 6",
        add_help=False,
    )
    parser.add_argument(
        "--provider",
        choices=list(PROVIDER_MODELS.keys()),
        default="groq",
        help="LLM provider to use (default: groq)",
    )
    parser.add_argument(
        "--thinking",
        choices=THINKING_LEVELS,
        default=None,
        metavar="LEVEL",
        help="Enable thinking mode with budget level: low | medium | high (gemini only)",
    )
    return parser


def parse_chat_args(raw: list[str]) -> argparse.Namespace | None:
    """Parse a list of CLI tokens; return None on --help or parse error."""
    parser = build_chat_parser()
    try:
        return parser.parse_args(raw)
    except SystemExit:
        return None


def resolve_model(provider: str, thinking: str | None) -> tuple[str, bool]:
    """
    Return (model_name, thinking_active).

    Rules
    -----
    - thinking requested + gemini  → use thinking model, flag True
    - thinking requested + groq    → warn and fall back, flag False
    - no thinking                  → use provider default, flag False
    """
    cfg = PROVIDER_MODELS[provider]

    if thinking is not None:
        if provider == "gemini" and cfg["thinking"]:
            return cfg["thinking"], True
        else:
            print_error(
                f"Thinking mode is not supported for '{provider}'. "
                "Falling back to the standard model."
            )
    return cfg["default"], False


def print_chat_config(provider: str, model: str, thinking: bool, level: str | None) -> None:
    """Pretty-print the resolved chat configuration."""
    print()
    print(Fore.CYAN + "  ┌─ Chat Configuration " + "─" * 24 + Style.RESET_ALL)
    print(Fore.CYAN + f"  │  Provider : " + Style.RESET_ALL + provider)
    print(Fore.CYAN + f"  │  Model    : " + Style.RESET_ALL + model)
    thinking_str = (
        Fore.GREEN + f"enabled ({level})" + Style.RESET_ALL
        if thinking
        else Fore.YELLOW + "disabled" + Style.RESET_ALL
    )
    print(Fore.CYAN + f"  │  Thinking : " + Style.RESET_ALL + thinking_str)
    print(Fore.CYAN + "  └" + "─" * 35 + Style.RESET_ALL)
    print()


# ── interactive argument prompt (shown when option 6 is selected) ─────────────
def prompt_chat_args() -> list[str]:
    """
    Ask the user interactively for --provider and --thinking, then return
    the equivalent argv list so parse_chat_args() can handle it uniformly.
    """
    print()
    print(Fore.CYAN + "  Configure Chat with Memory" + Style.RESET_ALL)
    print(Fore.CYAN + "  (press Enter to keep defaults)" + Style.RESET_ALL)
    print()

    # ── provider ──────────────────────────────────────────────────────────────
    providers = list(PROVIDER_MODELS.keys())
    print(Fore.CYAN + "  Providers:" + Style.RESET_ALL)
    for i, p in enumerate(providers, 1):
        default_tag = Fore.GREEN + "  [default]" + Style.RESET_ALL if p == "groq" else ""
        print(f"    {i}. {p}{default_tag}")

    valid = {str(i): p for i, p in enumerate(providers, 1)}
    raw_provider = input(
        Fore.GREEN + f"  Select provider (1-{len(providers)}, default 1): " + Style.RESET_ALL
    ).strip()
    chosen_provider = valid.get(raw_provider, providers[0] if raw_provider == "" else None)
    if chosen_provider is None:
        print_error("Invalid choice; defaulting to groq.")
        chosen_provider = "groq"

    argv: list[str] = ["--provider", chosen_provider]

    # ── ollama: let user pick a local model ───────────────────────────────────
    if chosen_provider == "ollama":
        models = PROVIDER_MODELS["ollama"]["models"]
        print(Fore.CYAN + "  Local models:" + Style.RESET_ALL)
        for i, m in enumerate(models, 1):
            default_tag = Fore.GREEN + "  [default]" + Style.RESET_ALL if m == PROVIDER_MODELS["ollama"]["default"] else ""
            print(f"    {i}. {m}{default_tag}")
        raw_model = input(
            Fore.GREEN + f"  Select model (1-{len(models)}, default 1): " + Style.RESET_ALL
        ).strip()
        model_map = {str(i): m for i, m in enumerate(models, 1)}
        chosen_model = model_map.get(raw_model, models[0])
        # Override the default in PROVIDER_MODELS so resolve_model picks it up
        PROVIDER_MODELS["ollama"]["default"] = chosen_model
        print_info(f"Thinking mode is not available for ollama; skipping.")

    # ── thinking mode (gemini only) ───────────────────────────────────────────
    elif chosen_provider == "gemini":
        enable = input(Fore.GREEN + "  Enable thinking mode? (y/N): " + Style.RESET_ALL).strip().lower()
        if enable in {"y", "yes"}:
            print(Fore.CYAN + "  Thinking budget level:" + Style.RESET_ALL)
            for i, lvl in enumerate(THINKING_LEVELS, 1):
                print(f"    {i}. {lvl}")
            raw_lvl = input(Fore.GREEN + "  Select level (1-3, default 2): " + Style.RESET_ALL).strip()
            level_map = {"1": "low", "2": "medium", "3": "high", "": "medium"}
            chosen_level = level_map.get(raw_lvl, "medium")
            argv += ["--thinking", chosen_level]

    else:
        print_info("Thinking mode is only available for Gemini; skipping.")

    return argv


# ── main chat loop ────────────────────────────────────────────────────────────
async def run_chat(argv: list[str] | None = None):
    """
    Entry point for option 6.

    argv  - pre-built argument list (used when called programmatically).
            When None, the user is prompted interactively.
    """
    print_section("Chat with Memory")

    # ── resolve configuration ─────────────────────────────────────────────────
    if argv is None:
        argv = prompt_chat_args()

    args = parse_chat_args(argv)
    if args is None:
        return  # --help was printed or parse failed

    provider = args.provider
    thinking_level = args.thinking
    model, thinking_active = resolve_model(provider, thinking_level)

    print_chat_config(provider, model, thinking_active, thinking_level)

    # ── usage hints ───────────────────────────────────────────────────────────
    print_info("Type your message and press Enter.")
    print_info("Type 'history' to see full conversation.")
    print_info("Type 'reset' to clear memory.")
    print_info("Type 'exit' to return to menu.")

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
                    print(Fore.GREEN + "  You      : " + Style.RESET_ALL + msg["content"])
                else:
                    print(Fore.YELLOW + "  Assistant: " + Style.RESET_ALL + msg["content"])

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
    # ── CLI shortcut: `python -m src.main 6 --provider gemini --thinking high` ─
    cli_argv = sys.argv[1:]
    if cli_argv and cli_argv[0] == "6":
        await run_chat(argv=cli_argv[1:] or None)
        return

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