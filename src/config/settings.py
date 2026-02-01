"""
OpenClaw Agent Configuration
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Ollama Configuration
    ollama_host: str = Field(default="http://localhost:11434")
    ollama_model: str = Field(default="llama3.2")
    
    # Gemini Configuration
    gemini_api_key: Optional[str] = Field(default=None)
    gemini_model: str = Field(default="gemini-1.5-pro")
    
    # Model Selection
    complexity_threshold: int = Field(default=500)
    gemini_trigger_keywords: str = Field(
        default="analyze|generate code|complex|explain in detail|research"
    )
    
    # WhatsApp Configuration
    whatsapp_session_path: str = Field(default="./data/whatsapp-session")
    whatsapp_allowed_numbers: str = Field(default="")
    
    # Agent Configuration
    log_level: str = Field(default="info")
    response_timeout: int = Field(default=30)
    max_history_length: int = Field(default=20)
    
    @property
    def gemini_keywords_list(self) -> List[str]:
        """Parse Gemini trigger keywords into a list (pipe-separated)."""
        return [k.strip().lower() for k in self.gemini_trigger_keywords.split("|")]
    
    @property
    def allowed_numbers_list(self) -> List[str]:
        """Parse allowed WhatsApp numbers into a list (pipe-separated)."""
        if not self.whatsapp_allowed_numbers:
            return []
        return [n.strip() for n in self.whatsapp_allowed_numbers.split("|")]
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }


# Global settings instance
settings = Settings()
