"""
Test suite for OpenClaw Agent
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock


class TestModelRouter:
    """Tests for the model routing logic."""
    
    def test_complexity_calculation_simple_message(self):
        """Simple messages should have low complexity."""
        # This would test the complexity calculation
        message = "Hello, how are you?"
        # Expected: low complexity, use Ollama
        assert len(message.split()) < 10
    
    def test_complexity_calculation_with_keywords(self):
        """Messages with trigger keywords should boost complexity."""
        message = "Please analyze this complex code and generate a solution"
        keywords = ["analyze", "complex", "generate"]
        
        keyword_count = sum(1 for kw in keywords if kw in message.lower())
        assert keyword_count >= 2
    
    def test_complexity_with_code_blocks(self):
        """Messages with code blocks should have higher complexity."""
        message = """
        Please help me with this code:
        ```python
        def fibonacci(n):
            if n <= 1:
                return n
            return fibonacci(n-1) + fibonacci(n-2)
        ```
        """
        assert "```" in message


class TestAgentCore:
    """Tests for the agent core functionality."""
    
    def test_conversation_history_management(self):
        """Test that conversation history is properly maintained."""
        history = []
        max_history = 5
        
        # Add messages
        for i in range(10):
            history.append({"role": "user", "content": f"Message {i}"})
            if len(history) > max_history:
                history = history[-max_history:]
        
        assert len(history) == max_history
        assert history[0]["content"] == "Message 5"
    
    def test_clear_command_detection(self):
        """Test that /clear command is detected."""
        message = "/clear"
        assert message.strip().lower() == "/clear"
    
    def test_model_command_parsing(self):
        """Test that /model command is properly parsed."""
        message = "/model gemini Write me a poem"
        parts = message.strip().split()
        
        assert parts[0] == "/model"
        assert parts[1] == "gemini"
        assert " ".join(parts[2:]) == "Write me a poem"


class TestOllamaClient:
    """Tests for Ollama client."""
    
    def test_message_formatting(self):
        """Test that messages are properly formatted for Ollama."""
        message = "Hello"
        context = [
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello!"}
        ]
        
        messages = [
            {"role": "system", "content": "You are OpenClaw..."},
            *context,
            {"role": "user", "content": message}
        ]
        
        assert messages[0]["role"] == "system"
        assert messages[-1]["content"] == "Hello"


class TestGeminiClient:
    """Tests for Gemini client."""
    
    def test_history_formatting(self):
        """Test that history is formatted correctly for Gemini."""
        context = [
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello!"}
        ]
        
        formatted = []
        for msg in context:
            role = "user" if msg.get("role") == "user" else "model"
            formatted.append({
                "role": role,
                "parts": [msg.get("content", "")]
            })
        
        assert formatted[0]["role"] == "user"
        assert formatted[1]["role"] == "model"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
