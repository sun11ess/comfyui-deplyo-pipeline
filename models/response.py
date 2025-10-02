from pydantic import BaseModel
from datetime import datetime

class GenerationResponse(BaseModel):
    id: int
    workflow_name: str
    prompt: str
    negative_prompt: str
    file_path: str
    created_at: datetime

    class Config:
        orm_mode = True  # allows SQLAlchemy objects to be converted
