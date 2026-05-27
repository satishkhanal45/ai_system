#provider URLs and headers

from utils.config import GROQ_API_KEY, GEMINI_API_KEY, OLLAMA_BASE_URL

PROVIDERS = {
    "groq": {
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "headers": {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        },
    },
    "gemini": {
        "url": f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}",
        "headers": {
            "Content-Type": "application/json",
        },
    },
    "ollama": {
        "url": f"{OLLAMA_BASE_URL}/api/chat",
        "headers": {
            "Content-Type": "application/json",
        },
    },
}