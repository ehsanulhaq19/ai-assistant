import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.exc import OperationalError
from app.core.database import engine, Base
from app.core.config import settings

logger = logging.getLogger(__name__)

class DatabaseService:

    @staticmethod
    def get_admin_url():
        """Return SQLAlchemy URL to connect without specifying database."""
        return URL.create(
            drivername="mysql+pymysql",  # or "mysql+mysqlclient"
            username=settings.MYSQL_USER,
            password=settings.MYSQL_PASSWORD,
            host=settings.MYSQL_HOST,
            port=settings.MYSQL_PORT,
            database=None
        )

    @staticmethod
    def ensure_database_exists():
        db_name = settings.MYSQL_DATABASE

        admin_engine = create_engine(DatabaseService.get_admin_url(), isolation_level="AUTOCOMMIT")

        try:
            with admin_engine.connect() as conn:
                result = conn.execute(
                    text("SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = :dbname"),
                    {"dbname": db_name}
                )
                if not result.fetchone():
                    conn.execute(text(f"CREATE DATABASE `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
                    logger.info(f"Database '{db_name}' created.")
                else:
                    logger.info(f"Database '{db_name}' already exists.")
            return True
        except Exception as e:
            logger.error(f"Error ensuring database exists: {str(e)}")
            return False

    @staticmethod
    def check_database_connection():
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Database connection successful")
            return True
        except OperationalError as e:
            logger.error(f"Database connection failed: {str(e)}")
            return False

    @staticmethod
    def create_tables():
        try:
            logger.info("Creating tables...")
            Base.metadata.create_all(bind=engine)
            logger.info("Tables created successfully!")
            return True
        except Exception as e:
            logger.error(f"Failed to create tables: {str(e)}")
            return False

    @staticmethod
    def initialize_database():
        if not DatabaseService.check_database_connection():
            logger.warning("Trying to create database because connection failed...")
            if not DatabaseService.ensure_database_exists():
                return False
        return DatabaseService.create_tables()
