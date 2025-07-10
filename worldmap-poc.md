# World Map Generator (POC 1) - Implementation Plan

## Overview
This document outlines the detailed implementation plan for the World Map Generator proof-of-concept, the first POC in the Solar Factions architecture. This POC focuses on creating and visualizing a 2D space map with procedurally generated entities following the object-oriented inheritance hierarchy.

## Objectives
- Create a procedural 2D space map generator
- Implement the entity inheritance hierarchy (Entity → SpaceObject → Vessel/Structure/NaturalObject)
- Visualize the generated world using pygame
- Export maps in various formats (JSON, image)
- Establish the foundation for other POCs

## Technology Stack
- **Language**: Python 3.11+
- **Visualization**: pygame for 2D rendering
- **Data Storage**: JSON files for map definitions
- **Validation**: Pydantic for data models
- **Coordinates**: Simple 2D coordinate system (x, y)
- **Image Export**: PIL/Pillow for image generation

## Implementation Phases

### Phase 1: Core Foundation (Week 1-2)

#### 1.1 Project Setup
```bash
# Directory structure
world_map/
├── __init__.py
├── main.py                    # Entry point and demo
├── generator.py               # Map generation algorithms
├── renderer.py                # Pygame visualization
├── coordinates.py             # 2D coordinate system
├── entities/
│   ├── __init__.py
│   ├── base.py                # Base Entity class
│   ├── objects.py             # SpaceObject hierarchy
│   ├── vessels.py             # Vessel hierarchy
│   ├── structures.py          # Station/structure hierarchy
│   └── resources.py           # Asteroid/resource hierarchy
├── data/
│   ├── map_templates.json     # Map generation templates
│   ├── entity_types.json      # Entity type definitions
│   └── generated_maps/        # Output directory
├── tests/
│   ├── __init__.py
│   ├── test_entities.py
│   ├── test_generator.py
│   └── test_renderer.py
└── requirements.txt
```

#### 1.2 Dependencies
```txt
# requirements.txt
pygame>=2.5.0
pydantic>=2.0.0
Pillow>=10.0.0
numpy>=1.24.0
dataclasses-json>=0.6.0
```

#### 1.3 Core Coordinate System
```python
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
        x = np.random.uniform(self.min_x, self.max_x)
        y = np.random.uniform(self.min_y, self.max_y)
        return Coordinates(x, y)
    
    def center(self) -> Coordinates:
        return Coordinates(
            (self.min_x + self.max_x) / 2,
            (self.min_y + self.max_y) / 2
        )
```

### Phase 2: Entity Hierarchy Implementation (Week 2-3)

#### 2.1 Base Entity Class
```python
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
```

#### 2.2 SpaceObject Hierarchy
```python
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
```

#### 2.3 Ship Classes
```python
# entities/vessels.py
from entities.objects import Vessel
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
```

#### 2.4 Station Classes
```python
# entities/structures.py
from entities.objects import SpaceObject
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
```

#### 2.5 Natural Objects
```python
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
```

### Phase 3: Map Generation (Week 3-4)

#### 3.1 Map Generation Configuration
```json
// data/map_templates.json
{
  "templates": {
    "basic_sector": {
      "name": "Basic Sector",
      "description": "A simple sector with basic entities",
      "size": {"width": 1000, "height": 1000},
      "entity_counts": {
        "trading_stations": {"min": 2, "max": 5},
        "industrial_stations": {"min": 1, "max": 3},
        "freighter_ships": {"min": 5, "max": 15},
        "fighter_ships": {"min": 3, "max": 8},
        "metallic_asteroids": {"min": 20, "max": 40},
        "ice_asteroids": {"min": 15, "max": 30}
      },
      "placement_rules": {
        "stations": {
          "min_distance_from_edge": 100,
          "min_distance_between": 150
        },
        "asteroids": {
          "cluster_probability": 0.6,
          "cluster_size": {"min": 3, "max": 8},
          "cluster_spread": 50
        },
        "ships": {
          "spawn_near_stations": true,
          "station_proximity": 100
        }
      }
    },
    "resource_rich": {
      "name": "Resource Rich Sector",
      "description": "A sector with abundant resources",
      "size": {"width": 1200, "height": 1200},
      "entity_counts": {
        "trading_stations": {"min": 1, "max": 2},
        "industrial_stations": {"min": 2, "max": 4},
        "freighter_ships": {"min": 8, "max": 20},
        "fighter_ships": {"min": 2, "max": 6},
        "metallic_asteroids": {"min": 40, "max": 80},
        "ice_asteroids": {"min": 30, "max": 60}
      },
      "placement_rules": {
        "asteroids": {
          "cluster_probability": 0.8,
          "cluster_size": {"min": 5, "max": 12},
          "cluster_spread": 75
        }
      }
    }
  }
}
```

