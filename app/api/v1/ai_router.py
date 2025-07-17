from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging
from app.core.database import get_db
from app.schemas import QueryRequest, QueryResponse
from app.services.ai_router_service import AIRouterService
from app.services.rate_limiter import RateLimiter
from app.repository import UserRepository, AIQueryRepository
from app.core.models_config import ModelConfig
from app.core.auth_dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/ai", tags=["AI"])

ai_router_service = AIRouterService()
rate_limiter = RateLimiter()

@router.post("/query", response_model=QueryResponse, summary="Query AI", description="Send a query to the AI system. Authentication required.")
async def query_ai(
    request: QueryRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    try:
        user_repo = UserRepository(db)
        user = user_repo.get_by_id(request.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        if user.id != current_user.id:
            raise HTTPException(status_code=403, detail="Forbidden: user mismatch")
        if not rate_limiter.is_allowed(request.user_id, user.plan_type.value):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Free users are limited to {rate_limiter.get_remaining_requests(request.user_id, user.plan_type.value)} requests per minute."
            )
        rate_limiter.increment_request(request.user_id, user.plan_type.value)
        ai_response = await ai_router_service.execute_query(
            query=request.query,
            user_id=request.user_id,
            session_id=request.session_id,
            db=db
        )
        ai_router_service.save_query_to_db(
            db=db,
            user_id=request.user_id,
            session_id=request.session_id,
            query_text=request.query,
            ai_response=ai_response
        )
        user_repo.increment_daily_query_count(request.user_id)
        remaining_queries = ai_router_service.get_remaining_queries(db, request.user_id)
        return QueryResponse(
            response=ai_response.response,
            model_used=ai_response.model_used,
            tokens_used=ai_response.tokens_used,
            cost_usd=ai_response.cost_usd,
            processing_time=ai_response.processing_time,
            session_id=request.session_id,
            remaining_queries=remaining_queries
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in query_ai: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/models", summary="Get available models", description="Get information about available AI models and selection logic. Authentication required.")
async def get_available_models(current_user=Depends(get_current_user)):
    return {
        "models": ModelConfig.get_all_models(),
        "selection_logic": ModelConfig.get_selection_logic()
    }

@router.get("/usage/{user_id}", summary="Get user usage statistics", description="Get detailed usage statistics for a user. Authentication required.")
async def get_user_usage(
    user_id: int, 
    db: Session = Depends(get_db), 
    current_user=Depends(get_current_user)
):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden: can only access own usage statistics")
    
    user_repo = UserRepository(db)
    ai_query_repo = AIQueryRepository(db)
    user = user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    try:
        usage_summary = ai_query_repo.get_user_usage_summary(user_id)
        return {
            "user_id": user_id,
            "plan_type": user.plan_type.value,
            "daily_query_count": user.daily_query_count,
            "total_queries": usage_summary["total_queries"],
            "total_cost_usd": usage_summary["total_cost_usd"],
            "remaining_queries": ai_router_service.get_remaining_queries(db, user_id),
            "recent_queries": usage_summary["recent_queries"],
            "model_breakdown": usage_summary["model_breakdown"]
        }
    except Exception as e:
        logger.error(f"Error getting user usage for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while retrieving usage statistics"
        ) 