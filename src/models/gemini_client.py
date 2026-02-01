"""
Gemini Client - Google's Gemini API integration for complex tasks
"""
import google.generativeai as genai
from typing import Optional, List, Dict
from loguru import logger

from src.config.settings import settings


class GeminiClient:
    """Client for interacting with Google Gemini API."""
    
    def __init__(self):
        if not settings.gemini_api_key:
            raise ValueError("Gemini API key not configured")
        
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(settings.gemini_model)
        self.model_name = settings.gemini_model
        
        logger.info(f"Gemini client initialized with model: {self.model_name}")
    
    def _format_history(self, context: Optional[List[Dict]] = None) -> List[Dict]:
        """Format conversation history for Gemini."""
        if not context:
            return []
        
        history = []
        for msg in context:
            role = "user" if msg.get("role") == "user" else "model"
            history.append({
                "role": role,
                "parts": [msg.get("content", "")]
            })
        
        return history
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for Gemini."""
        return """You are OpenClaw, an advanced AI assistant capable of handling complex tasks.

Your capabilities include:
- Deep analysis and reasoning
- Code generation and debugging
- Research and comprehensive explanations
- Multi-step problem solving

Guidelines:
- Provide thorough, well-structured responses
- Use code blocks with syntax highlighting when appropriate
- Break down complex topics into digestible parts
- Be accurate and acknowledge uncertainty when applicable"""
    
    async def generate(
        self, 
        message: str, 
        context: Optional[List[Dict]] = None
    ) -> str:
        """
        Generate a response using Gemini.
        
        Args:
            message: The user's message
            context: Optional conversation history
        
        Returns:
            The generated response text
        """
        logger.debug(f"Gemini request: {self.model_name}")
        
        try:
            # Start a chat session with history
            history = self._format_history(context)
            
            # Add system context to the first message
            system_prompt = self._build_system_prompt()
            
            if history:
                chat = self.model.start_chat(history=history)
                response = await chat.send_message_async(message)
            else:
                # For first message, include system prompt
                full_prompt = f"{system_prompt}\n\nUser: {message}"
                response = await self.model.generate_content_async(full_prompt)
            
            return response.text
        
        except Exception as e:
            logger.error(f"Gemini generation error: {e}")
            raise
    
    async def generate_with_thinking(
        self, 
        message: str, 
        context: Optional[List[Dict]] = None
    ) -> Dict[str, str]:
        """
        Generate a response with chain-of-thought reasoning visible.
        
        Returns:
            Dict with 'thinking' and 'response' keys
        """
        thinking_prompt = f"""Let's approach this step by step.

Question: {message}

First, let me think through this:
<thinking>
[Your step-by-step reasoning here]
</thinking>

Now, my response:
<response>
[Your final answer here]
</response>"""
        
        response = await self.generate(thinking_prompt, context)
        
        # Parse thinking and response
        import re
        thinking_match = re.search(r'<thinking>(.*?)</thinking>', response, re.DOTALL)
        response_match = re.search(r'<response>(.*?)</response>', response, re.DOTALL)
        
        return {
            "thinking": thinking_match.group(1).strip() if thinking_match else "",
            "response": response_match.group(1).strip() if response_match else response
        }
