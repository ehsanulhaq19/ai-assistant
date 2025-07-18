from typing import Optional
from sqlalchemy.orm import Session
from app.services.base_ai_service import BaseAIService, AIResponse
from app.services.openai_service import OpenAIService
from app.services.claude_service import ClaudeService
from app.models import User, AIQuery, PlanType
from app.repository import UserRepository, AIQueryRepository
from app.core.config import settings
from app.core.models_config import ModelConfig
import logging

logger = logging.getLogger(__name__)

class AIRouterService:
    
    def __init__(self):
        self.openai_service = OpenAIService(
            api_key=settings.OPENAI_API_KEY,
            organization=settings.OPENAI_ORGANIZATION
        )
        self.claude_service = ClaudeService(api_key=settings.ANTHROPIC_API_KEY)
    
    async def select_model(self, query: str, user_plan: PlanType) -> tuple[str, BaseAIService]:
        complexity = self.openai_service.get_query_complexity(query)
        is_code, is_creative = await self.openai_service.classify_query_type(query)
        
        if is_code:
            return "gpt-4o", self.openai_service
        elif is_creative:
            return "claude-3-5-sonnet-20241022", self.claude_service
        elif complexity == "simple":
            return "gpt-4o-mini", self.openai_service
        elif complexity == "complex":
            return "claude-3-5-sonnet-20241022", self.claude_service
        else:
            return "gpt-4o-mini", self.openai_service
    
    async def execute_query(
        self, 
        query: str, 
        user_id: int, 
        session_id: str, 
        db: Session
    ) -> AIResponse:
        
        user_repo = UserRepository(db)
        user = user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        primary_model, primary_service = await self.select_model(query, user.plan_type)
        
        try:
            if isinstance(primary_service, OpenAIService):
                if primary_model == "gpt-4o-mini":
                    response = await primary_service.query_gpt4o_mini(query)
                else:
                    response = await primary_service.query_gpt4o(query)
            else:
                response = await primary_service.query_sonnet(query)
            
            return response
            
        except Exception as e:
            logger.warning(f"Primary model {primary_model} failed: {str(e)}")
            
            try:
                logger.info("Trying fallback to GPT-4o-mini")
                fallback_response = await self.openai_service.query_gpt4o_mini(query)
                fallback_response.model_used = f"{fallback_response.model_used} (fallback)"
                return fallback_response
                
            except Exception as fallback_error:
                logger.error(f"Fallback model also failed: {str(fallback_error)}")
                raise Exception("All AI models are currently unavailable")
    
    def save_query_to_db(
        self, 
        db: Session, 
        user_id: int, 
        session_id: str, 
        query_text: str, 
        ai_response: AIResponse
    ) -> AIQuery:
        
        ai_query_repo = AIQueryRepository(db)
        
        db_query = AIQuery(
            user_id=user_id,
            session_id=session_id,
            query_text=query_text,
            model_used=ai_response.model_used,
            response=ai_response.response,
            tokens_used=ai_response.tokens_used,
            cost_usd=ai_response.cost_usd,
            processing_time=ai_response.processing_time
        )
        
        return ai_query_repo.create(db_query)
    
    def get_remaining_queries(self, db: Session, user_id: int) -> int:
        user_repo = UserRepository(db)
        user = user_repo.get_by_id(user_id)
        if not user:
            return 0
        
        if user.plan_type == PlanType.FREE:
            return max(0, settings.FREE_USER_RATE_LIMIT - user.daily_query_count)
        else:
            return 999999 