# AI System — Week 1

End-to-end AI system built with Python covering async API clients, streaming, structured outputs, and observability.

---

## Project Structure

```
ai_system/
├── api/
│   ├── __init__.py              # API module boundary
│   ├── client.py                # Async httpx client with retries and timeouts
│   ├── providers.py             # Provider URLs and headers (Groq, Gemini, Ollama)
│   └── streaming.py             # Async token streaming client
├── services/
│   ├── __init__.py              # Services module boundary
│   ├── llm_service.py           # Unified LLM call service
│   ├── stream_service.py        # Streaming pipeline service
│   ├── structured_service.py    # Structured output service
│   └── debug_service.py         # Request tracing and failure simulation
├── utils/
│   ├── __init__.py              # Utils module boundary
│   ├── config.py                # Environment variable loader
│   ├── logger.py                # Structured logging system
│   ├── schemas.py               # Pydantic request/response schemas
│   ├── tracer.py                # Request tracing (latency, tokens)
│   └── validators.py            # LLM output validation and JSON recovery
├── config_switcher.py           # Runtime provider switching
├── menu.py                      # Interactive terminal task runner
├── main.py                      # Direct task runner
├── .env                         # API keys and config (not committed)
├── .gitignore                   # Ignores .env and .venv
└── pyproject.toml               # Project dependencies (uv)
```

---

## Setup

**1. Install uv**
```bash
pip install uv
```

**2. Create and enter the project**
```bash
uv init ai_system
cd ai_system
```

**3. Install dependencies**
```bash
uv add httpx python-dotenv pydantic
```

**4. Create `.env` file**
```env
APP_NAME=ai_system
LOG_LEVEL=INFO
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
OLLAMA_BASE_URL=http://localhost:11434
```

Get your keys from:
- Groq → https://console.groq.com
- Gemini → https://aistudio.google.com/apikey
- Ollama → https://ollama.com/download (no key needed, runs locally)

---

## Running

### Interactive menu
```bash
uv run menu.py
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
║  0. Exit                                     ║
╚══════════════════════════════════════════════╝
```

Enter a number to run the task. Press Enter after each task to return to the menu.

### Direct run
```bash
uv run main.py
```

---

## Tasks

**T1 — System Architecture + Project Scaffold**
Sets up the project folder structure, `.env` config loading, structured logging, and module boundaries (`api/`, `services/`, `utils/`). This is the foundation every other task is built on.

**T2 — Multi-Provider Async API Layer**
Async HTTP client using `httpx` supporting Groq, Gemini, and Ollama. All providers share a unified request/response schema via Pydantic. Retries up to 3 times on failure, respects a 30 second timeout per attempt.

**T3 — Streaming + Async Execution System**
Streams LLM responses token by token in real time instead of waiting for the full response. Measures time-to-first-token and total latency on every stream. Handles partial failures mid-stream with retry logic.

**T4 — Structured Data + Validation Layer**
Forces the LLM to return a strict JSON format with `summary`, `keywords`, and `sentiment` fields. Recovers from common malformed JSON patterns: markdown code fences, single quotes, trailing commas, and extra text around the JSON. Validates all fields strictly using Pydantic.

**T5 — Observability + Debugging System**
Logs every request as a structured JSON event including prompt, response, latency, and token counts. Simulates API failures with an invalid model name to verify retry and error handling. Switches providers at runtime without restarting. Demonstrates async speedup by running concurrent requests vs sequential.

---

## Dependencies

| Package | Purpose |
|---|---|
| `httpx` | Async HTTP client for LLM API calls |
| `pydantic` | Schema validation and structured outputs |
| `python-dotenv` | Loads `.env` into environment variables |

---

## Models

| Provider | Model | Notes |
|---|---|---|
| Groq | `llama-3.3-70b-versatile` | Primary model, fast and capable |
| Groq | `llama-3.1-8b-instant` | Smaller, used for provider switch demo |
| Gemini | `gemini-2.0-flash` | Free tier has daily quota limit |
| Ollama | `llama3.2` | Local only, requires `ollama serve` running |

---

## Notes

- `.env` is listed in `.gitignore` 
- Groq is the recommended provider — free, fast, and no daily quota issues
- Gemini free tier exhausts quickly — switch to Groq if you hit a 429 error
- Ollama requires the app installed locally and `ollama serve` running in a separate terminal
- All provider configs live in `api/providers.py` — adding a new provider is one block
- Runtime provider switching is handled by `config_switcher.py` without restarting the app