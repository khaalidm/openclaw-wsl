"""
OpenClaw Agent Core - Main agent logic and conversation handling
"""
import asyncio
from typing import Optional, Dict, Any, List, Callable
from loguru import logger
from datetime import datetime

from src.config.settings import settings
from src.models.router import ModelRouter


class Agent:
    """
    Main agent class that handles conversations and routes to appropriate models.
    """
    
    def __init__(self):
        self.router = ModelRouter()
        self.conversations: Dict[str, List[Dict]] = {}  # user_id -> message history
        self.max_history = settings.max_history_length
        self._message_handlers: List[Callable] = []
        
        logger.info("OpenClaw Agent initialized")
    
    def _get_conversation(self, user_id: str) -> List[Dict]:
        """Get or create conversation history for a user."""
        if user_id not in self.conversations:
            self.conversations[user_id] = []
        return self.conversations[user_id]
    
    def _add_to_history(self, user_id: str, role: str, content: str):
        """Add a message to conversation history."""
        history = self._get_conversation(user_id)
        history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        # Trim history if too long
        if len(history) > self.max_history:
            self.conversations[user_id] = history[-self.max_history:]
    
    def clear_history(self, user_id: str):
        """Clear conversation history for a user."""
        if user_id in self.conversations:
            del self.conversations[user_id]
            logger.info(f"Cleared history for user: {user_id}")
    
    def on_message(self, handler: Callable):
        """Register a message handler callback."""
        self._message_handlers.append(handler)
    
    async def process_message(
        self, 
        message: str, 
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process an incoming message and generate a response.
        
        Args:
            message: The user's message
            user_id: Unique identifier for the user
            metadata: Optional metadata (e.g., source channel)
        
        Returns:
            Response dict with text and metadata
        """
        logger.info(f"Processing message from {user_id}: {message[:50]}...")
        
        # Check for special commands
        if message.strip().lower() == "/clear":
            self.clear_history(user_id)
            return {
                "text": "Conversation history cleared.",
                "model": "system",
                "success": True
            }
        
        if message.strip().lower() == "/status":
            return await self._handle_status_command()
        
        if message.strip().lower().startswith("/model "):
            return await self._handle_model_command(message, user_id)
        
        # Add message to history
        self._add_to_history(user_id, "user", message)
        
        # Get conversation context (exclude current message which is already in format)
        context = self._get_conversation(user_id)[:-1]
        
        # Generate response
        response = await self.router.generate(message, context)
        
        # Add response to history
        if response["success"]:
            self._add_to_history(user_id, "assistant", response["text"])
        
        # Notify handlers
        for handler in self._message_handlers:
            try:
                await handler(user_id, message, response)
            except Exception as e:
                logger.error(f"Message handler error: {e}")
        
        return response
    
    async def _handle_status_command(self) -> Dict[str, Any]:
        """Handle /status command."""
        ollama_status = "✅ Available" if self.router.ollama else "❌ Not configured"
        gemini_status = "✅ Available" if self.router.gemini else "❌ Not configured"
        
        status_text = f"""**OpenClaw Status**

🤖 **Models**
- Ollama ({settings.ollama_model}): {ollama_status}
- Gemini ({settings.gemini_model}): {gemini_status}

⚙️ **Configuration**
- Complexity Threshold: {settings.complexity_threshold}
- Max History: {settings.max_history_length}
- Active Conversations: {len(self.conversations)}"""
        
        return {
            "text": status_text,
            "model": "system",
            "success": True
        }
    
    async def _handle_model_command(self, message: str, user_id: str) -> Dict[str, Any]:
        """Handle /model [ollama|gemini] command to force a specific model."""
        parts = message.strip().split()
        if len(parts) < 2:
            return {
                "text": "Usage: /model [ollama|gemini] <message>",
                "model": "system",
                "success": True
            }
        
        model = parts[1].lower()
        if model not in ["ollama", "gemini"]:
            return {
                "text": "Invalid model. Use 'ollama' or 'gemini'.",
                "model": "system",
                "success": True
            }
        
        # Extract the actual message after /model <model>
        actual_message = " ".join(parts[2:]) if len(parts) > 2 else ""
        
        if not actual_message:
            return {
                "text": f"Model set to {model}. Now send your message.",
                "model": "system",
                "success": True
            }
        
        # Process with forced model
        self._add_to_history(user_id, "user", actual_message)
        context = self._get_conversation(user_id)[:-1]
        
        response = await self.router.generate(actual_message, context, force_model=model)
        
        if response["success"]:
            self._add_to_history(user_id, "assistant", response["text"])
        
        return response


# Singleton instance
_agent: Optional[Agent] = None


def get_agent() -> Agent:
    """Get or create the global agent instance."""
    global _agent
    if _agent is None:
        _agent = Agent()
    return _agent
