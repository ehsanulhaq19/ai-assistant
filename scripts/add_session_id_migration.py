#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import engine
import logging

logger = logging.getLogger(__name__)

def add_session_id_column():
    """
    Add session_id column to the users table if it doesn't exist.
    This is a safe migration that won't fail if the column already exists.
    """
    try:
        with engine.connect() as connection:
            # Check if session_id column already exists
            result = connection.execute(text("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = 'users' 
                AND COLUMN_NAME = 'session_id'
            """))
            
            if result.fetchone():
                logger.info("session_id column already exists in users table")
                return True
            
            # Add session_id column
            connection.execute(text("""
                ALTER TABLE users 
                ADD COLUMN session_id VARCHAR(255) NULL,
                ADD INDEX idx_session_id (session_id)
            """))
            connection.commit()
            
            logger.info("Successfully added session_id column to users table")
            return True
            
    except Exception as e:
        logger.error(f"Failed to add session_id column: {str(e)}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    success = add_session_id_column()
    if success:
        print("Migration completed successfully!")
    else:
        print("Migration failed!")
        sys.exit(1) 