import unittest
import sys
import os
import json
from datetime import datetime
from typing import List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from coordinates import Coordinates, Region
from entities.base import Entity
from entities.vessels import FreighterClass, FighterClass
from entities.structures import TradingStation, IndustrialStation
from entities.resources import MetallicAsteroid, IceAsteroid
from generator import MapGenerator
from renderer import MapRenderer

class TestDataFlowPatterns(unittest.TestCase):
    """Test the four core data flow patterns established by the World Map POC:
    1. Entity Management → Centralized entity creation, update, and deletion
    2. Spatial Relationships → Position-based queries and interactions
    3. Data Serialization → JSON-based data exchange format
    4. Rendering Pipeline → Visual representation and user interaction
    """

    def setUp(self):
        """Set up test fixtures for each test method."""
        self.test_position = Coordinates(100.0, 200.0)
        self.test_entities = []
        
        # Create a diverse set of entities for testing
        self.freighter = FreighterClass(position=Coordinates(100.0, 200.0))
        self.fighter = FighterClass(position=Coordinates(150.0, 250.0))
        self.trading_station = TradingStation(position=Coordinates(50.0, 50.0))
        self.industrial_station = IndustrialStation(position=Coordinates(300.0, 400.0))
        self.metallic_asteroid = MetallicAsteroid(position=Coordinates(200.0, 150.0))
        self.ice_asteroid = IceAsteroid(position=Coordinates(250.0, 300.0))
        
        self.test_entities = [
            self.freighter, self.fighter, self.trading_station,
            self.industrial_station, self.metallic_asteroid, self.ice_asteroid
        ]

    def test_entity_management_pattern(self):
        """Test Pattern 1: Entity Management → Centralized entity creation, update, and deletion"""
        
        # Test entity creation
        initial_count = len(self.test_entities)
        new_entity = FreighterClass(position=Coordinates(500.0, 600.0))
        self.test_entities.append(new_entity)
        
        self.assertEqual(len(self.test_entities), initial_count + 1)
        self.assertIn(new_entity, self.test_entities)
        self.assertIsNotNone(new_entity.id)
        self.assertIsNotNone(new_entity.created_at)
        self.assertIsNotNone(new_entity.updated_at)
        
        # Test entity update
        original_updated_at = new_entity.updated_at
        new_entity.update()
        self.assertGreater(new_entity.updated_at, original_updated_at)
        
        # Test entity deletion
        self.test_entities.remove(new_entity)
        self.assertEqual(len(self.test_entities), initial_count)
        self.assertNotIn(new_entity, self.test_entities)
        
        # Test entity metadata management
        test_metadata = {"custom_field": "test_value", "behavior_state": "active"}
        new_entity.metadata.update(test_metadata)
        self.assertEqual(new_entity.metadata["custom_field"], "test_value")
        self.assertEqual(new_entity.metadata["behavior_state"], "active")
        
        # Test entity type hierarchy
        self.assertIsInstance(self.freighter, Entity)
        self.assertIsInstance(self.trading_station, Entity)
        self.assertIsInstance(self.metallic_asteroid, Entity)
        
        print("✓ Entity Management Pattern: All tests passed")

    def test_spatial_relationships_pattern(self):
        """Test Pattern 2: Spatial Relationships → Position-based queries and interactions"""
        
        # Test coordinate system functionality
        coord1 = Coordinates(0.0, 0.0)
        coord2 = Coordinates(30.0, 40.0)
        
        # Test distance calculation
        distance = coord1.distance_to(coord2)
        self.assertAlmostEqual(distance, 50.0, places=5)
        
        # Test angle calculation
        angle = coord1.angle_to(coord2)
        self.assertIsInstance(angle, float)
        
        # Test movement toward target
        moved_coord = coord1.move_toward(coord2, 10.0)
        self.assertAlmostEqual(coord1.distance_to(moved_coord), 10.0, places=5)
        
        # Test collision detection
        asteroid1 = MetallicAsteroid(position=Coordinates(100.0, 100.0))
        asteroid2 = MetallicAsteroid(position=Coordinates(103.0, 100.0))  # 3 units apart
        asteroid3 = MetallicAsteroid(position=Coordinates(110.0, 100.0))  # 10 units apart
        
        # Should collide (distance < sum of collision radii)
        self.assertTrue(asteroid1.collides_with(asteroid2))
        # Should not collide (distance > sum of collision radii)
        self.assertFalse(asteroid1.collides_with(asteroid3))
        
        # Test region-based spatial queries
        test_region = Region(0.0, 0.0, 200.0, 200.0)
        entities_in_region = [e for e in self.test_entities if test_region.contains(e.position)]
        
        # Verify entities within region bounds
        for entity in entities_in_region:
            self.assertTrue(test_region.contains(entity.position))
        
        # Test proximity-based queries
        center = Coordinates(150.0, 200.0)
        radius = 100.0
        nearby_entities = [e for e in self.test_entities if center.distance_to(e.position) <= radius]
        
        # Verify all nearby entities are within radius
        for entity in nearby_entities:
            self.assertLessEqual(center.distance_to(entity.position), radius)
        
        # Test vessel movement capabilities
        original_position = self.freighter.position
        target_position = Coordinates(120.0, 220.0)
        
        # Test movement validation
        self.assertTrue(self.freighter.can_move())
        
        # Test movement execution
        moved = self.freighter.move_to(target_position)
        if moved:
            self.assertEqual(self.freighter.position, target_position)
        else:
            # If not fully moved, should be closer to target
            new_distance = original_position.distance_to(self.freighter.position)
            self.assertGreater(new_distance, 0)
        
        print("✓ Spatial Relationships Pattern: All tests passed")

    def test_data_serialization_pattern(self):
        """Test Pattern 3: Data Serialization → JSON-based data exchange format"""
        
        # Test individual entity serialization
        entity_dict = self.freighter.to_dict()
        
        # Verify required fields
        required_fields = ['id', 'type', 'position', 'created_at', 'updated_at', 'metadata']
        for field in required_fields:
            self.assertIn(field, entity_dict)
        
        # Verify data types and format
        self.assertIsInstance(entity_dict['id'], str)
        self.assertEqual(entity_dict['type'], 'FreighterClass')
        self.assertIsInstance(entity_dict['position'], dict)
        self.assertIn('x', entity_dict['position'])
        self.assertIn('y', entity_dict['position'])
        self.assertIsInstance(entity_dict['created_at'], str)
        self.assertIsInstance(entity_dict['updated_at'], str)
        self.assertIsInstance(entity_dict['metadata'], dict)
        
        # Test datetime serialization format
        created_at = datetime.fromisoformat(entity_dict['created_at'])
        updated_at = datetime.fromisoformat(entity_dict['updated_at'])
        self.assertIsInstance(created_at, datetime)
        self.assertIsInstance(updated_at, datetime)
        
        # Test map-level serialization
        map_data = {
            'generated_at': datetime.now().isoformat(),
            'entity_count': len(self.test_entities),
            'entities': [entity.to_dict() for entity in self.test_entities]
        }
        
        # Test JSON serialization
        json_string = json.dumps(map_data)
        self.assertIsInstance(json_string, str)
        
        # Test JSON deserialization
        deserialized_data = json.loads(json_string)
        self.assertEqual(deserialized_data['entity_count'], len(self.test_entities))
        self.assertEqual(len(deserialized_data['entities']), len(self.test_entities))
        
        # Test entity type diversity in serialization
        entity_types = [entity['type'] for entity in deserialized_data['entities']]
        expected_types = ['FreighterClass', 'FighterClass', 'TradingStation', 
                         'IndustrialStation', 'MetallicAsteroid', 'IceAsteroid']
        for expected_type in expected_types:
            self.assertIn(expected_type, entity_types)
        
        # Test serialization roundtrip consistency
        original_position = self.freighter.position
        serialized = self.freighter.to_dict()
        self.assertEqual(serialized['position']['x'], original_position.x)
        self.assertEqual(serialized['position']['y'], original_position.y)
        
        print("✓ Data Serialization Pattern: All tests passed")

    def test_rendering_pipeline_pattern(self):
        """Test Pattern 4: Rendering Pipeline → Visual representation and user interaction"""
        
        # Test renderer initialization
        renderer = MapRenderer(width=800, height=600)
        self.assertEqual(renderer.width, 800)
        self.assertEqual(renderer.height, 600)
        self.assertIsNotNone(renderer.screen)
        
        # Test coordinate transformation
        world_pos = Coordinates(100.0, 200.0)
        screen_pos = renderer.world_to_screen(world_pos)
        self.assertIsInstance(screen_pos, tuple)
        self.assertEqual(len(screen_pos), 2)
        
        # Test reverse coordinate transformation
        back_to_world = renderer.screen_to_world(screen_pos)
        self.assertAlmostEqual(back_to_world.x, world_pos.x, places=1)
        self.assertAlmostEqual(back_to_world.y, world_pos.y, places=1)
        
        # Test entity rendering properties
        for entity in self.test_entities:
            # Test polymorphic rendering methods
            display_name = entity.get_display_name()
            render_color = entity.get_render_color()
            render_size = entity.get_render_size()
            
            self.assertIsInstance(display_name, str)
            self.assertIsInstance(render_color, tuple)
            self.assertEqual(len(render_color), 3)  # RGB tuple
            self.assertIsInstance(render_size, int)
            self.assertGreater(render_size, 0)
            
            # Verify color values are valid RGB
            for color_value in render_color:
                self.assertGreaterEqual(color_value, 0)
                self.assertLessEqual(color_value, 255)
        
        # Test entity selection functionality
        test_screen_pos = (400, 300)  # Center of 800x600 screen
        selected_entity = renderer.find_entity_at_position(self.test_entities, test_screen_pos)
        
        # Entity selection should return None or a valid entity
        if selected_entity is not None:
            self.assertIn(selected_entity, self.test_entities)
        
        # Test zoom functionality
        original_zoom = renderer.zoom_level
        renderer.zoom_level = 2.0
        self.assertEqual(renderer.zoom_level, 2.0)
        
        # Test coordinate transformation with zoom
        zoomed_screen_pos = renderer.world_to_screen(world_pos)
        self.assertNotEqual(zoomed_screen_pos, screen_pos)
        
        # Restore original zoom
        renderer.zoom_level = original_zoom
        
        # Test view offset functionality
        original_offset = renderer.view_offset
        renderer.view_offset = Coordinates(50.0, 50.0)
        
        offset_screen_pos = renderer.world_to_screen(world_pos)
        self.assertNotEqual(offset_screen_pos, screen_pos)
        
        # Restore original offset
        renderer.view_offset = original_offset
        
        # Test entity visibility (off-screen culling)
        far_entity = FreighterClass(position=Coordinates(10000.0, 10000.0))
        far_screen_pos = renderer.world_to_screen(far_entity.position)
        
        # Entity should be considered off-screen
        self.assertTrue(far_screen_pos[0] < -50 or far_screen_pos[0] > renderer.width + 50 or
                       far_screen_pos[1] < -50 or far_screen_pos[1] > renderer.height + 50)
        
        print("✓ Rendering Pipeline Pattern: All tests passed")

    def test_integration_pattern_interoperability(self):
        """Test that all four patterns work together seamlessly"""
        
        # Test full integration workflow
        # 1. Create entities (Entity Management)
        test_station = TradingStation(position=Coordinates(400.0, 300.0))
        test_ship = FreighterClass(position=Coordinates(350.0, 250.0))
        
        # 2. Perform spatial operations (Spatial Relationships)
        distance = test_station.position.distance_to(test_ship.position)
        self.assertGreater(distance, 0)
        
        # Check if ship can dock at station (spatial + business logic)
        can_dock = test_station.can_dock()
        self.assertTrue(can_dock)
        
        # 3. Serialize the state (Data Serialization)
        entities = [test_station, test_ship]
        serialized_data = {
            'entities': [entity.to_dict() for entity in entities],
            'interactions': {
                'distance_between': distance,
                'docking_available': can_dock
            }
        }
        
        json_data = json.dumps(serialized_data)
        self.assertIsInstance(json_data, str)
        
        # 4. Render the entities (Rendering Pipeline)
        renderer = MapRenderer()
        
        # Test that entities can be rendered
        for entity in entities:
            screen_pos = renderer.world_to_screen(entity.position)
            self.assertIsInstance(screen_pos, tuple)
            
            # Test rendering properties
            color = entity.get_render_color()
            size = entity.get_render_size()
            name = entity.get_display_name()
            
            self.assertIsInstance(color, tuple)
            self.assertIsInstance(size, int)
            self.assertIsInstance(name, str)
        
        # Test that the integrated system maintains consistency
        # Entity updates should affect all patterns
        original_position = test_ship.position
        test_ship.position = Coordinates(380.0, 280.0)
        test_ship.update()
        
        # Spatial relationships should reflect the change
        new_distance = test_station.position.distance_to(test_ship.position)
        self.assertNotEqual(distance, new_distance)
        
        # Serialization should reflect the change
        updated_data = test_ship.to_dict()
        self.assertEqual(updated_data['position']['x'], 380.0)
        self.assertEqual(updated_data['position']['y'], 280.0)
        
        # Rendering should reflect the change
        new_screen_pos = renderer.world_to_screen(test_ship.position)
        original_screen_pos = renderer.world_to_screen(original_position)
        self.assertNotEqual(new_screen_pos, original_screen_pos)
        
        print("✓ Integration Pattern Interoperability: All tests passed")

    def test_map_generation_integration(self):
        """Test that map generation works with all data flow patterns"""
        
        # Test template-based generation
        generator = MapGenerator()
        
        # Generate a test map
        entities = generator.generate_map("basic_sector", seed=42)
        
        # Verify Entity Management pattern
        self.assertGreater(len(entities), 0)
        for entity in entities:
            self.assertIsInstance(entity, Entity)
            self.assertIsNotNone(entity.id)
            self.assertIsNotNone(entity.position)
        
        # Verify Spatial Relationships pattern
        # Check that entities are within expected bounds
        for entity in entities:
            self.assertGreaterEqual(entity.position.x, 0)
            self.assertGreaterEqual(entity.position.y, 0)
            self.assertLessEqual(entity.position.x, 1000)  # basic_sector width
            self.assertLessEqual(entity.position.y, 1000)  # basic_sector height
        
        # Verify Data Serialization pattern
        # Test export functionality
        test_filename = "test_integration_map"
        generator.export_map(entities, test_filename)
        
        # Verify file was created and contains valid JSON
        export_path = f"data/generated_maps/{test_filename}.json"
        self.assertTrue(os.path.exists(export_path))
        
        with open(export_path, 'r') as f:
            map_data = json.load(f)
        
        self.assertIn('generated_at', map_data)
        self.assertIn('entity_count', map_data)
        self.assertIn('entities', map_data)
        self.assertEqual(map_data['entity_count'], len(entities))
        
        # Clean up test file
        if os.path.exists(export_path):
            os.remove(export_path)
        
        # Verify Rendering Pipeline pattern
        # All generated entities should be renderable
        for entity in entities:
            display_name = entity.get_display_name()
            render_color = entity.get_render_color()
            render_size = entity.get_render_size()
            
            self.assertIsInstance(display_name, str)
            self.assertIsInstance(render_color, tuple)
            self.assertIsInstance(render_size, int)
        
        print("✓ Map Generation Integration: All tests passed")

if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)
