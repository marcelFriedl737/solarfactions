# Solar Factions - Simplified System

A streamlined space map generation and visualization system that demonstrates how to create complex simulations with simple, maintainable code.

## Features

- **Simple Entity System**: Uses tuples for positions and dictionaries for properties
- **JSON-Based Components**: Configurable and extendable components through JSON files
- **Template-Based Generation**: Generate maps using predefined templates
- **Easy Data Persistence**: Save and load maps with JSON serialization
- **Interactive Visualization**: Real-time map viewer with pygame
- **Comprehensive Testing**: Full test coverage with integration tests
- **Self-Contained**: No dependencies on external code
- **Component Manager**: Utility for managing and creating custom components

## Quick Start

### Generate and Display a Map

```python
from simple.generator import SimpleMapGenerator
from simple.renderer import SimpleRenderer

# Generate a map
generator = SimpleMapGenerator()
entities = generator.generate_map('basic')

# Display it
renderer = SimpleRenderer()
renderer.run(entities)
```

### Command Line Interface

```bash
# Generate and display a basic map
python main.py

# Use a specific template
python main.py --template frontier

# Save a generated map
python main.py --template warzone --save my_battle

# Load and display a saved map
python main.py --load my_battle

# List available maps
python main.py --list

# Show detailed statistics
python main.py --stats --info
```

### Interactive Mode

```bash
# Start interactive mode
python main.py

# Available commands in interactive mode:
# generate [template] - Generate a new map
# save [name] - Save current map
# load [name] - Load a saved map
# list - List saved maps
# show - Show current map info
# render - Display current map
# templates - Show available templates
# quit - Exit
```

## Architecture

### Entity System
- `Entity`: Core entity class with position, properties, and components
- `EntityFactory`: Creates entities from templates
- Simple tuple-based positions `(x, y)` instead of complex coordinate objects

### Data Management
- `DataManager`: Handles saving/loading maps and templates
- JSON-based serialization for easy debugging and modification
- Organized file structure with separate folders for saves, templates, etc.

### Map Generation
- `SimpleMapGenerator`: Creates maps from templates
- Configurable templates define entity types, counts, and properties
- Reproducible generation with seed support

### Visualization
- `SimpleRenderer`: pygame-based map viewer
- Interactive controls for panning, zooming, and entity selection
- Real-time display of entity information

## Directory Structure

```
simple/
├── __init__.py           # Package initialization
├── main.py              # Main entry point
├── demo_visual.py       # Quick demonstration
├── entities/
│   ├── __init__.py      # Entity system exports
│   └── entity.py        # Core entity implementation
├── data_manager.py      # Data persistence
├── generator.py         # Map generation
├── renderer.py          # Visual display
├── component_manager.py # Component management utility
├── config/
│   ├── __init__.py      # Configuration exports
│   └── config.py        # System configuration
├── data/
│   ├── components/      # Component definitions
│   │   ├── components.json       # Core components
│   │   └── custom_components.json # Custom components
│   ├── templates/       # Map generation templates
│   ├── generated_maps/  # Auto-generated maps
│   ├── saved_maps/      # User-saved maps
│   └── backups/         # Backup files
├── tests/
│   ├── __init__.py      # Test package
│   ├── test_system.py   # Integration tests
│   └── test_entities.py # Unit tests
└── docs/
    └── README.md        # This file
```

## Available Templates

- **basic**: Standard solar system with planets and ships
- **frontier**: Mining-focused system with asteroids and industrial activity
- **warzone**: Military conflict zone with fighters and fortifications

## Controls (Visual Mode)

- **Mouse**: Click and drag to pan the view
- **Mouse Wheel**: Zoom in/out
- **Click on Entity**: Select and view details
- **G**: Toggle grid display
- **L**: Toggle entity labels
- **I**: Toggle information panel
- **ESC**: Exit

## Testing

Run the test suite to verify everything works:

```bash
python main.py --test
```

Or run specific tests:

```bash
python -m pytest tests/
```

## Dependencies

- **pygame**: For visualization (optional, only needed for rendering)
- **Python 3.6+**: Core language requirement

Install pygame if you want visual rendering:

```bash
pip install pygame
```

## Design Philosophy

This simplified system demonstrates several important principles:

1. **Simplicity**: Use basic data structures (tuples, dicts) instead of complex objects
2. **Modularity**: Each component has a single, clear responsibility
3. **Testability**: Easy to test with minimal setup
4. **Flexibility**: Template system allows easy customization
5. **Self-Containment**: No external dependencies beyond the package

The goal is to show that you can create powerful, flexible systems without overengineering. This approach makes the code easier to understand, maintain, and extend.

## Examples

### Custom Component Example

```python
from simple.entities.entity import Entity, create_component, register_component

# Create a custom component definition
shield_component = {
    "description": "Advanced shield system",
    "properties": {
        "shield_capacity": {"type": "integer", "default": 1000},
        "recharge_rate": {"type": "float", "default": 50.0},
        "active": {"type": "boolean", "default": true}
    }
}

# Register the component
register_component('advanced_shields', shield_component)

# Use it on an entity
ship = Entity('battleship', (400, 300), name='Defender')
ship.add_component('advanced_shields', shield_capacity=1500, recharge_rate=75.0)
```

### Component Management

```bash
# List all available components
python component_manager.py list

# Show component details
python component_manager.py show movement

# Create a new component interactively
python component_manager.py create

# Validate component files
python component_manager.py validate data/components/custom_components.json
```

### Creating Custom Entities

```python
from simple.entities.entity import Entity

# Create a custom entity
station = Entity('research_station', (400, 300))
station.set_property('research_focus', 'xenobiology')
station.set_property('staff_count', 50)

# Add components
station.add_component('research', {
    'projects': ['alien_flora', 'atmosphere_analysis'],
    'funding': 1000000
})

station.add_component('defense', {
    'shields': 'moderate',
    'weapons': 'minimal'
})
```

### Custom Map Generation

```python
from simple.generator import SimpleMapGenerator

generator = SimpleMapGenerator()

# Generate with specific parameters
entities = generator.generate_map('basic', seed=42)

# Save for later use
generator.data_manager.save_entities(entities, 'custom_map')
```

### Data Analysis

```python
from simple.data_manager import DataManager

dm = DataManager()
entities = dm.load_entities('my_map')

# Get statistics
stats = dm.export_statistics(entities)
print(f"Total entities: {stats['total_entities']}")
print(f"Entity types: {stats['entity_types']}")
```

This simplified system provides a solid foundation for space simulation games, educational tools, or procedural content generation systems.
