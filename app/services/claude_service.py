import anthropic
import time
from app.services.base_ai_service import BaseAIService, AIResponse
from app.core.models_config import ModelConfig

class ClaudeService(BaseAIService):
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
    
    async def query(self, prompt: str, model: str = "claude-3-5-sonnet-20241022") -> AIResponse:
        start_time = time.time()
        
        try:
            response = await self.client.messages.create(
                model=model,
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            processing_time = time.time() - start_time
            
            # Get the response text from the first content block
            response_text = response.content[0].text if response.content else ""
            estimated_tokens = len(prompt.split()) + len(response_text.split())
            tokens_used = estimated_tokens
            
            self.cost_per_1k_tokens = ModelConfig.get_model_cost(model)
            cost_usd = self.calculate_cost(tokens_used)
            
            return AIResponse(
                response=response_text,
                tokens_used=tokens_used,
                model_used=model,
                cost_usd=cost_usd,
                processing_time=processing_time
            )
            
        except Exception as e:
            raise Exception(f"Claude API error: {str(e)}")
    
    async def query_lightweight(self, prompt: str) -> AIResponse:
        return await self.query(prompt, "claude-3-haiku-20240307")
    
    async def query_sonnet(self, prompt: str) -> AIResponse:
        return await self.query(prompt, "claude-3-5-sonnet-20241022") 