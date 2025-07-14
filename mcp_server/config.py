"""
Configuration management for Ardour MCP Server
"""

import os
from pydantic import Field
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # OSC Configuration
    osc_target_ip: str = Field(default="127.0.0.1", env="OSC_TARGET_IP")
    osc_target_port: int = Field(default=3819, env="OSC_TARGET_PORT")
    
    # FastAPI Server Configuration
    http_host: str = Field(default="0.0.0.0", env="HTTP_HOST")
    http_port: int = Field(default=8000, env="HTTP_PORT")
    
    # Application Configuration
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="info", env="LOG_LEVEL")
    
    # Optional API Keys
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False
    }

# Global settings instance
settings = Settings()

def get_settings() -> Settings:
    """Get application settings"""
    return settings

def validate_settings() -> bool:
    """Validate that all required settings are present"""
    required_settings = [
        settings.osc_target_ip,
        settings.osc_target_port,
        settings.http_host,
        settings.http_port
    ]
    
    return all(setting is not None for setting in required_settings)

def get_osc_config() -> dict:
    """Get OSC client configuration"""
    return {
        "ip": settings.osc_target_ip,
        "port": settings.osc_target_port
    }

def get_server_config() -> dict:
    """Get HTTP server configuration"""
    return {
        "host": settings.http_host,
        "port": settings.http_port
    }