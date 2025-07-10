import unittest
import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from generator import MapGenerator
from entities.base import Entity
from entities.vessels import FreighterClass, FighterClass
from entities.structures import TradingStation, IndustrialStation
from entities.resources import MetallicAsteroid, IceAsteroid

class TestMapGenerator(unittest.TestCase):
    def setUp(self):
        # Create a minimal test template
        self.test_template = {
            "templates": {
                "test_sector": {
                    "name": "Test Sector",
                    "description": "A test sector",
                    "size": {"width": 500, "height": 500},
                    "entity_counts": {
                        "trading_stations": {"min": 1, "max": 2},
                        "freighter_ships": {"min": 2, "max": 4},
                        "metallic_asteroids": {"min": 3, "max": 5}
                    },
                    "placement_rules": {
                        "stations": {
                            "min_distance_from_edge": 50,
                            "min_distance_between": 100
                        },
                        "asteroids": {
                            "cluster_probability": 0.5,
                            "cluster_size": {"min": 2, "max": 4},
                            "cluster_spread": 25
                        },
                        "ships": {
                            "spawn_near_stations": True,
                            "station_proximity": 50
                        }
                    }
                }
            }
        }
        
        # Write test template to file
        with open('data/test_templates.json', 'w') as f:
            json.dump(self.test_template, f)
    
    def test_generator_initialization(self):
        generator = MapGenerator('data/test_templates.json')
        self.assertIn('test_sector', generator.templates)
        self.assertEqual(generator.templates['test_sector'].name, 'Test Sector')
    
    def test_map_generation(self):
        generator = MapGenerator('data/test_templates.json')
        entities = generator.generate_map('test_sector', seed=42)
        
        # Check that entities were generated
        self.assertGreater(len(entities), 0)
        
        # Check entity types
        trading_stations = [e for e in entities if isinstance(e, TradingStation)]
        freighters = [e for e in entities if isinstance(e, FreighterClass)]
        asteroids = [e for e in entities if isinstance(e, MetallicAsteroid)]
        
        # Verify counts are within expected ranges
        self.assertGreaterEqual(len(trading_stations), 1)
        self.assertLessEqual(len(trading_stations), 2)
        
        self.assertGreaterEqual(len(freighters), 2)
        self.assertLessEqual(len(freighters), 4)
        
        self.assertGreaterEqual(len(asteroids), 3)
        self.assertLessEqual(len(asteroids), 5)
    
    def test_deterministic_generation(self):
        generator = MapGenerator('data/test_templates.json')
        
        # Generate same map twice with same seed
        entities1 = generator.generate_map('test_sector', seed=123)
        entities2 = generator.generate_map('test_sector', seed=123)
        
        self.assertEqual(len(entities1), len(entities2))
        
        # Check that positions are the same (deterministic)
        for e1, e2 in zip(entities1, entities2):
            self.assertEqual(e1.position.x, e2.position.x)
            self.assertEqual(e1.position.y, e2.position.y)
            self.assertEqual(type(e1), type(e2))
    
    def test_export_functionality(self):
        generator = MapGenerator('data/test_templates.json')
        entities = generator.generate_map('test_sector', seed=42)
        
        # Export map
        generator.export_map(entities, 'test_export')
        
        # Check that file was created
        self.assertTrue(os.path.exists('data/generated_maps/test_export.json'))
        
        # Check file content
        with open('data/generated_maps/test_export.json', 'r') as f:
            data = json.load(f)
        
        self.assertIn('generated_at', data)
        self.assertIn('entity_count', data)
        self.assertIn('entities', data)
        self.assertEqual(data['entity_count'], len(entities))
    
    def tearDown(self):
        # Clean up test files
        if os.path.exists('data/test_templates.json'):
            os.remove('data/test_templates.json')
        if os.path.exists('data/generated_maps/test_export.json'):
            os.remove('data/generated_maps/test_export.json')

if __name__ == '__main__':
    unittest.main()
