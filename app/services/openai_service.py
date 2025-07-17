import openai
import time
from typing import Optional
from app.services.base_ai_service import BaseAIService, AIResponse
from app.core.models_config import ModelConfig

class OpenAIService(BaseAIService):
    
    def __init__(self, api_key: str, organization: Optional[str] = None):
        super().__init__(api_key)
        self.client = openai.AsyncOpenAI(api_key=api_key, organization=organization)
    
    async def query(self, prompt: str, model: str = "gpt-4o-mini") -> AIResponse:
        start_time = time.time()
        
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4000,
                temperature=0.7
            )
            
            processing_time = time.time() - start_time
            tokens_used = response.usage.total_tokens
            
            self.cost_per_1k_tokens = ModelConfig.get_model_cost(model)
            cost_usd = self.calculate_cost(tokens_used)
            
            return AIResponse(
                response=response.choices[0].message.content,
                tokens_used=tokens_used,
                model_used=model,
                cost_usd=cost_usd,
                processing_time=processing_time
            )
            
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    async def query_lightweight(self, prompt: str) -> AIResponse:
        return await self.query(prompt, "gpt-4o-mini")
    
    async def query_gpt4o_mini(self, prompt: str) -> AIResponse:
        return await self.query(prompt, "gpt-4o-mini")
    
    async def query_gpt4o(self, prompt: str) -> AIResponse:
        return await self.query(prompt, "gpt-4o") 