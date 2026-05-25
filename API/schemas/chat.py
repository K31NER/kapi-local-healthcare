from typing import Optional
from pydantic import BaseModel

class ChatStreamInput(BaseModel):
    question: str
    session_id: Optional[str] = None
    user_id: str
