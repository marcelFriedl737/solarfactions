# test_entities.py - Tests for simplified entity system
"""
Unit tests for the simplified entity system.
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from entities.entity import Entity, EntityFactory, create_basic_templates


class TestSimpleEntity(unittest.TestCase):
    def test_entity_creation(self):
        """Test basic entity creation"""
        entity = Entity('test_ship', (100, 200), name='Test Ship', crew=5)
        
        self.assertEqual(entity.type, 'test_ship')
        self.assertEqual(entity.position, (100, 200))
        self.assertEqual(entity.get_property('name'), 'Test Ship')
        self.assertEqual(entity.get_property('crew'), 5)
        self.assertIsNotNone(entity.id)
    
    def test_entity_properties(self):
        """Test entity property management"""
        entity = Entity('ship', (0, 0))
        
        # Test setting properties
        entity.set_property('fuel', 100)
        self.assertEqual(entity.get_property('fuel'), 100)
        
        # Test default values
        self.assertEqual(entity.get_property('unknown', 'default'), 'default')
        
        # Test property update
        entity.set_property('fuel', 80)
        self.assertEqual(entity.get_property('fuel'), 80)
    
    def test_entity_components(self):
        """Test entity component system"""
        entity = Entity('ship', (0, 0))
        
        # Test adding components
        entity.add_component('movement', {'speed': 50, 'direction': 'north'})
        self.assertTrue(entity.has_component('movement'))
        
        # Test getting components
        movement = entity.get_component('movement')
        self.assertEqual(movement['speed'], 50)
        self.assertEqual(movement['direction'], 'north')
        
        # Test removing components
        entity.remove_component('movement')
        self.assertFalse(entity.has_component('movement'))
    
    def test_entity_serialization(self):
        """Test entity serialization and deserialization"""
        entity = Entity('cargo_ship', (100, 200), name='Trader', crew=3)
        entity.add_component('cargo', {'capacity': 100, 'current': 50})
        
        # Serialize
        data = entity.to_dict()
        self.assertIn('id', data)
        self.assertIn('type', data)
        self.assertIn('position', data)
        self.assertIn('properties', data)
        self.assertIn('components', data)
        
        # Deserialize
        restored_entity = Entity.from_dict(data)
        self.assertEqual(restored_entity.type, entity.type)
        self.assertEqual(restored_entity.position, entity.position)
        self.assertEqual(restored_entity.get_property('name'), entity.get_property('name'))
        self.assertTrue(restored_entity.has_component('cargo'))
        self.assertEqual(restored_entity.get_component('cargo'), entity.get_component('cargo'))
    
    def test_entity_string_representation(self):
        """Test entity string representation"""
        entity = Entity('star', (500, 400), name='Sol', temperature=5778)
        str_repr = str(entity)
        self.assertIn('Sol', str_repr)
        self.assertIn('star', str_repr)
        self.assertIn('500', str_repr)
        self.assertIn('400', str_repr)


class TestEntityFactory(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.factory = EntityFactory()
        templates = create_basic_templates()
        for entity_type, template in templates.items():
            self.factory.register_template(entity_type, template)
    
    def test_factory_creation(self):
        """Test factory entity creation"""
        ship = self.factory.create_entity('cargo_ship', (100, 200), name='My Ship')
        
        self.assertEqual(ship.type, 'cargo_ship')
        self.assertEqual(ship.position, (100, 200))
        self.assertEqual(ship.get_property('name'), 'My Ship')
        self.assertTrue(ship.has_component('movement'))
        self.assertTrue(ship.has_component('cargo'))
    
    def test_factory_templates(self):
        """Test template system"""
        # Test star creation
        star = self.factory.create_entity('star', (500, 400), name='Test Star')
        self.assertEqual(star.type, 'star')
        self.assertTrue(star.get_property('temperature') > 0)
        
        # Test planet creation
        planet = self.factory.create_entity('planet', (300, 400), name='Test Planet')
        self.assertEqual(planet.type, 'planet')
        self.assertIsInstance(planet.get_property('habitable'), bool)
        
        # Test fighter creation
        fighter = self.factory.create_entity('fighter', (200, 300), name='Test Fighter')
        self.assertEqual(fighter.type, 'fighter')
        self.assertTrue(fighter.has_component('movement'))
        self.assertTrue(fighter.has_component('combat'))
    
    def test_custom_template_registration(self):
        """Test custom template registration"""
        custom_template = {
            'properties': {'test_prop': 'test_value'},
            'components': {
                'test_component': {'test_data': 123}
            }
        }
        
        self.factory.register_template('custom_entity', custom_template)
        
        entity = self.factory.create_entity('custom_entity', (0, 0))
        self.assertEqual(entity.get_property('test_prop'), 'test_value')
        self.assertTrue(entity.has_component('test_component'))
        self.assertEqual(entity.get_component('test_component')['test_data'], 123)


class TestEntityTemplates(unittest.TestCase):
    def test_basic_templates(self):
        """Test that basic templates are created correctly"""
        templates = create_basic_templates()
        
        # Check that we have the expected entity types
        expected_types = ['star', 'planet', 'asteroid', 'space_station', 
                         'cargo_ship', 'fighter', 'mining_ship']
        
        for entity_type in expected_types:
            self.assertIn(entity_type, templates)
            template = templates[entity_type]
            self.assertIn('properties', template)
            self.assertIn('components', template)
    
    def test_template_completeness(self):
        """Test that templates have reasonable defaults"""
        templates = create_basic_templates()
        
        # Stars should have temperature
        star_template = templates['star']
        self.assertIn('temperature', star_template['properties'])
        
        # Ships should have movement
        ship_types = ['cargo_ship', 'fighter', 'mining_ship']
        for ship_type in ship_types:
            template = templates[ship_type]
            self.assertIn('movement', template['components'])
        
        # Cargo ships should have cargo
        cargo_template = templates['cargo_ship']
        self.assertIn('cargo', cargo_template['components'])
        
        # Fighters should have combat
        fighter_template = templates['fighter']
        self.assertIn('combat', fighter_template['components'])


if __name__ == '__main__':
    unittest.main()
