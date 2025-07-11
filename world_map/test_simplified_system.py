# test_simplified_system.py - Tests for the simplified system
"""
Simple integration tests for the simplified Solar Factions system.
Focuses on key workflows rather than exhaustive unit testing.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from entities.simple import Entity, EntityFactory, create_basic_templates
from data_manager import DataManager
from simple_generator import SimpleMapGenerator


def test_entity_creation():
    """Test that we can create and use entities"""
    print("Testing entity creation...")
    
    # Create a simple entity
    entity = Entity('test_ship', (100, 200), name='Test Ship', crew=5)
    
    # Test basic properties
    assert entity.type == 'test_ship'
    assert entity.position == (100, 200)
    assert entity.get_property('name') == 'Test Ship'
    assert entity.get_property('crew') == 5
    
    # Test components
    entity.add_component('movement', {'speed': 50, 'direction': 'north'})
    assert entity.has_component('movement')
    assert entity.get_component('movement')['speed'] == 50
    
    # Test serialization
    entity_data = entity.to_dict()
    recreated_entity = Entity.from_dict(entity_data)
    assert recreated_entity.type == entity.type
    assert recreated_entity.position == entity.position
    assert recreated_entity.has_component('movement')
    
    print("✓ Entity creation works!")


def test_entity_factory():
    """Test the entity factory system"""
    print("Testing entity factory...")
    
    # Create factory with templates
    factory = EntityFactory()
    templates = create_basic_templates()
    
    for entity_type, template in templates.items():
        factory.register_template(entity_type, template)
    
    # Create entities using factory
    ship = factory.create_entity('cargo_ship', (100, 200), name='My Ship')
    assert ship.type == 'cargo_ship'
    assert ship.get_property('name') == 'My Ship'
    assert ship.has_component('movement')
    assert ship.has_component('cargo')
    
    print("✓ Entity factory works!")


def test_data_management():
    """Test data loading and saving"""
    print("Testing data management...")
    
    # Create data manager
    dm = DataManager()
    
    # Create test entities
    factory = dm.get_entity_factory()
    entities = [
        factory.create_entity('star', (500, 400), name='Test Star'),
        factory.create_entity('planet', (300, 400), name='Test Planet'),
        factory.create_entity('cargo_ship', (100, 200), name='Test Ship')
    ]
    
    # Save and load
    dm.save_entities(entities, 'test_save')
    loaded_entities = dm.load_entities('test_save')
    
    assert len(loaded_entities) == 3
    assert loaded_entities[0].type == 'star'
    assert loaded_entities[1].type == 'planet'
    assert loaded_entities[2].type == 'cargo_ship'
    
    # Test statistics
    stats = dm.export_statistics(loaded_entities)
    assert stats['total_entities'] == 3
    assert 'star' in stats['entity_types']
    
    print("✓ Data management works!")


def test_map_generation():
    """Test map generation with different templates"""
    print("Testing map generation...")
    
    generator = SimpleMapGenerator()
    
    # Test different templates
    templates = ['basic', 'frontier', 'warzone']
    
    for template_name in templates:
        entities = generator.generate_map(template_name, seed=42)
        
        assert len(entities) > 0
        assert all(isinstance(e, Entity) for e in entities)
        assert all(e.position is not None for e in entities)
        
        # Check that we have different entity types
        entity_types = set(e.type for e in entities)
        assert len(entity_types) > 1
        
        # Get stats
        stats = generator.get_generation_stats(entities)
        assert stats['total_entities'] == len(entities)
        assert stats['seed_used'] == 42
    
    print("✓ Map generation works!")


def test_complete_workflow():
    """Test complete workflow from generation to save/load"""
    print("Testing complete workflow...")
    
    # Generate map
    generator = SimpleMapGenerator()
    entities = generator.generate_map('basic', seed=123)
    
    # Save map
    generator.data_manager.save_entities(entities, 'workflow_test')
    
    # Load map back
    loaded_entities = generator.data_manager.load_entities('workflow_test')
    
    # Verify integrity
    assert len(loaded_entities) == len(entities)
    
    # Check that all entities maintained their properties
    for original, loaded in zip(entities, loaded_entities):
        assert original.type == loaded.type
        assert original.position == loaded.position
        assert original.properties == loaded.properties
        assert original.components == loaded.components
    
    # Verify we can work with loaded entities
    for entity in loaded_entities:
        if entity.type == 'cargo_ship':
            assert entity.has_component('movement')
            assert entity.has_component('cargo')
        elif entity.type == 'star':
            assert entity.get_property('temperature') is not None
    
    print("✓ Complete workflow works!")


def test_template_system():
    """Test template loading and customization"""
    print("Testing template system...")
    
    dm = DataManager()
    
    # Load default templates
    basic_template = dm.load_template('basic')
    assert 'entities' in basic_template
    assert len(basic_template['entities']) > 0
    
    # Test custom template
    custom_template = {
        'name': 'Custom Test',
        'description': 'A test template',
        'entities': [
            {
                'type': 'star',
                'count': 1,
                'bounds': {'x': [400, 600], 'y': [300, 500]},
                'properties': {'name': 'Custom Star'}
            }
        ]
    }
    
    dm.save_template('custom_test', custom_template)
    loaded_template = dm.load_template('custom_test')
    
    assert loaded_template['name'] == 'Custom Test'
    assert len(loaded_template['entities']) == 1
    
    print("✓ Template system works!")


def run_all_tests():
    """Run all tests"""
    print("Running simplified system tests...\n")
    
    try:
        test_entity_creation()
        test_entity_factory()
        test_data_management()
        test_map_generation()
        test_complete_workflow()
        test_template_system()
        
        print("\n🎉 All tests passed!")
        print("The simplified system is working correctly!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
