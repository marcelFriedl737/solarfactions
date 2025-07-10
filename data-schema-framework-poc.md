# Data Schema Framework (POC 2) - Implementation Plan

## Overview
This document outlines the detailed implementation plan for the Data Schema Framework proof-of-concept, the second POC in the Solar Factions architecture. This POC focuses on creating a robust, type-safe data validation and serialization system that integrates with the World Map POC while establishing the foundation for future POCs.

## Objectives
- Create comprehensive Pydantic models for all game entities
- Implement automatic data validation and serialization
- Establish schema evolution and migration patterns
- Provide type-safe integration with World Map POC entities
- Enable configuration-driven entity definitions
- Support JSON/YAML import/export functionality

## Technology Stack
- **Language**: Python 3.11+
- **Validation**: Pydantic v2.0+ for data models and validation
- **Serialization**: JSON and YAML support
- **Configuration**: YAML for human-readable configs
- **Schema Management**: JSON Schema for validation definitions
- **Testing**: pytest for comprehensive validation testing

## Integration with World Map POC

### Entity Model Migration Strategy
The Data Schema Framework will enhance the existing World Map POC entities with Pydantic validation:

```python
# World Map POC Entity (current)
class Entity(BaseModel, ABC):
    id: UUID = Field(default_factory=uuid4)
    position: Coordinates
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)

# Data Schema Framework Enhancement (new)
class ValidatedEntity(BaseModel, ABC):
    # Enhanced validation with custom validators
    id: UUID = Field(default_factory=uuid4, description="Unique entity identifier")
    position: Coordinates = Field(..., description="Entity position in 2D space")
    created_at: datetime = Field(default_factory=datetime.now, description="Entity creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Flexible metadata storage")
    
    # Enhanced validation methods
    @field_validator('position')
    @classmethod
    def validate_position(cls, v: Coordinates) -> Coordinates:
        if not isinstance(v, Coordinates):
            raise ValueError("Position must be a Coordinates object")
        return v
    
    @field_validator('id')
    @classmethod
    def validate_id(cls, v: UUID) -> UUID:
        if not isinstance(v, UUID):
            raise ValueError("ID must be a valid UUID")
        return v
    
    class Config:
        arbitrary_types_allowed = True
        validate_assignment = True
        use_enum_values = True
```

## Implementation Phases

### Phase 1: Core Schema Infrastructure (Week 1-2)

#### 1.1 Project Setup
```bash
# Directory structure
data_schema/
├── __init__.py
├── main.py                    # Entry point and demo
├── models/
│   ├── __init__.py
│   ├── base/
│   │   ├── __init__.py
│   │   ├── entity.py          # Enhanced base Entity class
│   │   ├── mixins.py          # Shared functionality mixins
│   │   └── validators.py      # Custom validation functions
│   ├── entities/
│   │   ├── __init__.py
│   │   ├── objects.py         # SpaceObject hierarchy
│   │   ├── vessels.py         # Vessel types and hierarchies
│   │   ├── structures.py      # Station/structure hierarchy
│   │   └── resources.py       # Asteroid/resource hierarchy
│   ├── actors.py              # AI actor definitions
│   ├── economy.py             # Trade, production models
│   └── world.py               # Map, region models
├── validators.py              # Global validation logic
├── serializers.py             # JSON/YAML serialization
├── schema_manager.py          # Schema evolution management
├── config_loader.py           # Configuration loading utilities
├── data/
│   ├── schemas/
│   │   ├── entities.json      # Entity schema definitions
│   │   ├── actors.json        # Actor schema definitions
│   │   ├── economy.json       # Economic schema definitions
│   │   └── world.json         # World schema definitions
│   ├── configs/
│   │   ├── entity_templates.yml
│   │   ├── ship_classes.yml
│   │   ├── station_types.yml
│   │   └── resource_types.yml
│   └── migrations/
│       └── schema_versions/
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_validation.py
│   ├── test_serialization.py
│   └── test_integration.py
└── requirements.txt
```

#### 1.2 Dependencies
```txt
# requirements.txt
pydantic>=2.0.0
pydantic-settings>=2.0.0
PyYAML>=6.0
jsonschema>=4.0.0
typing-extensions>=4.0.0
# Integration with World Map POC
pygame>=2.5.0
numpy>=1.24.0
```

