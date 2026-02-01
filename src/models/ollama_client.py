"""
Ollama Client - Local LLM integration
"""
import aiohttp
from typing import Optional, List, Dict, Any
from loguru import logger

from src.config.settings import settings


class OllamaClient:
    """Client for interacting with local Ollama instance."""
    
    def __init__(self):
        self.host = settings.ollama_host
        self.model = settings.ollama_model
        self.timeout = aiohttp.ClientTimeout(total=settings.response_timeout)
        
    async def _check_health(self) -> bool:
        """Check if Ollama is running and accessible."""
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(f"{self.host}/api/version") as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Ollama health check failed: {e}")
            return False
    
    def _format_messages(self, message: str, context: Optional[List[Dict]] = None) -> List[Dict]:
        """Format messages for Ollama chat API."""
        messages = []
        
        # Add system prompt
        messages.append({
            "role": "system",
            "content": (
                "You are OpenClaw, a helpful AI assistant. You provide clear, concise, "
                "and accurate responses. When you don't know something, you say so."
            )
        })
        
        # Add context/history
        if context:
            messages.extend(context)
        
        # Add current message
        messages.append({
            "role": "user",
            "content": message
        })
        
        return messages
    
    async def generate(
        self, 
        message: str, 
        context: Optional[List[Dict]] = None
    ) -> str:
        """
        Generate a response using Ollama.
        
        Args:
            message: The user's message
            context: Optional conversation history
        
        Returns:
            The generated response text
        """
        messages = self._format_messages(message, context)
        
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }
        
        logger.debug(f"Ollama request: {self.model}")
        
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            async with session.post(
                f"{self.host}/api/chat",
                json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Ollama error ({response.status}): {error_text}")
                
                data = await response.json()
                return data["message"]["content"]
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """List available models in Ollama."""
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            async with session.get(f"{self.host}/api/tags") as response:
                if response.status != 200:
                    return []
                data = await response.json()
                return data.get("models", [])
