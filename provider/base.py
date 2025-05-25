from abc import ABC, abstractmethod
from typing import Any, Dict, List, Union

class BaseProvider(ABC):
    """Base class for all LLM providers"""
    
    def __init__(self, api_key: str, model_name: str):
        self.api_key = api_key
        self.model_name = model_name
        
    @abstractmethod
    def generate_response(self, message: Union[str, List[Dict[str, str]]], **kwargs) -> str:
        """Generate a response from the model"""
        pass
    
    @abstractmethod
    def validate_model(self) -> bool:
        """Validate if the model exists and is accessible"""
        pass
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the name of the provider"""
        pass