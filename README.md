# AI System — Week 1

End-to-end AI system built with Python covering async API clients, streaming, structured outputs, observability, and a chat interface with memory.

---

## Project Structure

```
AI_SYSTEM/
├── src/
│   ├── api/
│   │   ├── __init__.py              # API module boundary
│   │   ├── client.py                # Async httpx client with retries and timeouts
│   │   ├── providers.py             # Provider URLs and headers (Groq, Gemini, Ollama)
│   │   └── streaming.py             # Async token streaming client
│   ├── services/
│   │   ├── __init__.py              # Services module boundary
│   │   ├── chat_service.py          # Chat with memory service
│   │   ├── debug_service.py         # Request tracing and failure simulation
│   │   ├── llm_service.py           # Unified LLM call service
│   │   ├── stream_service.py        # Streaming pipeline service
│   │   └── structured_service.py    # Structured output + validation service
│   ├── utils/
│   │   ├── __init__.py              # Utils module boundary
│   │   ├── cli.py                   # CLI colors and formatting helpers
│   │   ├── config.py                # Environment variable loader
│   │   ├── logger.py                # Structured logging system
│   │   ├── schemas.py               # Pydantic request/response schemas
│   │   ├── tracer.py                # Request tracing (latency, tokens)
│   │   └── validators.py            # LLM output validation and JSON recovery
│   ├── config_switcher.py           # Runtime provider switching
│   └── main.py                      # Interactive terminal task runner (entry point)
├── logs/
│   ├── app.log                      # All application logs
│   ├── error.log                    # Error-only logs
│   └── requests.log                 # Request/response logs
├── .env                             # API keys and config (not committed)
├── .gitignore                       # Ignores .env, .venv, logs/
├── .python-version                  # Python version pin
├── pyproject.toml                   # Project dependencies (uv)
├── test_logging.py                  # Logging test script
├── uv.lock                          # Dependency lockfile
└── README.md                        # Project documentation
```

---

## Setup

**1. Install uv**
```bash
pip install uv
```

**2. Clone and enter the project**
```bash
cd ai_system
```

**3. Install dependencies**
```bash
uv add httpx python-dotenv pydantic colorama
```

**4. Create `.env` file**
```env
APP_NAME=ai_system
LOG_LEVEL=INFO
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
OLLAMA_BASE_URL=http://localhost:11434
```

> `LOG_LEVEL` accepts both uppercase and lowercase values (`INFO` or `info`).

Get your keys from:
- Groq → https://console.groq.com
- Gemini → https://aistudio.google.com/apikey
- Ollama → https://ollama.com/download (no key needed, runs locally)

**5. Ollama setup (optional, for local models)**
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model
ollama pull llama3.2

# Ollama starts automatically — verify it's running
curl http://localhost:11434/api/tags
```

---

## Running

```bash
uv run python -m src.main
```

```
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
```

Enter a number to run the task. Press Enter after each task to return to the menu.

You can also launch Chat with Memory directly from the terminal with arguments:
```bash
uv run python -m src.main 6 --provider groq
uv run python -m src.main 6 --provider gemini --thinking high
uv run python -m src.main 6 --provider ollama
```

---

## Tasks

**T1 — System Architecture + Project Scaffold**
Sets up the project folder structure, `.env` config loading, structured logging, and module boundaries. This is the foundation every other task is built on. No API call is made — this task is about the project organization itself.

**T2 — Multi-Provider Async API Layer**
Async HTTP client using `httpx` supporting Groq, Gemini, and Ollama. All providers share a unified request/response schema via Pydantic. Automatically retries up to 3 times on failure and respects a 30 second timeout per attempt.

**T3 — Streaming + Async Execution System**
Prompts you for a custom input, then streams the LLM response token by token in real time with a slight delay between tokens for a natural reading pace. Measures time-to-first-token and total latency on every stream.

**T4 — Structured Data + Validation Layer**
Forces the LLM to return a strict JSON format containing `summary`, `keywords`, and `sentiment` fields. Recovers from common malformed JSON patterns including markdown code fences, single quotes, trailing commas, and extra text around the JSON. Validates all fields strictly using Pydantic.

**T5 — Observability + Debugging System**
Logs every request as a structured JSON event including prompt, response, latency, and token counts. Simulates API failures with an invalid model name to verify retry and error handling. Switches providers at runtime without restarting. Demonstrates async speedup by running concurrent requests versus sequential.

**T6 — Chat with Memory**
Conversational chat interface that remembers the full conversation history across turns. Supports three providers — Groq, Gemini, and Ollama — selected interactively at startup. Gemini supports thinking mode at low, medium, or high budget levels. Ollama runs fully locally with no API key or quota. Replies are kept to 5 lines or less via a system prompt.

---

## Chat with Memory — Provider Selection

When you select option 6, you are prompted to configure the session before chatting:

```
  Providers:
    1. groq  [default]
    2. gemini
    3. ollama
  Select provider (1-3, default 1):
