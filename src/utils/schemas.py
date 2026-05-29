from pydantic import BaseModel, field_validator

# --- existing schemas (keep these) ---

class LLMRequest(BaseModel):
    provider: str
    model: str
    prompt: str

class LLMResponse(BaseModel):
    provider: str
    model: str
    content: str
    status: str

# --- new structured output schema ---

class StructuredResponse(BaseModel):
    summary: str
    keywords: list[str]
    sentiment: str

    @field_validator("sentiment")
    def sentiment_must_be_valid(cls, v):
        allowed = {"positive", "negative", "neutral"}
        if v.lower() not in allowed:
            raise ValueError(f"sentiment must be one of {allowed}, got '{v}'")
        return v.lower()

    @field_validator("keywords")
    def keywords_must_not_be_empty(cls, v):
        if len(v) == 0:
            raise ValueError("keywords list must not be empty")
        return v