#### 1.3 Enhanced Base Entity System
```python
# models/base/entity.py
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional, Union, List
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, field_validator, ConfigDict
from enum import Enum

class EntityType(str, Enum):
    """Enumeration of all entity types for validation"""
    SPACE_OBJECT = "space_object"
    VESSEL = "vessel"
    SHIP = "ship"
    STRUCTURE = "structure"
    STATION = "station"
    NATURAL_OBJECT = "natural_object"
    ACTOR = "actor"

class EntityStatus(str, Enum):
    """Entity operational status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DESTROYED = "destroyed"
    UNDER_CONSTRUCTION = "under_construction"

# Import from World Map POC
from world_map.coordinates import Coordinates

class ValidatedEntity(BaseModel, ABC):
    """Enhanced base entity with comprehensive validation"""
    
    # Core identification
    id: UUID = Field(default_factory=uuid4, description="Unique entity identifier")
    entity_type: EntityType = Field(..., description="Type classification for validation")
    name: Optional[str] = Field(None, description="Human-readable entity name")
    
    # Spatial properties
    position: Coordinates = Field(..., description="Entity position in 2D space")
    
    # Temporal properties
    created_at: datetime = Field(default_factory=datetime.now, description="Entity creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    
    # Operational status
    status: EntityStatus = Field(default=EntityStatus.ACTIVE, description="Entity operational status")
    
    # Flexible storage
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Flexible metadata storage")
    tags: List[str] = Field(default_factory=list, description="Searchable entity tags")
    
    # Configuration
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True,
        use_enum_values=True,
        extra='forbid'  # Prevent unknown fields
    )
    
    # Validation methods
    @field_validator('position')
    @classmethod
    def validate_position(cls, v: Coordinates) -> Coordinates:
        """Validate position coordinates"""
        if not isinstance(v, Coordinates):
            raise ValueError("Position must be a Coordinates object")
        if not (-10000 <= v.x <= 10000 and -10000 <= v.y <= 10000):
            raise ValueError("Position coordinates must be within valid range")
        return v
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate entity name"""
        if v is not None:
            if len(v.strip()) == 0:
                raise ValueError("Name cannot be empty")
            if len(v) > 100:
                raise ValueError("Name cannot exceed 100 characters")
        return v
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: List[str]) -> List[str]:
        """Validate tags list"""
        if len(v) > 20:
            raise ValueError("Cannot have more than 20 tags")
        for tag in v:
            if not isinstance(tag, str) or len(tag.strip()) == 0:
                raise ValueError("All tags must be non-empty strings")
        return v
    
    # Abstract methods (maintained from World Map POC)
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
    
    # Enhanced methods
    def update(self) -> None:
        """Update entity state with validation"""
        self.updated_at = datetime.now()
        # Trigger validation on update
        self.model_validate(self.model_dump())
    
    def to_dict(self) -> Dict[str, Any]:
        """Enhanced serialization with type information"""
        return {
            'id': str(self.id),
            'entity_type': self.entity_type.value,
            'type': self.__class__.__name__,
            'name': self.name,
            'position': {'x': self.position.x, 'y': self.position.y},
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'status': self.status.value,
            'metadata': self.metadata,
            'tags': self.tags,
            'schema_version': '1.0'
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ValidatedEntity':
        """Enhanced deserialization with validation"""
        # Convert position back to Coordinates
        if 'position' in data and isinstance(data['position'], dict):
            data['position'] = Coordinates(
                x=data['position']['x'],
                y=data['position']['y']
            )
        
        # Parse datetime strings
        for field in ['created_at', 'updated_at']:
            if field in data and isinstance(data[field], str):
                data[field] = datetime.fromisoformat(data[field])
        
        # Convert id string to UUID
        if 'id' in data and isinstance(data['id'], str):
            data['id'] = UUID(data['id'])
        
        return cls(**data)
    
    def validate_constraints(self) -> List[str]:
        """Validate entity-specific business rules"""
        errors = []
        
        # Override in subclasses for specific validation
        if self.status == EntityStatus.DESTROYED and self.updated_at < self.created_at:
            errors.append("Destroyed entities cannot have update time before creation")
        
        return errors
```

#### 1.4 Validation Mixins
```python
# models/base/mixins.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, field_validator
from enum import Enum

class PhysicalMixin(BaseModel, ABC):
    """Mixin for entities with physical properties"""
    
    mass: float = Field(gt=0, description="Entity mass in metric tons")
    collision_radius: float = Field(gt=0, description="Collision detection radius")
    
    @field_validator('mass')
    @classmethod
    def validate_mass(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Mass must be positive")
        if v > 1000000:  # 1 million tons
            raise ValueError("Mass cannot exceed 1 million tons")
        return v
    
    @field_validator('collision_radius')
    @classmethod
    def validate_collision_radius(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Collision radius must be positive")
        if v > 100:
            raise ValueError("Collision radius cannot exceed 100 units")
        return v

class MovementMixin(BaseModel, ABC):
    """Mixin for entities capable of movement"""
    
    max_speed: float = Field(gt=0, description="Maximum movement speed")
    current_speed: float = Field(ge=0, default=0, description="Current movement speed")
    heading: float = Field(ge=0, lt=360, default=0, description="Current heading in degrees")
    
    @field_validator('max_speed')
    @classmethod
    def validate_max_speed(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Max speed must be positive")
        if v > 1000:
            raise ValueError("Max speed cannot exceed 1000 units/tick")
        return v
    
    @field_validator('current_speed')
    @classmethod
    def validate_current_speed(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Current speed cannot be negative")
        return v
    
    @field_validator('heading')
    @classmethod
    def validate_heading(cls, v: float) -> float:
        if not (0 <= v < 360):
            raise ValueError("Heading must be between 0 and 360 degrees")
        return v

class ResourceMixin(BaseModel, ABC):
    """Mixin for entities with resource capacity"""
    
    resource_capacity: Dict[str, float] = Field(default_factory=dict, description="Resource storage capacity")
    current_resources: Dict[str, float] = Field(default_factory=dict, description="Current resource amounts")
    
    @field_validator('resource_capacity')
    @classmethod
    def validate_resource_capacity(cls, v: Dict[str, float]) -> Dict[str, float]:
        for resource, capacity in v.items():
            if capacity < 0:
                raise ValueError(f"Resource capacity for {resource} cannot be negative")
        return v
    
    @field_validator('current_resources')
    @classmethod
    def validate_current_resources(cls, v: Dict[str, float]) -> Dict[str, float]:
        for resource, amount in v.items():
            if amount < 0:
                raise ValueError(f"Current resource amount for {resource} cannot be negative")
        return v
    
    def get_resource_utilization(self) -> Dict[str, float]:
        """Calculate resource utilization percentages"""
        utilization = {}
        for resource in self.resource_capacity:
            current = self.current_resources.get(resource, 0)
            capacity = self.resource_capacity[resource]
            utilization[resource] = (current / capacity) if capacity > 0 else 0
        return utilization

class CrewMixin(BaseModel, ABC):
    """Mixin for entities with crew capacity"""
    
    crew_capacity: int = Field(gt=0, description="Maximum crew capacity")
    current_crew: int = Field(ge=0, description="Current crew count")
    crew_efficiency: float = Field(ge=0, le=1, default=1.0, description="Crew efficiency rating")
    
    @field_validator('crew_capacity')
    @classmethod
    def validate_crew_capacity(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("Crew capacity must be positive")
        if v > 10000:
            raise ValueError("Crew capacity cannot exceed 10,000")
        return v
    
    @field_validator('current_crew')
    @classmethod
    def validate_current_crew(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Current crew cannot be negative")
        return v
    
    @field_validator('crew_efficiency')
    @classmethod
    def validate_crew_efficiency(cls, v: float) -> float:
        if not (0 <= v <= 1):
            raise ValueError("Crew efficiency must be between 0 and 1")
        return v
    
    def get_crew_utilization(self) -> float:
        """Calculate crew utilization percentage"""
        return self.current_crew / self.crew_capacity if self.crew_capacity > 0 else 0

class EconomicMixin(BaseModel, ABC):
    """Mixin for entities with economic properties"""
    
    value: float = Field(ge=0, description="Economic value in credits")
    maintenance_cost: float = Field(ge=0, description="Maintenance cost per tick")
    
    @field_validator('value')
    @classmethod
    def validate_value(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Economic value cannot be negative")
        return v
    
    @field_validator('maintenance_cost')
    @classmethod
    def validate_maintenance_cost(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Maintenance cost cannot be negative")
        return v
```

