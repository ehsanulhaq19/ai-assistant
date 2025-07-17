from pydantic import BaseModel, Field

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=5000, description="User query text")
    user_id: int = Field(..., gt=0, description="User ID")
    session_id: str = Field(..., min_length=1, max_length=255, description="Session identifier")

class QueryResponse(BaseModel):
    response: str = Field(..., description="AI generated response")
    model_used: str = Field(..., description="Model that was used for generation")
    tokens_used: int = Field(..., ge=0, description="Number of tokens used")
    cost_usd: float = Field(..., ge=0, description="Cost in USD")
    processing_time: float = Field(..., ge=0, description="Processing time in seconds")
    session_id: str = Field(..., description="Session identifier")
    remaining_queries: int = Field(..., ge=0, description="Remaining queries for the user") 