#### 3.2 Map Generator Implementation
```python
# generator.py
import json
import random
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from coordinates import Coordinates, Region
from entities.base import Entity
from entities.vessels import FreighterClass, FighterClass
from entities.structures import TradingStation, IndustrialStation
from entities.resources import MetallicAsteroid, IceAsteroid

@dataclass
class MapTemplate:
    name: str
    description: str
    size: Dict[str, int]
    entity_counts: Dict[str, Dict[str, int]]
    placement_rules: Dict[str, Any]

class MapGenerator:
    """Procedural map generation engine"""
    
    def __init__(self, template_file: str = "data/map_templates.json"):
        self.templates = self._load_templates(template_file)
        self.entity_registry = {
            'trading_stations': TradingStation,
            'industrial_stations': IndustrialStation,
            'freighter_ships': FreighterClass,
            'fighter_ships': FighterClass,
            'metallic_asteroids': MetallicAsteroid,
            'ice_asteroids': IceAsteroid
        }
    
    def _load_templates(self, file_path: str) -> Dict[str, MapTemplate]:
        """Load map generation templates from JSON file"""
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        templates = {}
        for name, template_data in data['templates'].items():
            templates[name] = MapTemplate(
                name=template_data['name'],
                description=template_data['description'],
                size=template_data['size'],
                entity_counts=template_data['entity_counts'],
                placement_rules=template_data['placement_rules']
            )
        
        return templates
    
    def generate_map(self, template_name: str, seed: int = None) -> List[Entity]:
        """Generate a map using the specified template"""
        if seed is not None:
            random.seed(seed)
        
        template = self.templates[template_name]
        entities = []
        
        # Create map region
        region = Region(0, 0, template.size['width'], template.size['height'])
        
        # Generate entities by type
        for entity_type, count_range in template.entity_counts.items():
            count = random.randint(count_range['min'], count_range['max'])
            entity_class = self.entity_registry[entity_type]
            
            if entity_type.endswith('_stations'):
                entities.extend(self._generate_stations(entity_class, count, region, template))
            elif entity_type.endswith('_ships'):
                entities.extend(self._generate_ships(entity_class, count, region, template, entities))
            elif entity_type.endswith('_asteroids'):
                entities.extend(self._generate_asteroids(entity_class, count, region, template))
        
        return entities
    
    def _generate_stations(self, entity_class: type, count: int, region: Region, template: MapTemplate) -> List[Entity]:
        """Generate stations with placement rules"""
        entities = []
        placement_rules = template.placement_rules.get('stations', {})
        
        min_edge_distance = placement_rules.get('min_distance_from_edge', 50)
        min_between_distance = placement_rules.get('min_distance_between', 100)
        
        # Create valid placement region
        valid_region = Region(
            region.min_x + min_edge_distance,
            region.min_y + min_edge_distance,
            region.max_x - min_edge_distance,
            region.max_y - min_edge_distance
        )
        
        attempts = 0
        while len(entities) < count and attempts < count * 10:
            position = valid_region.random_point()
            
            # Check minimum distance from other stations
            valid_position = True
            for existing in entities:
                if position.distance_to(existing.position) < min_between_distance:
                    valid_position = False
                    break
            
            if valid_position:
                entities.append(entity_class(position=position))
            
            attempts += 1
        
        return entities
    
    def _generate_ships(self, entity_class: type, count: int, region: Region, template: MapTemplate, existing_entities: List[Entity]) -> List[Entity]:
        """Generate ships with placement rules"""
        entities = []
        placement_rules = template.placement_rules.get('ships', {})
        
        spawn_near_stations = placement_rules.get('spawn_near_stations', False)
        station_proximity = placement_rules.get('station_proximity', 50)
        
        # Find stations for proximity spawning
        stations = [e for e in existing_entities if 'Station' in e.__class__.__name__]
        
        for _ in range(count):
            if spawn_near_stations and stations:
                # Spawn near a random station
                station = random.choice(stations)
                angle = random.uniform(0, 2 * 3.14159)
                distance = random.uniform(10, station_proximity)
                
                position = Coordinates(
                    station.position.x + distance * random.uniform(-1, 1),
                    station.position.y + distance * random.uniform(-1, 1)
                )
                
                # Ensure position is within region
                position.x = max(region.min_x, min(region.max_x, position.x))
                position.y = max(region.min_y, min(region.max_y, position.y))
            else:
                position = region.random_point()
            
            entities.append(entity_class(position=position))
        
        return entities
    
    def _generate_asteroids(self, entity_class: type, count: int, region: Region, template: MapTemplate) -> List[Entity]:
        """Generate asteroids with clustering rules"""
        entities = []
        placement_rules = template.placement_rules.get('asteroids', {})
        
        cluster_probability = placement_rules.get('cluster_probability', 0.5)
        cluster_size_range = placement_rules.get('cluster_size', {'min': 3, 'max': 8})
        cluster_spread = placement_rules.get('cluster_spread', 30)
        
        remaining_count = count
        
        while remaining_count > 0:
            if random.random() < cluster_probability and remaining_count > 1:
                # Create cluster
                cluster_size = min(
                    random.randint(cluster_size_range['min'], cluster_size_range['max']),
                    remaining_count
                )
                
                # Cluster center
                center = region.random_point()
                
                for _ in range(cluster_size):
                    # Position within cluster
                    angle = random.uniform(0, 2 * 3.14159)
                    distance = random.uniform(0, cluster_spread)
                    
                    position = Coordinates(
                        center.x + distance * random.uniform(-1, 1),
                        center.y + distance * random.uniform(-1, 1)
                    )
                    
                    # Ensure position is within region
                    position.x = max(region.min_x, min(region.max_x, position.x))
                    position.y = max(region.min_y, min(region.max_y, position.y))
                    
                    entities.append(entity_class(position=position))
                
                remaining_count -= cluster_size
            else:
                # Create single asteroid
                position = region.random_point()
                entities.append(entity_class(position=position))
                remaining_count -= 1
        
        return entities
    
    def export_map(self, entities: List[Entity], filename: str) -> None:
        """Export generated map to JSON file"""
        map_data = {
            'generated_at': datetime.now().isoformat(),
            'entity_count': len(entities),
            'entities': [entity.to_dict() for entity in entities]
        }
        
        with open(f"data/generated_maps/{filename}.json", 'w') as f:
            json.dump(map_data, f, indent=2)
```

