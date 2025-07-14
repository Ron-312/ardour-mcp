"""
Unit tests for OSC client
"""

import pytest
from unittest.mock import Mock, patch
from mcp_server.osc_client import OSCClient, get_osc_client, reset_osc_client

class TestOSCClient:
    """Test cases for OSC client"""
    
    def setup_method(self):
        """Setup for each test method"""
        reset_osc_client()
    
    @patch('mcp_server.osc_client.udp_client.SimpleUDPClient')
    def test_osc_client_initialization(self, mock_udp_client):
        """Test OSC client initialization"""
        mock_client = Mock()
        mock_udp_client.return_value = mock_client
        
        osc_client = OSCClient()
        
        assert osc_client.ip == "127.0.0.1"
        assert osc_client.port == 3819
        assert osc_client.client == mock_client
        mock_udp_client.assert_called_once_with("127.0.0.1", 3819)
    
    @patch('mcp_server.osc_client.udp_client.SimpleUDPClient')
    def test_osc_client_custom_ip_port(self, mock_udp_client):
        """Test OSC client with custom IP and port"""
        mock_client = Mock()
        mock_udp_client.return_value = mock_client
        
        osc_client = OSCClient(ip="192.168.1.100", port=3820)
        
        assert osc_client.ip == "192.168.1.100"
        assert osc_client.port == 3820
        mock_udp_client.assert_called_once_with("192.168.1.100", 3820)
    
    @patch('mcp_server.osc_client.udp_client.SimpleUDPClient')
    def test_send_message_success(self, mock_udp_client):
        """Test successful message sending"""
        mock_client = Mock()
        mock_udp_client.return_value = mock_client
        
        osc_client = OSCClient()
        result = osc_client.send_message("/test/address", "arg1", "arg2")
        
        assert result == True
        mock_client.send_message.assert_called_once_with("/test/address", ("arg1", "arg2"))
    
    @patch('mcp_server.osc_client.udp_client.SimpleUDPClient')
    def test_send_message_failure(self, mock_udp_client):
        """Test message sending failure"""
        mock_client = Mock()
        mock_client.send_message.side_effect = Exception("Network error")
        mock_udp_client.return_value = mock_client
        
        osc_client = OSCClient()
        result = osc_client.send_message("/test/address")
        
        assert result == False
    
    @patch('mcp_server.osc_client.udp_client.SimpleUDPClient')
    def test_transport_play(self, mock_udp_client):
        """Test transport play command"""
        mock_client = Mock()
        mock_udp_client.return_value = mock_client
        
        osc_client = OSCClient()
        result = osc_client.transport_play()
        
        assert result == True
        mock_client.send_message.assert_called_once_with("/ardour/transport_play", None)
    
    @patch('mcp_server.osc_client.udp_client.SimpleUDPClient')
    def test_transport_stop(self, mock_udp_client):
        """Test transport stop command"""
        mock_client = Mock()
        mock_udp_client.return_value = mock_client
        
        osc_client = OSCClient()
        result = osc_client.transport_stop()
        
        assert result == True
        mock_client.send_message.assert_called_once_with("/ardour/transport_stop", None)
    
    @patch('mcp_server.osc_client.udp_client.SimpleUDPClient')
    def test_set_strip_gain(self, mock_udp_client):
        """Test setting strip gain"""
        mock_client = Mock()
        mock_udp_client.return_value = mock_client
        
        osc_client = OSCClient()
        result = osc_client.set_strip_gain(1, -10.0)
        
        assert result == True
        mock_client.send_message.assert_called_once_with("/strip/0/gain", (-10.0,))
    
    @patch('mcp_server.osc_client.udp_client.SimpleUDPClient')
    def test_get_connection_info(self, mock_udp_client):
        """Test getting connection info"""
        mock_client = Mock()
        mock_udp_client.return_value = mock_client
        
        osc_client = OSCClient()
        info = osc_client.get_connection_info()
        
        assert info["ip"] == "127.0.0.1"
        assert info["port"] == 3819
        assert info["connected"] == True
    
    @patch('mcp_server.osc_client.udp_client.SimpleUDPClient')
    def test_get_osc_client_singleton(self, mock_udp_client):
        """Test singleton pattern for global OSC client"""
        mock_client = Mock()
        mock_udp_client.return_value = mock_client
        
        client1 = get_osc_client()
        client2 = get_osc_client()
        
        assert client1 is client2
        assert mock_udp_client.call_count == 1