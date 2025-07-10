# coordinates.py
from typing import Tuple, List
from dataclasses import dataclass
from math import sqrt, atan2, cos, sin
import numpy as np

@dataclass
class Coordinates:
    x: float
    y: float
    
    def distance_to(self, other: 'Coordinates') -> float:
        """Calculate Euclidean distance to another coordinate"""
        return sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
    
    def angle_to(self, other: 'Coordinates') -> float:
        """Calculate angle to another coordinate in radians"""
        return atan2(other.y - self.y, other.x - self.x)
    
    def move_toward(self, target: 'Coordinates', distance: float) -> 'Coordinates':
        """Move toward target by specified distance"""
        angle = self.angle_to(target)
        return Coordinates(
            self.x + cos(angle) * distance,
            self.y + sin(angle) * distance
        )
    
    def to_tuple(self) -> Tuple[float, float]:
        return (self.x, self.y)
    
    def to_int_tuple(self) -> Tuple[int, int]:
        return (int(self.x), int(self.y))

class Region:
    """Defines a rectangular region of space"""
    def __init__(self, min_x: float, min_y: float, max_x: float, max_y: float):
        self.min_x = min_x
        self.min_y = min_y
        self.max_x = max_x
        self.max_y = max_y
    
    def contains(self, coord: Coordinates) -> bool:
        return (self.min_x <= coord.x <= self.max_x and 
                self.min_y <= coord.y <= self.max_y)
    
    def random_point(self) -> Coordinates:
        """Generate random point within region"""
        import random
        x = random.uniform(self.min_x, self.max_x)
        y = random.uniform(self.min_y, self.max_y)
        return Coordinates(x, y)
    
    def center(self) -> Coordinates:
        return Coordinates(
            (self.min_x + self.max_x) / 2,
            (self.min_y + self.max_y) / 2
        )