# entities/objects.py
from typing import Optional
from entities.base import Entity
from coordinates import Coordinates

class SpaceObject(Entity):
    """Base class for all physical objects in space"""
    
    mass: float = 1.0
    collision_radius: float = 1.0
    
    def collides_with(self, other: 'SpaceObject') -> bool:
        """Check if this object collides with another"""
        distance = self.position.distance_to(other.position)
        return distance <= (self.collision_radius + other.collision_radius)

class Vessel(SpaceObject):
    """Base class for all mobile vessels"""
    
    max_speed: float = 10.0
    fuel_capacity: float = 100.0
    current_fuel: float = 100.0
    crew_capacity: int = 1
    current_crew: int = 1
    
    def can_move(self) -> bool:
        """Check if vessel can move"""
        return self.current_fuel > 0 and self.current_crew > 0
    
    def move_to(self, target: Coordinates) -> bool:
        """Move vessel toward target position"""
        if not self.can_move():
            return False
        
        distance = self.position.distance_to(target)
        if distance <= self.max_speed:
            self.position = target
            self.current_fuel -= distance * 0.1  # Fuel consumption
            self.update()
            return True
        else:
            self.position = self.position.move_toward(target, self.max_speed)
            self.current_fuel -= self.max_speed * 0.1
            self.update()
            return False