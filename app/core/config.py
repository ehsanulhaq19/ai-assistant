import os
from decouple import config
from typing import Optional

class Settings:
    DATABASE_URL: str = config("DATABASE_URL", default="mysql://root:password@localhost:3306/vexacore_ai")
    MYSQL_ROOT_PASSWORD: str = config("MYSQL_ROOT_PASSWORD", default="rootpassword")
    MYSQL_DATABASE: str = config("MYSQL_DATABASE", default="vexacore_ai")
    MYSQL_USER: str = config("MYSQL_USER", default="vexacore")
    MYSQL_PASSWORD: str = config("MYSQL_PASSWORD", default="vexacorepass")
    MYSQL_HOST: str = config("MYSQL_HOST", default="localhost")
    MYSQL_PORT: int = config("MYSQL_PORT", default=3306, cast=int)
    
    REDIS_URL: str = config("REDIS_URL", default="redis://localhost:6379/0")
    
    OPENAI_API_KEY: str = config("OPENAI_API_KEY", default="")
    OPENAI_ORGANIZATION: Optional[str] = config("OPENAI_ORGANIZATION", default=None)
    
    ANTHROPIC_API_KEY: str = config("ANTHROPIC_API_KEY", default="")
    
    SECRET_KEY: str = config("SECRET_KEY", default="your-secret-key-change-in-production")
    ALGORITHM: str = config("ALGORITHM", default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = config("ACCESS_TOKEN_EXPIRE_MINUTES", default=30, cast=int)
    
    FREE_USER_RATE_LIMIT: int = config("FREE_USER_RATE_LIMIT", default=5, cast=int)
    FREE_USER_RATE_LIMIT_WINDOW: int = config("FREE_USER_RATE_LIMIT_WINDOW", default=60, cast=int)
    
    GPT4O_MINI_COST: float = config("GPT4O_MINI_COST", default=0.00015, cast=float)
    GPT4O_COST: float = config("GPT4O_COST", default=0.005, cast=float)
    CLAUDE_SONNET_COST: float = config("CLAUDE_SONNET_COST", default=0.003, cast=float)
    CLAUDE_HAIKU_COST: float = config("CLAUDE_HAIKU_COST", default=0.00025, cast=float)
    
    HOST: str = config("HOST", default="0.0.0.0")
    PORT: int = config("PORT", default=8000, cast=int)
    DEBUG: bool = config("DEBUG", default=True, cast=bool)

settings = Settings() 