### Phase 2: Enhanced Entity Models (Week 2-3)

#### 2.1 SpaceObject Models
```python
# models/entities/objects.py
from typing import Dict, Any, Optional
from pydantic import Field, field_validator
from models.base.entity import ValidatedEntity, EntityType
from models.base.mixins import PhysicalMixin
from world_map.coordinates import Coordinates

class ValidatedSpaceObject(ValidatedEntity, PhysicalMixin):
    """Enhanced SpaceObject with comprehensive validation"""
    
    entity_type: EntityType = Field(default=EntityType.SPACE_OBJECT, description="Entity type")
    
    # Physical properties from mixin are automatically included
    
    def get_display_name(self) -> str:
        return self.name or f"SpaceObject {str(self.id)[:8]}"
    
    def get_render_color(self) -> tuple:
        return (128, 128, 128)  # Gray
    
    def get_render_size(self) -> int:
        return max(2, int(self.collision_radius))
    
    def collides_with(self, other: 'ValidatedSpaceObject') -> bool:
        """Enhanced collision detection with validation"""
        if not isinstance(other, ValidatedSpaceObject):
            raise ValueError("Can only check collision with other SpaceObjects")
        
        distance = self.position.distance_to(other.position)
        return distance <= (self.collision_radius + other.collision_radius)
    
    def validate_constraints(self) -> List[str]:
        """Validate SpaceObject-specific constraints"""
        errors = super().validate_constraints()
        
        # Collision radius should be reasonable for mass
        if self.mass > 100 and self.collision_radius < 2:
            errors.append("Large objects (>100 tons) should have collision radius >= 2")
        
        return errors

class ValidatedVessel(ValidatedSpaceObject, MovementMixin, CrewMixin):
    """Enhanced Vessel with movement and crew validation"""
    
    entity_type: EntityType = Field(default=EntityType.VESSEL, description="Entity type")
    
    # Fuel system
    fuel_capacity: float = Field(gt=0, description="Maximum fuel capacity")
    current_fuel: float = Field(ge=0, description="Current fuel amount")
    fuel_efficiency: float = Field(gt=0, description="Fuel consumption rate")
    
    @field_validator('fuel_capacity')
    @classmethod
    def validate_fuel_capacity(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Fuel capacity must be positive")
        if v > 100000:
            raise ValueError("Fuel capacity cannot exceed 100,000 units")
        return v
    
    @field_validator('current_fuel')
    @classmethod
    def validate_current_fuel(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Current fuel cannot be negative")
        return v
    
    @field_validator('fuel_efficiency')
    @classmethod
    def validate_fuel_efficiency(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Fuel efficiency must be positive")
        return v
    
    def can_move(self) -> bool:
        """Enhanced movement validation"""
        return (self.current_fuel > 0 and 
                self.current_crew > 0 and 
                self.status == EntityStatus.ACTIVE)
    
    def calculate_fuel_consumption(self, distance: float) -> float:
        """Calculate fuel consumption for a given distance"""
        base_consumption = distance * self.fuel_efficiency
        # Adjust for crew efficiency
        return base_consumption / self.crew_efficiency
    
    def move_to(self, target: Coordinates) -> bool:
        """Enhanced movement with fuel consumption"""
        if not self.can_move():
            return False
        
        distance = self.position.distance_to(target)
        fuel_needed = self.calculate_fuel_consumption(distance)
        
        if fuel_needed > self.current_fuel:
            return False
        
        # Move to target
        if distance <= self.max_speed:
            self.position = target
            self.current_fuel -= fuel_needed
        else:
            self.position = self.position.move_toward(target, self.max_speed)
            self.current_fuel -= self.calculate_fuel_consumption(self.max_speed)
        
        self.update()
        return True
    
    def get_display_name(self) -> str:
        return self.name or f"Vessel {str(self.id)[:8]}"
    
    def get_render_color(self) -> tuple:
        return (100, 100, 200)  # Blue
    
    def validate_constraints(self) -> List[str]:
        """Validate Vessel-specific constraints"""
        errors = super().validate_constraints()
        
        # Fuel validation
        if self.current_fuel > self.fuel_capacity:
            errors.append("Current fuel cannot exceed fuel capacity")
        
        # Crew validation
        if self.current_crew > self.crew_capacity:
            errors.append("Current crew cannot exceed crew capacity")
        
        # Speed validation
        if self.current_speed > self.max_speed:
            errors.append("Current speed cannot exceed maximum speed")
        
        return errors
```

