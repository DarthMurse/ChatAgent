from abc import ABC, abstractmethod
from typing import List, Dict, Any
from provider import ProviderFactory, BaseProvider

class BaseAgent(ABC):
    """Base class for all chat agents"""
    
    def __init__(self, provider: BaseProvider):
        self.provider = provider
        self.conversation_history = []
    
    def add_message_to_history(self, role: str, content: str):
        """Add a message to conversation history"""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": self._get_timestamp()
        })
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    def get_conversation_context(self) -> List[Dict[str, str]]:
        """Get conversation context for the model"""
        return [
            {"role": msg["role"], "content": msg["content"]} 
            for msg in self.conversation_history
        ]
    
    @abstractmethod
    def process_message(self, message: str) -> str:
        """Process a user message and return agent response"""
        pass
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()

class ChatAgent(BaseAgent):
    """Basic chat agent for general conversation"""
    
    def __init__(self, provider: BaseProvider):
        super().__init__(provider)
        self.system_prompt = "You are a helpful AI assistant. Provide clear, accurate, and helpful responses."
    
    def process_message(self, message: str) -> str:
        """Process user message and generate response"""
        try:
            # Add user message to history
            self.add_message_to_history("user", message)
            
            # Prepare context with system prompt
            context = [{"role": "system", "content": self.system_prompt}]
            context.extend(self.get_conversation_context())
            
            # Generate response
            response = self.provider.generate_response(context)
            
            # Add assistant response to history
            self.add_message_to_history("assistant", response)
            
            return response
            
        except Exception as e:
            error_msg = f"Error generating response: {str(e)}"
            self.add_message_to_history("assistant", error_msg)
            return error_msg