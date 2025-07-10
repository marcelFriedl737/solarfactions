# entities/vessels.py
from entities.objects import Vessel
from coordinates import Coordinates
from typing import List, Dict, Any

class Ship(Vessel):
    """Base class for all ships"""
    
    hull_integrity: float = 100.0
    shield_strength: float = 0.0
    armor_rating: float = 1.0
    weapon_hardpoints: int = 0
    upgrade_slots: int = 2
    
    def get_render_color(self) -> tuple:
        return (200, 200, 200)  # Light gray
    
    def get_render_size(self) -> int:
        return 3

class CargoShip(Ship):
    """Ships designed for cargo transport"""
    
    cargo_capacity: float = 100.0
    current_cargo: float = 0.0
    cargo_manifest: Dict[str, float] = {}
    
    def get_display_name(self) -> str:
        return f"Cargo Ship {str(self.id)[:8]}"
    
    def get_render_color(self) -> tuple:
        return (100, 150, 100)  # Green
    
    def load_cargo(self, commodity: str, amount: float) -> bool:
        """Load cargo if space available"""
        if self.current_cargo + amount <= self.cargo_capacity:
            self.cargo_manifest[commodity] = self.cargo_manifest.get(commodity, 0) + amount
            self.current_cargo += amount
            return True
        return False

class FreighterClass(CargoShip):
    """Large cargo haulers"""
    
    def __init__(self, position: Coordinates, **kwargs):
        super().__init__(
            position=position,
            mass=50.0,
            collision_radius=3.0,
            max_speed=5.0,
            fuel_capacity=200.0,
            current_fuel=200.0,
            crew_capacity=5,
            current_crew=5,
            cargo_capacity=500.0,
            **kwargs
        )
    
    def get_display_name(self) -> str:
        return f"Freighter {str(self.id)[:8]}"
    
    def get_render_size(self) -> int:
        return 5

class CombatShip(Ship):
    """Ships designed for combat"""
    
    weapon_damage: float = 10.0
    targeting_range: float = 20.0
    
    def get_display_name(self) -> str:
        return f"Combat Ship {str(self.id)[:8]}"
    
    def get_render_color(self) -> tuple:
        return (150, 50, 50)  # Red

class FighterClass(CombatShip):
    """Fast, agile combat ships"""
    
    def __init__(self, position: Coordinates, **kwargs):
        super().__init__(
            position=position,
            mass=10.0,
            collision_radius=1.5,
            max_speed=20.0,
            fuel_capacity=50.0,
            current_fuel=50.0,
            crew_capacity=1,
            current_crew=1,
            weapon_hardpoints=2,
            weapon_damage=15.0,
            targeting_range=25.0,
            **kwargs
        )
    
    def get_display_name(self) -> str:
        return f"Fighter {str(self.id)[:8]}"
    
    def get_render_size(self) -> int:
        return 2