#### 2.2 Ship Models
```python
# models/entities/vessels.py
from typing import Dict, Any, List, Optional
from pydantic import Field, field_validator
from enum import Enum
from models.entities.objects import ValidatedVessel
from models.base.mixins import ResourceMixin, EconomicMixin

class ShipClass(str, Enum):
    """Ship classification system"""
    CARGO = "cargo"
    COMBAT = "combat"
    UTILITY = "utility"
    SPECIALTY = "specialty"
    DRONE = "drone"

class WeaponHardpoint(BaseModel):
    """Weapon hardpoint configuration"""
    
    size: str = Field(..., description="Hardpoint size (small, medium, large)")
    occupied: bool = Field(default=False, description="Whether hardpoint is occupied")
    weapon_type: Optional[str] = Field(None, description="Type of weapon installed")
    
    @field_validator('size')
    @classmethod
    def validate_size(cls, v: str) -> str:
        valid_sizes = ['small', 'medium', 'large', 'capital']
        if v not in valid_sizes:
            raise ValueError(f"Hardpoint size must be one of: {valid_sizes}")
        return v

class ValidatedShip(ValidatedVessel, ResourceMixin, EconomicMixin):
    """Enhanced Ship with comprehensive validation"""
    
    # Ship classification
    ship_class: ShipClass = Field(..., description="Ship classification")
    
    # Combat capabilities
    hull_integrity: float = Field(ge=0, le=100, default=100, description="Hull integrity percentage")
    shield_strength: float = Field(ge=0, default=0, description="Shield strength")
    armor_rating: float = Field(ge=0, default=1, description="Armor damage reduction")
    
    # Weapon systems
    weapon_hardpoints: List[WeaponHardpoint] = Field(default_factory=list, description="Weapon hardpoints")
    
    # Upgrade system
    upgrade_slots: int = Field(ge=0, description="Available upgrade slots")
    installed_upgrades: List[str] = Field(default_factory=list, description="Installed upgrades")
    
    @field_validator('hull_integrity')
    @classmethod
    def validate_hull_integrity(cls, v: float) -> float:
        if not (0 <= v <= 100):
            raise ValueError("Hull integrity must be between 0 and 100")
        return v
    
    @field_validator('shield_strength')
    @classmethod
    def validate_shield_strength(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Shield strength cannot be negative")
        return v
    
    @field_validator('armor_rating')
    @classmethod
    def validate_armor_rating(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Armor rating cannot be negative")
        if v > 10:
            raise ValueError("Armor rating cannot exceed 10")
        return v
    
    @field_validator('installed_upgrades')
    @classmethod
    def validate_installed_upgrades(cls, v: List[str]) -> List[str]:
        if len(v) > 20:  # Reasonable limit
            raise ValueError("Cannot have more than 20 installed upgrades")
        return v
    
    def get_combat_rating(self) -> float:
        """Calculate overall combat effectiveness"""
        base_rating = (self.hull_integrity / 100) * self.armor_rating
        weapon_rating = len([hp for hp in self.weapon_hardpoints if hp.occupied])
        return base_rating + weapon_rating
    
    def get_display_name(self) -> str:
        return self.name or f"Ship {str(self.id)[:8]}"
    
    def get_render_color(self) -> tuple:
        return (200, 200, 200)  # Light gray
    
    def get_render_size(self) -> int:
        return max(3, int(self.collision_radius))
    
    def validate_constraints(self) -> List[str]:
        """Validate Ship-specific constraints"""
        errors = super().validate_constraints()
        
        # Upgrade validation
        if len(self.installed_upgrades) > self.upgrade_slots:
            errors.append("Number of installed upgrades cannot exceed available slots")
        
        # Combat system validation
        if self.hull_integrity <= 0 and self.status != EntityStatus.DESTROYED:
            errors.append("Ships with 0 hull integrity should be marked as destroyed")
        
        return errors

class ValidatedCargoShip(ValidatedShip):
    """Cargo ship with enhanced validation"""
    
    ship_class: ShipClass = Field(default=ShipClass.CARGO, description="Ship class")
    
    # Cargo-specific properties
    cargo_capacity: float = Field(gt=0, description="Maximum cargo capacity")
    current_cargo: float = Field(ge=0, default=0, description="Current cargo amount")
    cargo_manifest: Dict[str, float] = Field(default_factory=dict, description="Cargo breakdown by type")
    
    @field_validator('cargo_capacity')
    @classmethod
    def validate_cargo_capacity(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Cargo capacity must be positive")
        if v > 50000:
            raise ValueError("Cargo capacity cannot exceed 50,000 units")
        return v
    
    @field_validator('current_cargo')
    @classmethod
    def validate_current_cargo(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Current cargo cannot be negative")
        return v
    
    @field_validator('cargo_manifest')
    @classmethod
    def validate_cargo_manifest(cls, v: Dict[str, float]) -> Dict[str, float]:
        for commodity, amount in v.items():
            if amount < 0:
                raise ValueError(f"Cargo amount for {commodity} cannot be negative")
        return v
    
    def load_cargo(self, commodity: str, amount: float) -> bool:
        """Load cargo with validation"""
        if amount <= 0:
            return False
        
        if self.current_cargo + amount > self.cargo_capacity:
            return False
        
        self.cargo_manifest[commodity] = self.cargo_manifest.get(commodity, 0) + amount
        self.current_cargo += amount
        self.update()
        return True
    
    def unload_cargo(self, commodity: str, amount: float) -> bool:
        """Unload cargo with validation"""
        if amount <= 0:
            return False
        
        available = self.cargo_manifest.get(commodity, 0)
        if amount > available:
            return False
        
        self.cargo_manifest[commodity] -= amount
        if self.cargo_manifest[commodity] == 0:
            del self.cargo_manifest[commodity]
        
        self.current_cargo -= amount
        self.update()
        return True
    
    def get_display_name(self) -> str:
        return self.name or f"Cargo Ship {str(self.id)[:8]}"
    
    def get_render_color(self) -> tuple:
        return (100, 150, 100)  # Green
    
    def validate_constraints(self) -> List[str]:
        """Validate CargoShip-specific constraints"""
        errors = super().validate_constraints()
        
        # Cargo validation
        if self.current_cargo > self.cargo_capacity:
            errors.append("Current cargo cannot exceed cargo capacity")
        
        # Manifest validation
        manifest_total = sum(self.cargo_manifest.values())
        if abs(manifest_total - self.current_cargo) > 0.01:  # Allow small floating point errors
            errors.append("Cargo manifest total must match current cargo amount")
        
        return errors

class ValidatedFreighterClass(ValidatedCargoShip):
    """Large cargo hauler with enhanced validation"""
    
    def __init__(self, **data):
        # Set default values for freighter class
        if 'mass' not in data:
            data['mass'] = 50.0
        if 'collision_radius' not in data:
            data['collision_radius'] = 3.0
        if 'max_speed' not in data:
            data['max_speed'] = 5.0
        if 'fuel_capacity' not in data:
            data['fuel_capacity'] = 200.0
        if 'current_fuel' not in data:
            data['current_fuel'] = 200.0
        if 'crew_capacity' not in data:
            data['crew_capacity'] = 5
        if 'current_crew' not in data:
            data['current_crew'] = 5
        if 'cargo_capacity' not in data:
            data['cargo_capacity'] = 500.0
        if 'fuel_efficiency' not in data:
            data['fuel_efficiency'] = 0.1
        if 'upgrade_slots' not in data:
            data['upgrade_slots'] = 3
        
        super().__init__(**data)
    
    def get_display_name(self) -> str:
        return self.name or f"Freighter {str(self.id)[:8]}"
    
    def get_render_size(self) -> int:
        return 5
```

