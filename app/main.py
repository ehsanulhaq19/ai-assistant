from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
import logging

from app.api.v1.ai_router import router as ai_router
from app.api.v1.auth import router as auth_router
from app.services.database_service import DatabaseService
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="VexaCore AI - Smart AI Routing System",
    description="Advanced AI routing system with intelligent model selection and rate limiting. **Authentication required for most endpoints.**",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="VexaCore AI - Smart AI Routing System",
        version="1.0.0",
        description="""
        Advanced AI routing system with intelligent model selection and rate limiting.
        
        ## Authentication
        
        Most endpoints require JWT Bearer token authentication. To get a token:
        
        1. **Register** a new account at `/api/v1/auth/register`
        2. **Login** at `/api/v1/auth/login` to get your JWT token
        3. Use the token in the Authorization header: `Bearer <your_token>`
        
        ## Quick Start
        
        1. Register: `POST /api/v1/auth/register`
        2. Login: `POST /api/v1/auth/login`
        3. Query AI: `POST /api/v1/ai/query` (with Authorization header)
        
        ## Rate Limiting
        
        - **Free users**: 5 requests per minute
        - **Pro/Expert users**: Unlimited requests
        
        ## Model Selection
        
        The system automatically selects the best AI model:
        - **Simple queries** (< 50 words) → GPT-4o-mini
        - **Code queries** → GPT-4o
        - **Creative writing** → Claude Sonnet
        - **Complex queries** (50+ words) → Claude Sonnet
        """,
        routes=app.routes,
    )
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter your JWT token in the format: Bearer <token>"
        }
    }
    
    # Apply security to all endpoints that need it
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            # Skip auth endpoints that don't need authentication
            if path.startswith("/api/v1/auth/register") or path.startswith("/api/v1/auth/login"):
                continue
            
            # Skip root and health endpoints
            if path in ["/", "/health"]:
                continue
                
            # Add security requirement to all other endpoints
            openapi_schema["paths"][path][method]["security"] = [
                {
                    "BearerAuth": []
                }
            ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting VexaCore AI application...")
    if not DatabaseService.initialize_database():
        logger.error("Failed to initialize database. Application may not function correctly.")
    logger.info("VexaCore AI application started successfully!")

app.include_router(auth_router)
app.include_router(ai_router)

@app.get("/", summary="API Information", description="Get API information and available endpoints")
async def root():
    return {
        "message": "VexaCore AI - Smart AI Routing System",
        "version": "1.0.0",
        "docs": "/docs",
        "authentication": {
            "type": "JWT Bearer Token",
            "register": "/api/v1/auth/register",
            "login": "/api/v1/auth/login"
        },
        "endpoints": {
            "ai_query": "/api/v1/ai/query",
            "models_info": "/api/v1/ai/models",
            "user_usage": "/api/v1/ai/usage/{user_id}",
            "register": "/api/v1/auth/register",
            "login": "/api/v1/auth/login",
            "logout": "/api/v1/auth/logout",
            "me": "/api/v1/auth/me"
        },
        "rate_limiting": {
            "free_users": "5 requests per minute",
            "pro_expert_users": "Unlimited"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "VexaCore AI"}

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    ) 