# entities/resources.py
from entities.objects import SpaceObject
from typing import Dict
from coordinates import Coordinates

class NaturalObject(SpaceObject):
    """Base class for natural space objects"""
    
    def get_render_color(self) -> tuple:
        return (150, 150, 150)  # Gray
    
    def get_render_size(self) -> int:
        return 2

class Asteroid(NaturalObject):
    """Minable asteroid objects"""
    
    resource_content: Dict[str, float] = {}
    mining_difficulty: float = 1.0
    depletion_rate: float = 0.1
    
    def get_display_name(self) -> str:
        return f"Asteroid {str(self.id)[:8]}"
    
    def can_mine(self) -> bool:
        """Check if asteroid has resources to mine"""
        return sum(self.resource_content.values()) > 0
    
    def mine_resource(self, resource_type: str, amount: float) -> float:
        """Mine specified amount of resource"""
        available = self.resource_content.get(resource_type, 0)
        actual_amount = min(amount, available)
        
        if actual_amount > 0:
            self.resource_content[resource_type] -= actual_amount
            return actual_amount
        return 0

class MetallicAsteroid(Asteroid):
    """Asteroids rich in metals"""
    
    def __init__(self, position: Coordinates, **kwargs):
        super().__init__(
            position=position,
            mass=20.0,
            collision_radius=2.0,
            resource_content={
                "iron": 100.0,
                "copper": 50.0,
                "titanium": 25.0
            },
            mining_difficulty=0.8,
            **kwargs
        )
    
    def get_display_name(self) -> str:
        return f"Metallic Asteroid {str(self.id)[:8]}"
    
    def get_render_color(self) -> tuple:
        return (120, 120, 120)  # Dark gray

class IceAsteroid(Asteroid):
    """Asteroids rich in water ice"""
    
    def __init__(self, position: Coordinates, **kwargs):
        super().__init__(
            position=position,
            mass=15.0,
            collision_radius=1.8,
            resource_content={
                "water": 200.0,
                "hydrogen": 30.0
            },
            mining_difficulty=0.5,
            **kwargs
        )
    
    def get_display_name(self) -> str:
        return f"Ice Asteroid {str(self.id)[:8]}"
    
    def get_render_color(self) -> tuple:
        return (200, 230, 255)  # Light blue