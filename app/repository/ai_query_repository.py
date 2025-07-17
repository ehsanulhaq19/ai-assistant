from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import AIQuery
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

class AIQueryRepository:
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, query_id: int) -> Optional[AIQuery]:
        return self.db.query(AIQuery).filter(AIQuery.id == query_id).first()
    
    def get_by_user_id(self, user_id: int, limit: int = 10) -> List[AIQuery]:
        return self.db.query(AIQuery).filter(
            AIQuery.user_id == user_id
        ).order_by(AIQuery.created_at.desc()).limit(limit).all()
    
    def get_by_session_id(self, session_id: str) -> List[AIQuery]:
        return self.db.query(AIQuery).filter(
            AIQuery.session_id == session_id
        ).order_by(AIQuery.created_at.desc()).all()
    
    def create(self, ai_query: AIQuery) -> AIQuery:
        self.db.add(ai_query)
        self.db.commit()
        self.db.refresh(ai_query)
        return ai_query
    
    def update(self, ai_query: AIQuery) -> AIQuery:
        self.db.commit()
        self.db.refresh(ai_query)
        return ai_query
    
    def delete(self, query_id: int) -> bool:
        ai_query = self.get_by_id(query_id)
        if ai_query:
            self.db.delete(ai_query)
            self.db.commit()
            return True
        return False
    
    def get_total_queries_by_user(self, user_id: int) -> int:
        return self.db.query(AIQuery).filter(AIQuery.user_id == user_id).count()
    
    def get_total_cost_by_user(self, user_id: int) -> float:
        result = self.db.query(func.sum(AIQuery.cost_usd)).filter(
            AIQuery.user_id == user_id
        ).scalar()
        return float(result) if result else 0.0
    
    def get_queries_by_date_range(
        self, 
        user_id: int, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[AIQuery]:
        return self.db.query(AIQuery).filter(
            AIQuery.user_id == user_id,
            AIQuery.created_at >= start_date,
            AIQuery.created_at <= end_date
        ).order_by(AIQuery.created_at.desc()).all()
    
    def get_recent_queries(self, hours: int = 24) -> List[AIQuery]:
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        return self.db.query(AIQuery).filter(
            AIQuery.created_at >= cutoff_time
        ).order_by(AIQuery.created_at.desc()).all()
    
    def get_queries_by_model(self, model_used: str) -> List[AIQuery]:
        return self.db.query(AIQuery).filter(
            AIQuery.model_used == model_used
        ).order_by(AIQuery.created_at.desc()).all()
    
    def get_model_usage_stats(self) -> Dict[str, Any]:
        stats = self.db.query(
            AIQuery.model_used,
            func.count(AIQuery.id).label('total_queries'),
            func.sum(AIQuery.tokens_used).label('total_tokens'),
            func.sum(AIQuery.cost_usd).label('total_cost'),
            func.avg(AIQuery.processing_time).label('avg_processing_time')
        ).group_by(AIQuery.model_used).all()
        
        return {
            'model_stats': [
                {
                    'model': stat.model_used,
                    'total_queries': stat.total_queries,
                    'total_tokens': int(stat.total_tokens) if stat.total_tokens else 0,
                    'total_cost': float(stat.total_cost) if stat.total_cost else 0.0,
                    'avg_processing_time': float(stat.avg_processing_time) if stat.avg_processing_time else 0.0
                }
                for stat in stats
            ]
        }
    
    def get_user_usage_summary(self, user_id: int) -> Dict[str, Any]:
        total_queries = self.get_total_queries_by_user(user_id)
        total_cost = self.get_total_cost_by_user(user_id)
        
        recent_queries = self.get_by_user_id(user_id, limit=10)
        
        model_breakdown = self.db.query(
            AIQuery.model_used,
            func.count(AIQuery.id).label('count')
        ).filter(AIQuery.user_id == user_id).group_by(AIQuery.model_used).all()
        
        return {
            'user_id': user_id,
            'total_queries': total_queries,
            'total_cost_usd': round(total_cost, 6),
            'recent_queries': [
                {
                    'query': q.query_text[:100] + "..." if len(q.query_text) > 100 else q.query_text,
                    'model_used': q.model_used,
                    'tokens_used': q.tokens_used,
                    'cost_usd': float(q.cost_usd),
                    'created_at': q.created_at.isoformat()
                }
                for q in recent_queries
            ],
            'model_breakdown': [
                {
                    'model': stat.model_used,
                    'count': stat.count
                }
                for stat in model_breakdown
            ]
        }
    
    def cleanup_old_queries(self, days: int = 90) -> int:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        deleted = self.db.query(AIQuery).filter(
            AIQuery.created_at < cutoff_date
        ).delete()
        self.db.commit()
        return deleted 