### Phase 3: Configuration System (Week 3-4)

#### 3.1 Configuration Loading
```python
# config_loader.py
import yaml
import json
from typing import Dict, Any, List, Optional, Type
from pathlib import Path
from pydantic import BaseModel, Field, ValidationError
from models.base.entity import ValidatedEntity

class EntityTemplate(BaseModel):
    """Template for entity configuration"""
    
    name: str = Field(..., description="Template name")
    entity_class: str = Field(..., description="Entity class name")
    description: Optional[str] = Field(None, description="Template description")
    defaults: Dict[str, Any] = Field(default_factory=dict, description="Default values")
    constraints: Dict[str, Any] = Field(default_factory=dict, description="Validation constraints")
    tags: List[str] = Field(default_factory=list, description="Template tags")

class ConfigurationManager:
    """Manages entity templates and configurations"""
    
    def __init__(self, config_dir: str = "data/configs"):
        self.config_dir = Path(config_dir)
        self.templates: Dict[str, EntityTemplate] = {}
        self.entity_classes: Dict[str, Type[ValidatedEntity]] = {}
        
        # Load configurations
        self._load_templates()
        self._register_entity_classes()
    
    def _load_templates(self):
        """Load entity templates from YAML files"""
        template_files = self.config_dir.glob("*.yml")
        
        for file_path in template_files:
            try:
                with open(file_path, 'r') as f:
                    data = yaml.safe_load(f)
                
                if 'templates' in data:
                    for template_name, template_data in data['templates'].items():
                        template = EntityTemplate(
                            name=template_name,
                            **template_data
                        )
                        self.templates[template_name] = template
                        
            except Exception as e:
                print(f"Error loading template file {file_path}: {e}")
    
    def _register_entity_classes(self):
        """Register available entity classes"""
        # Import all entity classes
        from models.entities.objects import ValidatedSpaceObject, ValidatedVessel
        from models.entities.vessels import ValidatedShip, ValidatedCargoShip, ValidatedFreighterClass
        
        self.entity_classes.update({
            'ValidatedSpaceObject': ValidatedSpaceObject,
            'ValidatedVessel': ValidatedVessel,
            'ValidatedShip': ValidatedShip,
            'ValidatedCargoShip': ValidatedCargoShip,
            'ValidatedFreighterClass': ValidatedFreighterClass
        })
    
    def create_entity_from_template(self, template_name: str, **overrides) -> ValidatedEntity:
        """Create entity instance from template"""
        if template_name not in self.templates:
            raise ValueError(f"Template '{template_name}' not found")
        
        template = self.templates[template_name]
        
        if template.entity_class not in self.entity_classes:
            raise ValueError(f"Entity class '{template.entity_class}' not registered")
        
        entity_class = self.entity_classes[template.entity_class]
        
        # Merge template defaults with overrides
        entity_data = {**template.defaults, **overrides}
        
        # Create and validate entity
        return entity_class(**entity_data)
    
    def get_template(self, name: str) -> Optional[EntityTemplate]:
        """Get template by name"""
        return self.templates.get(name)
    
    def list_templates(self) -> List[str]:
        """List all available templates"""
        return list(self.templates.keys())
    
    def validate_template(self, template_name: str) -> List[str]:
        """Validate template configuration"""
        if template_name not in self.templates:
            return [f"Template '{template_name}' not found"]
        
        template = self.templates[template_name]
        errors = []
        
        # Check if entity class exists
        if template.entity_class not in self.entity_classes:
            errors.append(f"Entity class '{template.entity_class}' not registered")
        else:
            # Try to create entity with template defaults
            try:
                entity_class = self.entity_classes[template.entity_class]
                entity_class(**template.defaults)
            except ValidationError as e:
                errors.extend([str(error) for error in e.errors()])
        
        return errors
```

