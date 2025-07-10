# entities/base.py
from abc import ABC, abstractmethod
from uuid import uuid4, UUID
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from coordinates import Coordinates

class Entity(BaseModel, ABC):
    """Abstract base class for all game entities"""
    
    id: UUID = Field(default_factory=uuid4)
    position: Coordinates
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        arbitrary_types_allowed = True
    
    @abstractmethod
    def get_display_name(self) -> str:
        """Return human-readable name for this entity"""
        pass
    
    @abstractmethod
    def get_render_color(self) -> tuple:
        """Return RGB color tuple for rendering"""
        pass
    
    @abstractmethod
    def get_render_size(self) -> int:
        """Return size in pixels for rendering"""
        pass
    
    def update(self) -> None:
        """Update entity state"""
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize entity to dictionary"""
        return {
            'id': str(self.id),
            'type': self.__class__.__name__,
            'position': {'x': self.position.x, 'y': self.position.y},
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'metadata': self.metadata
        }