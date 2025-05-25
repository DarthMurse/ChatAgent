from typing import Union, List, Dict
from .base import BaseProvider
import anthropic

class ClaudeProvider(BaseProvider):
    """Claude provider using official Anthropic client"""
    
    def __init__(self, api_key: str, model_name: str):
        super().__init__(api_key, model_name)
        self.client = anthropic.Anthropic(api_key=api_key)
    
    def generate_response(self, message: Union[str, List[Dict[str, str]]], **kwargs) -> str:
        """Generate response using Anthropic API"""
        try:
            if isinstance(message, str):
                messages = [{"role": "user", "content": message}]
            elif isinstance(message, list):
                # Filter out system messages for Anthropic format
                messages = [msg for msg in message if msg.get("role") in ["user", "assistant"]]
                if not messages:
                    messages = [{"role": "user", "content": str(message)}]
            else:
                messages = [{"role": "user", "content": str(message)}]
            
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=kwargs.get('max_tokens', 1000),
                messages=messages
            )
            return response.content[0].text
        except Exception as e:
            raise Exception(f"Claude API error: {str(e)}")
    
    def validate_model(self) -> bool:
        """Validate if the model exists by making a test call"""
        try:
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=1,
                messages=[{"role": "user", "content": "test"}]
            )
            return True
        except Exception as e:
            print(f"Model validation failed for {self.model_name}: {str(e)}")
            return False
    
    @property
    def provider_name(self) -> str:
        return "claude"