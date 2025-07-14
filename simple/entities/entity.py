# entity.py - Simplified Entity System
"""
Simplified entity system using composition over inheritance.
This replaces the complex hierarchy with a flexible component-based approach.
Components are now configurable and extendable through JSON files.
"""

from typing import Dict, Any, List, Tuple, Optional
import json
import uuid
import os
from datetime import datetime


class ComponentRegistry:
    """Registry for managing component definitions from JSON files"""
    
    def __init__(self):
        self.components = {}
        self.component_paths = []
        self._load_default_components()
    
    def _load_default_components(self):
        """Load default component definitions"""
        # Try to load from the data/components directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        components_dir = os.path.join(os.path.dirname(current_dir), 'data', 'components')
        
        # Load main components file
        main_components_path = os.path.join(components_dir, 'components.json')
        if os.path.exists(main_components_path):
            self.load_components_from_file(main_components_path)
        
        # Load custom components file
        custom_components_path = os.path.join(components_dir, 'custom_components.json')
        if os.path.exists(custom_components_path):
            self.load_components_from_file(custom_components_path)
    
    def load_components_from_file(self, filepath: str):
        """Load component definitions from a JSON file"""
        try:
            with open(filepath, 'r') as f:
                components = json.load(f)
            
            for component_name, component_def in components.items():
                self.register_component(component_name, component_def)
            
            if filepath not in self.component_paths:
                self.component_paths.append(filepath)
        
        except Exception as e:
            print(f"Warning: Could not load components from {filepath}: {e}")
    
    def register_component(self, name: str, definition: Dict[str, Any]):
        """Register a component definition"""
        self.components[name] = definition
    
    def get_component_definition(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a component definition by name"""
        return self.components.get(name)
    
    def create_component(self, name: str, **overrides) -> Dict[str, Any]:
        """Create a component instance with default values and overrides"""
        definition = self.get_component_definition(name)
        if not definition:
            # Return a basic component if definition not found
            return overrides
        
        # Start with default values from the definition
        component_data = {}
        properties = definition.get('properties', {})
        
        for prop_name, prop_def in properties.items():
            if isinstance(prop_def, dict) and 'default' in prop_def:
                component_data[prop_name] = prop_def['default']
            else:
                component_data[prop_name] = prop_def
        
        # Apply overrides
        component_data.update(overrides)
        
        return component_data
    
    def get_available_components(self) -> List[str]:
        """Get list of all available component names"""
        return list(self.components.keys())
    
    def get_component_description(self, name: str) -> str:
        """Get description of a component"""
        definition = self.get_component_definition(name)
        if definition:
            return definition.get('description', f'{name} component')
        return f'Unknown component: {name}'
    
    def validate_component_data(self, name: str, data: Dict[str, Any]) -> bool:
        """Validate component data against its definition"""
        definition = self.get_component_definition(name)
        if not definition:
            return True  # Allow unknown components
        
        properties = definition.get('properties', {})
        
        for prop_name, prop_value in data.items():
            if prop_name in properties:
                prop_def = properties[prop_name]
                if isinstance(prop_def, dict) and 'type' in prop_def:
                    expected_type = prop_def['type']
                    # Basic type validation
                    if expected_type == 'integer' and not isinstance(prop_value, int):
                        return False
                    elif expected_type == 'float' and not isinstance(prop_value, (int, float)):
                        return False
                    elif expected_type == 'string' and not isinstance(prop_value, str):
                        return False
                    elif expected_type == 'boolean' and not isinstance(prop_value, bool):
                        return False
                    elif expected_type == 'array' and not isinstance(prop_value, list):
                        return False
                    elif expected_type == 'object' and not isinstance(prop_value, dict):
                        return False
        
        return True


# Global component registry instance
component_registry = ComponentRegistry()


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
    
    def add_component(self, name: str, component_data: Dict[str, Any] = None, **kwargs):
        """Add a component to this entity"""
        if component_data is None:
            component_data = {}
        
        # Merge component_data with kwargs
        component_data.update(kwargs)
        
        # Use the component registry to create the component with proper defaults
        self.components[name] = component_registry.create_component(name, **component_data)
        self.updated_at = datetime.now()
    
    def add_component_from_template(self, name: str, **overrides):
        """Add a component using the registry template with optional overrides"""
        self.add_component(name, **overrides)
    
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
        for component_name, component_config in template.get('components', {}).items():
            if isinstance(component_config, dict):
                # If it's a dictionary, use it as override data
                entity.add_component(component_name, **component_config)
            else:
                # If it's a string or other type, treat it as a component name
                entity.add_component(component_name)
        
        return entity
    
    def load_templates(self, filepath: str):
        """Load entity templates from JSON file"""
        with open(filepath, 'r') as f:
            templates = json.load(f)
        
        for entity_type, template in templates.items():
            self.register_template(entity_type, template)


# Component management functions
def get_available_components() -> List[str]:
    """Get list of all available component names"""
    return component_registry.get_available_components()


def get_component_info(name: str) -> Dict[str, Any]:
    """Get detailed information about a component"""
    definition = component_registry.get_component_definition(name)
    if definition:
        return {
            'name': name,
            'description': definition.get('description', 'No description'),
            'properties': definition.get('properties', {}),
            'available': True
        }
    return {
        'name': name,
        'description': 'Unknown component',
        'properties': {},
        'available': False
    }


def create_component(name: str, **overrides) -> Dict[str, Any]:
    """Create a component instance with default values and overrides"""
    return component_registry.create_component(name, **overrides)


def load_custom_components(filepath: str):
    """Load custom component definitions from a JSON file"""
    component_registry.load_components_from_file(filepath)


def register_component(name: str, definition: Dict[str, Any]):
    """Register a new component definition"""
    component_registry.register_component(name, definition)


# Legacy ComponentTemplates class for backward compatibility
class ComponentTemplates:
    """Legacy component templates - now uses the registry system"""
    
    @staticmethod
    def get_movement(**overrides):
        return create_component('movement', **overrides)
    
    @staticmethod
    def get_health(**overrides):
        return create_component('health', **overrides)
    
    @staticmethod
    def get_cargo(**overrides):
        return create_component('cargo', **overrides)
    
    @staticmethod
    def get_combat(**overrides):
        return create_component('combat', **overrides)
    
    @staticmethod
    def get_mining(**overrides):
        return create_component('mining', **overrides)
    
    @staticmethod
    def get_trading(**overrides):
        return create_component('trading', **overrides)
    
    # Legacy static properties for backward compatibility
    @property
    def MOVEMENT(self):
        return create_component('movement')
    
    @property
    def HEALTH(self):
        return create_component('health')
    
    @property
    def CARGO(self):
        return create_component('cargo')
    
    @property
    def COMBAT(self):
        return create_component('combat')
    
    @property
    def MINING(self):
        return create_component('mining')
    
    @property
    def TRADING(self):
        return create_component('trading')


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
                'trading': {},  # Use default trading component
                'cargo': {}     # Use default cargo component
            }
        },
        'cargo_ship': {
            'properties': {
                'name': 'Cargo Ship',
                'size': 'medium',
                'crew': 5
            },
            'components': {
                'movement': {},  # Use default movement component
                'health': {},    # Use default health component
                'cargo': {}      # Use default cargo component
            }
        },
        'fighter': {
            'properties': {
                'name': 'Fighter',
                'size': 'small',
                'crew': 1
            },
            'components': {
                'movement': {},  # Use default movement component
                'health': {},    # Use default health component
                'combat': {}     # Use default combat component
            }
        },
        'mining_ship': {
            'properties': {
                'name': 'Mining Ship',
                'size': 'medium',
                'crew': 3
            },
            'components': {
                'movement': {},  # Use default movement component
                'health': {},    # Use default health component
                'cargo': {},     # Use default cargo component
                'mining': {}     # Use default mining component
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
    
    # Add a new component using the registry
    ship.add_component('communication', sensor_range=75.0, communication_range=150.0)
    print(f"Ship has communication: {ship.has_component('communication')}")
    print(f"Ship sensor range: {ship.get_component('communication').get('sensor_range', 0)}")
    
    # Add a custom component
    ship.add_component('stealth', stealth_rating=25, cloaking_active=False)
    print(f"Ship has stealth: {ship.has_component('stealth')}")
    
    # Show available components
    print(f"\nAvailable components: {get_available_components()}")
    
    # Show component info
    movement_info = get_component_info('movement')
    print(f"\nMovement component info:")
    print(f"  Description: {movement_info['description']}")
    print(f"  Properties: {list(movement_info['properties'].keys())}")
    
    # Serialize and deserialize
    ship_data = ship.to_dict()
    reconstructed_ship = Entity.from_dict(ship_data)
    print(f"\nReconstructed: {reconstructed_ship}")
    print(f"Reconstructed ship components: {list(reconstructed_ship.components.keys())}")
    
    # Demonstrate dynamic component creation
    print(f"\nDynamic component creation:")
    mining_component = create_component('mining', mining_rate=10.0, specialized_resources=['platinum'])
    print(f"Mining component: {mining_component}")
    
    # Add it to an entity
    ship.add_component('mining', **mining_component)
    print(f"Ship now has mining: {ship.has_component('mining')}")
    print(f"Ship mining rate: {ship.get_component('mining').get('mining_rate', 0)}")
