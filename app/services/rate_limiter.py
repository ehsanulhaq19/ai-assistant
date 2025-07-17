import redis
import time
from typing import Optional
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    
    def __init__(self):
        self.redis_client = redis.from_url(settings.REDIS_URL)
    
    def _get_key(self, user_id: int) -> str:
        current_minute = int(time.time() // 60)
        return f"rate_limit:{user_id}:{current_minute}"
    
    def is_allowed(self, user_id: int, user_plan: str) -> bool:
        if user_plan in ['pro', 'expert']:
            return True
        
        key = self._get_key(user_id)
        current_count = self.redis_client.get(key)
        
        if current_count is None:
            current_count = 0
        else:
            current_count = int(current_count)
        
        return current_count < settings.FREE_USER_RATE_LIMIT
    
    def increment_request(self, user_id: int, user_plan: str) -> int:
        if user_plan in ['pro', 'expert']:
            return 999999
        
        key = self._get_key(user_id)
        current_count = self.redis_client.incr(key)
        
        if current_count == 1:
            self.redis_client.expire(key, settings.FREE_USER_RATE_LIMIT_WINDOW)
        
        return current_count
    
    def get_remaining_requests(self, user_id: int, user_plan: str) -> int:
        if user_plan in ['pro', 'expert']:
            return 999999
        
        key = self._get_key(user_id)
        current_count = self.redis_client.get(key)
        
        if current_count is None:
            return settings.FREE_USER_RATE_LIMIT
        else:
            return max(0, settings.FREE_USER_RATE_LIMIT - int(current_count)) 