```

**Groq** (default) — fastest, generous free tier, no daily quota issues.

**Gemini** — additionally prompts for thinking mode:
```
  Enable thinking mode? (y/N): y
  Thinking budget level:
    1. low
    2. medium
    3. high
  Select level (1-3, default 2):
```
Thinking mode uses `gemini-2.5-flash-preview-05-20` with extended reasoning. The free tier has a daily quota — switch to Groq if you hit a 429 error.

**Ollama** — additionally prompts for a local model:
```
  Local models:
    1. llama3.2  [default]
    2. llama3.2:1b
    3. phi3
    4. mistral
  Select model (1-4, default 1):
```
Runs fully offline. Requires Ollama installed and the chosen model pulled (`ollama pull llama3.2`).

---

## Chat Commands

When running task 6 (Chat with Memory):

| Command | Action |
|---|---|
| `history` | Shows the full conversation so far |
| `reset` | Clears conversation memory |
| `exit` | Returns to the main menu |

---

## Logging

All logs are saved permanently to `logs/app.log`. Every request, response, and error is recorded with a timestamp.

```bash
cat logs/app.log        # view all logs
tail -f logs/app.log    # watch logs live as they are written
```

---

## CLI Colors

| Color | Meaning |
|---|---|
| Cyan | Menu, labels, info messages |
| Green | Success messages, user input |
| Yellow | Assistant responses, streamed tokens |
| Magenta | Section headers, stream markers |
| Red | Errors and failures |

---

## Dependencies

| Package | Purpose |
|---|---|
| `httpx` | Async HTTP client for LLM API calls |
| `pydantic` | Schema validation and structured outputs |
| `python-dotenv` | Loads `.env` into environment variables |
| `colorama` | Terminal colors and formatting |

---

## Models

| Provider | Model | Notes |
|---|---|---|
| Groq | `llama-3.3-70b-versatile` | Primary model, fast and capable |
| Groq | `llama-3.1-8b-instant` | Smaller, used for provider switch demo in T5 |
| Gemini | `gemini-2.5-flash-preview-05-20` | Default and thinking model; free tier has daily quota |
| Ollama | `llama3.2` | Default local model; pull with `ollama pull llama3.2` |
| Ollama | `llama3.2:1b` | Smaller/faster local variant |
| Ollama | `phi3` | Microsoft model, good quality for its size |
| Ollama | `mistral` | 7B model, strong general purpose |

---

## Notes

- `.env` is listed in `.gitignore` 
- `logs/` is listed in `.gitignore` — log files are local only
- `LOG_LEVEL` in `.env` accepts both `INFO` and `info` (case-insensitive)
- Groq is the recommended provider — free, fast, and no daily quota issues
- Gemini free tier exhausts quickly — if you hit a 429 with a daily quota violation, wait until the next day or add billing at aistudio.google.com
- Ollama requires the app installed locally; it starts automatically on install and runs in the background
- All provider configs live in `src/api/providers.py` — adding a new provider requires one block there and one entry in `PROVIDER_MODELS` in `main.py`
- Runtime provider switching is handled by `config_switcher.py` without restarting the app
- Chat memory works by sending the full conversation history to the LLM on every request
- Ollama uses a different JSON response format from Groq/Gemini — `parse_ollama_response()` in `client.py` handles this