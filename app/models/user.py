from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class PlanType(enum.Enum):
    FREE = "free"
    PRO = "pro"
    EXPERT = "expert"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    plan_type = Column(Enum(PlanType), default=PlanType.FREE)
    daily_query_count = Column(Integer, default=0)
    daily_premium_count = Column(Integer, default=0)
    session_id = Column(String(255), nullable=True, index=True) 