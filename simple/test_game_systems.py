# test_game_systems.py - Tests for the new game systems
"""
Test suite for the tick-based game loop, movement system, and AI system.
"""

import unittest
import time
import tempfile
import os
import json
from entities.entity import Entity
from game_loop import GameLoop, GameState
from movement_system import MovementSystem, MovementData, LinearMovement
from ai_system import AISystem, AIState, AIMemory
from game_manager import GameManager


class TestGameLoop(unittest.TestCase):
    """Test the tick-based game loop"""
    
    def setUp(self):
        self.game_loop = GameLoop(target_tps=10, target_fps=30)
        self.update_count = 0
        self.render_count = 0
    
    def tearDown(self):
        if self.game_loop.state.is_running:
            self.game_loop.stop()
    
    def test_game_loop_initialization(self):
        """Test game loop initialization"""
        self.assertFalse(self.game_loop.state.is_running)
        self.assertEqual(self.game_loop.state.tick, 0)
        self.assertEqual(self.game_loop.state.game_time, 0.0)
        self.assertEqual(self.game_loop.state.speed_multiplier, 1.0)
    
    def test_system_registration(self):
        """Test adding and removing systems"""
        def dummy_update(dt):
            self.update_count += 1
        
        def dummy_render(dt):
            self.render_count += 1
        
        # Add systems
        self.game_loop.add_update_system(dummy_update)
        self.game_loop.add_render_system(dummy_render)
        
        self.assertEqual(len(self.game_loop.update_systems), 1)
        self.assertEqual(len(self.game_loop.render_systems), 1)
        
        # Remove systems
        self.game_loop.remove_update_system(dummy_update)
        self.game_loop.remove_render_system(dummy_render)
        
        self.assertEqual(len(self.game_loop.update_systems), 0)
        self.assertEqual(len(self.game_loop.render_systems), 0)
    
    def test_speed_control(self):
        """Test speed control functionality"""
        # Test normal speed setting
        self.game_loop.set_speed(2.0)
        self.assertEqual(self.game_loop.state.speed_multiplier, 2.0)
        
        # Test speed limits
        self.game_loop.set_speed(0.05)  # Below minimum
        self.assertEqual(self.game_loop.state.speed_multiplier, 0.1)
        
        self.game_loop.set_speed(15.0)  # Above maximum
        self.assertEqual(self.game_loop.state.speed_multiplier, 10.0)
    
    def test_pause_resume(self):
        """Test pause and resume functionality"""
        self.game_loop.start()
        self.assertTrue(self.game_loop.state.is_running)
        self.assertFalse(self.game_loop.state.is_paused)
        
        self.game_loop.pause()
        self.assertTrue(self.game_loop.state.is_paused)
        
        self.game_loop.resume()
        self.assertFalse(self.game_loop.state.is_paused)
    
    def test_step_functionality(self):
        """Test single step functionality"""
        def count_updates(dt):
            self.update_count += 1
        
        self.game_loop.add_update_system(count_updates)
        
        # Need to start the game loop for step to work
        self.game_loop.start()
        
        initial_count = self.update_count
        initial_tick = self.game_loop.state.tick
        
        self.game_loop.step()
        
        # Allow some time for the step to be processed
        import time
        time.sleep(0.1)
        
        # Check that at least one tick was processed
        self.assertGreaterEqual(self.game_loop.state.tick, initial_tick + 1)
        self.assertGreater(self.update_count, initial_count)
    
    def test_statistics(self):
        """Test statistics collection"""
        stats = self.game_loop.get_stats()
        
        required_keys = ['tick', 'game_time', 'real_time', 'is_running', 
                        'is_paused', 'speed_multiplier', 'target_tps', 'target_fps']
        
        for key in required_keys:
            self.assertIn(key, stats)


