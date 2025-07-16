"""
Dynamic Plugin Parameter Mapping System

This module provides dynamic mapping between plugin parameter names and OSC parameter IDs
based on real plugin discovery data from Ardour.
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from mcp_server.osc_listener import get_osc_listener, PluginParameter

logger = logging.getLogger(__name__)

@dataclass
class ParameterMapping:
    """Represents a parameter mapping for a specific plugin"""
    plugin_id: int
    track_id: int
    parameter_name: str
    parameter_id: int
    parameter_type: str
    unit: str
    min_value: float
    max_value: float
    current_value: float

class PluginParameterMapper:
    """Dynamic plugin parameter mapping system"""
    
    def __init__(self):
        """Initialize the parameter mapper"""
        self.parameter_cache: Dict[str, Dict[int, ParameterMapping]] = {}
        self.plugin_name_cache: Dict[str, str] = {}
        
    def get_plugin_key(self, track_id: int, plugin_id: int) -> str:
        """Generate a unique key for a plugin"""
        return f"{track_id}_{plugin_id}"
    
    def discover_and_map_parameters(self, track_id: int, plugin_id: int, timeout: float = 5.0) -> Dict[str, ParameterMapping]:
        """Discover parameters for a plugin and create mappings
        
        Args:
            track_id: Track ID (0-based)
            plugin_id: Plugin ID (0-based)
            timeout: Discovery timeout in seconds
            
        Returns:
            Dictionary mapping parameter names to ParameterMapping objects
        """
        plugin_key = self.get_plugin_key(track_id, plugin_id)
        
        # Check cache first
        if plugin_key in self.parameter_cache:
            logger.info(f"Using cached parameter mappings for plugin {plugin_key}")
            return self.parameter_cache[plugin_key]
        
        # Discover parameters from OSC
        osc_listener = get_osc_listener()
        discovered_params = osc_listener.discover_plugin_parameters(track_id, plugin_id, timeout)
        
        if not discovered_params:
            logger.warning(f"No parameters discovered for plugin {plugin_key}")
            return {}
        
        # Create mappings
        mappings = {}
        for param in discovered_params:
            mapping = ParameterMapping(
                plugin_id=plugin_id,
                track_id=track_id,
                parameter_name=param.name,
                parameter_id=param.id,
                parameter_type=param.type,
                unit=param.unit,
                min_value=param.min_value,
                max_value=param.max_value,
                current_value=param.value
            )
            mappings[param.name.lower()] = mapping
            
        # Cache the mappings
        self.parameter_cache[plugin_key] = mappings
        
        logger.info(f"Mapped {len(mappings)} parameters for plugin {plugin_key}")
        return mappings
    
    def get_parameter_mapping(self, track_id: int, plugin_id: int, parameter_name: str) -> Optional[ParameterMapping]:
        """Get parameter mapping for a specific parameter
        
        Args:
            track_id: Track ID (0-based)
            plugin_id: Plugin ID (0-based)
            parameter_name: Parameter name (case-insensitive)
            
        Returns:
            ParameterMapping if found, None otherwise
        """
        plugin_key = self.get_plugin_key(track_id, plugin_id)
        
        # Ensure parameters are discovered
        if plugin_key not in self.parameter_cache:
            self.discover_and_map_parameters(track_id, plugin_id)
        
        # Look up parameter mapping
        if plugin_key in self.parameter_cache:
            mappings = self.parameter_cache[plugin_key]
            return mappings.get(parameter_name.lower())
        
        return None
    
    def get_parameter_id(self, track_id: int, plugin_id: int, parameter_name: str) -> Optional[int]:
        """Get OSC parameter ID for a parameter name
        
        Args:
            track_id: Track ID (0-based)
            plugin_id: Plugin ID (0-based)
            parameter_name: Parameter name (case-insensitive)
            
        Returns:
            Parameter ID if found, None otherwise
        """
        mapping = self.get_parameter_mapping(track_id, plugin_id, parameter_name)
        return mapping.parameter_id if mapping else None
    
    def get_parameter_info(self, track_id: int, plugin_id: int, parameter_name: str) -> Optional[Dict]:
        """Get detailed parameter information
        
        Args:
            track_id: Track ID (0-based)
            plugin_id: Plugin ID (0-based)
            parameter_name: Parameter name (case-insensitive)
            
        Returns:
            Dictionary with parameter information
        """
        mapping = self.get_parameter_mapping(track_id, plugin_id, parameter_name)
        if not mapping:
            return None
            
        return {
            "name": mapping.parameter_name,
            "id": mapping.parameter_id,
            "type": mapping.parameter_type,
            "unit": mapping.unit,
            "min_value": mapping.min_value,
            "max_value": mapping.max_value,
            "current_value": mapping.current_value
        }
    
    def list_parameter_names(self, track_id: int, plugin_id: int) -> List[str]:
        """List all parameter names for a plugin
        
        Args:
            track_id: Track ID (0-based)
            plugin_id: Plugin ID (0-based)
            
        Returns:
            List of parameter names
        """
        plugin_key = self.get_plugin_key(track_id, plugin_id)
        
        # Ensure parameters are discovered
        if plugin_key not in self.parameter_cache:
            self.discover_and_map_parameters(track_id, plugin_id)
        
        if plugin_key in self.parameter_cache:
            mappings = self.parameter_cache[plugin_key]
            return [mapping.parameter_name for mapping in mappings.values()]
        
        return []
    
    def find_parameter_by_pattern(self, track_id: int, plugin_id: int, pattern: str) -> List[ParameterMapping]:
        """Find parameters by name pattern
        
        Args:
            track_id: Track ID (0-based)
            plugin_id: Plugin ID (0-based)
            pattern: Search pattern (case-insensitive)
            
        Returns:
            List of matching ParameterMapping objects
        """
        plugin_key = self.get_plugin_key(track_id, plugin_id)
        
        # Ensure parameters are discovered
        if plugin_key not in self.parameter_cache:
            self.discover_and_map_parameters(track_id, plugin_id)
        
        matches = []
        if plugin_key in self.parameter_cache:
            mappings = self.parameter_cache[plugin_key]
            pattern_lower = pattern.lower()
            
            for mapping in mappings.values():
                if pattern_lower in mapping.parameter_name.lower():
                    matches.append(mapping)
        
        return matches
    
    def get_parameters_by_type(self, track_id: int, plugin_id: int, param_type: str) -> List[ParameterMapping]:
        """Get parameters by type
        
        Args:
            track_id: Track ID (0-based)
            plugin_id: Plugin ID (0-based)
            param_type: Parameter type (frequency, gain, time, etc.)
            
        Returns:
            List of matching ParameterMapping objects
        """
        plugin_key = self.get_plugin_key(track_id, plugin_id)
        
        # Ensure parameters are discovered
        if plugin_key not in self.parameter_cache:
            self.discover_and_map_parameters(track_id, plugin_id)
        
        matches = []
        if plugin_key in self.parameter_cache:
            mappings = self.parameter_cache[plugin_key]
            
            for mapping in mappings.values():
                if mapping.parameter_type == param_type:
                    matches.append(mapping)
        
        return matches
    
    def update_parameter_value(self, track_id: int, plugin_id: int, parameter_name: str, value: float):
        """Update cached parameter value
        
        Args:
            track_id: Track ID (0-based)
            plugin_id: Plugin ID (0-based)
            parameter_name: Parameter name (case-insensitive)
            value: New parameter value
        """
        mapping = self.get_parameter_mapping(track_id, plugin_id, parameter_name)
        if mapping:
            mapping.current_value = value
            logger.debug(f"Updated parameter {parameter_name} value to {value}")
    
    def clear_cache(self, track_id: Optional[int] = None, plugin_id: Optional[int] = None):
        """Clear parameter cache
        
        Args:
            track_id: If specified, clear only this track's cache
            plugin_id: If specified with track_id, clear only this plugin's cache
        """
        if track_id is not None and plugin_id is not None:
            plugin_key = self.get_plugin_key(track_id, plugin_id)
            if plugin_key in self.parameter_cache:
                del self.parameter_cache[plugin_key]
                logger.info(f"Cleared parameter cache for plugin {plugin_key}")
        elif track_id is not None:
            # Clear all plugins on track
            keys_to_remove = [key for key in self.parameter_cache.keys() if key.startswith(f"{track_id}_")]
            for key in keys_to_remove:
                del self.parameter_cache[key]
            logger.info(f"Cleared parameter cache for track {track_id}")
        else:
            # Clear all cache
            self.parameter_cache.clear()
            logger.info("Cleared all parameter cache")
    
    def get_smart_parameter_suggestions(self, track_id: int, plugin_id: int, input_name: str) -> List[str]:
        """Get smart parameter suggestions based on input
        
        Args:
            track_id: Track ID (0-based)
            plugin_id: Plugin ID (0-based)
            input_name: Input parameter name or pattern
            
        Returns:
            List of suggested parameter names
        """
        # Common parameter name mappings
        name_mappings = {
            "thresh": ["threshold", "thresh", "thr"],
            "ratio": ["ratio", "compression", "comp_ratio"],
            "attack": ["attack", "att", "attack_time"],
            "release": ["release", "rel", "release_time"],
            "gain": ["gain", "makeup", "output", "level"],
            "freq": ["frequency", "freq", "center", "corner"],
            "q": ["q", "quality", "bandwidth", "resonance"],
            "low": ["low", "bass", "low_freq", "low_gain"],
            "mid": ["mid", "middle", "mid_freq", "mid_gain"],
            "high": ["high", "treble", "high_freq", "high_gain"],
            "wet": ["wet", "mix", "blend", "depth"],
            "dry": ["dry", "original", "direct"],
            "time": ["time", "delay", "predelay", "length"],
            "feedback": ["feedback", "regeneration", "fb"],
            "pan": ["pan", "stereo", "width", "position"]
        }
        
        # Get all parameter names for this plugin
        all_params = self.list_parameter_names(track_id, plugin_id)
        
        # Find matches using smart mapping
        suggestions = []
        input_lower = input_name.lower()
        
        # Direct matches first
        for param in all_params:
            if input_lower in param.lower():
                suggestions.append(param)
        
        # Smart mapping matches
        for smart_name, alternatives in name_mappings.items():
            if input_lower in alternatives:
                for param in all_params:
                    for alt in alternatives:
                        if alt in param.lower() and param not in suggestions:
                            suggestions.append(param)
        
        return suggestions[:5]  # Return top 5 suggestions

# Global parameter mapper instance
_parameter_mapper: Optional[PluginParameterMapper] = None

def get_parameter_mapper() -> PluginParameterMapper:
    """Get global parameter mapper instance"""
    global _parameter_mapper
    if _parameter_mapper is None:
        _parameter_mapper = PluginParameterMapper()
    return _parameter_mapper

def reset_parameter_mapper():
    """Reset global parameter mapper instance"""
    global _parameter_mapper
    _parameter_mapper = None