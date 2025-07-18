"""
Selection Manager for Ardour MCP Server
Manages selected strips and plugins for OSC operations
"""

import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum
import threading
import time

logger = logging.getLogger(__name__)


class SelectionType(Enum):
    """Type of selection (GUI selection or local expansion)"""
    GUI_SELECTION = "gui_selection"
    LOCAL_EXPANSION = "local_expansion"


@dataclass
class SelectionState:
    """Current selection state"""
    strip_id: Optional[int] = None
    plugin_id: Optional[int] = None
    selection_type: SelectionType = SelectionType.GUI_SELECTION
    expanded: bool = False
    last_updated: float = 0.0
    
    def __post_init__(self):
        if self.last_updated == 0.0:
            self.last_updated = time.time()
    
    def is_valid(self) -> bool:
        """Check if selection is valid"""
        return self.strip_id is not None
    
    def clear(self):
        """Clear selection state"""
        self.strip_id = None
        self.plugin_id = None
        self.selection_type = SelectionType.GUI_SELECTION
        self.expanded = False
        self.last_updated = time.time()


class SelectionManager:
    """Manages selection state for Ardour OSC operations"""
    
    def __init__(self):
        self._selection_state = SelectionState()
        self._lock = threading.Lock()
        self._listeners: List[callable] = []
        logger.info("SelectionManager initialized")
    
    def get_current_selection(self) -> SelectionState:
        """Get current selection state"""
        with self._lock:
            return SelectionState(
                strip_id=self._selection_state.strip_id,
                plugin_id=self._selection_state.plugin_id,
                selection_type=self._selection_state.selection_type,
                expanded=self._selection_state.expanded,
                last_updated=self._selection_state.last_updated
            )
    
    def select_strip(self, strip_id: int, force_gui_selection: bool = False) -> bool:
        """Select a strip (GUI selection)
        
        Args:
            strip_id: Strip ID to select
            force_gui_selection: Force GUI selection even if in expansion mode
            
        Returns:
            True if selection changed
        """
        with self._lock:
            old_state = self._selection_state
            
            # GUI selection overrides expansion
            if force_gui_selection or self._selection_state.selection_type == SelectionType.GUI_SELECTION:
                self._selection_state.strip_id = strip_id
                self._selection_state.selection_type = SelectionType.GUI_SELECTION
                self._selection_state.expanded = True  # GUI selection sets expanded mode
                self._selection_state.last_updated = time.time()
                
                # Reset plugin selection when strip changes
                if old_state.strip_id != strip_id:
                    self._selection_state.plugin_id = None
                
                logger.info(f"Strip {strip_id} selected (GUI selection)")
                self._notify_listeners(old_state, self._selection_state)
                return True
            
            return False
    
    def expand_strip(self, strip_id: int, expanded: bool = True) -> bool:
        """Expand a strip (local expansion)
        
        Args:
            strip_id: Strip ID to expand
            expanded: True to expand, False to contract
            
        Returns:
            True if expansion state changed
        """
        with self._lock:
            old_state = self._selection_state
            
            if expanded:
                self._selection_state.strip_id = strip_id
                self._selection_state.selection_type = SelectionType.LOCAL_EXPANSION
                self._selection_state.expanded = True
                self._selection_state.last_updated = time.time()
                
                # Reset plugin selection when strip changes
                if old_state.strip_id != strip_id:
                    self._selection_state.plugin_id = None
                
                logger.info(f"Strip {strip_id} expanded (local expansion)")
            else:
                # Setting expand to False resets to GUI selection
                self._selection_state.selection_type = SelectionType.GUI_SELECTION
                self._selection_state.expanded = False
                self._selection_state.last_updated = time.time()
                
                logger.info(f"Strip expansion disabled, reverting to GUI selection")
            
            self._notify_listeners(old_state, self._selection_state)
            return True
    
    def select_plugin(self, plugin_id: int, strip_id: Optional[int] = None) -> bool:
        """Select a plugin on the current or specified strip
        
        Args:
            plugin_id: Plugin ID to select
            strip_id: Strip ID (optional, uses current if not provided)
            
        Returns:
            True if plugin selection changed
        """
        with self._lock:
            old_state = self._selection_state
            
            # Use current strip if not specified
            if strip_id is None:
                strip_id = self._selection_state.strip_id
                
            if strip_id is None:
                logger.warning("Cannot select plugin without a selected strip")
                return False
            
            # Update strip selection if different
            if self._selection_state.strip_id != strip_id:
                self._selection_state.strip_id = strip_id
                self._selection_state.selection_type = SelectionType.GUI_SELECTION
                self._selection_state.expanded = True
            
            self._selection_state.plugin_id = plugin_id
            self._selection_state.last_updated = time.time()
            
            logger.info(f"Plugin {plugin_id} selected on strip {strip_id}")
            self._notify_listeners(old_state, self._selection_state)
            return True
    
    def select_plugin_delta(self, delta: int) -> bool:
        """Select plugin by delta from current plugin
        
        Args:
            delta: Delta to apply to current plugin selection
            
        Returns:
            True if plugin selection changed
        """
        with self._lock:
            if self._selection_state.strip_id is None:
                logger.warning("Cannot select plugin delta without a selected strip")
                return False
            
            current_plugin = self._selection_state.plugin_id or 0
            new_plugin = max(0, current_plugin + delta)
            
            return self.select_plugin(new_plugin)
    
    def clear_selection(self) -> bool:
        """Clear current selection"""
        with self._lock:
            old_state = self._selection_state
            self._selection_state.clear()
            
            logger.info("Selection cleared")
            self._notify_listeners(old_state, self._selection_state)
            return True
    
    def get_selected_strip_id(self) -> Optional[int]:
        """Get currently selected strip ID"""
        with self._lock:
            return self._selection_state.strip_id
    
    def get_selected_plugin_id(self) -> Optional[int]:
        """Get currently selected plugin ID"""
        with self._lock:
            return self._selection_state.plugin_id
    
    def is_expanded(self) -> bool:
        """Check if current selection is in expanded mode"""
        with self._lock:
            return self._selection_state.expanded
    
    def get_selection_type(self) -> SelectionType:
        """Get current selection type"""
        with self._lock:
            return self._selection_state.selection_type
    
    def add_listener(self, listener: callable):
        """Add a selection change listener
        
        Args:
            listener: Callable that receives (old_state, new_state)
        """
        with self._lock:
            self._listeners.append(listener)
    
    def remove_listener(self, listener: callable):
        """Remove a selection change listener"""
        with self._lock:
            if listener in self._listeners:
                self._listeners.remove(listener)
    
    def _notify_listeners(self, old_state: SelectionState, new_state: SelectionState):
        """Notify listeners of selection changes"""
        for listener in self._listeners:
            try:
                listener(old_state, new_state)
            except Exception as e:
                logger.error(f"Error notifying selection listener: {e}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert selection state to dictionary"""
        with self._lock:
            return {
                "strip_id": self._selection_state.strip_id,
                "plugin_id": self._selection_state.plugin_id,
                "selection_type": self._selection_state.selection_type.value,
                "expanded": self._selection_state.expanded,
                "last_updated": self._selection_state.last_updated,
                "is_valid": self._selection_state.is_valid()
            }


# Global selection manager instance
_selection_manager: Optional[SelectionManager] = None


def get_selection_manager() -> SelectionManager:
    """Get global selection manager instance"""
    global _selection_manager
    if _selection_manager is None:
        _selection_manager = SelectionManager()
    return _selection_manager


def reset_selection_manager():
    """Reset global selection manager instance"""
    global _selection_manager
    _selection_manager = None