class TestMovementSystem(unittest.TestCase):
    """Test the movement system"""
    
    def setUp(self):
        self.movement_system = MovementSystem()
        self.test_entity = Entity("test_type", (0.0, 0.0), name="test_entity")
    
    def test_movement_system_initialization(self):
        """Test movement system initialization"""
        self.assertIsInstance(self.movement_system.behaviors, dict)
        self.assertIsInstance(self.movement_system.entity_movements, dict)
        self.assertIsInstance(self.movement_system.entity_behaviors, dict)
    
    def test_linear_movement_behavior(self):
        """Test linear movement behavior"""
        config = {
            'name': 'test_linear',
            'max_speed': 50.0,
            'enabled': True
        }
        
        behavior = LinearMovement(config)
        movement_data = MovementData(
            velocity=(10.0, 0.0),
            acceleration=(5.0, 0.0)
        )
        
        initial_pos = self.test_entity.position
        behavior.update(self.test_entity, 0.1, movement_data)
        
        # Check that position changed
        self.assertNotEqual(self.test_entity.position, initial_pos)
        
        # Check that velocity was updated
        self.assertNotEqual(movement_data.velocity, (10.0, 0.0))
    
    def test_behavior_assignment(self):
        """Test assigning behaviors to entities"""
        # Create a test behavior
        config = {'name': 'test_behavior', 'enabled': True}
        behavior = LinearMovement(config)
        self.movement_system.add_behavior('test_behavior', behavior)
        
        # Assign to entity
        self.movement_system.assign_behavior(self.test_entity.id, 'test_behavior')
        
        self.assertIn(self.test_entity.id, self.movement_system.entity_behaviors)
        self.assertIn(self.test_entity.id, self.movement_system.entity_movements)
    
    def test_config_loading(self):
        """Test loading configuration from file"""
        # Create temporary config file
        config_data = {
            "behaviors": [
                {
                    "name": "test_config",
                    "type": "linear",
                    "max_speed": 100.0,
                    "enabled": True
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name
        
        try:
            self.movement_system.load_config(temp_path)
            self.assertIn('test_config', self.movement_system.behaviors)
        finally:
            os.unlink(temp_path)
    
    def test_target_setting(self):
        """Test setting targets for entities"""
        # Create a test behavior first
        config = {'name': 'test_behavior', 'enabled': True}
        behavior = LinearMovement(config)
        self.movement_system.add_behavior('test_behavior', behavior)
        
        # Set up entity with movement data
        self.movement_system.assign_behavior(self.test_entity.id, 'test_behavior')
        
        # Set target
        target = (100.0, 100.0)
        self.movement_system.set_target(self.test_entity.id, target)
        
        movement_data = self.movement_system.get_movement_data(self.test_entity.id)
        self.assertEqual(movement_data.target_position, target)


class TestAISystem(unittest.TestCase):
    """Test the AI system"""
    
    def setUp(self):
        self.ai_system = AISystem()
        self.test_entity = Entity("test_type", (0.0, 0.0), name="test_entity")
        self.test_entities = [self.test_entity]
    
    def test_ai_system_initialization(self):
        """Test AI system initialization"""
        self.assertIsInstance(self.ai_system.behaviors, dict)
        self.assertIsInstance(self.ai_system.entity_ai_states, dict)
        self.assertIn('idle', self.ai_system.behavior_classes)
    
    def test_ai_assignment(self):
        """Test assigning AI to entities"""
        self.ai_system.assign_ai(self.test_entity.id, 'idle')
        
        self.assertIn(self.test_entity.id, self.ai_system.entity_ai_states)
        ai_state = self.ai_system.get_ai_state(self.test_entity.id)
        self.assertIsInstance(ai_state, AIState)
        self.assertEqual(ai_state.behavior_name, 'idle')
    
    def test_behavior_execution(self):
        """Test behavior execution"""
        # Create default idle behavior
        from ai_system import IdleBehavior
        idle_config = {'name': 'test_idle', 'enabled': True, 'energy_recovery_rate': 10.0}
        idle_behavior = IdleBehavior(idle_config)
        self.ai_system.add_behavior('test_idle', idle_behavior)
        
        # Assign AI with reduced energy
        self.ai_system.assign_ai(self.test_entity.id, 'test_idle', energy=50.0)
        
        # Get initial energy
        ai_state = self.ai_system.get_ai_state(self.test_entity.id)
        initial_energy = ai_state.energy
        
        # Update AI
        self.ai_system.update(self.test_entities, 0.1)
        
        # Check that energy increased (idle behavior should recover energy)
        self.assertGreater(ai_state.energy, initial_energy)
    
    def test_behavior_priority(self):
        """Test behavior priority system"""
        from ai_system import IdleBehavior
        
        # Create behaviors with different priorities
        low_priority = IdleBehavior({'name': 'low', 'priority': 5, 'enabled': True})
        high_priority = IdleBehavior({'name': 'high', 'priority': 10, 'enabled': True})
        
        self.ai_system.add_behavior('low', low_priority)
        self.ai_system.add_behavior('high', high_priority)
        
        # Assign AI with low priority initially
        self.ai_system.assign_ai(self.test_entity.id, 'low')
        
        # Update - should switch to higher priority behavior
        self.ai_system.update(self.test_entities, 0.1)
        
        ai_state = self.ai_system.get_ai_state(self.test_entity.id)
        # The behavior should switch to the higher priority one
        self.assertEqual(ai_state.behavior_name, 'high')
    
    def test_config_loading(self):
        """Test loading AI configuration from file"""
        config_data = {
            "behaviors": [
                {
                    "name": "test_ai",
                    "type": "idle",
                    "priority": 1,
                    "energy_recovery_rate": 5.0,
                    "enabled": True
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name
        
        try:
            self.ai_system.load_config(temp_path)
            self.assertIn('test_ai', self.ai_system.behaviors)
        finally:
            os.unlink(temp_path)


class TestGameManager(unittest.TestCase):
    """Test the game manager integration"""
    
    def setUp(self):
        # Create temporary directory for test data
        self.test_dir = tempfile.mkdtemp()
        self.game_manager = GameManager(self.test_dir)
    
    def tearDown(self):
        if self.game_manager.is_running:
            self.game_manager.stop_game_loop()
        
        # Clean up test directory
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_game_manager_initialization(self):
        """Test game manager initialization"""
        self.assertIsInstance(self.game_manager.game_loop, GameLoop)
        self.assertIsInstance(self.game_manager.movement_system, MovementSystem)
        self.assertIsInstance(self.game_manager.ai_system, AISystem)
        self.assertEqual(self.game_manager.entities, [])
        self.assertFalse(self.game_manager.is_running)
    
    def test_map_generation(self):
        """Test map generation"""
        success = self.game_manager.generate_map("basic", seed=42)
        self.assertTrue(success)
        self.assertGreater(len(self.game_manager.entities), 0)
    
    def test_game_loop_control(self):
        """Test game loop control methods"""
        # Generate a map first
        self.game_manager.generate_map("basic", seed=42)
        
        # Start game loop
        self.game_manager.start_game_loop()
        self.assertTrue(self.game_manager.is_running)
        self.assertTrue(self.game_manager.game_loop.state.is_running)
        
        # Test pause/resume
        self.game_manager.pause_game()
        self.assertTrue(self.game_manager.game_loop.state.is_paused)
        
        self.game_manager.resume_game()
        self.assertFalse(self.game_manager.game_loop.state.is_paused)
        
        # Test speed control
        self.game_manager.set_game_speed(2.0)
        self.assertEqual(self.game_manager.game_loop.state.speed_multiplier, 2.0)
        
        # Stop game loop
        self.game_manager.stop_game_loop()
        self.assertFalse(self.game_manager.is_running)
    
    def test_entity_info(self):
        """Test entity information retrieval"""
        # Generate a map
        self.game_manager.generate_map("basic", seed=42)
        
        # Get entity list
        entities = self.game_manager.list_entities()
        self.assertGreater(len(entities), 0)
        
        # Get detailed info for first entity
        if entities:
            entity_info = self.game_manager.get_entity_info(entities[0]['id'])
            self.assertIn('id', entity_info)
            self.assertIn('type', entity_info)
            self.assertIn('position', entity_info)
    
    def test_behavior_assignment(self):
        """Test that behaviors are properly assigned to entities"""
        # Generate a map
        self.game_manager.generate_map("frontier", seed=42)
        
        # Check that entities have behaviors assigned
        entities = self.game_manager.list_entities()
        behavior_assigned = False
        
        for entity_info in entities:
            detailed_info = self.game_manager.get_entity_info(entity_info['id'])
            if 'ai' in detailed_info:
                behavior_assigned = True
                break
        
        self.assertTrue(behavior_assigned, "No AI behaviors were assigned to entities")
    
    def test_headless_simulation(self):
        """Test running headless simulation"""
        # Generate a map
        self.game_manager.generate_map("basic", seed=42)
        
        # Run short simulation
        start_time = time.time()
        self.game_manager.run_headless(0.5)  # Run for 0.5 seconds
        end_time = time.time()
        
        # Check that simulation actually ran
        self.assertGreaterEqual(end_time - start_time, 0.4)  # Allow some tolerance
        
        # Check that game loop processed ticks
        stats = self.game_manager.game_loop.get_stats()
        self.assertGreater(stats['tick'], 0)


def run_performance_test():
    """Run performance test for the game systems"""
    print("Running performance test...")
    
    # Create game manager
    game_manager = GameManager()
    
    # Generate a large map
    game_manager.generate_map("warzone", seed=42)
    
    # Start game loop
    game_manager.start_game_loop()
    
    # Run for a short time
    start_time = time.time()
    time.sleep(2.0)
    end_time = time.time()
    
    # Get statistics
    stats = game_manager.game_loop.get_stats()
    
    print(f"Performance Test Results:")
    print(f"  Duration: {end_time - start_time:.2f} seconds")
    print(f"  Ticks processed: {stats['tick']}")
    print(f"  Average TPS: {stats['actual_tps']:.1f}")
    print(f"  Average FPS: {stats['actual_fps']:.1f}")
    print(f"  Entities simulated: {len(game_manager.entities)}")
    print(f"  Ticks per second: {stats['tick'] / (end_time - start_time):.1f}")
    
    # Stop game loop
    game_manager.stop_game_loop()
    
    print("Performance test completed!")


if __name__ == '__main__':
    import sys
    
    # Check if performance test is requested
    if len(sys.argv) > 1 and sys.argv[1] == 'performance':
        run_performance_test()
    else:
        # Run unit tests
        unittest.main()
