from pydantic import BaseModel

class PromptRequest(BaseModel):
    prompt: str
    negative_prompt: str = "low quality, blurry, bad anatomy"