#### 3.2 Configuration Templates
```yaml
# data/configs/ship_classes.yml
templates:
  basic_freighter:
    entity_class: "ValidatedFreighterClass"
    description: "Basic cargo hauler for short-range operations"
    defaults:
      name: "Basic Freighter"
      mass: 50.0
      collision_radius: 3.0
      max_speed: 5.0
      fuel_capacity: 200.0
      current_fuel: 200.0
      crew_capacity: 5
      current_crew: 5
      cargo_capacity: 500.0
      fuel_efficiency: 0.1
      upgrade_slots: 3
      hull_integrity: 100.0
      armor_rating: 1.0
      value: 100000.0
      maintenance_cost: 50.0
    tags: ["cargo", "civilian", "basic"]
    
  heavy_freighter:
    entity_class: "ValidatedFreighterClass"
    description: "Heavy cargo hauler for long-range operations"
    defaults:
      name: "Heavy Freighter"
      mass: 100.0
      collision_radius: 4.0
      max_speed: 3.0
      fuel_capacity: 500.0
      current_fuel: 500.0
      crew_capacity: 10
      current_crew: 10
      cargo_capacity: 1000.0
      fuel_efficiency: 0.15
      upgrade_slots: 5
      hull_integrity: 100.0
      armor_rating: 2.0
      value: 250000.0
      maintenance_cost: 100.0
    tags: ["cargo", "civilian", "heavy"]
    
  combat_freighter:
    entity_class: "ValidatedFreighterClass"
    description: "Armed cargo hauler for dangerous regions"
    defaults:
      name: "Combat Freighter"
      mass: 75.0
      collision_radius: 3.5
      max_speed: 4.0
      fuel_capacity: 300.0
      current_fuel: 300.0
      crew_capacity: 8
      current_crew: 8
      cargo_capacity: 400.0
      fuel_efficiency: 0.12
      upgrade_slots: 4
      hull_integrity: 100.0
      armor_rating: 3.0
      shield_strength: 50.0
      value: 180000.0
      maintenance_cost: 80.0
      weapon_hardpoints:
        - size: "medium"
          occupied: true
          weapon_type: "plasma_cannon"
        - size: "small"
          occupied: true
          weapon_type: "point_defense"
    tags: ["cargo", "combat", "armed"]
```

### Phase 4: Serialization and Schema Management (Week 4-5)

#### 4.1 Advanced Serialization
```python
# serializers.py
import json
import yaml
from typing import Dict, Any, List, Optional, Type, Union
from datetime import datetime
from uuid import UUID
from pathlib import Path
from pydantic import BaseModel, ValidationError
from models.base.entity import ValidatedEntity

class SerializationError(Exception):
    """Custom exception for serialization errors"""
    pass

class EntitySerializer:
    """Enhanced serialization for entities"""
    
    SCHEMA_VERSION = "1.0"
    
    def __init__(self):
        self.entity_classes: Dict[str, Type[ValidatedEntity]] = {}
        self._register_entity_classes()
    
    def _register_entity_classes(self):
        """Register all entity classes for deserialization"""
        from models.entities.objects import ValidatedSpaceObject, ValidatedVessel
        from models.entities.vessels import ValidatedShip, ValidatedCargoShip, ValidatedFreighterClass
        
        self.entity_classes.update({
            'ValidatedSpaceObject': ValidatedSpaceObject,
            'ValidatedVessel': ValidatedVessel,
            'ValidatedShip': ValidatedShip,
            'ValidatedCargoShip': ValidatedCargoShip,
            'ValidatedFreighterClass': ValidatedFreighterClass
        })
    
    def serialize_entity(self, entity: ValidatedEntity) -> Dict[str, Any]:
        """Serialize entity to dictionary with metadata"""
        data = entity.to_dict()
        data['schema_version'] = self.SCHEMA_VERSION
        data['serialized_at'] = datetime.now().isoformat()
        return data
    
    def deserialize_entity(self, data: Dict[str, Any]) -> ValidatedEntity:
        """Deserialize entity from dictionary with validation"""
        if 'type' not in data:
            raise SerializationError("Entity data missing 'type' field")
        
        entity_type = data['type']
        if entity_type not in self.entity_classes:
            raise SerializationError(f"Unknown entity type: {entity_type}")
        
        entity_class = self.entity_classes[entity_type]
        
        try:
            return entity_class.from_dict(data)
        except ValidationError as e:
            raise SerializationError(f"Validation error deserializing {entity_type}: {e}")
    
    def serialize_entities(self, entities: List[ValidatedEntity]) -> Dict[str, Any]:
        """Serialize multiple entities with metadata"""
        return {
            'schema_version': self.SCHEMA_VERSION,
            'serialized_at': datetime.now().isoformat(),
            'entity_count': len(entities),
            'entities': [self.serialize_entity(entity) for entity in entities]
        }
    
    def deserialize_entities(self, data: Dict[str, Any]) -> List[ValidatedEntity]:
        """Deserialize multiple entities with validation"""
        if 'entities' not in data:
            raise SerializationError("Data missing 'entities' field")
        
        entities = []
        for entity_data in data['entities']:
            try:
                entity = self.deserialize_entity(entity_data)
                entities.append(entity)
            except SerializationError as e:
                print(f"Warning: Failed to deserialize entity: {e}")
                continue
        
        return entities
    
    def save_to_json(self, entities: List[ValidatedEntity], file_path: str):
        """Save entities to JSON file"""
        data = self.serialize_entities(entities)
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def load_from_json(self, file_path: str) -> List[ValidatedEntity]:
        """Load entities from JSON file"""
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        return self.deserialize_entities(data)
    
    def save_to_yaml(self, entities: List[ValidatedEntity], file_path: str):
        """Save entities to YAML file"""
        data = self.serialize_entities(entities)
        
        with open(file_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)
    
    def load_from_yaml(self, file_path: str) -> List[ValidatedEntity]:
        """Load entities from YAML file"""
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        
        return self.deserialize_entities(data)
```

