from typing import Dict, Any
from app.core.config import settings

class ModelConfig:
    
    MODELS = {
        "gpt-4o-mini": {
            "provider": "OpenAI",
            "use_case": "Simple queries (< 50 words)",
            "cost_per_1k_tokens": settings.GPT4O_MINI_COST,
            "max_tokens": 4000,
            "classification_model": True
        },
        "gpt-4o": {
            "provider": "OpenAI", 
            "use_case": "Complex queries, code-related tasks",
            "cost_per_1k_tokens": settings.GPT4O_COST,
            "max_tokens": 4000,
            "classification_model": False
        },
        "claude-3-5-sonnet-20241022": {
            "provider": "Anthropic",
            "use_case": "Creative writing, complex reasoning",
            "cost_per_1k_tokens": settings.CLAUDE_SONNET_COST,
            "max_tokens": 4000,
            "classification_model": False
        },
        "claude-3-haiku-20240307": {
            "provider": "Anthropic",
            "use_case": "Lightweight classification tasks",
            "cost_per_1k_tokens": settings.CLAUDE_HAIKU_COST,
            "max_tokens": 4000,
            "classification_model": True
        }
    }
    
    SELECTION_LOGIC = {
        "simple_queries": "GPT-4o-mini (cost-effective)",
        "code_queries": "GPT-4o (better code understanding)",
        "creative_writing": "Claude Sonnet (creative capabilities)",
        "complex_queries": "Claude Sonnet (better reasoning)",
        "fallback": "GPT-4o-mini (reliability)"
    }
    
    @classmethod
    def get_model_info(cls, model_name: str) -> Dict[str, Any]:
        return cls.MODELS.get(model_name, {})
    
    @classmethod
    def get_all_models(cls) -> Dict[str, Any]:
        return cls.MODELS
    
    @classmethod
    def get_selection_logic(cls) -> Dict[str, str]:
        return cls.SELECTION_LOGIC
    
    @classmethod
    def get_classification_models(cls) -> Dict[str, Any]:
        return {name: info for name, info in cls.MODELS.items() if info.get("classification_model", False)}
    
    @classmethod
    def get_production_models(cls) -> Dict[str, Any]:
        return {name: info for name, info in cls.MODELS.items() if not info.get("classification_model", False)}
    
    @classmethod
    def get_model_cost(cls, model_name: str) -> float:
        model_info = cls.get_model_info(model_name)
        return model_info.get("cost_per_1k_tokens", 0.0)
    
    @classmethod
    def get_model_provider(cls, model_name: str) -> str:
        model_info = cls.get_model_info(model_name)
        return model_info.get("provider", "")
    
    @classmethod
    def is_classification_model(cls, model_name: str) -> bool:
        model_info = cls.get_model_info(model_name)
        return model_info.get("classification_model", False) 