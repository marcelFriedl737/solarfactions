# demo_visual.py - Quick visual demonstration of the simplified system
"""
Quick demonstration script that generates a map and shows it visually.
This shows how easy it is to create and visualize content with the simplified system.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from entities.simple import Entity
from data_manager import DataManager
from simple_generator import SimpleMapGenerator
from simple_renderer import SimpleRenderer

def main():
    print("Solar Factions - Visual Demonstration")
    print("=====================================")
    
    # Create generator and generate a map
    print("1. Generating a diverse map...")
    generator = SimpleMapGenerator()
    entities = generator.generate_map('basic', seed=999)
    
    print(f"   Generated {len(entities)} entities")
    
    # Show what we created
    entity_types = {}
    for entity in entities:
        entity_types[entity.type] = entity_types.get(entity.type, 0) + 1
    
    print("   Entity types:")
    for entity_type, count in entity_types.items():
        print(f"     - {entity_type}: {count}")
    
    # Add some interesting components to ships
    print("\n2. Adding components to ships...")
    for entity in entities:
        if entity.type == 'cargo_ship':
            entity.add_component('trade_mission', {
                'destination': 'Trading Station',
                'cargo_type': 'electronics',
                'value': 15000
            })
            print(f"   Added trade mission to {entity.get_property('name')}")
        
        elif entity.type == 'mining_ship':
            entity.add_component('mining_operation', {
                'target_asteroid': 'Asteroid Belt',
                'resource_type': 'platinum',
                'efficiency': 0.8
            })
            print(f"   Added mining operation to {entity.get_property('name')}")
    
    # Save the map
    print("\n3. Saving the map...")
    generator.data_manager.save_entities(entities, 'visual_demo')
    print("   Map saved as 'visual_demo'")
    
    # Show statistics
    print("\n4. Map statistics:")
    stats = generator.get_generation_stats(entities)
    print(f"   Total entities: {stats['total_entities']}")
    print(f"   Map bounds: X({stats['bounds']['x'][0]:.0f}, {stats['bounds']['x'][1]:.0f})")
    print(f"   Map bounds: Y({stats['bounds']['y'][0]:.0f}, {stats['bounds']['y'][1]:.0f})")
    print(f"   Seed used: {stats['seed_used']}")
    
    # Launch visual renderer
    print("\n5. Launching visual renderer...")
    print("   Controls:")
    print("     - Mouse: Click and drag to pan")
    print("     - Mouse wheel: Zoom in/out")
    print("     - Click on entities to select and see details")
    print("     - G: Toggle grid")
    print("     - L: Toggle labels")
    print("     - I: Toggle info panel")
    print("     - ESC: Exit")
    print("\n   Click on ships to see their components and missions!")
    
    try:
        renderer = SimpleRenderer(title="Solar Factions - Visual Demo")
        renderer.run(entities)
    except Exception as e:
        print(f"Could not start renderer: {e}")
        print("Make sure pygame is installed: pip install pygame")
        return 1
    
    print("\nDemo complete! The map has been saved as 'visual_demo'.")
    print("You can load it again with: python simple_main.py --load visual_demo")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
