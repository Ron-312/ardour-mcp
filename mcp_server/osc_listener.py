"""
OSC Listener for receiving feedback from Ardour DAW
"""

import logging
import threading
import time
from typing import Dict, List, Optional, Callable, Any
from pythonosc import dispatcher
from pythonosc import osc_server
from pythonosc.osc_message import OscMessage
from dataclasses import dataclass
from mcp_server.config import get_osc_config

logger = logging.getLogger(__name__)

@dataclass
class PluginParameter:
    """Represents a plugin parameter with its metadata"""
    id: int
    name: str
    value: float
    min_value: float
    max_value: float
    unit: str
    type: str
    controllable: bool
    
@dataclass
class PluginInfo:
    """Represents a plugin with its parameters"""
    id: int
    name: str
    enabled: bool
    parameters: List[PluginParameter]
    
@dataclass
class TrackInfo:
    """Represents a track with its plugins"""
    id: int
    name: str
    plugins: List[PluginInfo]

class OSCListener:
    """OSC listener for receiving feedback from Ardour"""
    
    def __init__(self, listen_port: int = 3820):
        """Initialize OSC listener
        
        Args:
            listen_port: Port to listen on for OSC feedback
        """
        self.listen_port = listen_port
        self.server = None
        self.server_thread = None
        self.running = False
        
        # Data storage for discovered plugins
        self.tracks: Dict[int, TrackInfo] = {}
        self.current_track_id: Optional[int] = None
        self.current_plugin_id: Optional[int] = None
        
        # Callbacks for real-time updates
        self.parameter_callbacks: List[Callable] = []
        self.plugin_callbacks: List[Callable] = []
        
        # Setup OSC dispatcher
        self.dispatcher = dispatcher.Dispatcher()
        self._setup_message_handlers()
        
    def _setup_message_handlers(self):
        """Setup OSC message handlers for different message types"""
        
        # Plugin parameter feedback
        self.dispatcher.map("/select/plugin/parameter", self._handle_plugin_parameter)
        self.dispatcher.map("/select/plugin/parameters", self._handle_plugin_parameters)
        
        # Plugin info feedback
        self.dispatcher.map("/select/plugin/name", self._handle_plugin_name)
        self.dispatcher.map("/select/plugin/activate", self._handle_plugin_activate)
        
        # Track/strip feedback
        self.dispatcher.map("/select/strip", self._handle_track_select)
        self.dispatcher.map("/strip/list", self._handle_strip_list)
        
        # Parameter value updates
        self.dispatcher.map("/select/plugin/parameter/value", self._handle_parameter_value)
        
        # Generic fallback for debugging
        self.dispatcher.map("/*", self._handle_debug_message)
        
    def _handle_plugin_parameter(self, unused_addr: str, *args):
        """Handle plugin parameter information"""
        try:
            if len(args) >= 6:
                param_id = int(args[0])
                param_name = str(args[1])
                param_value = float(args[2])
                param_min = float(args[3])
                param_max = float(args[4])
                param_unit = str(args[5]) if len(args) > 5 else ""
                
                logger.info(f"Plugin parameter: ID={param_id}, Name={param_name}, Value={param_value}, Range=[{param_min}, {param_max}], Unit={param_unit}")
                
                # Store parameter information
                if self.current_track_id is not None and self.current_plugin_id is not None:
                    self._store_parameter(param_id, param_name, param_value, param_min, param_max, param_unit)
                    
        except Exception as e:
            logger.error(f"Error handling plugin parameter: {e}")
            
    def _handle_plugin_parameters(self, unused_addr: str, *args):
        """Handle plugin parameters list"""
        try:
            logger.info(f"Plugin parameters list: {args}")
            # This might be a list of parameter IDs or a count
            if args:
                param_count = int(args[0])
                logger.info(f"Plugin has {param_count} parameters")
        except Exception as e:
            logger.error(f"Error handling plugin parameters list: {e}")
            
    def _handle_plugin_name(self, unused_addr: str, *args):
        """Handle plugin name information"""
        try:
            if args:
                plugin_name = str(args[0])
                logger.info(f"Plugin name: {plugin_name}")
                
                # Store plugin name
                if self.current_track_id is not None and self.current_plugin_id is not None:
                    self._store_plugin_name(plugin_name)
                    
        except Exception as e:
            logger.error(f"Error handling plugin name: {e}")
            
    def _handle_plugin_activate(self, unused_addr: str, *args):
        """Handle plugin activate/deactivate status"""
        try:
            if args:
                enabled = bool(int(args[0]))
                logger.info(f"Plugin enabled: {enabled}")
                
                # Store plugin activation status
                if self.current_track_id is not None and self.current_plugin_id is not None:
                    self._store_plugin_status(enabled)
                    
        except Exception as e:
            logger.error(f"Error handling plugin activate: {e}")
            
    def _handle_track_select(self, unused_addr: str, *args):
        """Handle track selection"""
        try:
            if args:
                track_id = int(args[0])
                self.current_track_id = track_id
                logger.info(f"Track selected: {track_id}")
                
        except Exception as e:
            logger.error(f"Error handling track select: {e}")
            
    def _handle_strip_list(self, unused_addr: str, *args):
        """Handle strip list information"""
        try:
            logger.info(f"Strip list: {args}")
            # This might contain track information
            for i, arg in enumerate(args):
                logger.info(f"Strip {i}: {arg}")
                
        except Exception as e:
            logger.error(f"Error handling strip list: {e}")
            
    def _handle_parameter_value(self, unused_addr: str, *args):
        """Handle parameter value updates"""
        try:
            if len(args) >= 2:
                param_id = int(args[0])
                param_value = float(args[1])
                logger.info(f"Parameter {param_id} updated to {param_value}")
                
                # Update stored parameter value
                if self.current_track_id is not None and self.current_plugin_id is not None:
                    self._update_parameter_value(param_id, param_value)
                    
        except Exception as e:
            logger.error(f"Error handling parameter value: {e}")
            
    def _handle_debug_message(self, unused_addr: str, *args):
        """Handle all other OSC messages for debugging"""
        logger.debug(f"OSC message: {unused_addr} - {args}")
        
    def _store_parameter(self, param_id: int, name: str, value: float, min_val: float, max_val: float, unit: str):
        """Store parameter information"""
        if self.current_track_id not in self.tracks:
            self.tracks[self.current_track_id] = TrackInfo(
                id=self.current_track_id,
                name=f"Track {self.current_track_id}",
                plugins=[]
            )
            
        track = self.tracks[self.current_track_id]
        
        # Find or create plugin
        plugin = None
        for p in track.plugins:
            if p.id == self.current_plugin_id:
                plugin = p
                break
                
        if plugin is None:
            plugin = PluginInfo(
                id=self.current_plugin_id,
                name=f"Plugin {self.current_plugin_id}",
                enabled=True,
                parameters=[]
            )
            track.plugins.append(plugin)
            
        # Add or update parameter
        param = PluginParameter(
            id=param_id,
            name=name,
            value=value,
            min_value=min_val,
            max_value=max_val,
            unit=unit,
            type=self._determine_parameter_type(name, unit),
            controllable=True
        )
        
        # Update existing parameter or add new one
        for i, existing_param in enumerate(plugin.parameters):
            if existing_param.id == param_id:
                plugin.parameters[i] = param
                return
                
        plugin.parameters.append(param)
        
    def _store_plugin_name(self, name: str):
        """Store plugin name"""
        if self.current_track_id in self.tracks:
            track = self.tracks[self.current_track_id]
            for plugin in track.plugins:
                if plugin.id == self.current_plugin_id:
                    plugin.name = name
                    break
                    
    def _store_plugin_status(self, enabled: bool):
        """Store plugin activation status"""
        if self.current_track_id in self.tracks:
            track = self.tracks[self.current_track_id]
            for plugin in track.plugins:
                if plugin.id == self.current_plugin_id:
                    plugin.enabled = enabled
                    break
                    
    def _update_parameter_value(self, param_id: int, value: float):
        """Update parameter value"""
        if self.current_track_id in self.tracks:
            track = self.tracks[self.current_track_id]
            for plugin in track.plugins:
                if plugin.id == self.current_plugin_id:
                    for param in plugin.parameters:
                        if param.id == param_id:
                            param.value = value
                            # Notify callbacks
                            for callback in self.parameter_callbacks:
                                callback(self.current_track_id, self.current_plugin_id, param_id, value)
                            break
                    break
                    
    def _determine_parameter_type(self, name: str, unit: str) -> str:
        """Determine parameter type based on name and unit"""
        name_lower = name.lower()
        unit_lower = unit.lower()
        
        if 'freq' in name_lower or 'hz' in unit_lower:
            return 'frequency'
        elif 'gain' in name_lower or 'level' in name_lower or 'db' in unit_lower:
            return 'gain'
        elif 'ratio' in name_lower or 'compress' in name_lower:
            return 'ratio'
        elif 'time' in name_lower or 'delay' in name_lower or 'ms' in unit_lower:
            return 'time'
        elif 'threshold' in name_lower:
            return 'threshold'
        elif 'pan' in name_lower:
            return 'pan'
        elif 'width' in name_lower or 'stereo' in name_lower:
            return 'width'
        else:
            return 'generic'
            
    def start(self):
        """Start the OSC listener"""
        if self.running:
            logger.warning("OSC listener already running")
            return
            
        try:
            self.server = osc_server.ThreadingOSCUDPServer(
                ("127.0.0.1", self.listen_port), 
                self.dispatcher
            )
            
            self.server_thread = threading.Thread(target=self.server.serve_forever)
            self.server_thread.daemon = True
            self.server_thread.start()
            
            self.running = True
            logger.info(f"OSC listener started on port {self.listen_port}")
            
        except Exception as e:
            logger.error(f"Failed to start OSC listener: {e}")
            raise
            
    def stop(self):
        """Stop the OSC listener"""
        if not self.running:
            return
            
        try:
            if self.server:
                self.server.shutdown()
                self.server.server_close()
                
            if self.server_thread:
                self.server_thread.join(timeout=1.0)
                
            self.running = False
            logger.info("OSC listener stopped")
            
        except Exception as e:
            logger.error(f"Error stopping OSC listener: {e}")
            
    def discover_plugins(self, track_id: int, timeout: float = 5.0) -> List[PluginInfo]:
        """Discover plugins on a specific track
        
        Args:
            track_id: Track ID to discover plugins for
            timeout: Timeout in seconds for discovery
            
        Returns:
            List of discovered plugins
        """
        from mcp_server.osc_client import get_osc_client
        
        self.current_track_id = track_id
        
        # Clear existing data for this track
        if track_id in self.tracks:
            del self.tracks[track_id]
            
        client = get_osc_client()
        
        # Request plugin list for track
        logger.info(f"Discovering plugins for track {track_id}")
        client.list_track_plugins(track_id)
        
        # Wait for responses
        start_time = time.time()
        while time.time() - start_time < timeout:
            time.sleep(0.1)
            
        # Return discovered plugins
        if track_id in self.tracks:
            return self.tracks[track_id].plugins
        else:
            return []
            
    def discover_plugin_parameters(self, track_id: int, plugin_id: int, timeout: float = 5.0) -> List[PluginParameter]:
        """Discover parameters for a specific plugin
        
        Args:
            track_id: Track ID
            plugin_id: Plugin ID
            timeout: Timeout in seconds for discovery
            
        Returns:
            List of discovered parameters
        """
        from mcp_server.osc_client import get_osc_client
        
        self.current_track_id = track_id
        self.current_plugin_id = plugin_id
        
        client = get_osc_client()
        
        # Request plugin parameters
        logger.info(f"Discovering parameters for plugin {plugin_id} on track {track_id}")
        client.get_plugin_parameters(track_id, plugin_id)
        client.get_plugin_info(track_id, plugin_id)
        
        # Wait for responses
        start_time = time.time()
        while time.time() - start_time < timeout:
            time.sleep(0.1)
            
        # Return discovered parameters
        if track_id in self.tracks:
            for plugin in self.tracks[track_id].plugins:
                if plugin.id == plugin_id:
                    return plugin.parameters
                    
        return []
        
    def get_all_tracks(self) -> Dict[int, TrackInfo]:
        """Get all discovered tracks and their plugins"""
        return self.tracks.copy()
        
    def get_track_plugins(self, track_id: int) -> List[PluginInfo]:
        """Get plugins for a specific track"""
        if track_id in self.tracks:
            return self.tracks[track_id].plugins
        return []
        
    def get_plugin_parameters(self, track_id: int, plugin_id: int) -> List[PluginParameter]:
        """Get parameters for a specific plugin"""
        if track_id in self.tracks:
            for plugin in self.tracks[track_id].plugins:
                if plugin.id == plugin_id:
                    return plugin.parameters
        return []
        
    def add_parameter_callback(self, callback: Callable[[int, int, int, float], None]):
        """Add callback for parameter value changes"""
        self.parameter_callbacks.append(callback)
        
    def add_plugin_callback(self, callback: Callable[[int, int], None]):
        """Add callback for plugin changes"""
        self.plugin_callbacks.append(callback)

# Global listener instance
_osc_listener: Optional[OSCListener] = None

def get_osc_listener() -> OSCListener:
    """Get global OSC listener instance"""
    global _osc_listener
    if _osc_listener is None:
        _osc_listener = OSCListener()
    return _osc_listener

def start_osc_listener():
    """Start global OSC listener"""
    listener = get_osc_listener()
    if not listener.running:
        listener.start()

def stop_osc_listener():
    """Stop global OSC listener"""
    listener = get_osc_listener()
    if listener.running:
        listener.stop()