# JSON-Based Component System

The simplified Solar Factions system now supports configurable and extendable components through JSON files. This allows users to customize entity behavior without modifying the core code.

## Overview

Components are defined in JSON files and provide modular functionality to entities. Each component defines:
- **Description**: What the component does
- **Properties**: Configuration options with types, defaults, and descriptions

## Component Files

### Core Components
- `data/components/components.json` - Standard components (movement, health, cargo, etc.)
- `data/components/custom_components.json` - User-defined components

### Loading Components
Components are automatically loaded when the entity system starts:
1. Core components from `components.json`
2. Custom components from `custom_components.json`
3. Additional files can be loaded with `load_custom_components(filepath)`

## Available Components

### Movement Component
```json
{
  "movement": {
    "description": "Basic movement component for entities that can move",
    "properties": {
      "max_speed": {"type": "float", "default": 100.0, "description": "Maximum speed in units per second"},
      "acceleration": {"type": "float", "default": 10.0, "description": "Acceleration rate"},
      "velocity": {"type": "array", "default": [0.0, 0.0], "description": "Current velocity vector [x, y]"},
      "destination": {"type": "position", "default": null, "description": "Target destination coordinates"},
      "fuel": {"type": "float", "default": 100.0, "description": "Current fuel level"},
      "fuel_consumption": {"type": "float", "default": 1.0, "description": "Fuel consumption rate per unit distance"}
    }
  }
}
```

### Health Component
```json
{
  "health": {
    "description": "Health and damage system",
    "properties": {
      "max_health": {"type": "integer", "default": 100, "description": "Maximum health points"},
      "current_health": {"type": "integer", "default": 100, "description": "Current health points"},
      "shields": {"type": "integer", "default": 0, "description": "Shield points"},
      "max_shields": {"type": "integer", "default": 50, "description": "Maximum shield points"},
      "armor": {"type": "integer", "default": 0, "description": "Armor rating"},
      "shield_recharge_rate": {"type": "float", "default": 5.0, "description": "Shield recharge rate per second"}
    }
  }
}
```

### Other Components
- **cargo**: Storage and inventory management
- **combat**: Weapon systems and combat mechanics
- **mining**: Resource extraction capabilities
- **trading**: Economic and commerce systems
- **research**: Research and development
- **production**: Manufacturing capabilities
- **communication**: Sensors and communication systems
- **ai**: AI behavior and decision making
- **stealth**: Stealth and cloaking systems
- **diplomatic**: Faction relations and diplomacy
- **exploration**: Discovery and mapping systems

## Using Components

### In Python Code

```python
from entities.entity import Entity, get_available_components, create_component

# Create an entity and add components
ship = Entity('cargo_ship', (100, 200), name='Trader')

# Add component with defaults
ship.add_component('movement')

# Add component with custom values
ship.add_component('cargo', capacity=500, current_load=100)

# Add component with mixed defaults and overrides
ship.add_component('health', max_health=200, armor=25)

# Create component data separately
movement_data = create_component('movement', max_speed=150.0, fuel=75.0)
ship.add_component('movement', **movement_data)

# Check available components
print(f"Available: {get_available_components()}")
```

### In Entity Templates

```python
# Entity template using JSON-based components
template = {
    'properties': {
        'name': 'Advanced Fighter',
        'crew': 1
    },
    'components': {
        'movement': {'max_speed': 200.0, 'fuel': 150.0},
        'health': {'max_health': 80, 'shields': 100},
        'combat': {'weapon_damage': 25, 'weapon_type': 'plasma'}
    }
}
```

## Component Manager Utility

Use the `component_manager.py` utility to manage components:

```bash
# List all available components
python component_manager.py list

# Show detailed information about a component
python component_manager.py show movement

# Create a new component interactively
python component_manager.py create

# Validate a component file
python component_manager.py validate data/components/custom_components.json
```

## Creating Custom Components

### Method 1: Using the Component Manager
```bash
python component_manager.py create
```

### Method 2: Direct JSON Editing
Edit `data/components/custom_components.json`:

```json
{
  "shield_generator": {
    "description": "Advanced shield generation system",
    "properties": {
      "shield_capacity": {"type": "integer", "default": 1000, "description": "Maximum shield capacity"},
      "recharge_rate": {"type": "float", "default": 50.0, "description": "Shield recharge rate per second"},
      "energy_efficiency": {"type": "float", "default": 0.8, "description": "Energy efficiency ratio"},
      "overload_protection": {"type": "boolean", "default": true, "description": "Overload protection enabled"}
    }
  }
}
```

### Method 3: Programmatic Registration
```python
from entities.entity import register_component

# Define component
custom_component = {
    "description": "Custom navigation system",
    "properties": {
        "autopilot": {"type": "boolean", "default": false, "description": "Autopilot enabled"},
        "nav_accuracy": {"type": "float", "default": 0.95, "description": "Navigation accuracy"},
        "route_optimization": {"type": "boolean", "default": true, "description": "Route optimization enabled"}
    }
}

# Register it
register_component('navigation', custom_component)
```

## Property Types

Components support the following property types:

- **integer**: Whole numbers
- **float**: Decimal numbers  
- **string**: Text values
- **boolean**: True/false values
- **array**: Lists of values
- **object**: Nested dictionaries
- **position**: Special type for coordinates (treated as array)

## Integration with Map Generation

Components are automatically integrated with the map generation system. Entity templates in map generation templates can reference components:

```json
{
  "entities": [
    {
      "type": "advanced_fighter",
      "count": 5,
      "properties": {
        "pilot_skill": "ace"
      },
      "components": {
        "movement": {"max_speed": 250.0},
        "combat": {"weapon_damage": 30},
        "stealth": {"stealth_rating": 75}
      }
    }
  ]
}
```

## Benefits

1. **Flexibility**: Add new behaviors without code changes
2. **Modularity**: Mix and match components for different entity types
3. **Extensibility**: Users can create custom components
4. **Maintainability**: Component logic is separated from entity logic
5. **Configuration**: Easy to tweak values without recompiling
6. **Documentation**: Built-in descriptions and type information

## Backward Compatibility

The system maintains backward compatibility with the old `ComponentTemplates` class:

```python
# Old way (still works)
from entities.entity import ComponentTemplates
movement_data = ComponentTemplates.MOVEMENT

# New way (recommended)
from entities.entity import create_component
movement_data = create_component('movement')
```

This JSON-based component system provides the flexibility needed for complex game systems while maintaining simplicity and ease of use.
