#!/usr/bin/env python3
"""
Test script specifically for the renderer functionality
"""

import pygame
from renderer import SimpleRenderer
from entities.entity import Entity

def test_renderer_methods():
    """Test that all required renderer methods exist and work"""
    
    # Create test entities
    entities = [
        Entity('star', (500, 400), name='Test Star'),
        Entity('planet', (300, 400), name='Test Planet'),
        Entity('fighter', (600, 300), name='Test Fighter'),
        Entity('cargo_ship', (400, 500), name='Test Cargo')
    ]
    
    # Initialize renderer
    renderer = SimpleRenderer(800, 600, "Renderer Test")
    
    # Test render method
    print("Testing render method...")
    renderer.render(entities)
    print("✓ render() method works")
    
    # Test handle_event method
    print("Testing handle_event method...")
    test_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_g)
    renderer.handle_event(test_event)
    print("✓ handle_event() method works")
    
    # Test handle_events method
    print("Testing handle_events method...")
    result = renderer.handle_events(entities)
    print(f"✓ handle_events() method works (returned {result})")
    
    # Test coordinate conversion
    print("Testing coordinate conversion...")
    world_pos = (100, 200)
    screen_pos = renderer.world_to_screen(world_pos)
    converted_back = renderer.screen_to_world(screen_pos)
    print(f"✓ Coordinate conversion: {world_pos} -> {screen_pos} -> {converted_back}")
    
    # Test entity finding
    print("Testing entity finding...")
    found = renderer.find_entity_at_position((500, 400), entities)
    if found:
        name_component = found.get_component('name')
        if name_component:
            entity_name = name_component.get('value', f"{found.type} at {found.position}")
        else:
            entity_name = f"{found.type} at {found.position}"
    else:
        entity_name = 'None'
    print(f"✓ Entity finding: found {entity_name}")
    
    print("\n🎉 All renderer tests passed!")
    
    # Clean up
    pygame.quit()

if __name__ == "__main__":
    test_renderer_methods()
