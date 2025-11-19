"""
Tag Management System
Manages all variables (tags) used in the ladder logic program.
Similar to PLC tag database.
"""

from typing import Any, Dict
from threading import Lock


class TagDatabase:
    """
    Centralized tag storage similar to PLC tag database.
    Thread-safe for scan cycle operations.
    """
    
    def __init__(self):
        self.tags: Dict[str, Any] = {}
        self.lock = Lock()
        
        # Initialize system tags
        self.tags['_SYSTEM.SCAN_TIME'] = 0.0  # Scan cycle time in ms
        self.tags['_SYSTEM.RUNNING'] = False
        self.tags['_SYSTEM.ERROR'] = False
        self.tags['_SYSTEM.CYCLE_COUNT'] = 0
    
    def set(self, tag_name: str, value: Any) -> None:
        """Set a tag value (thread-safe)"""
        with self.lock:
            self.tags[tag_name] = value
    
    def get(self, tag_name: str, default: Any = False) -> Any:
        """Get a tag value (thread-safe)"""
        with self.lock:
            return self.tags.get(tag_name, default)
    
    def exists(self, tag_name: str) -> bool:
        """Check if tag exists"""
        with self.lock:
            return tag_name in self.tags
    
    def create(self, tag_name: str, initial_value: Any = False) -> None:
        """Create a new tag if it doesn't exist"""
        with self.lock:
            if tag_name not in self.tags:
                self.tags[tag_name] = initial_value
    
    def get_all(self) -> Dict[str, Any]:
        """Get all tags (returns a copy)"""
        with self.lock:
            return self.tags.copy()
    
    def clear_user_tags(self) -> None:
        """Clear all tags except system tags"""
        with self.lock:
            system_tags = {k: v for k, v in self.tags.items() if k.startswith('_SYSTEM')}
            self.tags = system_tags
