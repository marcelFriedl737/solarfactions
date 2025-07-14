#!/usr/bin/env python3
"""
Test script to verify AI-Component integration
"""

from ai_system import AISystem
from entities.entity import Entity, create_component
import json

def test_ai_component_integration():
    """Test AI system integration with components"""
    print("🧠 Testing AI-Component Integration")
    print("=" * 50)
    
    # Create AI system
    ai_system = AISystem()
    
    # Create default configs
    import os
    os.makedirs('test_data/behaviors', exist_ok=True)
    ai_system.create_default_config('test_data/behaviors/ai.json')
    ai_system.load_config('test_data/behaviors/ai.json')
    
    # Create test entities with AI components
    print("\n1. Creating entities with AI components...")
    
    # Fighter with aggressive AI
    fighter = Entity('fighter', (100, 100), name='Test Fighter')
    ai_component = create_component('ai', 
                                  ai_type='aggressive',
                                  current_goal='hunt_targets',
                                  aggression_level=0.8,
                                  intelligence_level=70)
    fighter.add_component('ai', **ai_component)
    print(f"✓ Created fighter with AI component: {fighter.get_component('ai')}")
    
    # Cargo ship with defensive AI
    cargo_ship = Entity('cargo_ship', (200, 200), name='Test Cargo')
    ai_component = create_component('ai',
                                  ai_type='merchant',
                                  current_goal='trade_route',
                                  aggression_level=0.2,
                                  intelligence_level=60)
    cargo_ship.add_component('ai', **ai_component)
    print(f"✓ Created cargo ship with AI component: {cargo_ship.get_component('ai')}")
    
    # Station with defensive AI
    station = Entity('space_station', (300, 300), name='Test Station')
    ai_component = create_component('ai',
                                  ai_type='defensive',
                                  current_goal='defend_area',
                                  aggression_level=0.6,
                                  intelligence_level=80)
    station.add_component('ai', **ai_component)
    print(f"✓ Created station with AI component: {station.get_component('ai')}")
    
    entities = [fighter, cargo_ship, station]
    
    print("\n2. Testing auto-assignment from components...")
    
    # Test auto-assignment
    ai_system.auto_assign_ai_from_components(entities)
    
    # Check if AI was assigned
    for entity in entities:
        ai_state = ai_system.get_ai_state(entity.id)
        if ai_state:
            print(f"✓ AI auto-assigned to {entity.type}: behavior={ai_state.behavior_name}, energy={ai_state.energy}")
        else:
            print(f"✗ No AI assigned to {entity.type}")
    
    print("\n3. Testing AI system update with component sync...")
    
    # Run a few update cycles
    for i in range(5):
        ai_system.update(entities, 0.1)
        
        # Check component synchronization
        for entity in entities:
            ai_state = ai_system.get_ai_state(entity.id)
            ai_component = entity.get_component('ai')
            
            if ai_state and ai_component:
                # Check if memory is synced
                component_memory = ai_component.get('memory', {})
                if component_memory:
                    print(f"✓ {entity.type} memory synced: {len(component_memory)} keys")
                
                # Check if current goal is synced
                if ai_component.get('current_goal') == ai_state.memory.current_goal:
                    print(f"✓ {entity.type} goal synced: {ai_state.memory.current_goal}")
    
    print("\n4. Testing direct AI assignment with component creation...")
    
    # Create entity without AI component
    mining_ship = Entity('mining_ship', (400, 400), name='Test Miner')
    
    # Assign AI directly (should create component)
    ai_system.assign_ai_to_entity(mining_ship, 'resource_hunter', 
                                aggression_level=0.3, 
                                intelligence_level=65)
    
    # Check if component was created
    ai_component = mining_ship.get_component('ai')
    if ai_component:
        print(f"✓ AI component created: {ai_component}")
    else:
        print("✗ AI component not created")
    
    print("\n5. Testing component-based behavior modification...")
    
    # Modify aggression level and see if it affects behavior
    original_aggression = fighter.get_component('ai')['aggression_level']
    fighter.get_component('ai')['aggression_level'] = 0.9  # Very aggressive
    
    # Get initial alertness
    fighter_ai = ai_system.get_ai_state(fighter.id)
    initial_alertness = fighter_ai.alertness
    
    # Update - should increase alertness due to high aggression
    ai_system.update([fighter], 0.1)
    
    final_alertness = fighter_ai.alertness
    if final_alertness > initial_alertness:
        print(f"✓ High aggression increased alertness: {initial_alertness} → {final_alertness}")
    else:
        print(f"- Alertness unchanged: {initial_alertness} → {final_alertness}")
    
    print("\n6. Testing component persistence...")
    
    # Simulate entity reload by recreating and checking component data
    saved_memory = fighter.get_component('ai')['memory']
    print(f"✓ Memory saved: {len(saved_memory)} keys")
    
    # Create new entity with saved component data
    new_fighter = Entity('fighter', (100, 100), name='Reloaded Fighter')
    new_fighter.add_component('ai', **fighter.get_component('ai'))
    
    # Load AI from component
    ai_state = ai_system._load_ai_from_component(new_fighter)
    if ai_state:
        print(f"✓ AI loaded from component: behavior={ai_state.behavior_name}")
        if ai_state.memory.blackboard == saved_memory.get('blackboard', {}):
            print("✓ Memory preserved across reload")
    
    print("\n🎉 AI-Component Integration Test Complete!")
    
    # Cleanup
    import shutil
    shutil.rmtree('test_data', ignore_errors=True)

if __name__ == "__main__":
    test_ai_component_integration()
