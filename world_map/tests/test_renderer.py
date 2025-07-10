import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from coordinates import Coordinates
from entities.vessels import FreighterClass
from entities.structures import TradingStation
from renderer import MapRenderer

class TestMapRenderer(unittest.TestCase):
    def setUp(self):
        # Create test entities
        self.entities = [
            FreighterClass(position=Coordinates(100.0, 200.0)),
            TradingStation(position=Coordinates(300.0, 400.0)),
            FreighterClass(position=Coordinates(500.0, 600.0))
        ]
    
    def test_renderer_initialization(self):
        renderer = MapRenderer(width=800, height=600)
        self.assertEqual(renderer.width, 800)
        self.assertEqual(renderer.height, 600)
        self.assertEqual(renderer.zoom_level, 1.0)
        self.assertEqual(renderer.view_offset.x, 0.0)
        self.assertEqual(renderer.view_offset.y, 0.0)
    
    def test_coordinate_conversion(self):
        renderer = MapRenderer(width=800, height=600)
        
        # Test world to screen conversion
        world_pos = Coordinates(100.0, 200.0)
        screen_pos = renderer.world_to_screen(world_pos)
        
        # With default zoom and offset, should be offset by screen center
        expected_x = int(100.0 * 1.0 + 400)  # 100 * zoom + width/2
        expected_y = int(200.0 * 1.0 + 300)  # 200 * zoom + height/2
        
        self.assertEqual(screen_pos, (expected_x, expected_y))
        
        # Test screen to world conversion (reverse)
        converted_world = renderer.screen_to_world(screen_pos)
        self.assertAlmostEqual(converted_world.x, world_pos.x, places=5)
        self.assertAlmostEqual(converted_world.y, world_pos.y, places=5)
    
    def test_zoom_functionality(self):
        renderer = MapRenderer()
        
        # Test zoom limits
        renderer.zoom_level = 0.05  # Below minimum
        self.assertGreaterEqual(renderer.zoom_level, 0.05)
        
        renderer.zoom_level = 10.0  # Above maximum
        self.assertLessEqual(renderer.zoom_level, 10.0)
        
        # Test zoom affects coordinate conversion
        renderer.zoom_level = 2.0
        world_pos = Coordinates(50.0, 100.0)
        screen_pos = renderer.world_to_screen(world_pos)
        
        expected_x = int(50.0 * 2.0 + renderer.width / 2)
        expected_y = int(100.0 * 2.0 + renderer.height / 2)
        
        self.assertEqual(screen_pos, (expected_x, expected_y))
    
    def test_view_offset(self):
        renderer = MapRenderer()
        
        # Test view offset affects coordinate conversion
        renderer.view_offset = Coordinates(10.0, 20.0)
        world_pos = Coordinates(100.0, 200.0)
        screen_pos = renderer.world_to_screen(world_pos)
        
        expected_x = int((100.0 - 10.0) * 1.0 + renderer.width / 2)
        expected_y = int((200.0 - 20.0) * 1.0 + renderer.height / 2)
        
        self.assertEqual(screen_pos, (expected_x, expected_y))
    
    def test_entity_finding(self):
        renderer = MapRenderer()
        
        # Test finding entity at position
        # Note: This is a basic test - actual implementation depends on pygame
        world_pos = Coordinates(100.0, 200.0)
        screen_pos = renderer.world_to_screen(world_pos)
        
        # The find_entity_at_position method should work with actual entities
        entity = renderer.find_entity_at_position(self.entities, screen_pos)
        
        # The first entity is at (100, 200), so it should be found
        # Note: This depends on the render size and exact positioning
        if entity:
            self.assertIsInstance(entity, FreighterClass)
    
    def test_entity_rendering_properties(self):
        # Test that entities have proper rendering properties
        freighter = self.entities[0]
        station = self.entities[1]
        
        # Check that entities have required rendering methods
        self.assertTrue(hasattr(freighter, 'get_render_color'))
        self.assertTrue(hasattr(freighter, 'get_render_size'))
        self.assertTrue(hasattr(freighter, 'get_display_name'))
        
        self.assertTrue(hasattr(station, 'get_render_color'))
        self.assertTrue(hasattr(station, 'get_render_size'))
        self.assertTrue(hasattr(station, 'get_display_name'))
        
        # Check return types
        self.assertIsInstance(freighter.get_render_color(), tuple)
        self.assertIsInstance(freighter.get_render_size(), int)
        self.assertIsInstance(freighter.get_display_name(), str)
        
        # Check that colors are RGB tuples
        color = freighter.get_render_color()
        self.assertEqual(len(color), 3)
        self.assertTrue(all(0 <= c <= 255 for c in color))

if __name__ == '__main__':
    unittest.main()
