# entity.py - Simplified Entity System
"""
Simplified entity system using composition over inheritance.
This replaces the complex hierarchy with a flexible component-based approach.
"""

from typing import Dict, Any, List, Tuple
import json
import uuid
from datetime import datetime


class Entity:
    """
    Simplified entity with component system.
    
    Instead of complex inheritance, entities are defined by:
    - Type: What kind of entity (ship, planet, asteroid, etc.)
    - Position: Where it is in space
    - Properties: Basic attributes (name, size, etc.)
    - Components: Modular behaviors (movement, combat, trading, etc.)
    """
    
    def __init__(self, entity_type: str, position: Tuple[float, float], **properties):
        self.id = str(uuid.uuid4())
        self.type = entity_type
        self.position = position
        self.properties = properties
        self.components = {}
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def add_component(self, name: str, component_data: Dict[str, Any]):
        """Add a component to this entity"""
        self.components[name] = component_data
        self.updated_at = datetime.now()
    
    def get_component(self, name: str) -> Dict[str, Any]:
        """Get a component from this entity"""
        return self.components.get(name, {})
    
    def has_component(self, name: str) -> bool:
        """Check if entity has a specific component"""
        return name in self.components
    
    def remove_component(self, name: str):
        """Remove a component from this entity"""
        if name in self.components:
            del self.components[name]
            self.updated_at = datetime.now()
    
    def get_property(self, name: str, default=None):
        """Get a property value"""
        return self.properties.get(name, default)
    
    def set_property(self, name: str, value: Any):
        """Set a property value"""
        self.properties[name] = value
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary for serialization"""
        return {
            'id': self.id,
            'type': self.type,
            'position': self.position,
            'properties': self.properties,
            'components': self.components,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Entity':
        """Create entity from dictionary"""
        entity = cls(
            entity_type=data['type'],
            position=tuple(data['position']),
            **data.get('properties', {})
        )
        entity.id = data.get('id', entity.id)
        entity.components = data.get('components', {})
        
        # Parse timestamps if present
        if 'created_at' in data:
            entity.created_at = datetime.fromisoformat(data['created_at'])
        if 'updated_at' in data:
            entity.updated_at = datetime.fromisoformat(data['updated_at'])
        
        return entity
    
    def __str__(self) -> str:
        name = self.get_property('name', f'{self.type}_{self.id[:8]}')
        return f"{name} ({self.type}) at {self.position}"
    
    def __repr__(self) -> str:
        return f"Entity(id='{self.id}', type='{self.type}', position={self.position})"


class EntityFactory:
    """Factory for creating entities from templates"""
    
    def __init__(self):
        self.templates = {}
    
    def register_template(self, entity_type: str, template: Dict[str, Any]):
        """Register a template for creating entities of a specific type"""
        self.templates[entity_type] = template
    
    def create_entity(self, entity_type: str, position: Tuple[float, float], **overrides) -> Entity:
        """Create an entity from a template"""
        template = self.templates.get(entity_type, {})
        
        # Merge template properties with overrides
        properties = template.get('properties', {}).copy()
        properties.update(overrides)
        
        # Create entity
        entity = Entity(entity_type, position, **properties)
        
        # Add template components
        for component_name, component_data in template.get('components', {}).items():
            entity.add_component(component_name, component_data)
        
        return entity
    
    def load_templates(self, filepath: str):
        """Load entity templates from JSON file"""
        with open(filepath, 'r') as f:
            templates = json.load(f)
        
        for entity_type, template in templates.items():
            self.register_template(entity_type, template)


# Common component types for easy reuse
class ComponentTemplates:
    """Predefined component templates for common functionality"""
    
    MOVEMENT = {
        'max_speed': 100.0,
        'acceleration': 10.0,
        'velocity': [0.0, 0.0],
        'destination': None
    }
    
    HEALTH = {
        'max_health': 100,
        'current_health': 100,
        'shields': 0,
        'armor': 0
    }
    
    CARGO = {
        'capacity': 100,
        'current_load': 0,
        'items': []
    }
    
    COMBAT = {
        'weapon_damage': 10,
        'weapon_range': 50,
        'weapon_cooldown': 1.0,
        'last_fired': 0
    }
    
    MINING = {
        'mining_rate': 5.0,
        'mining_range': 20.0,
        'target_asteroid': None
    }
    
    TRADING = {
        'credits': 1000,
        'buy_orders': [],
        'sell_orders': []
    }


# Example usage and predefined entity types
def create_basic_templates() -> Dict[str, Dict[str, Any]]:
    """Create basic entity templates"""
    return {
        'star': {
            'properties': {
                'name': 'Unknown Star',
                'temperature': 5778,
                'size': 'medium',
                'color': 'yellow'
            },
            'components': {}
        },
        'planet': {
            'properties': {
                'name': 'Unknown Planet',
                'size': 'medium',
                'habitable': False,
                'population': 0
            },
            'components': {}
        },
        'asteroid': {
            'properties': {
                'name': 'Asteroid',
                'size': 'small',
                'resources': ['iron', 'nickel']
            },
            'components': {}
        },
        'space_station': {
            'properties': {
                'name': 'Station',
                'size': 'large',
                'population': 100,
                'services': ['trading', 'repair']
            },
            'components': {
                'trading': ComponentTemplates.TRADING,
                'cargo': ComponentTemplates.CARGO
            }
        },
        'cargo_ship': {
            'properties': {
                'name': 'Cargo Ship',
                'size': 'medium',
                'crew': 5
            },
            'components': {
                'movement': ComponentTemplates.MOVEMENT,
                'health': ComponentTemplates.HEALTH,
                'cargo': ComponentTemplates.CARGO
            }
        },
        'fighter': {
            'properties': {
                'name': 'Fighter',
                'size': 'small',
                'crew': 1
            },
            'components': {
                'movement': ComponentTemplates.MOVEMENT,
                'health': ComponentTemplates.HEALTH,
                'combat': ComponentTemplates.COMBAT
            }
        },
        'mining_ship': {
            'properties': {
                'name': 'Mining Ship',
                'size': 'medium',
                'crew': 3
            },
            'components': {
                'movement': ComponentTemplates.MOVEMENT,
                'health': ComponentTemplates.HEALTH,
                'cargo': ComponentTemplates.CARGO,
                'mining': ComponentTemplates.MINING
            }
        }
    }


# Example usage
if __name__ == "__main__":
    # Create factory and register templates
    factory = EntityFactory()
    templates = create_basic_templates()
    
    for entity_type, template in templates.items():
        factory.register_template(entity_type, template)
    
    # Create some entities
    star = factory.create_entity('star', (500, 400), name='Sol', temperature=5778)
    planet = factory.create_entity('planet', (300, 400), name='Earth', habitable=True)
    ship = factory.create_entity('cargo_ship', (100, 200), name='Merchant One')
    
    print(f"Created: {star}")
    print(f"Created: {planet}")
    print(f"Created: {ship}")
    
    # Demonstrate component system
    print(f"\nShip has movement: {ship.has_component('movement')}")
    print(f"Ship cargo capacity: {ship.get_component('cargo').get('capacity', 0)}")
    
    # Add a new component
    ship.add_component('scanner', {'range': 100, 'resolution': 'high'})
    print(f"Ship has scanner: {ship.has_component('scanner')}")
    
    # Serialize and deserialize
    ship_data = ship.to_dict()
    reconstructed_ship = Entity.from_dict(ship_data)
    print(f"Reconstructed: {reconstructed_ship}")
