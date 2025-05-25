from typing import Union, List, Dict
from .base import BaseProvider
import openai

class OpenAIProvider(BaseProvider):
    """OpenAI provider using official OpenAI client"""
    
    def __init__(self, api_key: str, model_name: str):
        super().__init__(api_key, model_name)
        self.client = openai.OpenAI(api_key=api_key)
    
    def generate_response(self, message: Union[str, List[Dict[str, str]]], **kwargs) -> str:
        """Generate response using OpenAI API"""
        try:
            if isinstance(message, str):
                messages = [{"role": "user", "content": message}]
            else:
                messages = message
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=kwargs.get('max_tokens', 1000),
                temperature=kwargs.get('temperature', 0.7)
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    def validate_model(self) -> bool:
        """Validate if the model exists by making a test call"""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1
            )
            return True
        except Exception as e:
            print(f"Model validation failed for {self.model_name}: {str(e)}")
            return False
    
    @property
    def provider_name(self) -> str:
        return "openai"