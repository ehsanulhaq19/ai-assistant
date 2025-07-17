from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AIQueryResponse(BaseModel):
    id: int
    user_id: int
    session_id: str
    query_text: str
    model_used: str
    response: Optional[str]
    tokens_used: int
    cost_usd: float
    processing_time: float
    created_at: datetime

    class Config:
        from_attributes = True 