# simple_main.py - Simplified Solar Factions Entry Point
"""
Simplified entry point for Solar Factions that demonstrates the reduced complexity approach.
Shows how easy it is to generate, save, and work with maps using the simplified system.
"""

import sys
import argparse
import os
from typing import List

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from entities.simple import Entity
from data_manager import DataManager
from simple_generator import SimpleMapGenerator
from renderer import MapRenderer  # Use existing renderer


def main():
    """Main entry point with simplified command line interface"""
    parser = argparse.ArgumentParser(
        description='Solar Factions - Simplified Space Map Generator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python simple_main.py                          # Generate and show basic map
  python simple_main.py --template frontier     # Use frontier template
  python simple_main.py --save my_map          # Save generated map
  python simple_main.py --load my_map          # Load and display saved map
  python simple_main.py --list                 # List available maps
  python simple_main.py --seed 42 --save test  # Reproducible generation
        """
    )
    
    # Generation options
    parser.add_argument('--template', '-t', default='basic', 
                       help='Template to use (basic, frontier, warzone)')
    parser.add_argument('--seed', '-s', type=int, default=None,
                       help='Random seed for reproducible generation')
    
    # File operations
    parser.add_argument('--save', help='Save generated map with this name')
    parser.add_argument('--load', help='Load and display saved map')
    parser.add_argument('--list', action='store_true', help='List available saved maps')
    
    # Display options
    parser.add_argument('--no-render', action='store_true', help='Skip visual rendering')
    parser.add_argument('--stats', action='store_true', help='Show detailed statistics')
    parser.add_argument('--info', action='store_true', help='Show entity details')
    
    # System options
    parser.add_argument('--test', action='store_true', help='Run system tests')
    
    args = parser.parse_args()
    
    # Initialize system
    generator = SimpleMapGenerator()
    entities = None
    
    try:
        # Handle different commands
        if args.test:
            run_system_tests()
            return
        
        if args.list:
            list_saved_maps(generator.data_manager)
            return
        
        if args.load:
            entities = load_map(generator.data_manager, args.load)
        else:
            entities = generate_map(generator, args.template, args.seed)
        
        # Show information
        print_map_info(entities, generator, args.stats, args.info)
        
        # Save if requested
        if args.save:
            save_map(generator.data_manager, entities, args.save)
        
        # Render if not disabled
        if not args.no_render and entities:
            render_map(entities)
    
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


def generate_map(generator: SimpleMapGenerator, template: str, seed: int) -> List[Entity]:
    """Generate a new map"""
    print(f"Generating map using template: {template}")
    if seed is not None:
        print(f"Using seed: {seed}")
    
    entities = generator.generate_map(template, seed)
    print(f"Generated {len(entities)} entities")
    
    return entities


def load_map(data_manager: DataManager, filename: str) -> List[Entity]:
    """Load a saved map"""
    print(f"Loading map: {filename}")
    
    try:
        entities = data_manager.load_entities(filename)
        print(f"Loaded {len(entities)} entities")
        return entities
    except FileNotFoundError:
        print(f"Map file not found: {filename}")
        print("Available maps:")
        for map_name in data_manager.list_saved_maps():
            print(f"  - {map_name}")
        raise


def save_map(data_manager: DataManager, entities: List[Entity], filename: str):
    """Save a map"""
    print(f"Saving map as: {filename}")
    data_manager.save_entities(entities, filename)
    print(f"Map saved successfully")


def list_saved_maps(data_manager: DataManager):
    """List all saved maps"""
    maps = data_manager.list_saved_maps()
    
    if not maps:
        print("No saved maps found")
        return
    
    print("Available saved maps:")
    for map_name in maps:
        print(f"  - {map_name}")


def print_map_info(entities: List[Entity], generator: SimpleMapGenerator, 
                  show_stats: bool, show_details: bool):
    """Print information about the map"""
    if not entities:
        print("No entities to display")
        return
    
    # Basic info
    print(f"\nMap contains {len(entities)} entities")
    
    # Entity type summary
    entity_types = {}
    for entity in entities:
        entity_types[entity.type] = entity_types.get(entity.type, 0) + 1
    
    print("Entity types:")
    for entity_type, count in entity_types.items():
        print(f"  - {entity_type}: {count}")
    
    # Detailed statistics
    if show_stats:
        stats = generator.get_generation_stats(entities)
        print(f"\nDetailed Statistics:")
        print(f"  Average position: ({stats['average_position'][0]:.1f}, {stats['average_position'][1]:.1f})")
        print(f"  Map bounds: X({stats['bounds']['x'][0]:.1f}, {stats['bounds']['x'][1]:.1f}), Y({stats['bounds']['y'][0]:.1f}, {stats['bounds']['y'][1]:.1f})")
        if stats['seed_used']:
            print(f"  Seed used: {stats['seed_used']}")
    
    # Entity details
    if show_details:
        print(f"\nEntity Details:")
        for entity in entities:
            print(f"  {entity}")
            if entity.components:
                print(f"    Components: {list(entity.components.keys())}")


def render_map(entities: List[Entity]):
    """Render the map using the existing renderer"""
    print("\nOpening map renderer...")
    print("Controls:")
    print("  - Mouse: Click and drag to pan")
    print("  - Mouse wheel: Zoom in/out")
    print("  - ESC: Exit")
    print("  - Click on entities to see details")
    
    try:
        renderer = MapRenderer()
        renderer.run(entities)
    except Exception as e:
        print(f"Could not start renderer: {e}")
        print("Make sure pygame is installed: pip install pygame")


def run_system_tests():
    """Run simplified system tests"""
    print("Running simplified system tests...")
    
    try:
        # Import and run tests
        from test_simplified_system import run_all_tests
        success = run_all_tests()
        
        if success:
            print("\n✅ All tests passed - system is working correctly!")
        else:
            print("\n❌ Some tests failed")
            return 1
    
    except ImportError as e:
        print(f"Could not import tests: {e}")
        return 1
    
    return 0


def interactive_mode():
    """Interactive mode for exploring the system"""
    print("Solar Factions - Interactive Mode")
    print("Type 'help' for commands or 'quit' to exit")
    
    generator = SimpleMapGenerator()
    current_entities = None
    
    while True:
        try:
            command = input("\n> ").strip().lower()
            
            if command in ['quit', 'exit', 'q']:
                break
            
            elif command == 'help':
                print("Available commands:")
                print("  generate [template] - Generate a new map")
                print("  save [name] - Save current map")
                print("  load [name] - Load a saved map")
                print("  list - List saved maps")
                print("  show - Show current map info")
                print("  render - Display current map")
                print("  templates - Show available templates")
                print("  quit - Exit interactive mode")
            
            elif command.startswith('generate'):
                parts = command.split()
                template = parts[1] if len(parts) > 1 else 'basic'
                current_entities = generator.generate_map(template)
                print(f"Generated {len(current_entities)} entities using {template} template")
            
            elif command.startswith('save'):
                if not current_entities:
                    print("No map to save. Generate a map first.")
                    continue
                
                parts = command.split()
                if len(parts) < 2:
                    print("Usage: save [name]")
                    continue
                
                name = parts[1]
                generator.data_manager.save_entities(current_entities, name)
                print(f"Map saved as {name}")
            
            elif command.startswith('load'):
                parts = command.split()
                if len(parts) < 2:
                    print("Usage: load [name]")
                    continue
                
                name = parts[1]
                try:
                    current_entities = generator.data_manager.load_entities(name)
                    print(f"Loaded {len(current_entities)} entities from {name}")
                except FileNotFoundError:
                    print(f"Map {name} not found")
            
            elif command == 'list':
                list_saved_maps(generator.data_manager)
            
            elif command == 'show':
                if current_entities:
                    print_map_info(current_entities, generator, True, False)
                else:
                    print("No map loaded. Generate or load a map first.")
            
            elif command == 'render':
                if current_entities:
                    render_map(current_entities)
                else:
                    print("No map loaded. Generate or load a map first.")
            
            elif command == 'templates':
                print("Available templates: basic, frontier, warzone")
            
            else:
                print(f"Unknown command: {command}")
                print("Type 'help' for available commands")
        
        except KeyboardInterrupt:
            print("\nUse 'quit' to exit")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        # No arguments - run interactive mode
        interactive_mode()
    else:
        # Command line arguments provided
        sys.exit(main())
