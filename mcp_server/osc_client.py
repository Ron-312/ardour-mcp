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
            
            logger.info(f"OSC message sent successfully: {address} {args}")
            return True
        except Exception as e:
            logger.error(f"Failed to send OSC message {address}: {e}")
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
    
    def set_strip_name(self, strip_number: int, name: str) -> bool:
        """Set name for a specific strip/track
        
        Args:
            strip_number: Track number (1-based)
            name: New name for the track
            
        Returns:
            True if message sent successfully, False otherwise
        """
        # Convert to 0-based for OSC message
        strip_index = strip_number - 1
        address = f"/strip/{strip_index}/name"
        return self.send_message(address, name)
    
    def set_strip_record_enable(self, strip_number: int, enabled: bool = True) -> bool:
        """Enable/disable recording for a specific strip/track
        
        Args:
            strip_number: Track number (1-based)
            enabled: True to enable recording, False to disable
            
        Returns:
            True if message sent successfully, False otherwise
        """
        # Convert to 0-based for OSC message
        strip_index = strip_number - 1
        address = f"/strip/{strip_index}/recenable"
        return self.send_message(address, 1 if enabled else 0)
    
    def set_strip_record_safe(self, strip_number: int, safe: bool = True) -> bool:
        """Enable/disable record safe for a specific strip/track
        
        Args:
            strip_number: Track number (1-based)
            safe: True to enable record safe, False to disable
            
        Returns:
            True if message sent successfully, False otherwise
        """
        # Convert to 0-based for OSC message
        strip_index = strip_number - 1
        address = f"/strip/{strip_index}/record_safe"
        return self.send_message(address, 1 if safe else 0)
    
    def set_strip_pan(self, strip_number: int, pan_position: float) -> bool:
        """Set pan position for a specific strip/track
        
        Args:
            strip_number: Track number (1-based)
            pan_position: Pan position (-1.0 = full left, 0.0 = center, 1.0 = full right)
            
        Returns:
            True if message sent successfully, False otherwise
        """
        # Convert to 0-based for OSC message
        strip_index = strip_number - 1
        address = f"/strip/{strip_index}/pan_stereo_position"
        # Clamp pan position to valid range
        pan_position = max(-1.0, min(1.0, pan_position))
        return self.send_message(address, pan_position)
    
    def query_strip_list(self) -> bool:
        """Query Ardour for list of all strips/tracks
        
        Returns:
            True if message sent successfully, False otherwise
        """
        logger.info("[OSC CLIENT] Sending strip list query to Ardour")
        success = self.send_message("/strip/list", 1)
        if success:
            logger.info("[OSC CLIENT] Strip list query sent successfully")
        else:
            logger.error("[OSC CLIENT] Failed to send strip list query")
        return success
    
    # Send/Aux Control Commands
    def set_send_level(self, track_index: int, send_index: int, level: float) -> bool:
        """Set send level for track to specific aux
        
        Args:
            track_index: Track index (0-based)
            send_index: Send index (0-based)  
            level: Send level (0.0-1.0)
            
        Returns:
            True if message sent successfully, False otherwise
        """
        return self.send_message(f"/strip/{track_index}/send/{send_index}/fader", level)
    
    def set_send_gain(self, track_index: int, send_index: int, gain_db: float) -> bool:
        """Set send gain in dB for track to specific aux
        
        Args:
            track_index: Track index (0-based)
            send_index: Send index (0-based)
            gain_db: Send gain in dB
            
        Returns:
            True if message sent successfully, False otherwise
        """
        return self.send_message(f"/strip/{track_index}/send/{send_index}/gain", gain_db)
    
    def set_send_enable(self, track_index: int, send_index: int, enabled: bool) -> bool:
        """Enable or disable a send
        
        Args:
            track_index: Track index (0-based)
            send_index: Send index (0-based)
            enabled: True to enable, False to disable
            
        Returns:
            True if message sent successfully, False otherwise
        """
        return self.send_message(f"/strip/{track_index}/send/{send_index}/enable", 1 if enabled else 0)
    
    def list_track_sends(self, track_index: int) -> bool:
        """List all sends for a track
        
        Args:
            track_index: Track index (0-based)
            
        Returns:
            True if message sent successfully, False otherwise
        """
        return self.send_message(f"/strip/{track_index}/sends", 1)
    
    # Surface Setup Commands
    def setup_surface(self, bank_size: int = 0, strip_types: int = 159, feedback: int = 0) -> bool:
        """Setup OSC surface configuration before querying strips
        
        Args:
            bank_size: Number of strips per bank (0 = infinite)
            strip_types: Bitwise value for included strip types (159 = all except hidden)
            feedback: Bitwise value for feedback configuration (0 = all off for now)
            
        Returns:
            True if message sent successfully, False otherwise
        """
        logger.info(f"[OSC CLIENT] Setting up surface: bank_size={bank_size}, strip_types={strip_types}, feedback={feedback}")
        
        # Decode strip types for logging
        strip_type_names = []
        if strip_types & 1:  strip_type_names.append("AudioTracks")
        if strip_types & 2:  strip_type_names.append("MidiTracks") 
        if strip_types & 4:  strip_type_names.append("AudioBusses")
        if strip_types & 8:  strip_type_names.append("MidiBusses")
        if strip_types & 16: strip_type_names.append("VCAs")
        if strip_types & 32: strip_type_names.append("Master")
        if strip_types & 64: strip_type_names.append("Monitor")
        
        logger.info(f"[OSC CLIENT] Strip types included: {', '.join(strip_type_names)}")
        
        success = self.send_message("/set_surface", bank_size, strip_types, feedback)
        if success:
            logger.info("[OSC CLIENT] Surface setup sent successfully")
        else:
            logger.error("[OSC CLIENT] Failed to send surface setup")
        return success
    
    def list_strips(self) -> bool:
        """Request list of all available strips from Ardour
        
        Returns:
            True if message sent successfully, False otherwise
        """
        # Send the strip list request
        return self.send_message("/strip/list", 1)

    # Plugin Discovery Commands
    def list_track_plugins(self, strip_id: int) -> bool:
        """List all plugins on a specific strip
        
        Args:
            strip_id: Surface Strip ID (SSID) from strip list (1-based)
            
        Returns:
            True if message sent successfully, False otherwise
        """
        # First select the strip
        success1 = self.send_message("/select/strip", strip_id)
        
        # Try to discover plugins by iterating through plugin positions
        # Since there's no direct "list plugins" command, we'll try to select
        # plugins at different positions and see what responds
        for plugin_index in range(8):  # Try first 8 plugin slots
            self.send_message("/select/plugin", plugin_index)
            # Request plugin activation state to see if plugin exists
            self.send_message("/select/plugin/activate", 0)  # Query current state
            
        return success1
    
    def get_plugin_parameters(self, strip_id: int, plugin_id: int) -> bool:
        """Get parameter list for a specific plugin
        
        Args:
            strip_id: Surface Strip ID (SSID) from strip list
            plugin_id: Plugin ID (1-based as returned by plugin list)
            
        Returns:
            True if message sent successfully, False otherwise
        """
        # Use the correct Ardour OSC command: /strip/plugin/descriptor ssid piid
        # where ssid is Surface Strip ID and piid is Plugin ID
        # Select the strip first
        self.send_message("/select/strip", strip_id)
        # Select the plugin
        self.send_message("/select/plugin", plugin_id)
        # Now we can query parameters through selection
        return True    
    
    def get_plugin_info(self, track_index: int, plugin_id: int) -> bool:
        """Get detailed information about a specific plugin
        
        Args:
            track_index: Track index (0-based)
            plugin_id: Plugin ID (0-based)
            
        Returns:
            True if message sent successfully, False otherwise
        """
        # Select track and plugin, then request info
        self.send_message("/select/strip", track_index)
        self.send_message("/select/plugin", plugin_id)
        return self.send_message("/select/plugin/name", 1)
    
    def scan_all_plugins(self) -> bool:
        """Scan all tracks for plugins
        
        Returns:
            True if message sent successfully, False otherwise
        """
        # Request comprehensive plugin scan
        # This would trigger a series of OSC messages to discover all plugins
        return self.send_message("/strip/list", 1)
    
    def select_track_and_plugin(self, track_index: int, plugin_id: int) -> bool:
        """Select a specific track and plugin for subsequent operations
        
        Args:
            track_index: Track index (0-based)
            plugin_id: Plugin ID (0-based)
            
        Returns:
            True if message sent successfully, False otherwise
        """
        success1 = self.send_message("/select/strip", track_index)
        success2 = self.send_message("/select/plugin", plugin_id)
        return success1 and success2
    
    def select_strip(self, strip_id: int) -> bool:
        """Select a strip (GUI selection)
        
        Args:
            strip_id: Strip ID to select
            
        Returns:
            True if message sent successfully, False otherwise
        """
        return self.send_message("/strip/select", strip_id, 1)
    
    def expand_strip(self, strip_id: int, expand: bool = True) -> bool:
        """Expand a strip (local expansion)
        
        Args:
            strip_id: Strip ID to expand
            expand: True to expand, False to contract
            
        Returns:
            True if message sent successfully, False otherwise
        """
        return self.send_message("/strip/expand", strip_id, 1 if expand else 0)
    
    def select_plugin_by_delta(self, delta: int) -> bool:
        """Select plugin by delta from current selection
        
        Args:
            delta: Delta to apply to current plugin selection
            
        Returns:
            True if message sent successfully, False otherwise
        """
        return self.send_message("/select/plugin", delta)
    
    def send_selected_operation(self, address: str, *args) -> bool:
        """Send OSC message for selected strip operations
        
        Args:
            address: OSC address (e.g., "/select/gain")
            *args: Message arguments
            
        Returns:
            True if message sent successfully, False otherwise
        """
        return self.send_message(address, *args)
    
    def set_plugin_activate(self, track_index: int, plugin_id: int, active: bool) -> bool:
        """Activate or bypass a plugin
        
        Args:
            track_index: Track index (0-based)
            plugin_id: Plugin ID (0-based)
            active: True to activate, False to bypass
            
        Returns:
            True if message sent successfully, False otherwise
        """
        # Select track and plugin first
        self.send_message("/select/strip", track_index)
        self.send_message("/select/plugin", plugin_id)
        # Then activate/deactivate
        return self.send_message("/select/plugin/activate", 1 if active else 0)
    
    def set_plugin_parameter(self, track_index: int, plugin_id: int, parameter_id: int, value: float) -> bool:
        """Set a plugin parameter value
        
        Args:
            track_index: Track index (0-based)
            plugin_id: Plugin ID (0-based)
            parameter_id: Parameter ID (1-based, as per Ardour OSC spec)
            value: Parameter value (0.0 to 1.0)
            
        Returns:
            True if message sent successfully, False otherwise
        """
        # Select track and plugin first
        self.send_message("/select/strip", track_index)
        self.send_message("/select/plugin", plugin_id)
        # Then set parameter value
        return self.send_message("/select/plugin/parameter", parameter_id, value)
    
    # Recording Control Commands
    def set_recording_enable(self, enabled: bool) -> bool:
        """Enable or disable global recording
        
        Args:
            enabled: True to enable recording, False to disable
            
        Returns:
            True if message sent successfully, False otherwise
        """
        return self.send_message("/rec_enable_toggle", 1 if enabled else 0)
    
    def set_punch_in(self, enabled: bool) -> bool:
        """Enable or disable punch-in recording
        
        Args:
            enabled: True to enable punch-in, False to disable
            
        Returns:
            True if message sent successfully, False otherwise
        """
        return self.send_message("/toggle_punch_in", 1 if enabled else 0)
    
    def set_punch_out(self, enabled: bool) -> bool:
        """Enable or disable punch-out recording
        
        Args:
            enabled: True to enable punch-out, False to disable
            
        Returns:
            True if message sent successfully, False otherwise
        """
        return self.send_message("/toggle_punch_out", 1 if enabled else 0)
    
    def set_global_input_monitor(self, enabled: bool) -> bool:
        """Enable or disable global input monitoring
        
        Args:
            enabled: True to enable input monitoring, False to disable
            
        Returns:
            True if message sent successfully, False otherwise
        """
        return self.send_message("/toggle_monitor_input", 1 if enabled else 0)
    
    def set_track_input_monitor(self, track_index: int, enabled: bool) -> bool:
        """Enable or disable input monitoring for specific track
        
        Args:
            track_index: Track index (0-based)
            enabled: True to enable input monitoring, False to disable
            
        Returns:
            True if message sent successfully, False otherwise
        """
        return self.send_message(f"/strip/{track_index}/monitor_input", 1 if enabled else 0)
    
    def get_recording_status(self) -> bool:
        """Get current recording status
        
        Returns:
            True if message sent successfully, False otherwise
        """
        # Request recording status information
        return self.send_message("/recording/status", 1)
    
    # Session Management Commands
    def open_add_track_dialog(self) -> bool:
        """Open Ardour's Add Track/Bus dialog
        
        Returns:
            True if message sent successfully, False otherwise
        """
        return self.send_message("/access_action", "Main/AddTrackBus")
    
    def save_session(self) -> bool:
        """Save current session
        
        Returns:
            True if message sent successfully, False otherwise
        """
        return self.send_message("/access_action", "Main/Save")
    
    def save_session_as(self) -> bool:
        """Open Save Session As dialog
        
        Returns:
            True if message sent successfully, False otherwise
        """
        return self.send_message("/access_action", "Main/SaveAs")
    
    def create_snapshot(self, switch_to_new: bool = False) -> bool:
        """Create a session snapshot
        
        Args:
            switch_to_new: If True, switch to new snapshot; if False, stay on current
            
        Returns:
            True if message sent successfully, False otherwise
        """
        if switch_to_new:
            return self.send_message("/access_action", "Main/QuickSnapshotSwitch")
        else:
            return self.send_message("/access_action", "Main/QuickSnapshotStay")
    
    def undo_last_action(self) -> bool:
        """Undo last action
        
        Returns:
            True if message sent successfully, False otherwise
        """
        return self.send_message("/access_action", "Editor/undo")
    
    def redo_last_action(self) -> bool:
        """Redo last action
        
        Returns:
            True if message sent successfully, False otherwise
        """
        return self.send_message("/access_action", "Editor/redo")
    
    # Transport Extensions
    def toggle_loop(self) -> bool:
        """Toggle loop mode
        
        Returns:
            True if message sent successfully, False otherwise
        """
        return self.send_message("/loop_toggle", 1)
    
    def goto_start(self) -> bool:
        """Move playhead to start"""
        return self.send_message("/goto_start", 1)
    
    def goto_end(self) -> bool:
        """Move playhead to end"""
        return self.send_message("/goto_end", 1)
    
    def add_marker(self) -> bool:
        """Add marker at current position
        
        Returns:
            True if message sent successfully, False otherwise
        """
        return self.send_message("/add_marker", 1)
    
    def next_marker(self) -> bool:
        """Go to next marker
        
        Returns:
            True if message sent successfully, False otherwise
        """
        return self.send_message("/next_marker", 1)
    
    def prev_marker(self) -> bool:
        """Go to previous marker
        
        Returns:
            True if message sent successfully, False otherwise
        """
        return self.send_message("/prev_marker", 1)
    
    def set_transport_speed(self, speed: float) -> bool:
        """Set transport speed
        
        Args:
            speed: Speed multiplier (-8.0 to 8.0, 1.0 = normal speed)
            
        Returns:
            True if message sent successfully, False otherwise
        """
        # Clamp speed to valid range
        speed = max(-8.0, min(8.0, speed))
        return self.send_message("/set_transport_speed", speed)
    
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