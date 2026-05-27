#unified request/response schema


from pydantic import BaseModel

class LLMRequest(BaseModel):
    provider: str       
    model: str
    prompt: str

class LLMResponse(BaseModel):
    provider: str
    model: str
    content: str
    status: str          # "success" or "error"