### Phase 4: Visualization (Week 4-5)

#### 4.1 Pygame Renderer
```python
# renderer.py
import pygame
import sys
from typing import List, Tuple, Optional
from entities.base import Entity
from coordinates import Coordinates

class MapRenderer:
    """Pygame-based map visualization"""
    
    def __init__(self, width: int = 1200, height: int = 800, title: str = "Solar Factions - World Map"):
        self.width = width
        self.height = height
        self.title = title
        
        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()
        
        # Rendering settings
        self.background_color = (10, 10, 30)  # Dark space blue
        self.grid_color = (30, 30, 50)
        self.grid_size = 50
        self.font = pygame.font.Font(None, 24)
        
        # View settings
        self.view_offset = Coordinates(0, 0)
        self.zoom_level = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 5.0
        
        # Selection
        self.selected_entity = None
        self.show_labels = True
        self.show_grid = True
    
    def world_to_screen(self, world_pos: Coordinates) -> Tuple[int, int]:
        """Convert world coordinates to screen coordinates"""
        screen_x = int((world_pos.x - self.view_offset.x) * self.zoom_level + self.width / 2)
        screen_y = int((world_pos.y - self.view_offset.y) * self.zoom_level + self.height / 2)
        return (screen_x, screen_y)
    
    def screen_to_world(self, screen_pos: Tuple[int, int]) -> Coordinates:
        """Convert screen coordinates to world coordinates"""
        world_x = (screen_pos[0] - self.width / 2) / self.zoom_level + self.view_offset.x
        world_y = (screen_pos[1] - self.height / 2) / self.zoom_level + self.view_offset.y
        return Coordinates(world_x, world_y)
    
    def draw_grid(self) -> None:
        """Draw background grid"""
        if not self.show_grid:
            return
        
        grid_spacing = int(self.grid_size * self.zoom_level)
        if grid_spacing < 10:  # Don't draw if too small
            return
        
        # Calculate grid offset
        offset_x = int((-self.view_offset.x * self.zoom_level + self.width / 2) % grid_spacing)
        offset_y = int((-self.view_offset.y * self.zoom_level + self.height / 2) % grid_spacing)
        
        # Draw vertical lines
        for x in range(offset_x, self.width, grid_spacing):
            pygame.draw.line(self.screen, self.grid_color, (x, 0), (x, self.height))
        
        # Draw horizontal lines
        for y in range(offset_y, self.height, grid_spacing):
            pygame.draw.line(self.screen, self.grid_color, (0, y), (self.width, y))
    
    def draw_entity(self, entity: Entity) -> None:
        """Draw a single entity"""
        screen_pos = self.world_to_screen(entity.position)
        
        # Skip if off-screen
        if (screen_pos[0] < -50 or screen_pos[0] > self.width + 50 or
            screen_pos[1] < -50 or screen_pos[1] > self.height + 50):
            return
        
        # Get entity rendering properties
        color = entity.get_render_color()
        size = max(1, int(entity.get_render_size() * self.zoom_level))
        
        # Draw entity
        pygame.draw.circle(self.screen, color, screen_pos, size)
        
        # Draw selection highlight
        if entity == self.selected_entity:
            pygame.draw.circle(self.screen, (255, 255, 255), screen_pos, size + 3, 2)
        
        # Draw label if enabled and zoomed in enough
        if self.show_labels and self.zoom_level > 0.5:
            label = entity.get_display_name()
            text_surface = self.font.render(label, True, (200, 200, 200))
            text_rect = text_surface.get_rect()
            text_rect.center = (screen_pos[0], screen_pos[1] - size - 15)
            self.screen.blit(text_surface, text_rect)
    
    def draw_entities(self, entities: List[Entity]) -> None:
        """Draw all entities"""
        for entity in entities:
            self.draw_entity(entity)
    
    def draw_ui(self, entities: List[Entity]) -> None:
        """Draw UI elements"""
        # Entity count
        count_text = f"Entities: {len(entities)}"
        count_surface = self.font.render(count_text, True, (255, 255, 255))
        self.screen.blit(count_surface, (10, 10))
        
        # Zoom level
        zoom_text = f"Zoom: {self.zoom_level:.2f}x"
        zoom_surface = self.font.render(zoom_text, True, (255, 255, 255))
        self.screen.blit(zoom_surface, (10, 35))
        
        # View position
        pos_text = f"View: ({self.view_offset.x:.1f}, {self.view_offset.y:.1f})"
        pos_surface = self.font.render(pos_text, True, (255, 255, 255))
        self.screen.blit(pos_surface, (10, 60))
        
        # Selected entity info
        if self.selected_entity:
            info_lines = [
                f"Selected: {self.selected_entity.get_display_name()}",
                f"Type: {self.selected_entity.__class__.__name__}",
                f"Position: ({self.selected_entity.position.x:.1f}, {self.selected_entity.position.y:.1f})"
            ]
            
            for i, line in enumerate(info_lines):
                info_surface = self.font.render(line, True, (255, 255, 255))
                self.screen.blit(info_surface, (10, self.height - 90 + i * 25))
        
        # Controls
        controls = [
            "Controls:",
            "WASD - Move view",
            "Mouse wheel - Zoom",
            "Click - Select entity",
            "G - Toggle grid",
            "L - Toggle labels",
            "ESC - Exit"
        ]
        
        for i, control in enumerate(controls):
            control_surface = self.font.render(control, True, (150, 150, 150))
            self.screen.blit(control_surface, (self.width - 200, 10 + i * 20))
    
    def find_entity_at_position(self, entities: List[Entity], screen_pos: Tuple[int, int]) -> Optional[Entity]:
        """Find entity at screen position"""
        world_pos = self.screen_to_world(screen_pos)
        
        for entity in entities:
            distance = world_pos.distance_to(entity.position)
            if distance <= entity.get_render_size() / self.zoom_level:
                return entity
        
        return None
    
    def handle_input(self, entities: List[Entity]) -> bool:
        """Handle pygame input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_g:
                    self.show_grid = not self.show_grid
                elif event.key == pygame.K_l:
                    self.show_labels = not self.show_labels
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.selected_entity = self.find_entity_at_position(entities, event.pos)
                elif event.button == 4:  # Mouse wheel up
                    self.zoom_level = min(self.max_zoom, self.zoom_level * 1.2)
                elif event.button == 5:  # Mouse wheel down
                    self.zoom_level = max(self.min_zoom, self.zoom_level / 1.2)
        
        # Handle continuous key presses
        keys = pygame.key.get_pressed()
        move_speed = 10 / self.zoom_level
        
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.view_offset.y -= move_speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.view_offset.y += move_speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.view_offset.x -= move_speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.view_offset.x += move_speed
        
        return True
    
    def render_frame(self, entities: List[Entity]) -> None:
        """Render a single frame"""
        self.screen.fill(self.background_color)
        
        self.draw_grid()
        self.draw_entities(entities)
        self.draw_ui(entities)
        
        pygame.display.flip()
        self.clock.tick(60)
    
    def run(self, entities: List[Entity]) -> None:
        """Main rendering loop"""
        running = True
        
        while running:
            running = self.handle_input(entities)
            self.render_frame(entities)
        
        pygame.quit()
    
    def export_screenshot(self, entities: List[Entity], filename: str) -> None:
        """Export current view as image"""
        self.render_frame(entities)
        pygame.image.save(self.screen, f"data/generated_maps/{filename}.png")
```

