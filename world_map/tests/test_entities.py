import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from coordinates import Coordinates
from entities.base import Entity
from entities.vessels import FreighterClass, FighterClass
from entities.structures import TradingStation, IndustrialStation
from entities.resources import MetallicAsteroid, IceAsteroid

class TestCoordinates(unittest.TestCase):
    def test_coordinates_creation(self):
        coord = Coordinates(10.0, 20.0)
        self.assertEqual(coord.x, 10.0)
        self.assertEqual(coord.y, 20.0)
    
    def test_distance_calculation(self):
        coord1 = Coordinates(0.0, 0.0)
        coord2 = Coordinates(3.0, 4.0)
        distance = coord1.distance_to(coord2)
        self.assertAlmostEqual(distance, 5.0, places=5)
    
    def test_coordinate_tuple_conversion(self):
        coord = Coordinates(10.5, 20.7)
        self.assertEqual(coord.to_tuple(), (10.5, 20.7))
        self.assertEqual(coord.to_int_tuple(), (10, 20))

class TestEntities(unittest.TestCase):
    def test_freighter_creation(self):
        position = Coordinates(100.0, 200.0)
        freighter = FreighterClass(position=position)
        
        self.assertEqual(freighter.position, position)
        self.assertEqual(freighter.cargo_capacity, 500.0)
        self.assertEqual(freighter.max_speed, 5.0)
        self.assertIsNotNone(freighter.id)
    
    def test_fighter_creation(self):
        position = Coordinates(50.0, 60.0)
        fighter = FighterClass(position=position)
        
        self.assertEqual(fighter.position, position)
        self.assertEqual(fighter.max_speed, 20.0)
        self.assertEqual(fighter.weapon_damage, 15.0)
        self.assertIsNotNone(fighter.id)
    
    def test_trading_station_creation(self):
        position = Coordinates(0.0, 0.0)
        station = TradingStation(position=position)
        
        self.assertEqual(station.position, position)
        self.assertEqual(station.docking_bays, 8)
        self.assertIn("trade", station.services)
        self.assertIsNotNone(station.id)
    
    def test_industrial_station_creation(self):
        position = Coordinates(150.0, 250.0)
        station = IndustrialStation(position=position)
        
        self.assertEqual(station.position, position)
        self.assertEqual(station.docking_bays, 6)
        self.assertIn("manufacturing", station.services)
        self.assertIsNotNone(station.id)
    
    def test_metallic_asteroid_creation(self):
        position = Coordinates(300.0, 400.0)
        asteroid = MetallicAsteroid(position=position)
        
        self.assertEqual(asteroid.position, position)
        self.assertIn("iron", asteroid.resource_content)
        self.assertIn("copper", asteroid.resource_content)
        self.assertIn("titanium", asteroid.resource_content)
        self.assertTrue(asteroid.can_mine())
    
    def test_ice_asteroid_creation(self):
        position = Coordinates(500.0, 600.0)
        asteroid = IceAsteroid(position=position)
        
        self.assertEqual(asteroid.position, position)
        self.assertIn("water", asteroid.resource_content)
        self.assertIn("hydrogen", asteroid.resource_content)
        self.assertTrue(asteroid.can_mine())
    
    def test_entity_serialization(self):
        position = Coordinates(100.0, 200.0)
        freighter = FreighterClass(position=position)
        
        data = freighter.to_dict()
        self.assertIn('id', data)
        self.assertIn('type', data)
        self.assertIn('position', data)
        self.assertEqual(data['type'], 'FreighterClass')
        self.assertEqual(data['position']['x'], 100.0)
        self.assertEqual(data['position']['y'], 200.0)
    
    def test_cargo_loading(self):
        position = Coordinates(100.0, 200.0)
        freighter = FreighterClass(position=position)
        
        # Test successful cargo loading
        result = freighter.load_cargo("iron", 100.0)
        self.assertTrue(result)
        self.assertEqual(freighter.current_cargo, 100.0)
        self.assertEqual(freighter.cargo_manifest["iron"], 100.0)
        
        # Test cargo capacity limit
        result = freighter.load_cargo("copper", 450.0)  # Total would be 550, over capacity
        self.assertFalse(result)
        self.assertEqual(freighter.current_cargo, 100.0)  # Should remain unchanged
    
    def test_mining_functionality(self):
        position = Coordinates(300.0, 400.0)
        asteroid = MetallicAsteroid(position=position)
        
        initial_iron = asteroid.resource_content["iron"]
        mined_amount = asteroid.mine_resource("iron", 50.0)
        
        self.assertEqual(mined_amount, 50.0)
        self.assertEqual(asteroid.resource_content["iron"], initial_iron - 50.0)
        
        # Test mining more than available
        remaining_iron = asteroid.resource_content["iron"]
        mined_amount = asteroid.mine_resource("iron", remaining_iron + 100.0)
        self.assertEqual(mined_amount, remaining_iron)
        self.assertEqual(asteroid.resource_content["iron"], 0.0)

if __name__ == '__main__':
    unittest.main()
