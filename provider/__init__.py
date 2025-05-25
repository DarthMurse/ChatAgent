from .base import BaseProvider
from .openai_provider import OpenAIProvider
from .claude_provider import ClaudeProvider
from .deepseek_provider import DeepSeekProvider

class ProviderFactory:
    """Factory class to create provider instances"""
    
    @staticmethod
    def create_provider(provider_name: str, api_key: str, model_name: str) -> BaseProvider:
        """Create a provider instance based on the provider name"""
        providers = {
            'openai': OpenAIProvider,
            'claude': ClaudeProvider,
            'deepseek': DeepSeekProvider
        }
        
        if provider_name not in providers:
            raise ValueError(f"Unsupported provider: {provider_name}")
        
        return providers[provider_name](api_key, model_name)
    
    @staticmethod
    def get_supported_providers():
        """Get list of supported provider names"""
        return ['openai', 'claude', 'deepseek']