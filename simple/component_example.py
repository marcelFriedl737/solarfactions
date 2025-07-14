#!/usr/bin/env python3
# component_example.py - Example of using the JSON-based component system
"""
Example demonstrating the new JSON-based component system.
Shows how to use predefined components and create custom ones.
"""

import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from entities.entity import (
    Entity, EntityFactory, 
    get_available_components, 
    get_component_info,
    create_component,
    register_component,
    create_basic_templates
)
from generator import SimpleMapGenerator
from data_manager import DataManager


def main():
    print("Solar Factions - JSON Component System Example")
    print("=" * 50)
    
    # 1. Show available components
    print("\n1. Available Components:")
    components = get_available_components()
    for comp in sorted(components):
        info = get_component_info(comp)
        print(f"   • {comp}: {info['description']}")
    
    # 2. Create entities with components
    print(f"\n2. Creating Entities with Components:")
    
    # Create a advanced fighter with custom component values
    fighter = Entity('advanced_fighter', (300, 400), name='Ace Squadron Leader')
    fighter.add_component('movement', max_speed=250.0, fuel=150.0)
    fighter.add_component('health', max_health=120, shields=80, armor=15)
    fighter.add_component('combat', weapon_damage=35, weapon_type='plasma_cannon')
    fighter.add_component('ai', intelligence_level=85, aggression_level=0.8)
    
    print(f"   Created: {fighter}")
    print(f"   Components: {list(fighter.components.keys())}")
    print(f"   Max Speed: {fighter.get_component('movement')['max_speed']}")
    print(f"   Weapon Type: {fighter.get_component('combat')['weapon_type']}")
    
    # Create a research vessel
    research_ship = Entity('research_vessel', (500, 300), name='Discovery')
    research_ship.add_component('movement', max_speed=80.0, fuel=200.0)
    research_ship.add_component('research', research_rate=5.0, research_focus='xenobiology')
    research_ship.add_component('communication', sensor_range=200.0, sensor_resolution='high')
    research_ship.add_component('exploration', exploration_range=300.0, survey_equipment=['advanced_scanner', 'spectrometer'])
    
    print(f"\n   Created: {research_ship}")
    print(f"   Components: {list(research_ship.components.keys())}")
    print(f"   Research Focus: {research_ship.get_component('research')['research_focus']}")
    print(f"   Sensor Range: {research_ship.get_component('communication')['sensor_range']}")
    
    # 3. Create custom components
    print(f"\n3. Creating Custom Components:")
    
    # Define a custom warp drive component
    warp_drive_def = {
        "description": "Faster-than-light travel system",
        "properties": {
            "warp_factor": {"type": "float", "default": 1.0, "description": "Warp speed multiplier"},
            "energy_consumption": {"type": "float", "default": 50.0, "description": "Energy per warp unit"},
            "max_distance": {"type": "float", "default": 1000.0, "description": "Maximum warp distance"},
            "cooldown_time": {"type": "float", "default": 30.0, "description": "Cooldown between warps"},
            "navigation_computer": {"type": "boolean", "default": True, "description": "Advanced navigation"}
        }
    }
    
    register_component('warp_drive', warp_drive_def)
    print(f"   Registered custom component: warp_drive")
    
    # Use the custom component
    explorer = Entity('deep_space_explorer', (600, 500), name='Voyager')
    explorer.add_component('warp_drive', warp_factor=3.5, max_distance=5000.0)
    explorer.add_component('exploration')
    
    print(f"   Added warp drive to: {explorer.get_property('name')}")
    print(f"   Warp Factor: {explorer.get_component('warp_drive')['warp_factor']}")
    print(f"   Max Distance: {explorer.get_component('warp_drive')['max_distance']}")
    
    # 4. Create entities using the factory
    print(f"\n4. Using Entity Factory:")
    
    factory = EntityFactory()
    templates = create_basic_templates()
    
    # Add custom template with our new component
    templates['warp_capable_ship'] = {
        'properties': {
            'name': 'Warp Ship',
            'crew': 20,
            'classification': 'explorer'
        },
        'components': {
            'movement': {'max_speed': 100.0},
            'health': {'max_health': 150},
            'warp_drive': {'warp_factor': 2.0},
            'exploration': {}
        }
    }
    
    for entity_type, template in templates.items():
        factory.register_template(entity_type, template)
    
    warp_ship = factory.create_entity('warp_capable_ship', (700, 600), name='Enterprise')
    print(f"   Created from template: {warp_ship}")
    print(f"   Components: {list(warp_ship.components.keys())}")
    
    # 5. Generate a map with the enhanced system
    print(f"\n5. Map Generation with Enhanced Components:")
    
    generator = SimpleMapGenerator()
    entities = generator.generate_map('basic', seed=456)
    
    print(f"   Generated {len(entities)} entities")
    
    # Show component usage statistics
    component_stats = {}
    for entity in entities:
        for comp_name in entity.components.keys():
            component_stats[comp_name] = component_stats.get(comp_name, 0) + 1
    
    if component_stats:
        print(f"   Component usage:")
        for comp_name, count in sorted(component_stats.items()):
            print(f"     {comp_name}: {count} entities")
    
    # 6. Save and load with custom components
    print(f"\n6. Data Persistence:")
    
    # Add our custom entities to the generated map
    all_entities = entities + [fighter, research_ship, explorer, warp_ship]
    
    dm = DataManager()
    dm.save_entities(all_entities, 'component_example')
    
    loaded_entities = dm.load_entities('component_example')
    print(f"   Saved and loaded {len(loaded_entities)} entities")
    
    # Verify custom components survived serialization
    custom_entities = [e for e in loaded_entities if e.has_component('warp_drive')]
    print(f"   Entities with warp_drive: {len(custom_entities)}")
    
    for entity in custom_entities:
        warp_data = entity.get_component('warp_drive')
        print(f"     {entity.get_property('name')}: Warp Factor {warp_data['warp_factor']}")
    
    print(f"\n✅ Component system example completed successfully!")
    print(f"   Total components available: {len(get_available_components())}")
    print(f"   Custom components created: 1 (warp_drive)")
    print(f"   Entities with components: {len([e for e in loaded_entities if e.components])}")


if __name__ == "__main__":
    main()
