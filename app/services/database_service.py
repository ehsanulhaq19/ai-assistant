from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import engine, SessionLocal
from app.models import Base
import logging

logger = logging.getLogger(__name__)

class DatabaseService:
    
    @staticmethod
    def create_tables():
        try:
            logger.info("Creating database tables...")
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables created successfully!")
            return True
        except Exception as e:
            logger.error(f"Failed to create database tables: {str(e)}")
            return False
    
    @staticmethod
    def check_database_connection():
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
                connection.commit()
            logger.info("Database connection successful")
            return True
        except Exception as e:
            logger.error(f"Database connection failed: {str(e)}")
            return False
    
    @staticmethod
    def initialize_database():
        if DatabaseService.check_database_connection():
            return DatabaseService.create_tables()
        return False 