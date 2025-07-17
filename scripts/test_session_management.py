#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.repository import UserRepository
from app.utils import generate_session_id
import logging

logger = logging.getLogger(__name__)

def test_session_management():
    """
    Test the session management functionality
    """
    db = SessionLocal()
    
    try:
        user_repo = UserRepository(db)
        
        # Get a test user (assuming sample data exists)
        user = user_repo.get_by_email("free@example.com")
        if not user:
            logger.error("Test user not found. Please run init_sample_data.py first.")
            return False
        
        logger.info(f"Testing session management for user: {user.email}")
        
        # Test 1: Generate and set session ID
        session_id = generate_session_id()
        logger.info(f"Generated session ID: {session_id}")
        
        success = user_repo.set_session_id(user.id, session_id)
        if not success:
            logger.error("Failed to set session ID")
            return False
        
        # Verify session ID was set
        updated_user = user_repo.get_by_id(user.id)
        if updated_user.session_id != session_id:
            logger.error("Session ID was not set correctly")
            return False
        
        logger.info("✓ Session ID set successfully")
        
        # Test 2: Get user by session ID
        user_by_session = user_repo.get_by_session_id(session_id)
        if not user_by_session or user_by_session.id != user.id:
            logger.error("Failed to retrieve user by session ID")
            return False
        
        logger.info("✓ User retrieved by session ID successfully")
        
        # Test 3: Clear session ID
        success = user_repo.clear_session_id(user.id)
        if not success:
            logger.error("Failed to clear session ID")
            return False
        
        # Verify session ID was cleared
        updated_user = user_repo.get_by_id(user.id)
        if updated_user.session_id is not None:
            logger.error("Session ID was not cleared correctly")
            return False
        
        logger.info("✓ Session ID cleared successfully")
        
        # Test 4: Verify user cannot be found by cleared session ID
        user_by_session = user_repo.get_by_session_id(session_id)
        if user_by_session:
            logger.error("User should not be found by cleared session ID")
            return False
        
        logger.info("✓ User not found by cleared session ID (as expected)")
        
        logger.info("All session management tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"Test failed with exception: {str(e)}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    success = test_session_management()
    if success:
        print("Session management test completed successfully!")
    else:
        print("Session management test failed!")
        sys.exit(1) 