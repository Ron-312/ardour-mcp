"""
OSC Client for communicating with Ardour DAW
"""

import logging
from typing import Optional, Any
from pythonosc import udp_client
from pythonosc.osc_message import OscMessage
from mcp_server.config import get_osc_config

logger = logging.getLogger(__name__)

class OSCClient:
    """OSC client for sending messages to Ardour"""
    
    def __init__(self, ip: Optional[str] = None, port: Optional[int] = None):
        """Initialize OSC client
        
        Args:
            ip: Target IP address (defaults to config value)
            port: Target port (defaults to config value)
        """
        osc_config = get_osc_config()
        self.ip = ip or osc_config["ip"]
        self.port = port or osc_config["port"]
        
        try:
            self.client = udp_client.SimpleUDPClient(self.ip, self.port)
            logger.info(f"OSC client initialized for {self.ip}:{self.port}")
        except Exception as e:
            logger.error(f"Failed to initialize OSC client: {e}")
            raise
    
    def send_message(self, address: str, *args: Any) -> bool:
        """Send OSC message to Ardour
        
        Args:
            address: OSC address (e.g., "/ardour/transport_play")
            *args: Message arguments
            
        Returns:
            True if message sent successfully, False otherwise
        """
        try:
            # Log connection details
            logger.info(f"OSC Client connecting to {self.ip}:{self.port}")
            logger.info(f"Sending OSC message: {address} with args: {args}")
            logger.info(f"Message type: address={type(address)}, args={type(args)}, arg_values={args}")
            
            # Send the message - python-osc requires at least one argument
            if args:
                logger.info(f"Sending with arguments: {args}")
                if len(args) == 1:
                    self.client.send_message(address, args[0])
                else:
                    self.client.send_message(address, list(args))
            else:
                logger.info("Sending with no arguments - using empty list")
                self.client.send_message(address, [])
            
            logger.info(f"✅ OSC message sent successfully: {address} {args}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to send OSC message {address}: {e}")
            logger.error(f"Connection details: {self.ip}:{self.port}")
            return False
    
    def transport_play(self) -> bool:
        """Start transport playback"""
        logger.info("Sending transport_play command...")
        return self.send_message("/transport_play", 1)
    
    def transport_stop(self) -> bool:
        """Stop transport playback"""
        logger.info("Sending transport_stop command...")
        return self.send_message("/transport_stop", 1)
    
    def transport_rewind(self) -> bool:
        """Rewind transport to beginning"""
        return self.send_message("/rewind", 1)
    
    def transport_fast_forward(self) -> bool:
        """Fast forward transport"""
        return self.send_message("/ffwd", 1)
    
    def goto_start(self) -> bool:
        """Move playhead to start"""
        return self.send_message("/goto_start", 1)
    
    def toggle_roll(self) -> bool:
        """Toggle between play and stop"""
        return self.send_message("/toggle_roll", 1)
    
    def set_strip_gain(self, strip_number: int, gain_db: float) -> bool:
        """Set gain for a specific strip/track
        
        Args:
            strip_number: Track number (1-based)
            gain_db: Gain in decibels
            
        Returns:
            True if message sent successfully, False otherwise
        """
        # Convert to 0-based for OSC message
        strip_index = strip_number - 1
        address = f"/strip/{strip_index}/gain"
        return self.send_message(address, gain_db)
    
    def set_strip_fader(self, strip_number: int, fader_position: float) -> bool:
        """Set fader position for a specific strip/track
        
        Args:
            strip_number: Track number (1-based)
            fader_position: Fader position (0.0 to 1.0)
            
        Returns:
            True if message sent successfully, False otherwise
        """
        # Convert to 0-based for OSC message
        strip_index = strip_number - 1
        address = f"/strip/{strip_index}/fader"
        return self.send_message(address, fader_position)
    
    def strip_mute(self, strip_number: int, mute: bool = True) -> bool:
        """Mute/unmute a specific strip/track
        
        Args:
            strip_number: Track number (1-based)
            mute: True to mute, False to unmute
            
        Returns:
            True if message sent successfully, False otherwise
        """
        # Convert to 0-based for OSC message
        strip_index = strip_number - 1
        address = f"/strip/{strip_index}/mute"
        return self.send_message(address, 1 if mute else 0)
    
    def strip_solo(self, strip_number: int, solo: bool = True) -> bool:
        """Solo/unsolo a specific strip/track
        
        Args:
            strip_number: Track number (1-based)
            solo: True to solo, False to unsolo
            
        Returns:
            True if message sent successfully, False otherwise
        """
        # Convert to 0-based for OSC message
        strip_index = strip_number - 1
        address = f"/strip/{strip_index}/solo"
        return self.send_message(address, 1 if solo else 0)
    
    def test_connection(self) -> bool:
        """Test connection to Ardour by sending a query message"""
        try:
            # Send a query to see if Ardour responds
            logger.info("Testing connection to Ardour...")
            self.send_message("/strip/list", 1)  # Query for strip list
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def get_connection_info(self) -> dict:
        """Get connection information
        
        Returns:
            Dictionary with connection details
        """
        return {
            "ip": self.ip,
            "port": self.port,
            "connected": hasattr(self, 'client') and self.client is not None
        }

# Global OSC client instance
_osc_client: Optional[OSCClient] = None

def get_osc_client() -> OSCClient:
    """Get global OSC client instance"""
    global _osc_client
    if _osc_client is None:
        _osc_client = OSCClient()
    return _osc_client

def reset_osc_client() -> None:
    """Reset global OSC client instance"""
    global _osc_client
    _osc_client = None