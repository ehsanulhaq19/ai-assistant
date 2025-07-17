from sqlalchemy import Column, Integer, String, Text, DateTime, DECIMAL, Float, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base

class AIQuery(Base):
    __tablename__ = "ai_queries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(String(255), nullable=False)
    query_text = Column(Text, nullable=False)
    model_used = Column(String(50), nullable=False)
    response = Column(Text)
    tokens_used = Column(Integer, default=0)
    cost_usd = Column(DECIMAL(8, 6), default=0.000000)
    processing_time = Column(Float, default=0)
    created_at = Column(DateTime, default=func.now()) 