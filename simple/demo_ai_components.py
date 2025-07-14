#!/usr/bin/env python3
"""
Demonstration of AI-Component Integration in Solar Factions
"""

from ai_system import AISystem
from entities.entity import Entity, create_component
from game_manager import GameManager
import time

def demo_ai_component_integration():
    """Demonstrate AI-Component integration features"""
    
    print("🚀 Solar Factions AI-Component Integration Demo")
    print("=" * 60)
    
    # Create game manager
    game_manager = GameManager()
    
    print("\n1. Creating entities with AI components...")
    
    # Create entities with specific AI components
    entities = []
    
    # Aggressive fighter with hunt behavior
    fighter = Entity('fighter', (100, 100), name='Hunter Alpha')
    ai_component = create_component('ai',
                                  ai_type='aggressive',
                                  current_goal='eliminate_pirates',
                                  aggression_level=0.9,
                                  intelligence_level=85)
    fighter.add_component('ai', **ai_component)
    entities.append(fighter)
    
    # Merchant with defensive behavior
    merchant = Entity('cargo_ship', (200, 200), name='Trade Vessel')
    ai_component = create_component('ai',
                                  ai_type='merchant',
                                  current_goal='complete_trade_route',
                                  aggression_level=0.1,
                                  intelligence_level=70)
    merchant.add_component('ai', **ai_component)
    entities.append(merchant)
    
    # Station with defensive AI
    station = Entity('space_station', (300, 300), name='Frontier Base')
    ai_component = create_component('ai',
                                  ai_type='defensive',
                                  current_goal='protect_sector',
                                  aggression_level=0.7,
                                  intelligence_level=90)
    station.add_component('ai', **ai_component)
    entities.append(station)
    
    # Pirate without AI component (will be auto-assigned)
    pirate = Entity('fighter', (400, 400), name='Rogue Fighter')
    entities.append(pirate)
    
    print(f"✓ Created {len(entities)} entities")
    for entity in entities:
        ai_comp = entity.get_component('ai')
        if ai_comp:
            print(f"  - {entity.properties.get('name', entity.type)}: {ai_comp['ai_type']} AI")
        else:
            print(f"  - {entity.properties.get('name', entity.type)}: No AI component")
    
    print("\n2. Setting up AI system...")
    
    # Set up AI system with entities
    game_manager.entities = entities
    game_manager._assign_behaviors_to_entities()
    
    print("✓ AI system configured")
    
    print("\n3. Demonstrating auto-assignment...")
    
    # Show AI states
    for entity in entities:
        ai_state = game_manager.ai_system.get_ai_state(entity.id)
        if ai_state:
            print(f"  - {entity.properties.get('name', entity.type)}: {ai_state.behavior_name} (Energy: {ai_state.energy:.1f})")
        else:
            print(f"  - {entity.properties.get('name', entity.type)}: No AI assigned")
    
    print("\n4. Running simulation to show component synchronization...")
    
    # Start game loop
    game_manager.start_game_loop()
    
    print("✓ Game loop started")
    
    # Run for a few seconds
    simulation_time = 3.0
    start_time = time.time()
    
    while time.time() - start_time < simulation_time:
        time.sleep(0.1)
        
        # Check AI states periodically
        if int((time.time() - start_time) * 10) % 10 == 0:
            print(f"\n--- At {time.time() - start_time:.1f}s ---")
            for entity in entities:
                ai_state = game_manager.ai_system.get_ai_state(entity.id)
                ai_comp = entity.get_component('ai')
                if ai_state and ai_comp:
                    memory_keys = len(ai_comp.get('memory', {}))
                    print(f"  {entity.properties.get('name', entity.type)}: "
                          f"{ai_state.behavior_name} | Energy: {ai_state.energy:.1f} | "
                          f"Memory: {memory_keys} items")
    
    print("\n5. Demonstrating component persistence...")
    
    # Show that AI data is persisted in components
    for entity in entities:
        ai_comp = entity.get_component('ai')
        if ai_comp:
            memory = ai_comp.get('memory', {})
            print(f"  {entity.properties.get('name', entity.type)}: "
                  f"Goal: {ai_comp.get('current_goal', 'None')} | "
                  f"Memory items: {len(memory)}")
    
    print("\n6. Testing dynamic AI modification...")
    
    # Change AI behavior through component
    print("  Changing Hunter Alpha to defensive mode...")
    fighter_ai = fighter.get_component('ai')
    fighter_ai['ai_type'] = 'defensive'
    fighter_ai['current_goal'] = 'defend_area'
    fighter_ai['aggression_level'] = 0.4
    
    # Let it update
    time.sleep(1)
    
    ai_state = game_manager.ai_system.get_ai_state(fighter.id)
    print(f"  Hunter Alpha behavior: {ai_state.behavior_name if ai_state else 'Unknown'}")
    
    # Stop game loop
    game_manager.stop_game_loop()
    print("✓ Game loop stopped")
    
    print("\n7. Final component state...")
    
    # Show final state of all AI components
    for entity in entities:
        ai_comp = entity.get_component('ai')
        if ai_comp:
            print(f"  {entity.properties.get('name', entity.type)}:")
            print(f"    Type: {ai_comp['ai_type']}")
            print(f"    Goal: {ai_comp.get('current_goal', 'None')}")
            print(f"    Aggression: {ai_comp['aggression_level']:.1f}")
            print(f"    Intelligence: {ai_comp['intelligence_level']}")
            print(f"    Memory Items: {len(ai_comp.get('memory', {}))}")
    
    print(f"\n🎉 AI-Component Integration Demo Complete!")
    print("\nKey Features Demonstrated:")
    print("  ✓ AI components define persistent AI behavior")
    print("  ✓ Auto-assignment of AI from component data")
    print("  ✓ Real-time synchronization between AI state and components")
    print("  ✓ Component-based AI configuration (aggression, intelligence)")
    print("  ✓ Memory persistence in components")
    print("  ✓ Dynamic AI modification through components")
    print("  ✓ Seamless integration with existing game systems")

if __name__ == "__main__":
    demo_ai_component_integration()
