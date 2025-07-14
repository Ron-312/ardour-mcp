"""
Unit tests for configuration management
"""

import pytest
import os
from mcp_server.config import Settings, get_settings, validate_settings, get_osc_config, get_server_config

def test_settings_default_values():
    """Test that settings have correct default values"""
    settings = Settings()
    
    assert settings.osc_target_ip == "127.0.0.1"
    assert settings.osc_target_port == 3819
    assert settings.http_host == "0.0.0.0"
    assert settings.http_port == 8000
    assert settings.debug == False
    assert settings.log_level == "info"

def test_settings_from_env(monkeypatch):
    """Test that settings are loaded from environment variables"""
    # Set environment variables
    monkeypatch.setenv("OSC_TARGET_IP", "192.168.1.100")
    monkeypatch.setenv("OSC_TARGET_PORT", "3820")
    monkeypatch.setenv("HTTP_HOST", "127.0.0.1")
    monkeypatch.setenv("HTTP_PORT", "9000")
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv("LOG_LEVEL", "debug")
    
    settings = Settings()
    
    assert settings.osc_target_ip == "192.168.1.100"
    assert settings.osc_target_port == 3820
    assert settings.http_host == "127.0.0.1"
    assert settings.http_port == 9000
    assert settings.debug == True
    assert settings.log_level == "debug"

def test_validate_settings():
    """Test settings validation"""
    assert validate_settings() == True

def test_get_osc_config():
    """Test OSC configuration retrieval"""
    config = get_osc_config()
    
    assert "ip" in config
    assert "port" in config
    assert config["ip"] == "127.0.0.1"
    assert config["port"] == 3819

def test_get_server_config():
    """Test server configuration retrieval"""
    config = get_server_config()
    
    assert "host" in config
    assert "port" in config
    assert config["host"] == "0.0.0.0"
    assert config["port"] == 8000