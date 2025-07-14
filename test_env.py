#!/usr/bin/env python3
"""Test script to verify environment variable loading with python-dotenv"""

import os
from dotenv import load_dotenv

def test_env_loading():
    """Test that environment variables are loaded correctly"""
    # Load environment variables from .env file
    load_dotenv()
    
    # Test OSC configuration
    osc_ip = os.getenv('OSC_TARGET_IP')
    osc_port = os.getenv('OSC_TARGET_PORT')
    
    # Test FastAPI configuration
    http_port = os.getenv('HTTP_PORT')
    http_host = os.getenv('HTTP_HOST')
    
    # Test application configuration
    debug = os.getenv('DEBUG')
    log_level = os.getenv('LOG_LEVEL')
    
    print("Environment Variables Loaded:")
    print(f"  OSC_TARGET_IP: {osc_ip}")
    print(f"  OSC_TARGET_PORT: {osc_port}")
    print(f"  HTTP_PORT: {http_port}")
    print(f"  HTTP_HOST: {http_host}")
    print(f"  DEBUG: {debug}")
    print(f"  LOG_LEVEL: {log_level}")
    
    # Verify required variables are set
    required_vars = ['OSC_TARGET_IP', 'OSC_TARGET_PORT', 'HTTP_PORT', 'HTTP_HOST']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"\nMissing required variables: {missing_vars}")
        return False
    
    print("\nAll required environment variables are set!")
    return True

if __name__ == "__main__":
    success = test_env_loading()
    exit(0 if success else 1)