#### 4.2 Schema Management
```python
# schema_manager.py
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
from pydantic import BaseModel, Field

class SchemaVersion(BaseModel):
    """Schema version metadata"""
    
    version: str = Field(..., description="Schema version number")
    created_at: datetime = Field(default_factory=datetime.now, description="Version creation date")
    description: str = Field(..., description="Version description")
    changes: List[str] = Field(default_factory=list, description="List of changes")
    migration_required: bool = Field(default=False, description="Whether migration is required")

class SchemaManager:
    """Manages schema versions and migrations"""
    
    def __init__(self, schema_dir: str = "data/schemas"):
        self.schema_dir = Path(schema_dir)
        self.schema_dir.mkdir(parents=True, exist_ok=True)
        self.versions: Dict[str, SchemaVersion] = {}
        self.current_version = "1.0"
        
        self._load_versions()
    
    def _load_versions(self):
        """Load schema versions from metadata"""
        version_file = self.schema_dir / "versions.json"
        
        if version_file.exists():
            with open(version_file, 'r') as f:
                data = json.load(f)
            
            for version_info in data.get('versions', []):
                version = SchemaVersion(**version_info)
                self.versions[version.version] = version
    
    def save_versions(self):
        """Save schema versions to metadata"""
        version_file = self.schema_dir / "versions.json"
        
        data = {
            'current_version': self.current_version,
            'versions': [version.dict() for version in self.versions.values()]
        }
        
        with open(version_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def add_version(self, version: str, description: str, changes: List[str], migration_required: bool = False):
        """Add new schema version"""
        schema_version = SchemaVersion(
            version=version,
            description=description,
            changes=changes,
            migration_required=migration_required
        )
        
        self.versions[version] = schema_version
        self.current_version = version
        self.save_versions()
    
    def get_version(self, version: str) -> Optional[SchemaVersion]:
        """Get schema version information"""
        return self.versions.get(version)
    
    def list_versions(self) -> List[str]:
        """List all schema versions"""
        return sorted(self.versions.keys())
    
    def generate_entity_schema(self, entity_class: type) -> Dict[str, Any]:
        """Generate JSON schema for entity class"""
        return entity_class.model_json_schema()
    
    def save_entity_schema(self, entity_class: type, file_name: str):
        """Save entity schema to file"""
        schema = self.generate_entity_schema(entity_class)
        schema_file = self.schema_dir / file_name
        
        with open(schema_file, 'w') as f:
            json.dump(schema, f, indent=2)
    
    def validate_data_against_schema(self, data: Dict[str, Any], schema_file: str) -> List[str]:
        """Validate data against JSON schema"""
        # This would implement JSON schema validation
        # For now, return empty list (no errors)
        return []
```

### Phase 5: Integration Testing (Week 5-6)

