# ai_system.py - JSON-configurable AI system
"""
AI system for Solar Factions that supports various AI behaviors
configurable through JSON files.
"""

import json
import math
import random
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass, field
from entities.entity import Entity


@dataclass
class AIMemory:
    """Memory storage for AI entities"""
    last_seen_targets: Dict[str, Tuple[float, float]] = field(default_factory=dict)
    last_seen_times: Dict[str, float] = field(default_factory=dict)
    current_target: Optional[str] = None
    current_goal: Optional[str] = None
    goal_data: Dict[str, Any] = field(default_factory=dict)
    blackboard: Dict[str, Any] = field(default_factory=dict)  # General purpose data storage


@dataclass
class AIState:
    """Current state of an AI entity"""
    behavior_name: str = "idle"
    state_time: float = 0.0  # Time in current state
    energy: float = 100.0
    alertness: float = 0.0
    memory: AIMemory = field(default_factory=AIMemory)


class AIBehavior:
    """Base class for AI behaviors"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = config.get('name', 'unknown')
        self.enabled = config.get('enabled', True)
        self.priority = config.get('priority', 0)
        
    def can_execute(self, entity: Entity, ai_state: AIState, entities: List[Entity]) -> bool:
        """Check if this behavior can be executed"""
        if not self.enabled:
            return False
        return self._can_execute(entity, ai_state, entities)
    
    def execute(self, entity: Entity, ai_state: AIState, entities: List[Entity], dt: float) -> None:
        """Execute the behavior"""
        if not self.enabled:
            return
        ai_state.state_time += dt
        self._execute(entity, ai_state, entities, dt)
    
    def _can_execute(self, entity: Entity, ai_state: AIState, entities: List[Entity]) -> bool:
        """Override this method in subclasses"""
        return True
    
    def _execute(self, entity: Entity, ai_state: AIState, entities: List[Entity], dt: float) -> None:
        """Override this method in subclasses"""
        pass


class IdleBehavior(AIBehavior):
    """Default idle behavior"""
    
    def _execute(self, entity: Entity, ai_state: AIState, entities: List[Entity], dt: float) -> None:
        # Gradually reduce alertness
        ai_state.alertness = max(0, ai_state.alertness - 0.1 * dt)
        
        # Recover energy
        recovery_rate = self.config.get('energy_recovery_rate', 10.0)
        ai_state.energy = min(100.0, ai_state.energy + recovery_rate * dt)


class PatrolBehavior(AIBehavior):
    """Patrol behavior - move between waypoints"""
    
    def _can_execute(self, entity: Entity, ai_state: AIState, entities: List[Entity]) -> bool:
        return ai_state.energy > 20.0  # Need energy to patrol
    
    def _execute(self, entity: Entity, ai_state: AIState, entities: List[Entity], dt: float) -> None:
        waypoints = self.config.get('waypoints', [])
        if not waypoints:
            return
            
        # Get current waypoint index from goal data
        current_wp = ai_state.memory.goal_data.get('current_waypoint', 0)
        target_pos = waypoints[current_wp]
        
        if hasattr(entity, 'position'):
            x, y = entity.position
            target_x, target_y = target_pos
            
            # Calculate distance to target
            distance = math.sqrt((target_x - x)**2 + (target_y - y)**2)
            tolerance = self.config.get('arrival_tolerance', 10.0)
            
            if distance < tolerance:
                # Move to next waypoint
                ai_state.memory.goal_data['current_waypoint'] = (current_wp + 1) % len(waypoints)
            
            # Set target for movement system
            ai_state.memory.current_target = None  # Clear entity target
            ai_state.memory.goal_data['target_position'] = target_pos
        
        # Consume energy
        energy_cost = self.config.get('energy_cost', 2.0)
        ai_state.energy = max(0, ai_state.energy - energy_cost * dt)


class HuntBehavior(AIBehavior):
    """Hunt behavior - search for and pursue targets"""
    
    def _can_execute(self, entity: Entity, ai_state: AIState, entities: List[Entity]) -> bool:
        return ai_state.energy > 30.0  # Need energy to hunt
    
    def _execute(self, entity: Entity, ai_state: AIState, entities: List[Entity], dt: float) -> None:
        detection_range = self.config.get('detection_range', 100.0)
        target_types = self.config.get('target_types', ['cargo_ship', 'mining_ship'])
        
        if not hasattr(entity, 'position'):
            return
            
        x, y = entity.position
        current_time = ai_state.state_time
        
        # Search for targets
        closest_target = None
        closest_distance = float('inf')
        
        for target in entities:
            if target == entity or not hasattr(target, 'position'):
                continue
                
            # Check if target is of correct type
            target_type = getattr(target, 'type', 'unknown')
            if target_type not in target_types:
                continue
                
            # Calculate distance
            tx, ty = target.position
            distance = math.sqrt((tx - x)**2 + (ty - y)**2)
            
            if distance <= detection_range and distance < closest_distance:
                closest_target = target
                closest_distance = distance
        
        # Update memory with target
        if closest_target:
            target_id = getattr(closest_target, 'id', 'unknown')
            ai_state.memory.last_seen_targets[target_id] = closest_target.position
            ai_state.memory.last_seen_times[target_id] = current_time
            ai_state.memory.current_target = target_id
            ai_state.memory.goal_data['target_position'] = closest_target.position
            ai_state.alertness = min(100.0, ai_state.alertness + 50.0 * dt)
        else:
            # No target found, reduce alertness
            ai_state.alertness = max(0, ai_state.alertness - 10.0 * dt)
            
            # Check memory for recent targets
            memory_duration = self.config.get('memory_duration', 10.0)
            for target_id, last_seen_time in ai_state.memory.last_seen_times.items():
                if current_time - last_seen_time < memory_duration:
                    # Move to last known position
                    ai_state.memory.current_target = target_id
                    ai_state.memory.goal_data['target_position'] = ai_state.memory.last_seen_targets[target_id]
                    break
        
        # Consume energy
        energy_cost = self.config.get('energy_cost', 5.0)
        ai_state.energy = max(0, ai_state.energy - energy_cost * dt)


class FleeBehavior(AIBehavior):
    """Flee behavior - escape from threats"""
    
    def _can_execute(self, entity: Entity, ai_state: AIState, entities: List[Entity]) -> bool:
        # Flee when energy is low or alertness is high
        return ai_state.energy < 30.0 or ai_state.alertness > 70.0
    
    def _execute(self, entity: Entity, ai_state: AIState, entities: List[Entity], dt: float) -> None:
        detection_range = self.config.get('detection_range', 80.0)
        threat_types = self.config.get('threat_types', ['fighter'])
        
        if not hasattr(entity, 'position'):
            return
            
        x, y = entity.position
        
        # Find nearest threat
        nearest_threat = None
        nearest_distance = float('inf')
        
        for threat in entities:
            if threat == entity or not hasattr(threat, 'position'):
                continue
                
            # Check if entity is a threat
            threat_type = getattr(threat, 'type', 'unknown')
            if threat_type not in threat_types:
                continue
                
            # Calculate distance
            tx, ty = threat.position
            distance = math.sqrt((tx - x)**2 + (ty - y)**2)
            
            if distance <= detection_range and distance < nearest_distance:
                nearest_threat = threat
                nearest_distance = distance
        
        # Flee from threat
        if nearest_threat:
            tx, ty = nearest_threat.position
            
            # Calculate flee direction (opposite of threat)
            flee_x = x - tx
            flee_y = y - ty
            
            # Normalize and scale
            flee_distance = math.sqrt(flee_x**2 + flee_y**2)
            if flee_distance > 0:
                flee_range = self.config.get('flee_range', 200.0)
                flee_x = x + (flee_x / flee_distance) * flee_range
                flee_y = y + (flee_y / flee_distance) * flee_range
                
                ai_state.memory.goal_data['target_position'] = (flee_x, flee_y)
                ai_state.alertness = min(100.0, ai_state.alertness + 30.0 * dt)
        
        # Consume energy
        energy_cost = self.config.get('energy_cost', 8.0)
        ai_state.energy = max(0, ai_state.energy - energy_cost * dt)


class GuardBehavior(AIBehavior):
    """Guard behavior - protect an area or entity"""
    
    def _can_execute(self, entity: Entity, ai_state: AIState, entities: List[Entity]) -> bool:
        return ai_state.energy > 40.0  # Need energy to guard
    
    def _execute(self, entity: Entity, ai_state: AIState, entities: List[Entity], dt: float) -> None:
        guard_position = self.config.get('guard_position', (0.0, 0.0))
        guard_radius = self.config.get('guard_radius', 100.0)
        alert_range = self.config.get('alert_range', 150.0)
        
        if not hasattr(entity, 'position'):
            return
            
        x, y = entity.position
        guard_x, guard_y = guard_position
        
        # Calculate distance from guard position
        distance_from_post = math.sqrt((x - guard_x)**2 + (y - guard_y)**2)
        
        # Look for intruders
        intruder_found = False
        for other in entities:
            if other == entity or not hasattr(other, 'position'):
                continue
                
            ox, oy = other.position
            distance_to_other = math.sqrt((ox - guard_x)**2 + (oy - guard_y)**2)
            
            if distance_to_other <= alert_range:
                # Intruder detected
                intruder_found = True
                ai_state.alertness = min(100.0, ai_state.alertness + 40.0 * dt)
                
                # Move to intercept
                ai_state.memory.goal_data['target_position'] = (ox, oy)
                break
        
        if not intruder_found:
            # Return to guard position if too far
            if distance_from_post > guard_radius:
                ai_state.memory.goal_data['target_position'] = guard_position
            else:
                # Stay at post
                ai_state.memory.goal_data['target_position'] = entity.position
            
            ai_state.alertness = max(0, ai_state.alertness - 5.0 * dt)
        
        # Consume energy
        energy_cost = self.config.get('energy_cost', 3.0)
        ai_state.energy = max(0, ai_state.energy - energy_cost * dt)


class TradeBehavior(AIBehavior):
    """Trade behavior - move between trade points"""
    
    def _can_execute(self, entity: Entity, ai_state: AIState, entities: List[Entity]) -> bool:
        return ai_state.energy > 25.0  # Need energy to trade
    
    def _execute(self, entity: Entity, ai_state: AIState, entities: List[Entity], dt: float) -> None:
        trade_routes = self.config.get('trade_routes', [])
        if not trade_routes:
            return
            
        # Get current route progress
        current_route = ai_state.memory.goal_data.get('current_route', 0)
        current_point = ai_state.memory.goal_data.get('current_point', 0)
        
        if current_route >= len(trade_routes):
            current_route = 0
            
        route = trade_routes[current_route]
        if current_point >= len(route):
            # Move to next route
            current_route = (current_route + 1) % len(trade_routes)
            current_point = 0
            ai_state.memory.goal_data['current_route'] = current_route
            ai_state.memory.goal_data['current_point'] = current_point
            return
        
        target_pos = route[current_point]
        
        if hasattr(entity, 'position'):
            x, y = entity.position
            target_x, target_y = target_pos
            
            # Calculate distance to target
            distance = math.sqrt((target_x - x)**2 + (target_y - y)**2)
            tolerance = self.config.get('arrival_tolerance', 15.0)
            
            if distance < tolerance:
                # Arrived at trade point
                current_point += 1
                ai_state.memory.goal_data['current_point'] = current_point
                
                # Wait time at trade point
                wait_time = self.config.get('wait_time', 2.0)
                ai_state.memory.goal_data['wait_until'] = ai_state.state_time + wait_time
            
            # Check if we should wait
            wait_until = ai_state.memory.goal_data.get('wait_until', 0.0)
            if ai_state.state_time < wait_until:
                # Waiting at trade point
                ai_state.memory.goal_data['target_position'] = entity.position
            else:
                # Moving to target
                ai_state.memory.goal_data['target_position'] = target_pos
        
        # Consume energy
        energy_cost = self.config.get('energy_cost', 1.5)
        ai_state.energy = max(0, ai_state.energy - energy_cost * dt)


class AISystem:
    """System that manages all AI behaviors"""
    
    def __init__(self, config_path: str = None):
        self.behaviors: Dict[str, AIBehavior] = {}
        self.entity_ai_states: Dict[str, AIState] = {}
        
        # Register built-in behaviors
        self.behavior_classes = {
            'idle': IdleBehavior,
            'patrol': PatrolBehavior,
            'hunt': HuntBehavior,
            'flee': FleeBehavior,
            'guard': GuardBehavior,
            'trade': TradeBehavior
        }
        
        # Load configuration
        if config_path:
            self.load_config(config_path)
    
    def load_config(self, config_path: str):
        """Load AI configuration from JSON file"""
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
            print(f"AI config file not found: {config_path}")
        except json.JSONDecodeError as e:
            print(f"Error parsing AI config: {e}")
    
    def add_behavior(self, name: str, behavior: AIBehavior):
        """Add a custom AI behavior"""
        self.behaviors[name] = behavior
    
    def assign_ai(self, entity_id: str, initial_behavior: str = 'idle', create_component: bool = True, **kwargs):
        """Assign AI to an entity"""
        ai_state = AIState(behavior_name=initial_behavior, **kwargs)
        self.entity_ai_states[entity_id] = ai_state
        
        # Optionally create AI component if entity exists
        if create_component:
            # Find entity by ID
            entity = self._find_entity_by_id(entity_id)
            if entity:
                self._create_ai_component(entity, initial_behavior, **kwargs)
    
    def _find_entity_by_id(self, entity_id: str) -> Optional[Entity]:
        """Helper method to find entity by ID - can be overridden"""
        # This is a placeholder - in practice, you'd pass entities or have a registry
        return None
    
    def _create_ai_component(self, entity: Entity, initial_behavior: str, **kwargs):
        """Create an AI component for an entity"""
        from entities.entity import create_component
        
        # Determine AI type based on behavior
        ai_type = 'basic'
        if 'hunt' in initial_behavior or 'pirate' in initial_behavior:
            ai_type = 'aggressive'
        elif 'guard' in initial_behavior or 'defend' in initial_behavior:
            ai_type = 'defensive'
        elif 'trade' in initial_behavior or 'merchant' in initial_behavior:
            ai_type = 'merchant'
        
        # Create AI component
        try:
            ai_component = create_component('ai', 
                                          ai_type=ai_type,
                                          current_goal=kwargs.get('current_goal'),
                                          aggression_level=kwargs.get('aggression_level', 0.5),
                                          intelligence_level=kwargs.get('intelligence_level', 50))
            entity.add_component('ai', **ai_component)
        except Exception as e:
            print(f"Warning: Could not create AI component: {e}")
    
    def assign_ai_to_entity(self, entity: Entity, initial_behavior: str = 'idle', **kwargs):
        """Assign AI directly to an entity object"""
        if not hasattr(entity, 'id'):
            return
            
        entity_id = entity.id
        
        # Extract AI state kwargs vs component kwargs
        ai_state_kwargs = {}
        component_kwargs = {}
        
        for key, value in kwargs.items():
            if key in ['energy', 'alertness', 'state_time']:
                ai_state_kwargs[key] = value
            else:
                component_kwargs[key] = value
        
        ai_state = AIState(behavior_name=initial_behavior, **ai_state_kwargs)
        self.entity_ai_states[entity_id] = ai_state
        
        # Create AI component
        self._create_ai_component(entity, initial_behavior, **component_kwargs)
    
    def update(self, entities: List[Entity], dt: float):
        """Update AI for all entities"""
        # Auto-assign AI to entities with AI components
        self.auto_assign_ai_from_components(entities)
        
        for entity in entities:
            if not hasattr(entity, 'id'):
                continue
                
            entity_id = entity.id
            if entity_id not in self.entity_ai_states:
                continue
                
            ai_state = self.entity_ai_states[entity_id]
            
            # Sync with AI component if it exists
            self._sync_with_ai_component(entity, ai_state)
            
            # Find best behavior to execute
            best_behavior = None
            best_priority = -1
            
            for behavior in self.behaviors.values():
                if behavior.can_execute(entity, ai_state, entities):
                    if behavior.priority > best_priority:
                        best_behavior = behavior
                        best_priority = behavior.priority
            
            # Execute behavior
            if best_behavior:
                # Check if behavior changed
                if ai_state.behavior_name != best_behavior.name:
                    ai_state.behavior_name = best_behavior.name
                    ai_state.state_time = 0.0  # Reset state time
                
                best_behavior.execute(entity, ai_state, entities, dt)
                
                # Sync state back to component
                self._sync_with_ai_component(entity, ai_state)
    
    def get_ai_state(self, entity_id: str) -> Optional[AIState]:
        """Get AI state for an entity"""
        return self.entity_ai_states.get(entity_id)
    
    def set_behavior(self, entity_id: str, behavior_name: str):
        """Force an entity to use a specific behavior"""
        if entity_id in self.entity_ai_states:
            self.entity_ai_states[entity_id].behavior_name = behavior_name
            self.entity_ai_states[entity_id].state_time = 0.0
    
    def create_default_config(self, config_path: str):
        """Create a default AI configuration file"""
        default_config = {
            "behaviors": [
                {
                    "name": "default_idle",
                    "type": "idle",
                    "priority": 0,
                    "energy_recovery_rate": 15.0,
                    "enabled": True
                },
                {
                    "name": "security_patrol",
                    "type": "patrol",
                    "priority": 10,
                    "waypoints": [
                        [0.0, 0.0],
                        [100.0, 0.0],
                        [100.0, 100.0],
                        [0.0, 100.0]
                    ],
                    "arrival_tolerance": 15.0,
                    "energy_cost": 3.0,
                    "enabled": True
                },
                {
                    "name": "pirate_hunt",
                    "type": "hunt",
                    "priority": 20,
                    "detection_range": 120.0,
                    "target_types": ["cargo_ship", "mining_ship"],
                    "memory_duration": 15.0,
                    "energy_cost": 6.0,
                    "enabled": True
                },
                {
                    "name": "merchant_flee",
                    "type": "flee",
                    "priority": 30,
                    "detection_range": 100.0,
                    "threat_types": ["fighter"],
                    "flee_range": 250.0,
                    "energy_cost": 10.0,
                    "enabled": True
                },
                {
                    "name": "station_guard",
                    "type": "guard",
                    "priority": 15,
                    "guard_position": [0.0, 0.0],
                    "guard_radius": 80.0,
                    "alert_range": 150.0,
                    "energy_cost": 4.0,
                    "enabled": True
                },
                {
                    "name": "trade_run",
                    "type": "trade",
                    "priority": 8,
                    "trade_routes": [
                        [
                            [200.0, 200.0],
                            [400.0, 200.0],
                            [400.0, 400.0]
                        ],
                        [
                            [100.0, 300.0],
                            [300.0, 300.0]
                        ]
                    ],
                    "arrival_tolerance": 20.0,
                    "wait_time": 3.0,
                    "energy_cost": 2.0,
                    "enabled": True
                }
            ]
        }
        
        try:
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=4)
            print(f"Created default AI config: {config_path}")
        except Exception as e:
            print(f"Error creating AI config: {e}")
    
    def _sync_with_ai_component(self, entity: Entity, ai_state: AIState):
        """Sync AI state with entity's AI component if it exists"""
        ai_component = entity.get_component('ai')
        if ai_component:
            # Update AI state from component
            ai_state.memory.current_goal = ai_component.get('current_goal', ai_state.memory.current_goal)
            
            # Update component memory from AI state
            ai_component['memory'] = {
                'last_seen_targets': dict(ai_state.memory.last_seen_targets),
                'last_seen_times': dict(ai_state.memory.last_seen_times),
                'current_target': ai_state.memory.current_target,
                'current_goal': ai_state.memory.current_goal,
                'goal_data': dict(ai_state.memory.goal_data),
                'blackboard': dict(ai_state.memory.blackboard)
            }
            
            # Update component state
            ai_component['current_goal'] = ai_state.memory.current_goal
            
            # Use component aggression and intelligence for behavior modification
            aggression = ai_component.get('aggression_level', 0.5)
            intelligence = ai_component.get('intelligence_level', 50)
            
            # Modify AI behavior based on component properties
            if aggression > 0.7:
                ai_state.alertness = min(100.0, ai_state.alertness + 10.0)
            elif aggression < 0.3:
                ai_state.alertness = max(0.0, ai_state.alertness - 5.0)
    
    def _load_ai_from_component(self, entity: Entity) -> Optional[AIState]:
        """Load AI state from entity's AI component"""
        ai_component = entity.get_component('ai')
        if not ai_component:
            return None
            
        # Create AI state from component
        ai_state = AIState()
        
        # Load memory from component
        memory_data = ai_component.get('memory', {})
        if memory_data:
            ai_state.memory.last_seen_targets = memory_data.get('last_seen_targets', {})
            ai_state.memory.last_seen_times = memory_data.get('last_seen_times', {})
            ai_state.memory.current_target = memory_data.get('current_target')
            ai_state.memory.current_goal = memory_data.get('current_goal')
            ai_state.memory.goal_data = memory_data.get('goal_data', {})
            ai_state.memory.blackboard = memory_data.get('blackboard', {})
        
        # Load current goal
        ai_state.memory.current_goal = ai_component.get('current_goal')
        
        # Set default behavior based on AI type
        ai_type = ai_component.get('ai_type', 'basic')
        if ai_type == 'aggressive':
            ai_state.behavior_name = 'pirate_hunt'
            ai_state.energy = 80.0
            ai_state.alertness = 60.0
        elif ai_type == 'defensive':
            ai_state.behavior_name = 'station_guard'
            ai_state.energy = 90.0
            ai_state.alertness = 30.0
        elif ai_type == 'merchant':
            ai_state.behavior_name = 'trade_run'
            ai_state.energy = 70.0
            ai_state.alertness = 20.0
        else:
            ai_state.behavior_name = 'default_idle'
            ai_state.energy = 100.0
            ai_state.alertness = 0.0
        
        return ai_state
    
    def auto_assign_ai_from_components(self, entities: List[Entity]):
        """Automatically assign AI to entities that have AI components"""
        for entity in entities:
            if not hasattr(entity, 'id'):
                continue
                
            entity_id = entity.id
            
            # Skip if AI already assigned
            if entity_id in self.entity_ai_states:
                continue
                
            # Try to load AI from component
            ai_state = self._load_ai_from_component(entity)
            if ai_state:
                self.entity_ai_states[entity_id] = ai_state
                print(f"Auto-assigned AI to entity {entity_id} based on component")
