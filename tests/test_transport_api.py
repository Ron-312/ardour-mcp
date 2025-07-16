"""
Unit tests for transport API endpoints
"""

import sys
import os
# Add the parent directory to Python path so we can import mcp_server
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from mcp_server.main import app

client = TestClient(app)

class TestTransportAPI:
    """Test cases for transport API endpoints"""
    
    @patch('mcp_server.api.transport.get_osc_client')
    def test_play_transport_success(self, mock_get_osc_client):
        """Test successful transport play"""
        mock_osc_client = Mock()
        mock_osc_client.transport_play.return_value = True
        mock_get_osc_client.return_value = mock_osc_client
        
        response = client.post("/transport/play")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["action"] == "play"
        assert data["osc_address"] == "/ardour/transport_play"
        mock_osc_client.transport_play.assert_called_once()
    
    @patch('mcp_server.api.transport.get_osc_client')
    def test_play_transport_failure(self, mock_get_osc_client):
        """Test transport play failure"""
        mock_osc_client = Mock()
        mock_osc_client.transport_play.return_value = False
        mock_get_osc_client.return_value = mock_osc_client
        
        response = client.post("/transport/play")
        
        assert response.status_code == 500
        data = response.json()
        assert "Failed to send transport play command" in data["detail"]
    
    @patch('mcp_server.api.transport.get_osc_client')
    def test_play_transport_exception(self, mock_get_osc_client):
        """Test transport play with exception"""
        mock_get_osc_client.side_effect = Exception("OSC connection error")
        
        response = client.post("/transport/play")
        
        assert response.status_code == 500
        data = response.json()
        assert "Internal server error" in data["detail"]
    
    @patch('mcp_server.api.transport.get_osc_client')
    def test_stop_transport_success(self, mock_get_osc_client):
        """Test successful transport stop"""
        mock_osc_client = Mock()
        mock_osc_client.transport_stop.return_value = True
        mock_get_osc_client.return_value = mock_osc_client
        
        response = client.post("/transport/stop")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["action"] == "stop"
        assert data["osc_address"] == "/ardour/transport_stop"
        mock_osc_client.transport_stop.assert_called_once()
    
    @patch('mcp_server.api.transport.get_osc_client')
    def test_stop_transport_failure(self, mock_get_osc_client):
        """Test transport stop failure"""
        mock_osc_client = Mock()
        mock_osc_client.transport_stop.return_value = False
        mock_get_osc_client.return_value = mock_osc_client
        
        response = client.post("/transport/stop")
        
        assert response.status_code == 500
        data = response.json()
        assert "Failed to send transport stop command" in data["detail"]