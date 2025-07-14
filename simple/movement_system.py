# movement_system.py - JSON-configurable movement system
"""
Movement system for Solar Factions that supports various movement behaviors
configurable through JSON files.
"""

import json
import math
import random
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass, field
from entities.entity import Entity


@dataclass
class MovementData:
    """Data for movement calculations"""
    velocity: Tuple[float, float] = (0.0, 0.0)
    acceleration: Tuple[float, float] = (0.0, 0.0)
    max_speed: float = 100.0
    rotation: float = 0.0  # radians
    angular_velocity: float = 0.0
    target_position: Optional[Tuple[float, float]] = None
    path_points: List[Tuple[float, float]] = field(default_factory=list)
    current_path_index: int = 0


class MovementBehavior:
    """Base class for movement behaviors"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = config.get('name', 'unknown')
        self.enabled = config.get('enabled', True)
        
    def update(self, entity: Entity, dt: float, movement_data: MovementData) -> None:
        """Update movement for an entity"""
        if not self.enabled:
            return
        self._update_movement(entity, dt, movement_data)
    
    def _update_movement(self, entity: Entity, dt: float, movement_data: MovementData) -> None:
        """Override this method in subclasses"""
        pass


class LinearMovement(MovementBehavior):
    """Simple linear movement with velocity"""
    
    def _update_movement(self, entity: Entity, dt: float, movement_data: MovementData) -> None:
        max_speed = self.config.get('max_speed', 50.0)
        
        # Apply acceleration
        acc_x, acc_y = movement_data.acceleration
        vel_x, vel_y = movement_data.velocity
        
        vel_x += acc_x * dt
        vel_y += acc_y * dt
        
        # Limit speed
        speed = math.sqrt(vel_x * vel_x + vel_y * vel_y)
        if speed > max_speed:
            vel_x = (vel_x / speed) * max_speed
            vel_y = (vel_y / speed) * max_speed
        
        movement_data.velocity = (vel_x, vel_y)
        
        # Update position
        if hasattr(entity, 'position'):
            x, y = entity.position
            x += vel_x * dt
            y += vel_y * dt
            entity.position = (x, y)


class CircularMovement(MovementBehavior):
    """Circular movement around a center point"""
    
    def _update_movement(self, entity: Entity, dt: float, movement_data: MovementData) -> None:
        center = self.config.get('center', (0.0, 0.0))
        radius = self.config.get('radius', 100.0)
        angular_speed = self.config.get('angular_speed', 1.0)
        
        # Update rotation
        movement_data.rotation += angular_speed * dt
        
        # Calculate new position
        if hasattr(entity, 'position'):
            x = center[0] + radius * math.cos(movement_data.rotation)
            y = center[1] + radius * math.sin(movement_data.rotation)
            entity.position = (x, y)


class OrbitMovement(MovementBehavior):
    """Orbit around another entity"""
    
    def _update_movement(self, entity: Entity, dt: float, movement_data: MovementData) -> None:
        target_id = self.config.get('target_entity_id')
        if not target_id:
            return
            
        # Find target entity (would need access to entity manager)
        # For now, use center from config
        center = self.config.get('fallback_center', (0.0, 0.0))
        radius = self.config.get('radius', 100.0)
        angular_speed = self.config.get('angular_speed', 0.5)
        
        # Update rotation
        movement_data.rotation += angular_speed * dt
        
        # Calculate new position
        if hasattr(entity, 'position'):
            x = center[0] + radius * math.cos(movement_data.rotation)
            y = center[1] + radius * math.sin(movement_data.rotation)
            entity.position = (x, y)


class PatrolMovement(MovementBehavior):
    """Patrol between waypoints"""
    
    def _update_movement(self, entity: Entity, dt: float, movement_data: MovementData) -> None:
        waypoints = self.config.get('waypoints', [])
        if not waypoints:
            return
            
        speed = self.config.get('speed', 30.0)
        tolerance = self.config.get('arrival_tolerance', 5.0)
        
        # Initialize path if needed
        if not movement_data.path_points:
            movement_data.path_points = waypoints.copy()
            movement_data.current_path_index = 0
        
        if not movement_data.path_points:
            return
            
        # Get current target
        target = movement_data.path_points[movement_data.current_path_index]
        
        if hasattr(entity, 'position'):
            x, y = entity.position
            target_x, target_y = target
            
            # Calculate direction to target
            dx = target_x - x
            dy = target_y - y
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance < tolerance:
                # Reached waypoint, move to next
                movement_data.current_path_index = (movement_data.current_path_index + 1) % len(movement_data.path_points)
            else:
                # Move towards target
                if distance > 0:
                    move_x = (dx / distance) * speed * dt
                    move_y = (dy / distance) * speed * dt
                    entity.position = (x + move_x, y + move_y)


class WanderMovement(MovementBehavior):
    """Random wandering movement"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.next_direction_change = 0.0
        self.current_direction = random.uniform(0, 2 * math.pi)
    
    def _update_movement(self, entity: Entity, dt: float, movement_data: MovementData) -> None:
        speed = self.config.get('speed', 20.0)
        direction_change_interval = self.config.get('direction_change_interval', 2.0)
        max_direction_change = self.config.get('max_direction_change', math.pi / 4)
        
        # Update direction change timer
        self.next_direction_change -= dt
        
        if self.next_direction_change <= 0:
            # Change direction
            direction_change = random.uniform(-max_direction_change, max_direction_change)
            self.current_direction += direction_change
            self.next_direction_change = direction_change_interval
        
        # Move in current direction
        if hasattr(entity, 'position'):
            x, y = entity.position
            move_x = math.cos(self.current_direction) * speed * dt
            move_y = math.sin(self.current_direction) * speed * dt
            entity.position = (x + move_x, y + move_y)


