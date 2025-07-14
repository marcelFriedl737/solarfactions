#!/usr/bin/env python3
# game_demo.py - Demonstration of the new game systems
"""
Demo script showing the new tick-based game loop, movement system, and AI system.
"""

import sys
import time
import argparse
from game_manager import GameManager


def run_interactive_demo():
    """Run interactive demo with visual renderer"""
    print("=== Solar Factions Interactive Demo ===")
    print("This demo shows the new game systems in action:")
    print("- Tick-based game loop with time controls")
    print("- JSON-configurable movement behaviors")
    print("- JSON-configurable AI behaviors")
    print("- Real-time entity interactions")
    print()
    
    # Create game manager
    game_manager = GameManager()
    
    # Generate a demo map
    print("Generating demo map...")
    if not game_manager.generate_map("frontier", seed=42):
        print("Failed to generate map")
        return
    
    # Run interactive mode
    print("Starting interactive demo...")
    print("Use controls shown in the window to interact with the simulation")
    
    game_manager.run_interactive()


def run_headless_demo():
    """Run headless demo for testing"""
    print("=== Solar Factions Headless Demo ===")
    print("Running simulation without graphics...")
    
    # Create game manager
    game_manager = GameManager()
    
    # Generate a demo map
    print("Generating demo map...")
    if not game_manager.generate_map("warzone", seed=123):
        print("Failed to generate map")
        return
    
    # Print initial state
    print("\nInitial state:")
    game_manager.print_statistics()
    
    # Run simulation
    print(f"\nRunning simulation for 15 seconds...")
    game_manager.run_headless(15.0)
    
    # Print final state
    print("\nFinal state:")
    game_manager.print_statistics()


def run_system_showcase():
    """Showcase individual systems"""
    print("=== System Showcase ===")
    
    # Create game manager
    game_manager = GameManager()
    
    # Generate a basic map
    print("Generating basic map...")
    if not game_manager.generate_map("basic", seed=456):
        print("Failed to generate map")
        return
    
    # Start game loop
    game_manager.start_game_loop()
    
    try:
        # Run at different speeds
        speeds = [0.5, 1.0, 2.0, 4.0, 1.0]
        for speed in speeds:
            print(f"\nSetting speed to {speed}x...")
            game_manager.set_game_speed(speed)
            time.sleep(3)
            
            # Show entity info
            entities = game_manager.list_entities()
            print(f"Active entities: {len(entities)}")
            
            # Show a few entity details
            for i, entity_info in enumerate(entities[:3]):
                detailed_info = game_manager.get_entity_info(entity_info['id'])
                print(f"  Entity {i+1}: {detailed_info['type']} at {detailed_info['position']}")
                if 'ai' in detailed_info:
                    print(f"    AI: {detailed_info['ai']['behavior']} (Energy: {detailed_info['ai']['energy']:.1f})")
                if 'movement' in detailed_info:
                    print(f"    Movement: Speed {detailed_info['movement']['velocity']}")
        
        # Test pause/resume
        print("\nTesting pause/resume...")
        game_manager.pause_game()
        time.sleep(2)
        
        print("Stepping through 3 ticks...")
        for i in range(3):
            game_manager.step_game()
            time.sleep(0.5)
        
        game_manager.resume_game()
        time.sleep(2)
        
        print("Showcase complete!")
        
    except KeyboardInterrupt:
        print("\nShowcase interrupted")
    
    finally:
        game_manager.stop_game_loop()


def run_behavior_demo():
    """Demonstrate behavior configuration"""
    print("=== Behavior Configuration Demo ===")
    
    # Create game manager
    game_manager = GameManager()
    
    # Generate a map
    print("Generating map for behavior demo...")
    if not game_manager.generate_map("frontier", seed=789):
        print("Failed to generate map")
        return
    
    # Start game loop
    game_manager.start_game_loop()
    
    try:
        # Show initial behaviors
        print("\nInitial behavior assignments:")
        entities = game_manager.list_entities()
        for entity_info in entities:
            detailed_info = game_manager.get_entity_info(entity_info['id'])
            entity_type = detailed_info['type']
            ai_behavior = detailed_info.get('ai', {}).get('behavior', 'none')
            print(f"  {entity_type}: {ai_behavior}")
        
        # Run simulation for a bit
        print("\nRunning initial simulation...")
        time.sleep(5)
        
        # Show behavior changes
        print("\nForcing behavior changes...")
        
        # Find different types of entities
        fighters = [e for e in entities if 'fighter' in e['type']]
        cargo_ships = [e for e in entities if 'cargo' in e['type']]
        
        if fighters:
            fighter_id = fighters[0]['id']
            print(f"Changing fighter to patrol behavior...")
            game_manager.ai_system.set_behavior(fighter_id, 'sector_patrol')
        
        if cargo_ships:
            cargo_id = cargo_ships[0]['id']
            print(f"Changing cargo ship to flee behavior...")
            game_manager.ai_system.set_behavior(cargo_id, 'merchant_escape')
        
        # Run more simulation
        print("\nRunning simulation with new behaviors...")
        time.sleep(5)
        
        # Show final state
        print("\nFinal behavior state:")
        for entity_info in entities:
            detailed_info = game_manager.get_entity_info(entity_info['id'])
            entity_type = detailed_info['type']
            ai_behavior = detailed_info.get('ai', {}).get('behavior', 'none')
            ai_energy = detailed_info.get('ai', {}).get('energy', 0)
            print(f"  {entity_type}: {ai_behavior} (Energy: {ai_energy:.1f})")
        
        print("Behavior demo complete!")
        
    except KeyboardInterrupt:
        print("\nBehavior demo interrupted")
    
    finally:
        game_manager.stop_game_loop()


def main():
    """Main demo runner"""
    parser = argparse.ArgumentParser(
        description="Solar Factions Game System Demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Demo modes:
  interactive  - Visual demo with renderer and controls
  headless     - Non-visual simulation test
  showcase     - Demonstrate system features
  behavior     - Show behavior configuration
        """
    )
    
    parser.add_argument(
        'mode', 
        choices=['interactive', 'headless', 'showcase', 'behavior'],
        default='interactive',
        nargs='?',
        help='Demo mode to run (default: interactive)'
    )
    
    args = parser.parse_args()
    
    # Check dependencies
    try:
        import pygame
    except ImportError:
        if args.mode == 'interactive':
            print("Error: pygame is required for interactive mode")
            print("Install with: pip install pygame")
            sys.exit(1)
    
    # Run selected demo
    if args.mode == 'interactive':
        run_interactive_demo()
    elif args.mode == 'headless':
        run_headless_demo()
    elif args.mode == 'showcase':
        run_system_showcase()
    elif args.mode == 'behavior':
        run_behavior_demo()


if __name__ == "__main__":
    main()
