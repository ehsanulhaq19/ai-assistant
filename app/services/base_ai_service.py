from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class AIResponse:
    response: str
    tokens_used: int
    model_used: str
    cost_usd: float
    processing_time: float

class BaseAIService(ABC):
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model_name = ""
        self.cost_per_1k_tokens = 0.0
    
    @abstractmethod
    async def query(self, prompt: str) -> AIResponse:
        pass
    
    def calculate_cost(self, tokens_used: int) -> float:
        return (tokens_used / 1000) * self.cost_per_1k_tokens
    
    async def classify_query_type(self, query: str) -> tuple[bool, bool]:
        """
        Use AI to classify if a query is code-related or creative writing
        Returns: (is_code, is_creative)
        """
        try:
            prompt = f"""Analyze the following query and classify it into one of three categories:

Query: "{query}"

Respond with ONLY one of these three options:
- "code" - if the query is about programming, coding, software development, algorithms, APIs, databases, technical implementation
- "creative" - if the query is about creative writing, storytelling, poems, fiction, artistic expression, creative content
- "general" - if the query is about general topics, factual information, or doesn't fit the above categories

Examples:
- "Write a Python function" → code
- "Debug this JavaScript error" → code
- "Write a story about a robot" → creative
- "Compose a poem about nature" → creative
- "What's the weather like?" → general
- "Explain quantum physics" → general

Response:"""
            
            response = await self.query_lightweight(prompt)
            result = response.response.strip().lower()
            
            is_code = result == "code"
            is_creative = result == "creative"
            
            return is_code, is_creative
            
        except Exception as e:
            # Fallback to keyword-based detection if AI classification fails
            return self._fallback_classification(query)
    
    async def query_lightweight(self, prompt: str) -> AIResponse:
        """
        Query a lightweight model for classification tasks
        This should be implemented by subclasses
        """
        # Default implementation - subclasses should override
        return await self.query(prompt)
    
    def _fallback_classification(self, query: str) -> tuple[bool, bool]:
        """Fallback keyword-based classification"""
        query_lower = query.lower()
        
        code_keywords = [
            'code', 'programming', 'function', 'class', 'method', 'algorithm',
            'debug', 'error', 'bug', 'syntax', 'compile', 'runtime', 'api',
            'database', 'sql', 'javascript', 'python', 'java', 'c++', 'html',
            'css', 'react', 'node', 'docker', 'git', 'deploy', 'server',
            'client', 'frontend', 'backend', 'framework', 'library'
        ]
        
        creative_keywords = [
            'story', 'poem', 'creative', 'fiction', 'narrative', 'character',
            'plot', 'scene', 'dialogue', 'description', 'imagine', 'write',
            'compose', 'artistic', 'expressive', 'emotional', 'metaphor',
            'simile', 'rhyme', 'verse', 'prose', 'novel', 'short story'
        ]
        
        is_code = any(keyword in query_lower for keyword in code_keywords)
        is_creative = any(keyword in query_lower for keyword in creative_keywords)
        
        return is_code, is_creative
    
    async def is_code_query(self, query: str) -> bool:
        is_code, _ = await self.classify_query_type(query)
        return is_code
    
    async def is_creative_writing(self, query: str) -> bool:
        _, is_creative = await self.classify_query_type(query)
        return is_creative
    
    def get_query_complexity(self, query: str) -> str:
        word_count = len(query.split())
        
        if word_count < 50:
            return "simple"
        else:
            return "complex" 