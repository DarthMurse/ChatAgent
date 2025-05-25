from .base_agent import BaseAgent, ChatAgent
from provider import ProviderFactory

class AgentFactory:
    """Factory class to create agent instances"""
    
    @staticmethod
    def create_agent(agent_type: str, provider_name: str, api_key: str, model_name: str) -> BaseAgent:
        """Create an agent instance with the specified provider"""
        # Create provider first
        provider = ProviderFactory.create_provider(provider_name, api_key, model_name)
        
        # Validate the model exists
        if not provider.validate_model():
            raise ValueError(f"Model '{model_name}' not found for provider '{provider_name}'. Please check the model name.")
        
        # Create agent based on type
        agents = {
            'chat': ChatAgent,
            'basic': ChatAgent,  # alias for chat
        }
        
        if agent_type not in agents:
            agent_type = 'chat'  # default to chat agent
        
        return agents[agent_type](provider)
    
    @staticmethod
    def get_supported_agent_types():
        """Get list of supported agent types"""
        return ['chat', 'basic']