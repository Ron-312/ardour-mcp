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
class StripInfo:
    """Represents a strip from Ardour's strip list"""
    ssid: int  # Surface Strip ID
    strip_type: str  # "AT", "MT", "B", etc.
    name: str
    inputs: int
    outputs: int
    mute: bool
    solo: bool

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
    track_id: Optional[int] = None  # Added track_id as requested
    
@dataclass
class TrackInfo:
    """Represents a track with its plugins"""
    id: int
    name: str
    plugins: List[PluginInfo]

class OSCListener:
    """OSC listener for receiving feedback from Ardour"""
    
    def __init__(self, listen_port: Optional[int] = None):
        """Initialize OSC listener
        
        Args:
            listen_port: Port to listen on for OSC feedback (defaults to config value)
        """
        if listen_port is None:
            osc_config = get_osc_config()
            # Use dedicated listen port for manual port mode (separate from send port)
            # This prevents hearing our own outgoing messages as echoes
            listen_port = osc_config.get("listen_port", 3820)  # Dedicated reply port
        self.listen_port = listen_port
        self.server = None
        self.server_thread = None
        self.running = False
        
        # Data storage for discovered plugins and strips
        self.tracks: Dict[int, TrackInfo] = {}
        self.strips: Dict[int, StripInfo] = {}  # SSID -> StripInfo mapping
        self.current_track_id: Optional[int] = None
        self.current_plugin_id: Optional[int] = None
        self.surface_setup_complete: bool = False
        
        # Track strip list discovery state
        self.strip_list_complete: bool = False
        self.strip_list_session_framerate: Optional[float] = None
        self.strip_list_last_frame: Optional[int] = None
        
        # Smart strip data collection - organized by strip ID
        self.strip_data: Dict[int, Dict[str, Any]] = {}  # {strip_id: {property: value}}
        self.strip_feedback_complete: bool = False
        self.strip_feedback_start_time: Optional[float] = None
        
        # Callbacks for real-time updates
        self.parameter_callbacks: List[Callable] = []
        self.plugin_callbacks: List[Callable] = []
        
        # Setup OSC dispatcher
        self.dispatcher = dispatcher.Dispatcher()
        self._setup_message_handlers()
        
    def _setup_message_handlers(self):
        """Setup OSC message handlers for different message types"""
        
        # Official Ardour OSC handlers based on documentation
        
        # Strip selection feedback
        self.dispatcher.map("/select/strip", self._handle_strip_select)
        
        # Plugin selection feedback  
        self.dispatcher.map("/select/plugin", self._handle_plugin_select)
        
        # Plugin parameter feedback (official format)
        self.dispatcher.map("/select/plugin/parameter", self._handle_plugin_parameter)
        
        # Plugin activation feedback
        self.dispatcher.map("/select/plugin/activate", self._handle_plugin_activate)
        
        # Strip list response handlers - Ardour sends responses to /reply, NOT /strip/list
        self.dispatcher.map("/reply", self._handle_ardour_reply)  # Standard OSC reply format
        
        # Non-standard #reply format (Ardour may use this)
        try:
            self.dispatcher.map("#reply", self._handle_non_standard_reply)  # Non-standard OSC format
        except Exception:
            # pythonosc may not support #reply, we'll catch it in default handler
            logger.debug("Could not map #reply handler, will catch in default handler")
        
        # End of route list detection
        self.dispatcher.map("/end_route_list", self._handle_end_route_list)
        
        # Smart strip feedback handler - captures all /strip/* messages
        self.dispatcher.map("/strip/*", self._handle_strip_feedback)  # Collect all strip data
        
        # Other debug handlers
        self.dispatcher.map("/select/*", self._handle_debug_message)  # Only select-related
        
        # Add catch-all for ANY message to debug what we're actually receiving
        self.dispatcher.set_default_handler(self._handle_any_message)  # Catch EVERYTHING
        
    def _handle_strip_select(self, unused_addr: str, *args):
        """Handle strip selection feedback"""
        try:
            if args:
                strip_id = int(args[0])
                self.current_track_id = strip_id
                logger.info(f"[SELECT] Strip selected: {strip_id}")
        except Exception as e:
            logger.error(f"Error handling strip select: {e}")
            
    def _handle_plugin_select(self, unused_addr: str, *args):
        """Handle plugin selection feedback"""
        try:
            if args:
                plugin_id = int(args[0])
                self.current_plugin_id = plugin_id
                logger.info(f"[SELECT] Plugin selected: {plugin_id}")
        except Exception as e:
            logger.error(f"Error handling plugin select: {e}")

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
        
        # Enhanced logging for different message types
        if "plugin" in unused_addr.lower():
            logger.info(f"[PLUGIN OSC MESSAGE]: {unused_addr} {args}")
        
        if "strip" in unused_addr.lower():
            logger.info(f"[STRIP OSC MESSAGE]: {unused_addr} {args}")
            
        # Enhanced logging for strip list related messages
        if "list" in unused_addr.lower():
            logger.info(f"[LIST OSC MESSAGE]: {unused_addr} {args}")
            
        # Log select messages which are important for feedback
        if "select" in unused_addr.lower():
            logger.info(f"[SELECT OSC MESSAGE]: {unused_addr} {args}")
            
        # Log any reply messages
        if "reply" in unused_addr.lower():
            logger.info(f"[REPLY OSC MESSAGE]: {unused_addr} {args}")
        
        # Store last message for debugging
        self.last_message = {
            'address': unused_addr,
            'args': args,
            'timestamp': time.time()
        }
        
    def _handle_plugin_list_response(self, unused_addr: str, *args):
        """Handle plugin list response from Ardour
        
        Expected format based on Ardour research:
        /strip/plugin/list ssid piid name enabled
        """
        try:
            logger.info(f"[PLUGIN LIST] Raw response: {unused_addr} {args}")
            
            if len(args) >= 4:
                strip_id = int(args[0])  # Track/strip ID
                plugin_id = int(args[1])  # Plugin ID 
                plugin_name = str(args[2])  # Plugin name
                enabled = bool(int(args[3]))  # Enabled state (1/0)
                
                logger.info(f"[PLUGIN LIST] Strip {strip_id}, Plugin {plugin_id}: {plugin_name} (enabled: {enabled})")
                
                # Store this plugin info
                self._store_plugin_from_list(strip_id, plugin_id, plugin_name, enabled)
                
            else:
                logger.warning(f"[PLUGIN LIST] Unexpected plugin list format: {args}")
                
        except Exception as e:
            logger.error(f"Error handling plugin list response: {e}")
            
    def _handle_plugin_descriptor_response(self, unused_addr: str, *args):
        """Handle plugin descriptor response from Ardour
        
        Expected format based on Ardour research:
        /strip/plugin/descriptor ssid piid param_id param_name flags datatype min max scale_points value
        """
        try:
            logger.info(f"[PLUGIN DESC] Raw response: {unused_addr} {args}")
            
            if len(args) >= 6:
                strip_id = int(args[0])
                plugin_id = int(args[1])
                param_id = int(args[2])
                param_name = str(args[3])
                flags = int(args[4]) if len(args) > 4 else 0
                datatype = str(args[5]) if len(args) > 5 else "FLOAT"
                
                # Optional additional fields
                min_val = float(args[6]) if len(args) > 6 else 0.0
                max_val = float(args[7]) if len(args) > 7 else 1.0
                current_val = float(args[-1]) if len(args) > 8 else 0.0
                
                logger.info(f"[PLUGIN DESC] Strip {strip_id}, Plugin {plugin_id}, Param {param_id}: {param_name}")
                
                # Store parameter info
                self._store_plugin_parameter_from_descriptor(strip_id, plugin_id, param_id, param_name, 
                                                           current_val, min_val, max_val, datatype)
                
        except Exception as e:
            logger.error(f"Error handling plugin descriptor response: {e}")
            
    def _handle_plugin_descriptor_end(self, unused_addr: str, *args):
        """Handle end of plugin descriptor list"""
        try:
            logger.info(f"[PLUGIN DESC END] Descriptor list complete: {args}")
        except Exception as e:
            logger.error(f"Error handling descriptor end: {e}")
            
    def _handle_reply_message(self, unused_addr: str, *args):
        """Handle generic reply messages from Ardour"""
        try:
            logger.info(f"[REPLY] Generic reply: {unused_addr} {args}")
            
            # Check if this is a plugin-related reply
            if len(args) > 0:
                first_arg = str(args[0])
                if "plugin" in first_arg.lower():
                    logger.info(f"[REPLY] Plugin-related reply detected: {args}")
                    
        except Exception as e:
            logger.error(f"Error handling reply message: {e}")
            
    def _handle_non_standard_reply(self, unused_addr: str, *args):
        """Handle non-standard #reply messages from Ardour"""
        try:
            logger.info(f"[#REPLY] Non-standard reply: {unused_addr} {args}")
            # Process the same way as standard replies
            self._process_potential_strip_data(unused_addr, args, "#REPLY")
        except Exception as e:
            logger.error(f"Error handling non-standard reply: {e}")
            
    def _handle_ardour_reply(self, unused_addr: str, *args):
        """Handle Ardour /reply messages which may contain strip information"""
        try:
            logger.info(f"[/REPLY] Standard reply: {unused_addr} {args}")
            # Process the same way for both reply types
            self._process_potential_strip_data(unused_addr, args, "/REPLY")
        except Exception as e:
            logger.error(f"Error handling Ardour reply: {e}")
            
    def _process_potential_strip_data(self, addr: str, args: tuple, source: str):
        """Process args that might contain strip information"""
        try:
            # Check if this is a strip list response
            if len(args) >= 7 and isinstance(args[0], int):
                # Try to parse as strip information
                try:
                    ssid = int(args[0])  # Surface Strip ID
                    strip_type = str(args[1])  # "AT", "MT", "B", etc.
                    name = str(args[2])  # Strip name
                    inputs = int(args[3])  # Number of inputs
                    outputs = int(args[4])  # Number of outputs
                    mute = bool(int(args[5]))  # Mute state
                    solo = bool(int(args[6]))  # Solo state
                    
                    # Store strip info
                    strip_info = StripInfo(
                        ssid=ssid,
                        strip_type=strip_type,
                        name=name,
                        inputs=inputs,
                        outputs=outputs,
                        mute=mute,
                        solo=solo
                    )
                    
                    self.strips[ssid] = strip_info
                    logger.info(f"[{source} STRIP] Stored strip {ssid}: {strip_type} '{name}' (I:{inputs} O:{outputs})")
                    
                except (ValueError, IndexError) as e:
                    # Not strip data, just log for debugging
                    logger.debug(f"[{source}] Could not parse as strip data: {args} - {e}")
            else:
                # Check if this is an end_route_list message
                if len(args) >= 1 and "end_route_list" in str(args[0]):
                    logger.info(f"[{source}] Found end_route_list in reply")
                    self._handle_end_route_list_in_reply(args)
                else:
                    logger.debug(f"[{source}] Generic reply: {args}")
                    
        except Exception as e:
            logger.error(f"Error processing potential strip data from {source}: {e}")
            
    def _handle_end_route_list(self, unused_addr: str, *args):
        """Handle end_route_list message indicating strip list is complete"""
        try:
            logger.info(f"[END ROUTE LIST] Strip list complete: {unused_addr} {args}")
            self.strip_list_complete = True
            
            # Parse additional information if available
            if len(args) >= 2:
                try:
                    self.strip_list_session_framerate = float(args[0])
                    self.strip_list_last_frame = int(args[1])
                    logger.info(f"[END ROUTE LIST] Session framerate: {self.strip_list_session_framerate}, Last frame: {self.strip_list_last_frame}")
                except (ValueError, IndexError):
                    logger.debug(f"[END ROUTE LIST] Could not parse session info: {args}")
                    
        except Exception as e:
            logger.error(f"Error handling end route list: {e}")
            
    def _handle_end_route_list_in_reply(self, args):
        """Handle end_route_list when it comes as part of /reply message"""
        try:
            logger.info(f"[END ROUTE LIST IN REPLY] Strip list complete: {args}")
            self.strip_list_complete = True
            
            # Parse additional information if available (args[1] and beyond)
            if len(args) >= 3:
                try:
                    self.strip_list_session_framerate = float(args[1])
                    self.strip_list_last_frame = int(args[2])
                    logger.info(f"[END ROUTE LIST] Session framerate: {self.strip_list_session_framerate}, Last frame: {self.strip_list_last_frame}")
                except (ValueError, IndexError):
                    logger.debug(f"[END ROUTE LIST] Could not parse session info: {args}")
                    
        except Exception as e:
            logger.error(f"Error handling end route list in reply: {e}")
            
    def _handle_any_message(self, unused_addr: str, *args):
        """Ultimate catch-all handler for ANY OSC message we receive"""
        logger.info(f"[OSC RECEIVED] Address: '{unused_addr}' Args: {args} Types: {[type(arg).__name__ for arg in args]}")
        
        # Check if this looks like a strip list response
        if len(args) >= 7:
            try:
                # Try to parse as potential strip data
                arg0, arg1, arg2 = args[0], args[1], args[2]
                if (isinstance(arg0, int) and 
                    isinstance(arg1, str) and len(arg1) <= 4 and  # Strip type like "AT", "MT"
                    isinstance(arg2, str)):  # Strip name
                    logger.info(f"[POTENTIAL STRIP DATA] SSID={arg0}, Type='{arg1}', Name='{arg2}', Full args={args}")
            except Exception:
                pass
                
        # Check for end route list
        if len(args) >= 1 and "end_route_list" in str(args[0]).lower():
            logger.info(f"[POTENTIAL END ROUTE LIST] Args: {args}")
            
        # Store for debugging
        self.last_message = {
            'address': unused_addr,
            'args': args,
            'timestamp': time.time()
        }
        
    def _handle_strip_feedback(self, address: str, *args):
        """Smart handler for all /strip/* feedback messages
        
        Parses address like '/strip/name/1' into property='name', strip_id=1
        Stores all strip data in organized structure for easy access
        """
        try:
            # EXTENSIVE DEBUG LOGGING
            logger.info(f"[STRIP FEEDBACK CALLED] Address: {address}, Args: {args}, Types: {[type(arg).__name__ for arg in args]}")
            
            # Parse the OSC address: /strip/property/strip_id or /strip/property/automation/strip_id
            parts = address.split('/')
            logger.info(f"[STRIP FEEDBACK] Address parts: {parts}")
            
            if len(parts) < 3:
                logger.warning(f"[STRIP FEEDBACK] Address too short: {address}")
                return
                
            # Extract strip ID (last part of address)
            try:
                strip_id = int(parts[-1])
                logger.info(f"[STRIP FEEDBACK] Extracted strip_id: {strip_id}")
            except (ValueError, IndexError) as e:
                logger.warning(f"[STRIP FEEDBACK] Could not extract strip_id from {parts[-1]}: {e}")
                return
                
            # Extract property name (parts between 'strip' and strip_id)
            property_parts = parts[2:-1]  # Skip '/strip' and strip_id
            property_name = '/'.join(property_parts)
            logger.info(f"[STRIP FEEDBACK] Property name: '{property_name}'")
            
            # Initialize strip data if not exists
            if strip_id not in self.strip_data:
                self.strip_data[strip_id] = {}
                logger.info(f"[STRIP FEEDBACK] Initialized strip_data for strip {strip_id}")
                
            # Store the property value
            if len(args) > 0:
                value = args[0]
                self.strip_data[strip_id][property_name] = value
                logger.info(f"[STRIP FEEDBACK] Stored: strip_data[{strip_id}]['{property_name}'] = {value}")
                
                # Track feedback timing
                if self.strip_feedback_start_time is None:
                    self.strip_feedback_start_time = time.time()
                    logger.info(f"[STRIP FEEDBACK] Started collecting strip data at {self.strip_feedback_start_time}")
                
                # Log important properties with EXTRA emphasis
                if property_name in ['name', 'mute', 'solo', 'gain']:
                    logger.info(f"[STRIP DATA ⭐] Strip {strip_id} {property_name}: {value}")
            else:
                logger.warning(f"[STRIP FEEDBACK] No args provided for {address}")
                    
        except Exception as e:
            logger.error(f"[STRIP FEEDBACK ERROR] Error handling {address}: {e}")
            import traceback
            logger.error(f"[STRIP FEEDBACK ERROR] Traceback: {traceback.format_exc()}")
            
    def get_strip_summary(self, strip_id: int) -> Optional[Dict[str, Any]]:
        """Get basic track summary for MCP client"""
        if strip_id not in self.strip_data:
            return None
            
        data = self.strip_data[strip_id]
        return {
            "ssid": strip_id,
            "name": data.get("name", f"Track {strip_id}"),
            "mute": bool(data.get("mute", 0.0)),
            "solo": bool(data.get("solo", 0.0)),
            "type": "AT"  # Default to Audio Track, could be enhanced later
        }
        
    def get_strip_details(self, strip_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed track info for specific requests"""
        if strip_id not in self.strip_data:
            return None
            
        data = self.strip_data[strip_id]
        return {
            "ssid": strip_id,
            "name": data.get("name", f"Track {strip_id}"),
            "mute": bool(data.get("mute", 0.0)),
            "solo": bool(data.get("solo", 0.0)),
            "gain_db": float(data.get("gain", 0.0)),
            "pan_position": float(data.get("pan_stereo_position", 0.5)),
            "pan_width": float(data.get("pan_stereo_width", 0.5)),
            "record_enabled": bool(data.get("recenable", 0.0)),
            "record_safe": bool(data.get("record_safe", 0.0)),
            "monitor_input": bool(data.get("monitor_input", 0)),
            "monitor_disk": bool(data.get("monitor_disk", 0)),
            "group": data.get("group", "").strip()
        }
        
    def get_all_strip_summaries(self) -> List[Dict[str, Any]]:
        """Get basic summaries of all discovered strips"""
        summaries = []
        for strip_id in sorted(self.strip_data.keys()):
            summary = self.get_strip_summary(strip_id)
            if summary:
                summaries.append(summary)
        return summaries
        
    def check_strip_feedback_complete(self, timeout: float = 2.0) -> bool:
        """Check if strip feedback collection seems complete"""
        if self.strip_feedback_start_time is None:
            return False
            
        # Consider complete if we have data and haven't received new data for a while
        elapsed = time.time() - self.strip_feedback_start_time
        if elapsed > timeout and len(self.strip_data) > 0:
            if not self.strip_feedback_complete:
                logger.info(f"[STRIP FEEDBACK] Complete - found {len(self.strip_data)} strips")
                self.strip_feedback_complete = True
            return True
            
        return False
            
    def _handle_strip_list_response(self, unused_addr: str, *args):
        """Handle strip list response from Ardour
        
        Expected format: /strip/list ssid strip_type name inputs outputs mute solo ...
        """
        try:
            logger.info(f"[STRIP LIST] Raw response: {unused_addr} {args}")
            
            if len(args) >= 7:
                ssid = int(args[0])  # Surface Strip ID
                strip_type = str(args[1])  # "AT", "MT", "B", etc.
                name = str(args[2])  # Strip name
                inputs = int(args[3])  # Number of inputs
                outputs = int(args[4])  # Number of outputs
                mute = bool(int(args[5]))  # Mute state
                solo = bool(int(args[6]))  # Solo state
                
                # Store strip info
                strip_info = StripInfo(
                    ssid=ssid,
                    strip_type=strip_type,
                    name=name,
                    inputs=inputs,
                    outputs=outputs,
                    mute=mute,
                    solo=solo
                )
                
                self.strips[ssid] = strip_info
                logger.info(f"[STRIP LIST] Stored strip {ssid}: {strip_type} '{name}' (I:{inputs} O:{outputs})")
                
            else:
                logger.warning(f"[STRIP LIST] Unexpected strip list format: {args}")
                
        except Exception as e:
            logger.error(f"Error handling strip list response: {e}")
        
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
        
    def _store_plugin_from_list(self, strip_id: int, plugin_id: int, plugin_name: str, enabled: bool):
        """Store plugin information from plugin list response"""
        try:
            # Ensure track exists
            if strip_id not in self.tracks:
                self.tracks[strip_id] = TrackInfo(
                    id=strip_id,
                    name=f"Track {strip_id}",
                    plugins=[]
                )
            
            track = self.tracks[strip_id]
            
            # Check if plugin already exists
            existing_plugin = None
            for plugin in track.plugins:
                if plugin.id == plugin_id:
                    existing_plugin = plugin
                    break
            
            if existing_plugin:
                # Update existing plugin
                existing_plugin.name = plugin_name
                existing_plugin.enabled = enabled
                existing_plugin.track_id = strip_id
                logger.info(f"[PLUGIN STORE] Updated plugin {plugin_id} on track {strip_id}: {plugin_name}")
            else:
                # Create new plugin
                new_plugin = PluginInfo(
                    id=plugin_id,
                    name=plugin_name,
                    enabled=enabled,
                    parameters=[],
                    track_id=strip_id
                )
                track.plugins.append(new_plugin)
                logger.info(f"[PLUGIN STORE] Added new plugin {plugin_id} on track {strip_id}: {plugin_name}")
                
        except Exception as e:
            logger.error(f"Error storing plugin from list: {e}")
            
    def _store_plugin_parameter_from_descriptor(self, strip_id: int, plugin_id: int, param_id: int, 
                                              param_name: str, current_val: float, min_val: float, 
                                              max_val: float, datatype: str):
        """Store plugin parameter from descriptor response"""
        try:
            # Ensure track and plugin exist
            if strip_id not in self.tracks:
                return
                
            track = self.tracks[strip_id]
            target_plugin = None
            
            for plugin in track.plugins:
                if plugin.id == plugin_id:
                    target_plugin = plugin
                    break
                    
            if not target_plugin:
                # Create plugin if it doesn't exist
                target_plugin = PluginInfo(
                    id=plugin_id,
                    name=f"Plugin {plugin_id}",
                    enabled=True,
                    parameters=[],
                    track_id=strip_id
                )
                track.plugins.append(target_plugin)
                
            # Determine parameter type and unit from datatype
            param_type = self._determine_parameter_type_from_datatype(param_name, datatype)
            unit = self._determine_unit_from_datatype(datatype, param_name)
            
            # Create parameter
            parameter = PluginParameter(
                id=param_id,
                name=param_name,
                value=current_val,
                min_value=min_val,
                max_value=max_val,
                unit=unit,
                type=param_type,
                controllable=True
            )
            
            # Update existing parameter or add new one
            existing_param = None
            for i, param in enumerate(target_plugin.parameters):
                if param.id == param_id:
                    existing_param = i
                    break
                    
            if existing_param is not None:
                target_plugin.parameters[existing_param] = parameter
            else:
                target_plugin.parameters.append(parameter)
                
            logger.info(f"[PARAM STORE] Stored parameter {param_id} for plugin {plugin_id} on track {strip_id}: {param_name}")
            
        except Exception as e:
            logger.error(f"Error storing plugin parameter from descriptor: {e}")
            
    def _determine_parameter_type_from_datatype(self, param_name: str, datatype: str) -> str:
        """Determine parameter type from Ardour datatype and parameter name"""
        name_lower = param_name.lower()
        datatype_lower = datatype.lower()
        
        # Check parameter name patterns
        if 'freq' in name_lower or 'frequency' in name_lower:
            return 'frequency'
        elif 'gain' in name_lower or 'level' in name_lower:
            return 'gain'
        elif 'threshold' in name_lower:
            return 'threshold'
        elif 'ratio' in name_lower:
            return 'ratio'
        elif 'attack' in name_lower or 'release' in name_lower:
            return 'time'
        elif 'pan' in name_lower:
            return 'pan'
        else:
            return 'generic'
            
    def _determine_unit_from_datatype(self, datatype: str, param_name: str) -> str:
        """Determine parameter unit from Ardour datatype and parameter name"""
        name_lower = param_name.lower()
        
        if 'freq' in name_lower or 'frequency' in name_lower:
            return 'Hz'
        elif 'gain' in name_lower or 'level' in name_lower or 'threshold' in name_lower:
            return 'dB'
        elif 'ratio' in name_lower:
            return ':1'
        elif 'attack' in name_lower or 'release' in name_lower:
            return 'ms'
        elif 'pan' in name_lower:
            return '%'
        else:
            return ''
        
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
            
    def setup_surface_and_discover_strips(self, timeout: float = 3.0) -> bool:
        """Setup OSC surface and discover available strips
        
        Args:
            timeout: Timeout in seconds for strip discovery
            
        Returns:
            True if setup successful, False otherwise
        """
        from mcp_server.osc_client import get_osc_client
        
        if self.surface_setup_complete:
            logger.info("[SURFACE] Surface already set up, skipping")
            return True
            
        client = get_osc_client()
        
        # Step 1: Setup surface
        logger.info("[SURFACE] Setting up OSC surface")
        success = client.setup_surface(bank_size=0, strip_types=159, feedback=0)
        if not success:
            logger.error("[SURFACE] Failed to setup OSC surface")
            return False
            
        # Step 2: Request strip list
        logger.info("[SURFACE] Requesting strip list")
        success = client.list_strips()
        if not success:
            logger.error("[SURFACE] Failed to request strip list")
            return False
            
        # Step 3: Wait for strip list responses
        logger.info(f"[SURFACE] Waiting for strip list (timeout: {timeout}s)...")
        start_time = time.time()
        initial_strip_count = len(self.strips)
        
        while time.time() - start_time < timeout:
            time.sleep(0.1)
            
        elapsed = time.time() - start_time
        strip_count = len(self.strips) - initial_strip_count
        
        if strip_count > 0:
            logger.info(f"[SURFACE] Discovered {strip_count} strips in {elapsed:.1f}s")
            logger.info(f"[SURFACE] Available strips: {list(self.strips.keys())}")
            self.surface_setup_complete = True
            return True
        else:
            logger.warning(f"[SURFACE] No strips discovered in {elapsed:.1f}s")
            return False

    def discover_plugins(self, track_id: int, timeout: float = 5.0) -> List[PluginInfo]:
        """Discover plugins on a specific track using proper strip IDs
        
        Args:
            track_id: Track ID (1-based for API compatibility) 
            timeout: Timeout in seconds for discovery
            
        Returns:
            List of discovered plugins
        """
        from mcp_server.osc_client import get_osc_client
        
        # Ensure surface is set up and strips are discovered
        if not self.setup_surface_and_discover_strips():
            logger.error(f"[DISCOVERY] Failed to setup surface, cannot discover plugins")
            return []
            
        # Find the corresponding strip ID for this track
        # We need to map the track_id (API 1-based) to an actual SSID
        track_strips = [strip for strip in self.strips.values() 
                       if strip.strip_type in ["AT", "MT"]]  # Audio/MIDI tracks only
        
        if not track_strips:
            logger.warning(f"[DISCOVERY] No audio/MIDI tracks found in strip list")
            return []
            
        # Sort by SSID to get consistent ordering
        track_strips.sort(key=lambda s: s.ssid)
        
        # Convert 1-based track_id to 0-based index for track_strips array
        track_index = track_id - 1
        if track_index >= len(track_strips):
            logger.warning(f"[DISCOVERY] Track {track_id} not found (only {len(track_strips)} tracks available)")
            return []
            
        strip = track_strips[track_index]
        strip_id = strip.ssid
        
        logger.info(f"[DISCOVERY] Track {track_id} -> Strip {strip_id} ('{strip.name}')")
        
        self.current_track_id = track_id
        
        # Clear existing data for this track
        if track_id in self.tracks:
            del self.tracks[track_id]
            
        client = get_osc_client()
        
        # Request plugin list for strip
        logger.info(f"[DISCOVERY] Starting plugin discovery for track {track_id} (strip {strip_id})")
        logger.info(f"[OSC SEND] /strip/plugin/list {strip_id}")
        
        success = client.list_track_plugins(strip_id)
        if not success:
            logger.error(f"[ERROR] Failed to send plugin list request for strip {strip_id}")
            return []
        
        logger.info(f"[WAIT] Waiting for plugin responses (timeout: {timeout}s)...")
        
        # Wait for responses
        start_time = time.time()
        message_count = 0
        while time.time() - start_time < timeout:
            # Check for new messages
            if hasattr(self, 'last_message') and self.last_message:
                if self.last_message['timestamp'] > start_time:
                    message_count += 1
                    logger.info(f"[OSC RECV] {self.last_message['address']} {self.last_message['args']}")
            
            time.sleep(0.1)
            
        elapsed = time.time() - start_time
        logger.info(f"[DISCOVERY] Completed after {elapsed:.1f}s, received {message_count} messages")
        
        # Return discovered plugins
        if track_id in self.tracks:
            plugins = self.tracks[track_id].plugins
            logger.info(f"[SUCCESS] Found {len(plugins)} plugins for track {track_id}: {[p.name for p in plugins]}")
            return plugins
        else:
            logger.warning(f"[NO PLUGINS] No plugins found for track {track_id} after {elapsed:.1f}s")
            logger.info(f"[CACHE] Available tracks in cache: {list(self.tracks.keys())}")
            return []
    
    def discover_specific_plugin(self, track_id: int, plugin_id: int, timeout: float = 5.0) -> Optional[PluginInfo]:
        """Discover a specific plugin on a track
        
        Args:
            track_id: Track ID to discover plugin on
            plugin_id: Specific plugin ID to discover
            timeout: Timeout in seconds for discovery
            
        Returns:
            Plugin info if found, None otherwise
        """
        logger.info(f"[DISCOVERY] Discovering specific plugin {plugin_id} on track {track_id}")
        
        # First discover all plugins on the track
        plugins = self.discover_plugins(track_id, timeout)
        
        # Find the specific plugin
        for plugin in plugins:
            if plugin.id == plugin_id:
                plugin.track_id = track_id  # Ensure track_id is set
                logger.info(f"[SUCCESS] Found specific plugin: {plugin.name} on track {track_id}")
                return plugin
        
        logger.warning(f"[NOT FOUND] Plugin {plugin_id} not found on track {track_id}")
        return None
            
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