#### 5.1 Integration Tests
```python
# tests/test_integration.py
import pytest
from pathlib import Path
from models.entities.objects import ValidatedSpaceObject, ValidatedVessel
from models.entities.vessels import ValidatedCargoShip, ValidatedFreighterClass
from config_loader import ConfigurationManager
from serializers import EntitySerializer
from world_map.coordinates import Coordinates
from world_map.generator import MapGenerator

class TestWorldMapIntegration:
    """Test integration with World Map POC"""
    
    def test_entity_compatibility(self):
        """Test that enhanced entities are compatible with World Map POC"""
        # Create enhanced entity
        entity = ValidatedFreighterClass(
            position=Coordinates(100, 200),
            name="Test Freighter"
        )
        
        # Test World Map POC interface methods
        assert entity.get_display_name() == "Test Freighter"
        assert isinstance(entity.get_render_color(), tuple)
        assert isinstance(entity.get_render_size(), int)
        assert isinstance(entity.to_dict(), dict)
    
    def test_serialization_compatibility(self):
        """Test serialization compatibility with World Map POC format"""
        serializer = EntitySerializer()
        
        # Create entity
        entity = ValidatedFreighterClass(
            position=Coordinates(100, 200),
            name="Test Freighter"
        )
        
        # Serialize
        data = serializer.serialize_entity(entity)
        
        # Check World Map POC format compatibility
        assert 'id' in data
        assert 'type' in data
        assert 'position' in data
        assert 'position' in data and 'x' in data['position'] and 'y' in data['position']
        assert 'created_at' in data
        assert 'updated_at' in data
        assert 'metadata' in data
        
        # Deserialize
        deserialized = serializer.deserialize_entity(data)
        assert deserialized.id == entity.id
        assert deserialized.position.x == entity.position.x
        assert deserialized.position.y == entity.position.y
    
    def test_map_generator_integration(self):
        """Test integration with World Map POC map generator"""
        # This would test loading World Map POC generated entities
        # and converting them to enhanced entities
        pass
    
    def test_validation_enhancement(self):
        """Test that validation enhances World Map POC entities"""
        # Test invalid data that would pass basic validation
        with pytest.raises(ValidationError):
            ValidatedFreighterClass(
                position=Coordinates(100, 200),
                mass=-10,  # Invalid negative mass
                name="Test Freighter"
            )
        
        with pytest.raises(ValidationError):
            ValidatedFreighterClass(
                position=Coordinates(100, 200),
                fuel_capacity=0,  # Invalid zero fuel capacity
                name="Test Freighter"
            )

class TestConfigurationSystem:
    """Test configuration-driven entity creation"""
    
    def test_template_loading(self):
        """Test loading entity templates"""
        config_manager = ConfigurationManager()
        
        # Check that templates are loaded
        templates = config_manager.list_templates()
        assert len(templates) > 0
    
    def test_entity_creation_from_template(self):
        """Test creating entities from templates"""
        config_manager = ConfigurationManager()
        
        # Create entity from template
        entity = config_manager.create_entity_from_template(
            "basic_freighter",
            position=Coordinates(100, 200)
        )
        
        assert isinstance(entity, ValidatedFreighterClass)
        assert entity.name == "Basic Freighter"
        assert entity.position.x == 100
        assert entity.position.y == 200
    
    def test_template_validation(self):
        """Test template validation"""
        config_manager = ConfigurationManager()
        
        # Validate all templates
        for template_name in config_manager.list_templates():
            errors = config_manager.validate_template(template_name)
            assert len(errors) == 0, f"Template {template_name} has errors: {errors}"

class TestPerformanceImpact:
    """Test performance impact of enhanced validation"""
    
    def test_entity_creation_performance(self):
        """Test that enhanced entities don't significantly impact performance"""
        import time
        
        start_time = time.time()
        
        # Create many entities
        entities = []
        for i in range(1000):
            entity = ValidatedFreighterClass(
                position=Coordinates(i, i),
                name=f"Freighter {i}"
            )
            entities.append(entity)
        
        end_time = time.time()
        creation_time = end_time - start_time
        
        # Should create 1000 entities in reasonable time (< 1 second)
        assert creation_time < 1.0, f"Entity creation took {creation_time:.2f}s"
    
    def test_serialization_performance(self):
        """Test serialization performance"""
        import time
        
        serializer = EntitySerializer()
        
        # Create entities
        entities = []
        for i in range(100):
            entity = ValidatedFreighterClass(
                position=Coordinates(i, i),
                name=f"Freighter {i}"
            )
            entities.append(entity)
        
        # Test serialization performance
        start_time = time.time()
        data = serializer.serialize_entities(entities)
        end_time = time.time()
        
        serialization_time = end_time - start_time
        assert serialization_time < 0.5, f"Serialization took {serialization_time:.2f}s"
        
        # Test deserialization performance
        start_time = time.time()
        deserialized = serializer.deserialize_entities(data)
        end_time = time.time()
        
        deserialization_time = end_time - start_time
        assert deserialization_time < 0.5, f"Deserialization took {deserialization_time:.2f}s"
        
        assert len(deserialized) == 100
```

## Success Criteria

### Functional Requirements
1. **Enhanced Validation**: All entity data is validated with comprehensive rules
2. **Template System**: Entities can be created from YAML configuration templates
3. **Serialization**: Enhanced JSON/YAML serialization with schema versioning
4. **Integration**: Seamless integration with World Map POC entities
5. **Performance**: Validation overhead < 10% of entity creation time

### Technical Requirements
1. **Type Safety**: Full Pydantic validation for all entity properties
2. **Schema Evolution**: Support for schema versioning and migration
3. **Configuration-Driven**: Entity templates defined in YAML files
4. **Backward Compatibility**: Works with existing World Map POC entities
5. **Error Handling**: Comprehensive error reporting for validation failures

### Testing Strategy
1. **Unit Tests**: Test each model class and validation rule
2. **Integration Tests**: Test compatibility with World Map POC
3. **Performance Tests**: Measure validation overhead
4. **Configuration Tests**: Test template loading and validation
5. **Schema Tests**: Test serialization and deserialization

## Development Timeline

- **Week 1**: Core schema infrastructure and enhanced base classes
- **Week 2**: Enhanced entity models with comprehensive validation
- **Week 3**: Configuration system and template loading
- **Week 4**: Serialization and schema management
- **Week 5**: Integration testing and performance optimization
- **Week 6**: Documentation and final testing

## Integration Benefits

### For World Map POC
- Enhanced data validation prevents invalid entity states
- Configuration-driven entity creation reduces code duplication
- Improved serialization with schema versioning
- Better error reporting for debugging

### For Future POCs
- Type-safe entity models provide reliable foundation
- Template system enables easy entity customization
- Schema evolution supports system upgrades
- Comprehensive validation catches errors early

This Data Schema Framework POC establishes a robust foundation for type-safe, validated entity management while maintaining full compatibility with the World Map POC and providing clear integration points for future POCs.
