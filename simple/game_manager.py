# game_manager.py - Main game manager integrating all systems
"""
Game manager that coordinates the game loop, movement system, AI system,
and rendering for Solar Factions.
"""

import os
import time
from typing import List, Dict, Optional, Tuple, Any
from entities.entity import Entity
from data_manager import DataManager
from generator import SimpleMapGenerator
from renderer import SimpleRenderer
from game_loop import GameLoop
from movement_system import MovementSystem
from ai_system import AISystem


class GameManager:
    """
    Main game manager that coordinates all systems.
    Provides high-level interface for running the game.
    """
    
    def __init__(self, data_path: str = "data"):
        self.data_path = data_path
        self.data_manager = DataManager(data_path)
        self.generator = SimpleMapGenerator()
        self.renderer = None
        
        # Game systems
        self.game_loop = GameLoop(target_tps=20, target_fps=60)
        self.movement_system = MovementSystem()
        self.ai_system = AISystem()
        
        # Game state
        self.entities: List[Entity] = []
        self.is_running = False
        self.show_debug = False
        self.selected_entity: Optional[Entity] = None
        
        # Configuration paths
        self.movement_config_path = os.path.join(data_path, "behaviors", "movement.json")
        self.ai_config_path = os.path.join(data_path, "behaviors", "ai.json")
        
        # Initialize systems
        self._initialize_systems()
    
    def _initialize_systems(self):
        """Initialize all game systems"""
        # Create config files if they don't exist
        os.makedirs(os.path.join(self.data_path, "behaviors"), exist_ok=True)
        
        if not os.path.exists(self.movement_config_path):
            self.movement_system.create_default_config(self.movement_config_path)
        
        if not os.path.exists(self.ai_config_path):
            self.ai_system.create_default_config(self.ai_config_path)
        
        # Load configurations
        self.movement_system.load_config(self.movement_config_path)
        self.ai_system.load_config(self.ai_config_path)
        
        # Register systems with game loop
        self.game_loop.add_update_system(self._update_game_logic)
        self.game_loop.add_render_system(self._update_rendering)
    
    def load_map(self, map_name: str) -> bool:
        """Load a saved map"""
        try:
            map_data = self.data_manager.load_map(map_name)
            if map_data and 'entities' in map_data:
                self.entities = [Entity.from_dict(e) for e in map_data['entities']]
                self._assign_behaviors_to_entities()
                print(f"Loaded map '{map_name}' with {len(self.entities)} entities")
                return True
        except Exception as e:
            print(f"Error loading map '{map_name}': {e}")
        return False
    
    def generate_map(self, template_name: str = "basic", seed: int = None) -> bool:
        """Generate a new map"""
        try:
            self.entities = self.generator.generate_map(template_name, seed)
            self._assign_behaviors_to_entities()
            print(f"Generated map with template '{template_name}' ({len(self.entities)} entities)")
            return True
        except Exception as e:
            print(f"Error generating map: {e}")
            return False
    
    def save_map(self, map_name: str) -> bool:
        """Save the current map"""
        try:
            map_data = {
                'entities': [e.to_dict() for e in self.entities],
                'timestamp': time.time()
            }
            self.data_manager.save_map(map_name, map_data)
            print(f"Saved map '{map_name}'")
            return True
        except Exception as e:
            print(f"Error saving map: {e}")
            return False
    
    def _assign_behaviors_to_entities(self):
        """Assign appropriate behaviors to entities based on their type"""
        for entity in self.entities:
            if not hasattr(entity, 'id') or not hasattr(entity, 'type'):
                continue
                
            entity_type = entity.type
            entity_id = entity.id
            
            # Assign movement behaviors
            if entity_type == 'fighter':
                self.movement_system.assign_behavior(entity_id, 'fast_patrol')
                self.ai_system.assign_ai_to_entity(entity, 'pirate_hunter')
            elif entity_type == 'cargo_ship':
                self.movement_system.assign_behavior(entity_id, 'cargo_route')
                self.ai_system.assign_ai_to_entity(entity, 'trade_circuit')
            elif entity_type == 'mining_ship':
                self.movement_system.assign_behavior(entity_id, 'exploration')
                self.ai_system.assign_ai_to_entity(entity, 'resource_hunter')
            elif entity_type == 'space_station':
                # Stations don't move but have defensive AI
                self.ai_system.assign_ai_to_entity(entity, 'station_defender')
            elif entity_type in ['star', 'planet']:
                # Celestial bodies don't move or have AI
                pass
            else:
                # Default behavior for other entities
                self.movement_system.assign_behavior(entity_id, 'slow_patrol')
                self.ai_system.assign_ai_to_entity(entity, 'default_idle')
    
    def start_rendering(self, width: int = 1200, height: int = 800):
        """Start the visual renderer"""
        if self.renderer is None:
            self.renderer = SimpleRenderer(width, height, "Solar Factions - Game Manager")
        return self.renderer
    
    def start_game_loop(self):
        """Start the main game loop"""
        if not self.is_running:
            self.is_running = True
            self.game_loop.start()
            print("Game loop started")
    
    def stop_game_loop(self):
        """Stop the main game loop"""
        if self.is_running:
            self.is_running = False
            self.game_loop.stop()
            print("Game loop stopped")
    
    def pause_game(self):
        """Pause the game"""
        self.game_loop.pause()
        print("Game paused")
    
    def resume_game(self):
        """Resume the game"""
        self.game_loop.resume()
        print("Game resumed")
    
    def set_game_speed(self, speed: float):
        """Set game speed multiplier"""
        self.game_loop.set_speed(speed)
        print(f"Game speed set to {speed:.1f}x")
    
    def step_game(self):
        """Execute one game step (for debugging)"""
        self.game_loop.step()
        print("Game stepped")
    
    def _update_game_logic(self, dt: float):
        """Update game logic (called by game loop)"""
        if not self.entities:
            return
        
        # Update AI system
        self.ai_system.update(self.entities, dt)
        
        # Update movement system
        self.movement_system.update(self.entities, dt)
        
        # Update AI movement targets based on AI decisions
        self._sync_ai_with_movement()
    
    def _sync_ai_with_movement(self):
        """Synchronize AI decisions with movement system"""
        for entity in self.entities:
            if not hasattr(entity, 'id'):
                continue
                
            entity_id = entity.id
            ai_state = self.ai_system.get_ai_state(entity_id)
            
            if ai_state and 'target_position' in ai_state.memory.goal_data:
                target_pos = ai_state.memory.goal_data['target_position']
                self.movement_system.set_target(entity_id, target_pos)
    
    def _update_rendering(self, dt: float):
        """Update rendering (called by game loop)"""
        if self.renderer:
            self.renderer.render(self.entities)
            
            # Show debug information if enabled
            if self.show_debug:
                self._render_debug_info()
    
    def _render_debug_info(self):
        """Render debug information overlay"""
        if not self.renderer:
            return
            
        # Get game statistics
        stats = self.game_loop.get_stats()
        
        # Create debug text
        debug_lines = [
            f"Tick: {stats['tick']}",
            f"Game Time: {stats['game_time']:.1f}s",
            f"Speed: {stats['speed_multiplier']:.1f}x",
            f"TPS: {stats['actual_tps']:.1f}/{stats['target_tps']}",
            f"FPS: {stats['actual_fps']:.1f}/{stats['target_fps']}",
            f"Entities: {len(self.entities)}",
            f"AI Behaviors: {len(self.ai_system.behaviors)}",
            f"Movement Behaviors: {len(self.movement_system.behaviors)}",
            f"Status: {'Running' if stats['is_running'] else 'Stopped'}",
            f"Paused: {'Yes' if stats['is_paused'] else 'No'}"
        ]
        
        # Render debug text
        y_offset = 10
        for line in debug_lines:
            text_surface = self.renderer.font.render(line, True, (255, 255, 255))
            self.renderer.screen.blit(text_surface, (10, y_offset))
            y_offset += 25
    
    def run_interactive(self):
        """Run in interactive mode with visual renderer"""
        import pygame
        
        # Initialize renderer
        renderer = self.start_rendering()
        
        # Start game loop
        self.start_game_loop()
        
        # Main event loop
        running = True
        clock = pygame.time.Clock()
        
        print("\n=== Solar Factions Game Manager ===")
        print("Controls:")
        print("  SPACE - Pause/Resume")
        print("  + - Increase speed")
        print("  - - Decrease speed")
        print("  S - Single step (when paused)")
        print("  D - Toggle debug info")
        print("  ESC - Exit")
        print("  Mouse - Pan view (drag)")
        print("  Mouse wheel - Zoom")
        print("  Click entity - Select")
        
        try:
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            running = False
                        elif event.key == pygame.K_SPACE:
                            if self.game_loop.state.is_paused:
                                self.resume_game()
                            else:
                                self.pause_game()
                        elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                            new_speed = min(10.0, self.game_loop.state.speed_multiplier * 1.5)
                            self.set_game_speed(new_speed)
                        elif event.key == pygame.K_MINUS:
                            new_speed = max(0.1, self.game_loop.state.speed_multiplier / 1.5)
                            self.set_game_speed(new_speed)
                        elif event.key == pygame.K_s:
                            if self.game_loop.state.is_paused:
                                self.step_game()
                        elif event.key == pygame.K_d:
                            self.show_debug = not self.show_debug
                            print(f"Debug info: {'ON' if self.show_debug else 'OFF'}")
                    
                    # Handle renderer events
                    renderer.handle_event(event)
                
                # Limit frame rate for event handling
                clock.tick(60)
                
        except KeyboardInterrupt:
            print("\nShutting down...")
        
        finally:
            self.stop_game_loop()
            pygame.quit()
    
    def run_headless(self, duration: float = 10.0):
        """Run in headless mode for testing"""
        print(f"Running headless simulation for {duration} seconds...")
        
        # Start game loop
        self.start_game_loop()
        
        start_time = time.time()
        last_stats_time = start_time
        
        try:
            while time.time() - start_time < duration:
                # Print statistics every few seconds
                if time.time() - last_stats_time >= 2.0:
                    self.game_loop.print_stats()
                    last_stats_time = time.time()
                
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\nSimulation interrupted")
        
        finally:
            self.stop_game_loop()
            self.game_loop.print_stats()
    
    def get_entity_info(self, entity_id: str) -> Dict[str, Any]:
        """Get detailed information about an entity"""
        entity = None
        for e in self.entities:
            if hasattr(e, 'id') and e.id == entity_id:
                entity = e
                break
        
        if not entity:
            return {"error": "Entity not found"}
        
        info = {
            "id": entity.id,
            "type": entity.type,
            "position": getattr(entity, 'position', (0, 0)),
            "components": list(entity.components.keys()) if hasattr(entity, 'components') else []
        }
        
        # Add AI information
        ai_state = self.ai_system.get_ai_state(entity_id)
        if ai_state:
            info["ai"] = {
                "behavior": ai_state.behavior_name,
                "state_time": ai_state.state_time,
                "energy": ai_state.energy,
                "alertness": ai_state.alertness,
                "current_target": ai_state.memory.current_target,
                "current_goal": ai_state.memory.current_goal
            }
        
        # Add movement information
        movement_data = self.movement_system.get_movement_data(entity_id)
        if movement_data:
            info["movement"] = {
                "velocity": movement_data.velocity,
                "max_speed": movement_data.max_speed,
                "target_position": movement_data.target_position,
                "path_points": len(movement_data.path_points)
            }
        
        return info
    
    def list_entities(self) -> List[Dict[str, Any]]:
        """List all entities with basic information"""
        entities_info = []
        for entity in self.entities:
            if hasattr(entity, 'id'):
                entities_info.append({
                    "id": entity.id,
                    "type": entity.type,
                    "position": getattr(entity, 'position', (0, 0))
                })
        return entities_info
    
    def print_statistics(self):
        """Print comprehensive game statistics"""
        print("\n=== Game Statistics ===")
        
        # Game loop stats
        self.game_loop.print_stats()
        
        # Entity counts
        entity_counts = {}
        for entity in self.entities:
            entity_type = entity.type
            entity_counts[entity_type] = entity_counts.get(entity_type, 0) + 1
        
        print(f"\n--- Entity Counts ---")
        for entity_type, count in sorted(entity_counts.items()):
            print(f"{entity_type}: {count}")
        
        # AI stats
        ai_behavior_counts = {}
        for entity in self.entities:
            if hasattr(entity, 'id'):
                ai_state = self.ai_system.get_ai_state(entity.id)
                if ai_state:
                    behavior = ai_state.behavior_name
                    ai_behavior_counts[behavior] = ai_behavior_counts.get(behavior, 0) + 1
        
        print(f"\n--- AI Behavior Counts ---")
        for behavior, count in sorted(ai_behavior_counts.items()):
            print(f"{behavior}: {count}")
        
        # Movement stats
        movement_behavior_counts = {}
        for entity_id in self.movement_system.entity_behaviors:
            behavior = self.movement_system.entity_behaviors[entity_id]
            movement_behavior_counts[behavior] = movement_behavior_counts.get(behavior, 0) + 1
        
        print(f"\n--- Movement Behavior Counts ---")
        for behavior, count in sorted(movement_behavior_counts.items()):
            print(f"{behavior}: {count}")
        
        print(f"\nTotal Systems: {len(self.game_loop.update_systems)} update, {len(self.game_loop.render_systems)} render")