class SeekMovement(MovementBehavior):
    """Seek towards a target position"""
    
    def _update_movement(self, entity: Entity, dt: float, movement_data: MovementData) -> None:
        target = self.config.get('target_position') or movement_data.target_position
        if not target:
            return
            
        speed = self.config.get('speed', 40.0)
        max_force = self.config.get('max_force', 100.0)
        
        if hasattr(entity, 'position'):
            x, y = entity.position
            target_x, target_y = target
            
            # Calculate desired velocity
            dx = target_x - x
            dy = target_y - y
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance > 0:
                # Normalize and scale to desired speed
                desired_vel_x = (dx / distance) * speed
                desired_vel_y = (dy / distance) * speed
                
                # Calculate steering force
                vel_x, vel_y = movement_data.velocity
                steer_x = desired_vel_x - vel_x
                steer_y = desired_vel_y - vel_y
                
                # Limit steering force
                steer_force = math.sqrt(steer_x * steer_x + steer_y * steer_y)
                if steer_force > max_force:
                    steer_x = (steer_x / steer_force) * max_force
                    steer_y = (steer_y / steer_force) * max_force
                
                # Apply steering force as acceleration
                movement_data.acceleration = (steer_x, steer_y)
                
                # Update velocity
                vel_x += steer_x * dt
                vel_y += steer_y * dt
                movement_data.velocity = (vel_x, vel_y)
                
                # Update position
                entity.position = (x + vel_x * dt, y + vel_y * dt)


class MovementSystem:
    """System that manages all movement behaviors"""
    
    def __init__(self, config_path: str = None):
        self.behaviors: Dict[str, MovementBehavior] = {}
        self.entity_movements: Dict[str, MovementData] = {}
        self.entity_behaviors: Dict[str, str] = {}
        
        # Register built-in behaviors
        self.behavior_classes = {
            'linear': LinearMovement,
            'circular': CircularMovement,
            'orbit': OrbitMovement,
            'patrol': PatrolMovement,
            'wander': WanderMovement,
            'seek': SeekMovement
        }
        
        # Load configuration
        if config_path:
            self.load_config(config_path)
    
    def load_config(self, config_path: str):
        """Load movement configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                
            # Load behavior definitions
            for behavior_def in config.get('behaviors', []):
                behavior_type = behavior_def.get('type')
                if behavior_type in self.behavior_classes:
                    behavior_class = self.behavior_classes[behavior_type]
                    behavior = behavior_class(behavior_def)
                    self.behaviors[behavior.name] = behavior
                    
        except FileNotFoundError:
            print(f"Movement config file not found: {config_path}")
        except json.JSONDecodeError as e:
            print(f"Error parsing movement config: {e}")
    
    def add_behavior(self, name: str, behavior: MovementBehavior):
        """Add a custom movement behavior"""
        self.behaviors[name] = behavior
    
    def assign_behavior(self, entity_id: str, behavior_name: str, **kwargs):
        """Assign a movement behavior to an entity"""
        if behavior_name not in self.behaviors:
            print(f"Unknown movement behavior: {behavior_name}")
            return
            
        self.entity_behaviors[entity_id] = behavior_name
        self.entity_movements[entity_id] = MovementData(**kwargs)
    
    def update(self, entities: List[Entity], dt: float):
        """Update movement for all entities"""
        for entity in entities:
            if not hasattr(entity, 'id'):
                continue
                
            entity_id = entity.id
            if entity_id in self.entity_behaviors:
                behavior_name = self.entity_behaviors[entity_id]
                if behavior_name in self.behaviors:
                    behavior = self.behaviors[behavior_name]
                    movement_data = self.entity_movements.get(entity_id)
                    if movement_data:
                        behavior.update(entity, dt, movement_data)
    
    def set_target(self, entity_id: str, target: Tuple[float, float]):
        """Set target position for an entity"""
        if entity_id in self.entity_movements:
            self.entity_movements[entity_id].target_position = target
    
    def get_movement_data(self, entity_id: str) -> Optional[MovementData]:
        """Get movement data for an entity"""
        return self.entity_movements.get(entity_id)
    
    def create_default_config(self, config_path: str):
        """Create a default movement configuration file"""
        default_config = {
            "behaviors": [
                {
                    "name": "slow_linear",
                    "type": "linear",
                    "max_speed": 30.0,
                    "enabled": True
                },
                {
                    "name": "fast_linear",
                    "type": "linear",
                    "max_speed": 100.0,
                    "enabled": True
                },
                {
                    "name": "planet_orbit",
                    "type": "circular",
                    "center": [0.0, 0.0],
                    "radius": 150.0,
                    "angular_speed": 0.5,
                    "enabled": True
                },
                {
                    "name": "patrol_route",
                    "type": "patrol",
                    "waypoints": [
                        [100.0, 100.0],
                        [200.0, 100.0],
                        [200.0, 200.0],
                        [100.0, 200.0]
                    ],
                    "speed": 40.0,
                    "arrival_tolerance": 10.0,
                    "enabled": True
                },
                {
                    "name": "random_wander",
                    "type": "wander",
                    "speed": 25.0,
                    "direction_change_interval": 3.0,
                    "max_direction_change": 1.57,
                    "enabled": True
                },
                {
                    "name": "seek_target",
                    "type": "seek",
                    "speed": 50.0,
                    "max_force": 150.0,
                    "enabled": True
                }
            ]
        }
        
        try:
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=4)
            print(f"Created default movement config: {config_path}")
        except Exception as e:
            print(f"Error creating movement config: {e}")
