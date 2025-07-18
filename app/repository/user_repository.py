from sqlalchemy.orm import Session
from app.models import User, PlanType
from typing import Optional, List

class UserRepository:
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_by_id_and_session_id(self, user_id: int, session_id: str) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id, User.session_id == session_id).first()
    
    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()
    
    def get_all(self) -> List[User]:
        return self.db.query(User).all()
    
    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def update(self, user: User) -> User:
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def delete(self, user_id: int) -> bool:
        user = self.get_by_id(user_id)
        if user:
            self.db.delete(user)
            self.db.commit()
            return True
        return False
    
    def set_session_id(self, user_id: int, session_id: str) -> bool:
        user = self.get_by_id(user_id)
        if user:
            user.session_id = session_id
            self.db.commit()
            return True
        return False
    
    def clear_session_id(self, user_id: int) -> bool:
        user = self.get_by_id(user_id)
        if user:
            user.session_id = None
            self.db.commit()
            return True
        return False
    
    def get_by_session_id(self, session_id: str) -> Optional[User]:
        return self.db.query(User).filter(User.session_id == session_id).first()
    
    def increment_daily_query_count(self, user_id: int) -> bool:
        user = self.get_by_id(user_id)
        if user:
            user.daily_query_count += 1
            self.db.commit()
            return True
        return False
    
    def increment_daily_premium_count(self, user_id: int) -> bool:
        user = self.get_by_id(user_id)
        if user:
            user.daily_premium_count += 1
            self.db.commit()
            return True
        return False
    
    def reset_daily_counts(self) -> int:
        updated = self.db.query(User).update({
            User.daily_query_count: 0,
            User.daily_premium_count: 0
        })
        self.db.commit()
        return updated
    
    def get_users_by_plan(self, plan_type: PlanType) -> List[User]:
        return self.db.query(User).filter(User.plan_type == plan_type).all()
    
    def get_free_users(self) -> List[User]:
        return self.get_users_by_plan(PlanType.FREE)
    
    def get_pro_users(self) -> List[User]:
        return self.get_users_by_plan(PlanType.PRO)
    
    def get_expert_users(self) -> List[User]:
        return self.get_users_by_plan(PlanType.EXPERT)
    
    def update_plan_type(self, user_id: int, plan_type: PlanType) -> bool:
        user = self.get_by_id(user_id)
        if user:
            user.plan_type = plan_type
            self.db.commit()
            return True
        return False 