"""
Model Router - Intelligent model selection between Ollama and Gemini
"""
import re
from typing import Optional, Dict, Any, List
from loguru import logger

from src.config.settings import settings
from src.models.ollama_client import OllamaClient
from src.models.gemini_client import GeminiClient


class ModelRouter:
    """
    Routes requests to the appropriate model based on complexity and requirements.
    
    Selection Logic:
    - Use Ollama (local) for: Simple queries, quick responses, privacy-sensitive data
    - Use Gemini (cloud) for: Complex reasoning, code generation, long context tasks
    """
    
    def __init__(self):
        self.ollama = OllamaClient()
        self.gemini = GeminiClient() if settings.gemini_api_key else None
        self.trigger_keywords = settings.gemini_keywords_list
        self.complexity_threshold = settings.complexity_threshold
        
        logger.info(f"Model Router initialized")
        logger.info(f"  - Ollama: {settings.ollama_model} @ {settings.ollama_host}")
        logger.info(f"  - Gemini: {'Available' if self.gemini else 'Not configured'}")
    
    def _calculate_complexity(self, message: str, context: Optional[List[Dict]] = None) -> int:
        """
        Calculate the complexity score of a message.
        
        Factors:
        - Message length
        - Presence of trigger keywords
        - Context length
        - Technical indicators (code blocks, etc.)
        """
        score = 0
        
        # Base score from message length
        score += len(message.split())
        
        # Check for trigger keywords
        message_lower = message.lower()
        for keyword in self.trigger_keywords:
            if keyword in message_lower:
                score += 200
                logger.debug(f"Trigger keyword found: '{keyword}'")
        
        # Check for code blocks or technical content
        if "```" in message or "def " in message or "function" in message:
            score += 150
        
        # Check for complex question indicators
        complex_patterns = [
            r'\bwhy\b.*\?',
            r'\bhow\b.*\bwork\b',
            r'\bexplain\b',
            r'\bcompare\b',
            r'\bdifference\b.*\bbetween\b',
        ]
        for pattern in complex_patterns:
            if re.search(pattern, message_lower):
                score += 100
        
        # Context length contribution
        if context:
            total_context_tokens = sum(len(msg.get("content", "").split()) for msg in context)
            score += total_context_tokens // 10
        
        return score
    
    def _should_use_gemini(self, message: str, context: Optional[List[Dict]] = None) -> bool:
        """Determine if Gemini should be used for this request."""
        if not self.gemini:
            return False
        
        complexity = self._calculate_complexity(message, context)
        should_use = complexity >= self.complexity_threshold
        
        logger.debug(f"Complexity score: {complexity}, threshold: {self.complexity_threshold}")
        logger.debug(f"Using {'Gemini' if should_use else 'Ollama'}")
        
        return should_use
    
    async def generate(
        self, 
        message: str, 
        context: Optional[List[Dict]] = None,
        force_model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a response using the appropriate model.
        
        Args:
            message: The user's message
            context: Optional conversation history
            force_model: Force a specific model ("ollama" or "gemini")
        
        Returns:
            Dict with response text and metadata
        """
        # Determine which model to use
        if force_model == "gemini" and self.gemini:
            use_gemini = True
        elif force_model == "ollama":
            use_gemini = False
        else:
            use_gemini = self._should_use_gemini(message, context)
        
        model_name = "gemini" if use_gemini else "ollama"
        
        try:
            if use_gemini:
                response = await self.gemini.generate(message, context)
            else:
                response = await self.ollama.generate(message, context)
            
            return {
                "text": response,
                "model": model_name,
                "model_version": settings.gemini_model if use_gemini else settings.ollama_model,
                "success": True
            }
        
        except Exception as e:
            logger.error(f"Error with {model_name}: {e}")
            
            # Fallback to other model
            if use_gemini and self.ollama:
                logger.info("Falling back to Ollama")
                try:
                    response = await self.ollama.generate(message, context)
                    return {
                        "text": response,
                        "model": "ollama",
                        "model_version": settings.ollama_model,
                        "success": True,
                        "fallback": True
                    }
                except Exception as fallback_error:
                    logger.error(f"Fallback also failed: {fallback_error}")
            
            return {
                "text": "I'm sorry, I encountered an error processing your request.",
                "model": model_name,
                "success": False,
                "error": str(e)
            }
