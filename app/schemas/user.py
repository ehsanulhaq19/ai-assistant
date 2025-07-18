from pydantic import BaseModel
from datetime import datetime
from app.models.user import PlanType
from typing import Optional

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    plan_type: PlanType
    daily_query_count: int
    daily_premium_count: int
    created_at: datetime
    session_id: Optional[str] = None

    class Config:
        from_attributes = True

class UserRegisterRequest(BaseModel):
    email: str
    name: str
    password: str
    plan_type: PlanType = PlanType.FREE

class UserLoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    session_id: str = None
    user_id: int = None

class LogoutResponse(BaseModel):
    message: str

class PlanUpdateRequest(BaseModel):
    plan_type: PlanType

class PlanUpdateResponse(BaseModel):
    message: str
    user_id: int
    new_plan_type: PlanType 