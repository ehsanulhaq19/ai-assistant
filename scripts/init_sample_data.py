#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models import User, PlanType
from app.repository import UserRepository
from app.core.auth import get_password_hash

def create_sample_users():
    db = SessionLocal()
    
    try:
        user_repo = UserRepository(db)
        existing_users = len(user_repo.get_all())
        if existing_users > 0:
            print("Users already exist, skipping sample user creation.")
            return
        
        sample_users = [
            {
                "email": "free@example.com",
                "name": "Free User",
                "password": "password123",
                "plan_type": PlanType.FREE
            },
            {
                "email": "pro@example.com", 
                "name": "Pro User",
                "password": "password123",
                "plan_type": PlanType.PRO
            },
            {
                "email": "expert@example.com",
                "name": "Expert User", 
                "password": "password123",
                "plan_type": PlanType.EXPERT
            }
        ]
        
        for user_data in sample_users:
            hashed_password = get_password_hash(user_data["password"])
            user = User(
                email=user_data["email"],
                name=user_data["name"],
                hashed_password=hashed_password,
                plan_type=user_data["plan_type"]
            )
            user_repo.create(user)
        
        print("Sample users created successfully!")
        print("\nSample users:")
        for user_data in sample_users:
            print(f"  - {user_data['email']} (Plan: {user_data['plan_type'].value})")
        print("  Password for all users: password123")
        
    except Exception as e:
        print(f"Error creating sample users: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    print("Initializing VexaCore AI Sample Data...")
    
    try:
        create_sample_users()
        print("\nSample data initialization completed successfully!")
        print("\nNext steps:")
        print("1. Set up your .env file with API keys")
        print("2. Start the application")
        print("3. Use the sample users to test the API")
        
    except Exception as e:
        print(f"Sample data initialization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 