### Phase 5: Integration and Testing (Week 5-6)

#### 5.1 Main Application
```python
# main.py
import sys
import argparse
from typing import List
from generator import MapGenerator
from renderer import MapRenderer
from entities.base import Entity

def main():
    parser = argparse.ArgumentParser(description='Solar Factions World Map Generator')
    parser.add_argument('--template', default='basic_sector', help='Map template to use')
    parser.add_argument('--seed', type=int, default=None, help='Random seed for generation')
    parser.add_argument('--export', help='Export map to file (without extension)')
    parser.add_argument('--no-render', action='store_true', help='Skip rendering')
    
    args = parser.parse_args()
    
    # Generate map
    print(f"Generating map using template: {args.template}")
    generator = MapGenerator()
    entities = generator.generate_map(args.template, args.seed)
    
    print(f"Generated {len(entities)} entities")
    
    # Export if requested
    if args.export:
        generator.export_map(entities, args.export)
        print(f"Map exported to: data/generated_maps/{args.export}.json")
    
    # Render if not skipped
    if not args.no_render:
        renderer = MapRenderer()
        renderer.run(entities)

if __name__ == "__main__":
    main()
```

## Success Criteria

### Functional Requirements
1. **Map Generation**: Generate procedural maps with configurable templates
2. **Entity Hierarchy**: Implement full OOP entity inheritance
3. **Visualization**: Interactive pygame-based map viewer
4. **Export**: Save maps as JSON and PNG files
5. **User Interaction**: Basic navigation and entity selection

### Technical Requirements
1. **Performance**: Handle 100+ entities at 60 FPS
2. **Modularity**: Clean separation between generation, rendering, and entities
3. **Extensibility**: Easy to add new entity types and templates
4. **Data Format**: JSON export compatible with other POCs

### Testing Strategy
1. **Unit Tests**: Test each entity class and generation algorithms
2. **Integration Tests**: Test map generation and rendering pipeline
3. **Performance Tests**: Measure rendering performance with large maps
4. **Manual Testing**: Interactive testing of UI and controls

## Development Timeline

- **Week 1**: Core foundation and coordinate system
- **Week 2**: Entity hierarchy implementation
- **Week 3**: Map generation algorithms
- **Week 4**: Pygame renderer and visualization
- **Week 5**: Integration and testing
- **Week 6**: Polish and documentation

## Next Steps

After completing this POC:

1. **Data Schema POC**: Use entity classes as basis for Pydantic models
2. **Behavior Engine POC**: Implement behaviors for generated entities
3. **Game Loop POC**: Add time-based updates to the world
4. **Integration**: Combine all POCs into unified engine

This POC establishes the foundation for all subsequent development phases.