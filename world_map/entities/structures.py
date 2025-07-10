# entities/structures.py
from entities.objects import SpaceObject
from coordinates import Coordinates
from typing import List, Dict, Any

class Structure(SpaceObject):
    """Base class for all fixed structures"""
    
    operational: bool = True
    power_capacity: float = 100.0
    current_power: float = 100.0
    
    def get_render_color(self) -> tuple:
        return (100, 100, 200)  # Blue
    
    def get_render_size(self) -> int:
        return 4

class Station(Structure):
    """Base class for all space stations"""
    
    docking_bays: int = 4
    occupied_bays: int = 0
    services: List[str] = []
    storage_capacity: float = 1000.0
    current_storage: float = 0.0
    
    def can_dock(self) -> bool:
        """Check if station has available docking"""
        return self.occupied_bays < self.docking_bays
    
    def dock_ship(self) -> bool:
        """Dock a ship if space available"""
        if self.can_dock():
            self.occupied_bays += 1
            return True
        return False
    
    def undock_ship(self) -> bool:
        """Undock a ship"""
        if self.occupied_bays > 0:
            self.occupied_bays -= 1
            return True
        return False

class TradingStation(Station):
    """Stations focused on trade and commerce"""
    
    def __init__(self, position: Coordinates, **kwargs):
        super().__init__(
            position=position,
            mass=100.0,
            collision_radius=5.0,
            docking_bays=8,
            services=["trade", "refuel", "repair"],
            storage_capacity=2000.0,
            **kwargs
        )
    
    def get_display_name(self) -> str:
        return f"Trading Station {str(self.id)[:8]}"
    
    def get_render_color(self) -> tuple:
        return (200, 150, 50)  # Gold
    
    def get_render_size(self) -> int:
        return 6

class IndustrialStation(Station):
    """Stations focused on production and manufacturing"""
    
    production_modules: List[str] = []
    production_efficiency: float = 1.0
    
    def __init__(self, position: Coordinates, **kwargs):
        super().__init__(
            position=position,
            mass=200.0,
            collision_radius=7.0,
            docking_bays=6,
            services=["manufacturing", "repair", "upgrade"],
            storage_capacity=3000.0,
            production_modules=["basic_manufacturing"],
            **kwargs
        )
    
    def get_display_name(self) -> str:
        return f"Industrial Station {str(self.id)[:8]}"
    
    def get_render_color(self) -> tuple:
        return (150, 100, 50)  # Brown
    
    def get_render_size(self) -> int:
        return 8