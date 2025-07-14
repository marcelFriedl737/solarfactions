# Advanced Usage Guide

## Table of Contents
1. [Advanced Entity Systems](#advanced-entity-systems)
2. [Complex AI Behaviors](#complex-ai-behaviors)
3. [Custom Movement Patterns](#custom-movement-patterns)
4. [Advanced Component Usage](#advanced-component-usage)
5. [Performance Optimization](#performance-optimization)
6. [Custom Map Generation](#custom-map-generation)
7. [System Extensions](#system-extensions)
8. [Integration Patterns](#integration-patterns)
9. [Advanced Debugging](#advanced-debugging)
10. [Production Deployment](#production-deployment)

## Advanced Entity Systems

### Hierarchical Entity Management

Create entities with parent-child relationships:

```python
from entities.entity import Entity
from game_manager import GameManager

class HierarchicalEntityManager:
    def __init__(self):
        self.game_manager = GameManager()
        self.entity_hierarchy = {}
        self.child_entities = {}
    
    def create_fleet(self, fleet_name, commander_pos, ships_data):
        """Create a fleet with a command ship and subordinates"""
        # Create command ship
        commander = Entity('command_ship', commander_pos, 
                         name=f"{fleet_name} Command",
                         fleet_id=fleet_name,
                         role='commander')
        
        # Add command and control components
        commander.add_component('command', {
            'subordinates': [],
            'formation': 'diamond',
            'orders': 'patrol_sector'
        })
        
        commander.add_component('communication', {
            'range': 500.0,
            'encryption': 'military',
            'frequency': 'fleet_command'
        })
        
        # Create subordinate ships
        subordinates = []
        for i, ship_data in enumerate(ships_data):
            ship_pos = (
                commander_pos[0] + ship_data.get('offset', [0, 0])[0],
                commander_pos[1] + ship_data.get('offset', [0, 0])[1]
            )
            
            ship = Entity(ship_data['type'], ship_pos,
                         name=f"{fleet_name} {ship_data['name']}",
                         fleet_id=fleet_name,
                         role='subordinate',
                         commander_id=commander.id)
            
            # Add subordinate components
            ship.add_component('subordinate', {
                'commander_id': commander.id,
                'formation_position': i,
                'follow_distance': ship_data.get('follow_distance', 50.0)
            })
            
            subordinates.append(ship)
        
        # Update commander's subordinate list
        commander.get_component('command')['subordinates'] = [s.id for s in subordinates]
        
        # Set up hierarchy tracking
        self.entity_hierarchy[commander.id] = [s.id for s in subordinates]
        for ship in subordinates:
            self.child_entities[ship.id] = commander.id
        
        return commander, subordinates
    
    def update_formation(self, commander_id, formation_type):
        """Update fleet formation"""
        if commander_id not in self.entity_hierarchy:
            return
        
        commander = self.find_entity_by_id(commander_id)
        if not commander:
            return
        
        subordinate_ids = self.entity_hierarchy[commander_id]
        formation_positions = self.calculate_formation_positions(
            commander.position, formation_type, len(subordinate_ids)
        )
        
        for i, sub_id in enumerate(subordinate_ids):
            subordinate = self.find_entity_by_id(sub_id)
            if subordinate:
                # Update formation position
                sub_comp = subordinate.get_component('subordinate')
                sub_comp['formation_position'] = i
                
                # Set movement target to formation position
                target_pos = formation_positions[i]
                self.game_manager.movement_system.set_target(sub_id, target_pos)
    
    def calculate_formation_positions(self, center_pos, formation_type, count):
        """Calculate positions for different formation types"""
        positions = []
        
        if formation_type == 'line':
            for i in range(count):
                offset_x = (i - count // 2) * 100
                positions.append((center_pos[0] + offset_x, center_pos[1]))
        
        elif formation_type == 'diamond':
            import math
            for i in range(count):
                angle = (2 * math.pi * i) / count
                radius = 80
                offset_x = math.cos(angle) * radius
                offset_y = math.sin(angle) * radius
                positions.append((center_pos[0] + offset_x, center_pos[1] + offset_y))
        
        elif formation_type == 'wedge':
            for i in range(count):
                row = i // 2
                side = i % 2
                offset_x = (side - 0.5) * 60 + row * 30
                offset_y = row * 80
                positions.append((center_pos[0] + offset_x, center_pos[1] + offset_y))
        
        return positions
    
    def find_entity_by_id(self, entity_id):
        """Find entity by ID in the current entity list"""
        for entity in self.game_manager.entities:
            if hasattr(entity, 'id') and entity.id == entity_id:
                return entity
        return None

# Usage example
manager = HierarchicalEntityManager()

# Create a patrol fleet
commander, subordinates = manager.create_fleet(
    "Alpha Fleet",
    (400, 300),
    [
        {'type': 'fighter', 'name': 'Alpha-1', 'offset': [50, 0], 'follow_distance': 40},
        {'type': 'fighter', 'name': 'Alpha-2', 'offset': [-50, 0], 'follow_distance': 40},
        {'type': 'fighter', 'name': 'Alpha-3', 'offset': [0, 50], 'follow_distance': 40},
        {'type': 'fighter', 'name': 'Alpha-4', 'offset': [0, -50], 'follow_distance': 40}
    ]
)

# Add to game manager
manager.game_manager.entities.extend([commander] + subordinates)

# Update formation
manager.update_formation(commander.id, 'diamond')
```

### Dynamic Entity Generation

Create entities dynamically based on game events:

```python
class DynamicEntityGenerator:
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.spawn_rules = []
        self.spawn_cooldowns = {}
    
    def add_spawn_rule(self, rule_name, condition_func, spawn_func, cooldown=5.0):
        """Add a rule for dynamic entity spawning"""
        self.spawn_rules.append({
            'name': rule_name,
            'condition': condition_func,
            'spawn': spawn_func,
            'cooldown': cooldown
        })
        self.spawn_cooldowns[rule_name] = 0.0
    
    def update(self, dt):
        """Check spawn conditions and create entities"""
        for rule in self.spawn_rules:
            # Update cooldown
            if rule['name'] in self.spawn_cooldowns:
                self.spawn_cooldowns[rule['name']] -= dt
            
            # Check if rule can execute
            if self.spawn_cooldowns[rule['name']] <= 0:
                if rule['condition'](self.game_manager.entities):
                    # Execute spawn function
                    new_entities = rule['spawn'](self.game_manager.entities)
                    if new_entities:
                        self.game_manager.entities.extend(new_entities)
                        self.spawn_cooldowns[rule['name']] = rule['cooldown']
    
    def create_trade_route_spawner(self):
        """Create spawner for trade route ships"""
        def trade_condition(entities):
            # Spawn if there are fewer than 3 cargo ships
            cargo_count = sum(1 for e in entities if e.type == 'cargo_ship')
            return cargo_count < 3
        
        def trade_spawn(entities):
            # Find stations for trade route
            stations = [e for e in entities if e.type == 'space_station']
            if len(stations) < 2:
                return None
            
            # Pick random start station
            import random
            start_station = random.choice(stations)
            
            # Create cargo ship
            cargo_ship = Entity('cargo_ship', start_station.position,
                              name=f"Trader {random.randint(1000, 9999)}",
                              origin_station=start_station.id)
            
            # Add trading components
            cargo_ship.add_component('trading', {
                'current_route': [s.id for s in stations[:2]],
                'cargo_capacity': 1000,
                'current_cargo': 0,
                'profit_margin': 0.15
            })
            
            cargo_ship.add_component('cargo', {
                'capacity': 1000,
                'current_load': 0,
                'manifest': []
            })
            
            return [cargo_ship]
        
        self.add_spawn_rule('trade_route', trade_condition, trade_spawn, 10.0)
    
    def create_patrol_spawner(self):
        """Create spawner for patrol ships"""
        def patrol_condition(entities):
            # Spawn patrol if there are pirates detected
            pirates = [e for e in entities if e.get_property('faction') == 'pirate']
            patrol_ships = [e for e in entities if e.get_property('role') == 'patrol']
            return len(pirates) > 0 and len(patrol_ships) < 2
        
        def patrol_spawn(entities):
            # Find a military base
            military_bases = [e for e in entities if e.type == 'military_base']
            if not military_bases:
                return None
            
            import random
            base = random.choice(military_bases)
            
            # Create patrol ship
            patrol_ship = Entity('fighter', base.position,
                               name=f"Patrol {random.randint(100, 999)}",
                               faction='military',
                               role='patrol',
                               home_base=base.id)
            
            # Add patrol components
            patrol_ship.add_component('patrol', {
                'patrol_radius': 200,
                'home_base': base.id,
                'alert_level': 'normal'
            })
            
            return [patrol_ship]
        
        self.add_spawn_rule('patrol', patrol_condition, patrol_spawn, 15.0)

# Usage
generator = DynamicEntityGenerator(game_manager)
generator.create_trade_route_spawner()
generator.create_patrol_spawner()

# Add to game loop
game_manager.game_loop.add_update_system(generator.update)
```

## Complex AI Behaviors

### State Machine AI

Create AI with complex state transitions:

```python
from ai_system import AIBehavior
from enum import Enum

class AIState(Enum):
    IDLE = "idle"
    PATROL = "patrol"
    INVESTIGATE = "investigate"
    ENGAGE = "engage"
    RETREAT = "retreat"
    REGROUP = "regroup"

class StateMachineAI(AIBehavior):
    def __init__(self, config):
        super().__init__(config)
        self.state_transitions = {
            AIState.IDLE: [AIState.PATROL, AIState.INVESTIGATE],
            AIState.PATROL: [AIState.IDLE, AIState.INVESTIGATE, AIState.ENGAGE],
            AIState.INVESTIGATE: [AIState.PATROL, AIState.ENGAGE, AIState.RETREAT],
            AIState.ENGAGE: [AIState.RETREAT, AIState.REGROUP],
            AIState.RETREAT: [AIState.REGROUP, AIState.IDLE],
            AIState.REGROUP: [AIState.PATROL, AIState.ENGAGE]
        }
    
    def _can_execute(self, entity, ai_state, entities):
        return True
    
    def _execute(self, entity, ai_state, entities, dt):
        current_state = AIState(ai_state.memory.get_data('current_state', AIState.IDLE.value))
        
        # Evaluate state transition conditions
        new_state = self.evaluate_state_transition(entity, ai_state, entities, current_state)
        
        if new_state != current_state:
            ai_state.memory.set_data('current_state', new_state.value)
            ai_state.memory.set_data('state_entry_time', ai_state.state_time)
            print(f"AI {entity.id} transitioning from {current_state.value} to {new_state.value}")
        
        # Execute state behavior
        self.execute_state_behavior(entity, ai_state, entities, new_state, dt)
    
    def evaluate_state_transition(self, entity, ai_state, entities, current_state):
        """Evaluate whether to transition to a new state"""
        # Check for threats
        threats = self.detect_threats(entity, entities)
        
        # Check health
        health_comp = entity.get_component('health')
        health_ratio = health_comp['current_health'] / health_comp['max_health'] if health_comp else 1.0
        
        # Check for allies
        allies = self.detect_allies(entity, entities)
        
        # State transition logic
        if current_state == AIState.IDLE:
            if threats:
                return AIState.INVESTIGATE
            elif ai_state.state_time > 5.0:  # Idle timeout
                return AIState.PATROL
        
        elif current_state == AIState.PATROL:
            if threats:
                return AIState.INVESTIGATE
            elif ai_state.state_time > 30.0:  # Patrol timeout
                return AIState.IDLE
        
        elif current_state == AIState.INVESTIGATE:
            if threats and len(threats) > 0:
                if health_ratio > 0.7:
                    return AIState.ENGAGE
                else:
                    return AIState.RETREAT
            elif ai_state.state_time > 10.0:  # Investigation timeout
                return AIState.PATROL
        
        elif current_state == AIState.ENGAGE:
            if health_ratio < 0.3:
                return AIState.RETREAT
            elif not threats:
                return AIState.PATROL
        
        elif current_state == AIState.RETREAT:
            if health_ratio > 0.8 and allies:
                return AIState.REGROUP
            elif not threats and ai_state.state_time > 15.0:
                return AIState.IDLE
        
        elif current_state == AIState.REGROUP:
            if len(allies) >= 2:
                return AIState.ENGAGE
            elif ai_state.state_time > 20.0:
                return AIState.PATROL
        
        return current_state
    
    def execute_state_behavior(self, entity, ai_state, entities, state, dt):
        """Execute behavior for the current state"""
        if state == AIState.IDLE:
            # Rest and recover
            ai_state.energy = min(100, ai_state.energy + dt * 5)
            ai_state.memory.set_data('target_position', entity.position)
        
        elif state == AIState.PATROL:
            # Patrol behavior
            patrol_points = ai_state.memory.get_data('patrol_points', [])
            if not patrol_points:
                # Generate patrol points around current position
                patrol_points = self.generate_patrol_points(entity.position)
                ai_state.memory.set_data('patrol_points', patrol_points)
            
            # Move to next patrol point
            current_target = ai_state.memory.get_data('current_patrol_target', 0)
            target_pos = patrol_points[current_target]
            
            # Check if reached target
            import math
            distance = math.sqrt((entity.position[0] - target_pos[0])**2 + 
                               (entity.position[1] - target_pos[1])**2)
            
            if distance < 30:
                current_target = (current_target + 1) % len(patrol_points)
                ai_state.memory.set_data('current_patrol_target', current_target)
            
            ai_state.memory.set_data('target_position', target_pos)
        
        elif state == AIState.INVESTIGATE:
            # Move toward last known threat position
            last_threat_pos = ai_state.memory.get_data('last_threat_position')
            if last_threat_pos:
                ai_state.memory.set_data('target_position', last_threat_pos)
        
        elif state == AIState.ENGAGE:
            # Engage closest threat
            threats = self.detect_threats(entity, entities)
            if threats:
                closest_threat = min(threats, key=lambda t: self.distance_to(entity, t))
                ai_state.memory.set_data('target_position', closest_threat.position)
                ai_state.memory.set_data('current_target', closest_threat.id)
        
        elif state == AIState.RETREAT:
            # Move away from threats
            threats = self.detect_threats(entity, entities)
            if threats:
                # Calculate retreat direction
                retreat_pos = self.calculate_retreat_position(entity, threats)
                ai_state.memory.set_data('target_position', retreat_pos)
        
        elif state == AIState.REGROUP:
            # Move toward allies
            allies = self.detect_allies(entity, entities)
            if allies:
                # Find center of allied group
                center_x = sum(a.position[0] for a in allies) / len(allies)
                center_y = sum(a.position[1] for a in allies) / len(allies)
                ai_state.memory.set_data('target_position', (center_x, center_y))
    
    def detect_threats(self, entity, entities):
        """Detect threatening entities"""
        threats = []
        entity_faction = entity.get_property('faction', 'neutral')
        
        for other in entities:
            if other.id == entity.id:
                continue
            
            other_faction = other.get_property('faction', 'neutral')
            if other_faction != entity_faction and other_faction != 'neutral':
                if self.distance_to(entity, other) < 150:
                    threats.append(other)
        
        return threats
    
    def detect_allies(self, entity, entities):
        """Detect allied entities"""
        allies = []
        entity_faction = entity.get_property('faction', 'neutral')
        
        for other in entities:
            if other.id == entity.id:
                continue
            
            other_faction = other.get_property('faction', 'neutral')
            if other_faction == entity_faction:
                if self.distance_to(entity, other) < 200:
                    allies.append(other)
        
        return allies
    
    def distance_to(self, entity1, entity2):
        """Calculate distance between entities"""
        import math
        return math.sqrt((entity1.position[0] - entity2.position[0])**2 + 
                        (entity1.position[1] - entity2.position[1])**2)
    
    def generate_patrol_points(self, center_pos):
        """Generate patrol points around a center position"""
        import math
        points = []
        for i in range(4):
            angle = (2 * math.pi * i) / 4
            radius = 100
            x = center_pos[0] + math.cos(angle) * radius
            y = center_pos[1] + math.sin(angle) * radius
            points.append((x, y))
        return points
    
    def calculate_retreat_position(self, entity, threats):
        """Calculate retreat position away from threats"""
        import math
        
        # Calculate direction away from threats
        avg_threat_x = sum(t.position[0] for t in threats) / len(threats)
        avg_threat_y = sum(t.position[1] for t in threats) / len(threats)
        
        # Direction away from threats
        dx = entity.position[0] - avg_threat_x
        dy = entity.position[1] - avg_threat_y
        
        # Normalize and scale
        length = math.sqrt(dx**2 + dy**2)
        if length > 0:
            dx /= length
            dy /= length
        
        # Retreat distance
        retreat_distance = 200
        retreat_x = entity.position[0] + dx * retreat_distance
        retreat_y = entity.position[1] + dy * retreat_distance
        
        return (retreat_x, retreat_y)

# Register the behavior
ai_system.add_behavior('state_machine', StateMachineAI({
    'name': 'state_machine',
    'priority': 30,
    'energy_cost': 5.0
}))
```

### Cooperative AI System

Create AI that coordinates with other entities:

```python
class CooperativeAI:
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.group_formations = {}
        self.shared_memory = {}
    
    def create_squad(self, entities, squad_id, formation='line'):
        """Create a cooperative squad"""
        self.group_formations[squad_id] = {
            'entities': [e.id for e in entities],
            'formation': formation,
            'leader': entities[0].id if entities else None,
            'target': None,
            'tactics': 'patrol'
        }
        
        # Assign roles
        for i, entity in enumerate(entities):
            entity.set_property('squad_id', squad_id)
            entity.set_property('squad_role', 'leader' if i == 0 else 'member')
            entity.set_property('squad_position', i)
    
    def update_squad_coordination(self, squad_id, dt):
        """Update squad coordination"""
        if squad_id not in self.group_formations:
            return
        
        formation = self.group_formations[squad_id]
        squad_entities = []
        
        # Get squad entities
        for entity in self.game_manager.entities:
            if hasattr(entity, 'id') and entity.id in formation['entities']:
                squad_entities.append(entity)
        
        if not squad_entities:
            return
        
        # Update formation positions
        leader = next((e for e in squad_entities if e.get_property('squad_role') == 'leader'), None)
        if leader:
            formation_positions = self.calculate_formation_positions(
                leader.position, formation['formation'], len(squad_entities)
            )
            
            # Assign positions to squad members
            for i, entity in enumerate(squad_entities):
                if entity.get_property('squad_role') != 'leader':
                    target_pos = formation_positions[i]
                    self.game_manager.movement_system.set_target(entity.id, target_pos)
    
    def share_intelligence(self, entity_id, intelligence_type, data):
        """Share intelligence between squad members"""
        entity = self.find_entity(entity_id)
        if not entity:
            return
        
        squad_id = entity.get_property('squad_id')
        if not squad_id:
            return
        
        # Store in shared memory
        if squad_id not in self.shared_memory:
            self.shared_memory[squad_id] = {}
        
        self.shared_memory[squad_id][intelligence_type] = {
            'data': data,
            'timestamp': time.time(),
            'source': entity_id
        }
        
        # Notify squad members
        for other_entity in self.game_manager.entities:
            if (other_entity.get_property('squad_id') == squad_id and 
                other_entity.id != entity_id):
                ai_state = self.game_manager.ai_system.get_ai_state(other_entity.id)
                if ai_state:
                    ai_state.memory.set_data(f'shared_{intelligence_type}', data)
    
    def calculate_formation_positions(self, leader_pos, formation, count):
        """Calculate formation positions relative to leader"""
        positions = []
        
        if formation == 'line':
            for i in range(count):
                offset = (i - count // 2) * 50
                positions.append((leader_pos[0] + offset, leader_pos[1] + 50))
        
        elif formation == 'wedge':
            for i in range(count):
                row = i // 2
                side = i % 2
                offset_x = (side - 0.5) * 40 + row * 20
                offset_y = row * 60
                positions.append((leader_pos[0] + offset_x, leader_pos[1] + offset_y))
        
        return positions
    
    def find_entity(self, entity_id):
        """Find entity by ID"""
        for entity in self.game_manager.entities:
            if hasattr(entity, 'id') and entity.id == entity_id:
                return entity
        return None

# Usage
cooperative_ai = CooperativeAI(game_manager)

# Create a squad
fighters = [e for e in entities if e.type == 'fighter'][:3]
cooperative_ai.create_squad(fighters, 'alpha_squad', 'wedge')

# Add to game loop
game_manager.game_loop.add_update_system(
    lambda dt: cooperative_ai.update_squad_coordination('alpha_squad', dt)
)
```

## Custom Movement Patterns

### Physics-Based Movement

Create realistic physics-based movement:

```python
from movement_system import MovementBehavior
import math

class PhysicsMovement(MovementBehavior):
    def __init__(self, config):
        super().__init__(config)
        self.gravity_sources = []
        self.physics_enabled = config.get('physics_enabled', True)
        self.drag_coefficient = config.get('drag_coefficient', 0.1)
        self.mass = config.get('mass', 1.0)
    
    def _update_movement(self, entity, dt, movement_data):
        if not self.physics_enabled:
            return super()._update_movement(entity, dt, movement_data)
        
        # Get current physics state
        velocity = movement_data.velocity
        position = entity.position
        
        # Calculate forces
        forces = [0.0, 0.0]
        
        # 1. Thrust force (toward target)
        thrust_force = self.calculate_thrust_force(entity, movement_data)
        forces[0] += thrust_force[0]
        forces[1] += thrust_force[1]
        
        # 2. Gravity forces
        gravity_force = self.calculate_gravity_force(entity, movement_data)
        forces[0] += gravity_force[0]
        forces[1] += gravity_force[1]
        
        # 3. Drag force
        drag_force = self.calculate_drag_force(velocity)
        forces[0] += drag_force[0]
        forces[1] += drag_force[1]
        
        # Apply forces to calculate acceleration
        acceleration = [forces[0] / self.mass, forces[1] / self.mass]
        
        # Update velocity
        velocity[0] += acceleration[0] * dt
        velocity[1] += acceleration[1] * dt
        
        # Apply velocity limits
        max_speed = movement_data.max_speed
        speed = math.sqrt(velocity[0]**2 + velocity[1]**2)
        if speed > max_speed:
            velocity[0] = (velocity[0] / speed) * max_speed
            velocity[1] = (velocity[1] / speed) * max_speed
        
        # Update position
        new_position = (
            position[0] + velocity[0] * dt,
            position[1] + velocity[1] * dt
        )
        
        entity.position = new_position
        movement_data.velocity = velocity
    
    def calculate_thrust_force(self, entity, movement_data):
        """Calculate thrust force toward target"""
        if not movement_data.target_position:
            return [0.0, 0.0]
        
        # Direction to target
        dx = movement_data.target_position[0] - entity.position[0]
        dy = movement_data.target_position[1] - entity.position[1]
        
        distance = math.sqrt(dx**2 + dy**2)
        if distance < 10:  # Close enough to target
            return [0.0, 0.0]
        
        # Normalize direction
        dx /= distance
        dy /= distance
        
        # Thrust magnitude
        thrust_magnitude = self.config.get('thrust_power', 50.0)
        
        return [dx * thrust_magnitude, dy * thrust_magnitude]
    
    def calculate_gravity_force(self, entity, movement_data):
        """Calculate gravitational forces from massive objects"""
        total_force = [0.0, 0.0]
        
        # Find gravity sources (stars, planets, etc.)
        for other in self.movement_system.entities:
            if other.id == entity.id:
                continue
            
            # Check if entity has mass
            mass_comp = other.get_component('physics')
            if not mass_comp or mass_comp.get('mass', 0) <= 0:
                continue
            
            # Calculate gravitational force
            dx = other.position[0] - entity.position[0]
            dy = other.position[1] - entity.position[1]
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance < 1:  # Avoid division by zero
                continue
            
            # Gravitational constant (scaled for game)
            G = 1000.0
            other_mass = mass_comp['mass']
            
            # Force magnitude
            force_magnitude = G * other_mass / (distance**2)
            
            # Force direction
            force_x = (dx / distance) * force_magnitude
            force_y = (dy / distance) * force_magnitude
            
            total_force[0] += force_x
            total_force[1] += force_y
        
        return total_force
    
    def calculate_drag_force(self, velocity):
        """Calculate drag force opposing motion"""
        speed = math.sqrt(velocity[0]**2 + velocity[1]**2)
        if speed < 0.1:
            return [0.0, 0.0]
        
        # Drag force opposes velocity
        drag_magnitude = self.drag_coefficient * speed**2
        
        # Normalize velocity direction
        drag_x = -(velocity[0] / speed) * drag_magnitude
        drag_y = -(velocity[1] / speed) * drag_magnitude
        
        return [drag_x, drag_y]

# Register physics movement
movement_system.add_behavior('physics', PhysicsMovement({
    'physics_enabled': True,
    'drag_coefficient': 0.05,
    'mass': 10.0,
    'thrust_power': 100.0
}))
```

### Swarm Movement

Create coordinated swarm behavior:

```python
class SwarmMovement(MovementBehavior):
    def __init__(self, config):
        super().__init__(config)
        self.neighbor_distance = config.get('neighbor_distance', 50.0)
        self.separation_distance = config.get('separation_distance', 20.0)
        self.alignment_strength = config.get('alignment_strength', 1.0)
        self.cohesion_strength = config.get('cohesion_strength', 1.0)
        self.separation_strength = config.get('separation_strength', 2.0)
    
    def _update_movement(self, entity, dt, movement_data):
        # Find nearby entities
        neighbors = self.find_neighbors(entity)
        
        # Calculate swarm forces
        separation = self.calculate_separation(entity, neighbors)
        alignment = self.calculate_alignment(entity, neighbors)
        cohesion = self.calculate_cohesion(entity, neighbors)
        
        # Combine forces
        total_force = [
            separation[0] * self.separation_strength +
            alignment[0] * self.alignment_strength +
            cohesion[0] * self.cohesion_strength,
            separation[1] * self.separation_strength +
            alignment[1] * self.alignment_strength +
            cohesion[1] * self.cohesion_strength
        ]
        
        # Apply force to velocity
        velocity = movement_data.velocity
        velocity[0] += total_force[0] * dt
        velocity[1] += total_force[1] * dt
        
        # Apply velocity to position
        new_position = (
            entity.position[0] + velocity[0] * dt,
            entity.position[1] + velocity[1] * dt
        )
        
        entity.position = new_position
        movement_data.velocity = velocity
    
    def find_neighbors(self, entity):
        """Find nearby entities for swarm calculation"""
        neighbors = []
        
        for other in self.movement_system.entities:
            if other.id == entity.id:
                continue
            
            # Check if same swarm
            if (entity.get_property('swarm_id') == other.get_property('swarm_id') and
                entity.get_property('swarm_id') is not None):
                
                distance = self.distance_to(entity, other)
                if distance < self.neighbor_distance:
                    neighbors.append(other)
        
        return neighbors
    
    def calculate_separation(self, entity, neighbors):
        """Calculate separation force to avoid crowding"""
        force = [0.0, 0.0]
        
        for neighbor in neighbors:
            distance = self.distance_to(entity, neighbor)
            if distance < self.separation_distance:
                # Calculate direction away from neighbor
                dx = entity.position[0] - neighbor.position[0]
                dy = entity.position[1] - neighbor.position[1]
                
                # Normalize and scale by inverse distance
                if distance > 0:
                    dx /= distance
                    dy /= distance
                    
                    strength = (self.separation_distance - distance) / self.separation_distance
                    force[0] += dx * strength
                    force[1] += dy * strength
        
        return force
    
    def calculate_alignment(self, entity, neighbors):
        """Calculate alignment force to match neighbor velocities"""
        if not neighbors:
            return [0.0, 0.0]
        
        # Average neighbor velocities
        avg_velocity = [0.0, 0.0]
        for neighbor in neighbors:
            neighbor_movement = self.movement_system.get_movement_data(neighbor.id)
            if neighbor_movement:
                avg_velocity[0] += neighbor_movement.velocity[0]
                avg_velocity[1] += neighbor_movement.velocity[1]
        
        avg_velocity[0] /= len(neighbors)
        avg_velocity[1] /= len(neighbors)
        
        # Calculate alignment force
        current_velocity = self.movement_system.get_movement_data(entity.id).velocity
        force = [
            avg_velocity[0] - current_velocity[0],
            avg_velocity[1] - current_velocity[1]
        ]
        
        return force
    
    def calculate_cohesion(self, entity, neighbors):
        """Calculate cohesion force to move toward group center"""
        if not neighbors:
            return [0.0, 0.0]
        
        # Calculate center of mass
        center = [0.0, 0.0]
        for neighbor in neighbors:
            center[0] += neighbor.position[0]
            center[1] += neighbor.position[1]
        
        center[0] /= len(neighbors)
        center[1] /= len(neighbors)
        
        # Calculate force toward center
        force = [
            center[0] - entity.position[0],
            center[1] - entity.position[1]
        ]
        
        return force
    
    def distance_to(self, entity1, entity2):
        """Calculate distance between entities"""
        import math
        return math.sqrt((entity1.position[0] - entity2.position[0])**2 + 
                        (entity1.position[1] - entity2.position[1])**2)

# Register swarm movement
movement_system.add_behavior('swarm', SwarmMovement({
    'neighbor_distance': 80.0,
    'separation_distance': 30.0,
    'alignment_strength': 1.5,
    'cohesion_strength': 1.0,
    'separation_strength': 2.0
}))
```

## Advanced Component Usage

### Dynamic Component Loading

Create a system for loading components at runtime:

```python
class DynamicComponentLoader:
    def __init__(self):
        self.component_cache = {}
        self.component_validators = {}
    
    def load_component_pack(self, pack_name, components_data):
        """Load a pack of related components"""
        for component_name, component_def in components_data.items():
            # Validate component definition
            if self.validate_component_definition(component_def):
                # Register component
                register_component(component_name, component_def)
                
                # Cache for quick access
                self.component_cache[component_name] = component_def
                
                print(f"Loaded component: {component_name}")
            else:
                print(f"Invalid component definition: {component_name}")
    
    def validate_component_definition(self, component_def):
        """Validate component definition structure"""
        required_fields = ['description', 'properties']
        
        for field in required_fields:
            if field not in component_def:
                return False
        
        # Validate properties
        for prop_name, prop_def in component_def['properties'].items():
            if 'type' not in prop_def:
                return False
            
            # Validate type
            valid_types = ['string', 'integer', 'float', 'boolean', 'array', 'object']
            if prop_def['type'] not in valid_types:
                return False
        
        return True
    
    def create_component_from_template(self, template_name, **overrides):
        """Create a component instance from a template"""
        if template_name not in self.component_cache:
            return None
        
        template = self.component_cache[template_name]
        component_data = {}
        
        # Apply defaults
        for prop_name, prop_def in template['properties'].items():
            component_data[prop_name] = prop_def.get('default', None)
        
        # Apply overrides
        for key, value in overrides.items():
            if key in template['properties']:
                component_data[key] = value
        
        return component_data

# Create advanced component examples
advanced_components = {
    'shield_generator': {
        'description': 'Advanced shield generation system',
        'properties': {
            'shield_capacity': {'type': 'integer', 'default': 1000},
            'recharge_rate': {'type': 'float', 'default': 50.0},
            'energy_efficiency': {'type': 'float', 'default': 0.8},
            'overload_protection': {'type': 'boolean', 'default': True},
            'harmonics': {'type': 'array', 'default': [1.0, 0.5, 0.25]}
        }
    },
    'jump_drive': {
        'description': 'Faster-than-light travel system',
        'properties': {
            'jump_range': {'type': 'float', 'default': 1000.0},
            'charge_time': {'type': 'float', 'default': 10.0},
            'energy_cost': {'type': 'integer', 'default': 500},
            'cooldown_time': {'type': 'float', 'default': 30.0},
            'accuracy': {'type': 'float', 'default': 0.95}
        }
    },
    'resource_processor': {
        'description': 'Advanced resource processing and refinement',
        'properties': {
            'processing_speed': {'type': 'float', 'default': 1.0},
            'efficiency_rating': {'type': 'float', 'default': 0.8},
            'supported_resources': {'type': 'array', 'default': ['ore', 'gas', 'crystal']},
            'output_quality': {'type': 'float', 'default': 1.0},
            'byproduct_generation': {'type': 'boolean', 'default': True}
        }
    }
}

# Load components
loader = DynamicComponentLoader()
loader.load_component_pack('advanced_systems', advanced_components)

# Use components
entity = Entity('advanced_ship', (400, 300))
shield_data = loader.create_component_from_template('shield_generator', 
                                                   shield_capacity=1500,
                                                   recharge_rate=75.0)
entity.add_component('shield_generator', **shield_data)
```

### Component Interaction System

Create a system for components to interact with each other:

```python
class ComponentInteractionSystem:
    def __init__(self):
        self.interaction_rules = {}
        self.component_dependencies = {}
    
    def register_interaction(self, component1, component2, interaction_func):
        """Register an interaction between two component types"""
        key = f"{component1}_{component2}"
        self.interaction_rules[key] = interaction_func
    
    def register_dependency(self, component, dependencies):
        """Register component dependencies"""
        self.component_dependencies[component] = dependencies
    
    def process_entity_interactions(self, entity, dt):
        """Process all component interactions for an entity"""
        if not hasattr(entity, 'components'):
            return
        
        component_names = list(entity.components.keys())
        
        # Process pairwise interactions
        for i, comp1 in enumerate(component_names):
            for comp2 in component_names[i+1:]:
                self.process_interaction(entity, comp1, comp2, dt)
    
    def process_interaction(self, entity, comp1_name, comp2_name, dt):
        """Process interaction between two components"""
        # Check both directions
        key1 = f"{comp1_name}_{comp2_name}"
        key2 = f"{comp2_name}_{comp1_name}"
        
        interaction_func = None
        if key1 in self.interaction_rules:
            interaction_func = self.interaction_rules[key1]
        elif key2 in self.interaction_rules:
            interaction_func = self.interaction_rules[key2]
        
        if interaction_func:
            comp1_data = entity.get_component(comp1_name)
            comp2_data = entity.get_component(comp2_name)
            
            try:
                interaction_func(entity, comp1_data, comp2_data, dt)
            except Exception as e:
                print(f"Error in component interaction {comp1_name}_{comp2_name}: {e}")
    
    def validate_dependencies(self, entity):
        """Validate that all component dependencies are satisfied"""
        missing_deps = []
        
        for comp_name in entity.components.keys():
            if comp_name in self.component_dependencies:
                required_deps = self.component_dependencies[comp_name]
                
                for dep in required_deps:
                    if not entity.has_component(dep):
                        missing_deps.append(f"{comp_name} requires {dep}")
        
        return missing_deps

# Create interaction system
interaction_system = ComponentInteractionSystem()

# Register interactions
def shield_power_interaction(entity, shield_data, power_data, dt):
    """Interaction between shield and power components"""
    # Shield consumes power
    power_needed = shield_data['recharge_rate'] * dt * 0.1
    
    if power_data['current_power'] >= power_needed:
        power_data['current_power'] -= power_needed
        
        # Recharge shields
        max_shields = shield_data['shield_capacity']
        current_shields = shield_data.get('current_shields', 0)
        
        if current_shields < max_shields:
            recharge_amount = shield_data['recharge_rate'] * dt
            shield_data['current_shields'] = min(max_shields, current_shields + recharge_amount)
    else:
        # Insufficient power - shields don't recharge
        shield_data['power_insufficient'] = True

def weapon_power_interaction(entity, weapon_data, power_data, dt):
    """Interaction between weapon and power components"""
    # Weapon charging
    if weapon_data.get('charging', False):
        power_needed = weapon_data['charge_rate'] * dt
        
        if power_data['current_power'] >= power_needed:
            power_data['current_power'] -= power_needed
            weapon_data['charge_level'] = min(100, weapon_data.get('charge_level', 0) + 10 * dt)
        else:
            weapon_data['charging'] = False

# Register interactions
interaction_system.register_interaction('shield_generator', 'power_core', shield_power_interaction)
interaction_system.register_interaction('weapon_system', 'power_core', weapon_power_interaction)

# Register dependencies
interaction_system.register_dependency('shield_generator', ['power_core'])
interaction_system.register_dependency('weapon_system', ['power_core'])

# Add to game loop
def update_component_interactions(dt):
    for entity in game_manager.entities:
        interaction_system.process_entity_interactions(entity, dt)

game_manager.game_loop.add_update_system(update_component_interactions)
```

## Performance Optimization

### Spatial Partitioning

Implement spatial partitioning for better performance:

```python
class SpatialGrid:
    def __init__(self, width, height, cell_size):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.cols = int(width / cell_size) + 1
        self.rows = int(height / cell_size) + 1
        self.grid = {}
        self.entity_locations = {}
    
    def clear(self):
        """Clear all entities from the grid"""
        self.grid = {}
        self.entity_locations = {}
    
    def add_entity(self, entity):
        """Add an entity to the spatial grid"""
        cell = self.get_cell(entity.position)
        
        if cell not in self.grid:
            self.grid[cell] = []
        
        self.grid[cell].append(entity)
        self.entity_locations[entity.id] = cell
    
    def remove_entity(self, entity):
        """Remove an entity from the spatial grid"""
        if entity.id in self.entity_locations:
            cell = self.entity_locations[entity.id]
            if cell in self.grid:
                self.grid[cell].remove(entity)
                if not self.grid[cell]:
                    del self.grid[cell]
            del self.entity_locations[entity.id]
    
    def update_entity(self, entity):
        """Update an entity's position in the grid"""
        new_cell = self.get_cell(entity.position)
        
        if entity.id in self.entity_locations:
            old_cell = self.entity_locations[entity.id]
            
            if old_cell != new_cell:
                # Remove from old cell
                if old_cell in self.grid:
                    self.grid[old_cell].remove(entity)
                    if not self.grid[old_cell]:
                        del self.grid[old_cell]
                
                # Add to new cell
                if new_cell not in self.grid:
                    self.grid[new_cell] = []
                self.grid[new_cell].append(entity)
                self.entity_locations[entity.id] = new_cell
    
    def get_cell(self, position):
        """Get the cell coordinates for a position"""
        col = int(position[0] / self.cell_size)
        row = int(position[1] / self.cell_size)
        return (col, row)
    
    def get_neighbors(self, entity, radius):
        """Get all entities within a radius"""
        neighbors = []
        entity_cell = self.get_cell(entity.position)
        
        # Calculate search radius in cells
        cell_radius = int(radius / self.cell_size) + 1
        
        # Search surrounding cells
        for col in range(entity_cell[0] - cell_radius, entity_cell[0] + cell_radius + 1):
            for row in range(entity_cell[1] - cell_radius, entity_cell[1] + cell_radius + 1):
                cell = (col, row)
                
                if cell in self.grid:
                    for other_entity in self.grid[cell]:
                        if other_entity.id != entity.id:
                            distance = self.calculate_distance(entity.position, other_entity.position)
                            if distance <= radius:
                                neighbors.append(other_entity)
        
        return neighbors
    
    def calculate_distance(self, pos1, pos2):
        """Calculate distance between two positions"""
        import math
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
    
    def get_entities_in_region(self, min_pos, max_pos):
        """Get all entities in a rectangular region"""
        entities = []
        
        min_cell = self.get_cell(min_pos)
        max_cell = self.get_cell(max_pos)
        
        for col in range(min_cell[0], max_cell[0] + 1):
            for row in range(min_cell[1], max_cell[1] + 1):
                cell = (col, row)
                
                if cell in self.grid:
                    for entity in self.grid[cell]:
                        if (min_pos[0] <= entity.position[0] <= max_pos[0] and
                            min_pos[1] <= entity.position[1] <= max_pos[1]):
                            entities.append(entity)
        
        return entities

# Optimized AI system using spatial partitioning
class OptimizedAISystem(AISystem):
    def __init__(self, config_path=None):
        super().__init__(config_path)
        self.spatial_grid = SpatialGrid(2000, 2000, 100)
        self.update_spatial_grid = True
    
    def update(self, entities, dt):
        """Update AI system with spatial optimization"""
        if self.update_spatial_grid:
            # Rebuild spatial grid
            self.spatial_grid.clear()
            for entity in entities:
                self.spatial_grid.add_entity(entity)
            self.update_spatial_grid = False
        
        # Update entities with spatial optimization
        for entity in entities:
            if hasattr(entity, 'id') and entity.id in self.entity_states:
                self.update_entity_optimized(entity, dt)
    
    def update_entity_optimized(self, entity, dt):
        """Update single entity with spatial optimization"""
        ai_state = self.entity_states[entity.id]
        
        # Get nearby entities efficiently
        nearby_entities = self.spatial_grid.get_neighbors(entity, 200)
        
        # Update AI with only nearby entities
        self.update_ai_state(entity, ai_state, nearby_entities, dt)
        
        # Update spatial grid if entity moved
        self.spatial_grid.update_entity(entity)
    
    def find_targets_optimized(self, entity, entities, detection_range):
        """Find targets using spatial optimization"""
        nearby_entities = self.spatial_grid.get_neighbors(entity, detection_range)
        
        targets = []
        for other in nearby_entities:
            if self.is_valid_target(entity, other):
                targets.append(other)
        
        return targets
```

### Object Pooling

Implement object pooling for better memory management:

```python
class ObjectPool:
    def __init__(self, object_class, initial_size=10):
        self.object_class = object_class
        self.available = []
        self.in_use = set()
        
        # Pre-allocate objects
        for _ in range(initial_size):
            obj = object_class()
            self.available.append(obj)
    
    def acquire(self, *args, **kwargs):
        """Get an object from the pool"""
        if self.available:
            obj = self.available.pop()
        else:
            obj = self.object_class()
        
        # Initialize object
        if hasattr(obj, 'initialize'):
            obj.initialize(*args, **kwargs)
        
        self.in_use.add(obj)
        return obj
    
    def release(self, obj):
        """Return an object to the pool"""
        if obj in self.in_use:
            self.in_use.remove(obj)
            
            # Clean up object
            if hasattr(obj, 'cleanup'):
                obj.cleanup()
            
            self.available.append(obj)
    
    def cleanup_unused(self, max_unused=20):
        """Clean up excess unused objects"""
        while len(self.available) > max_unused:
            self.available.pop()

# Pooled entity system
class PooledEntity:
    def __init__(self):
        self.reset()
    
    def initialize(self, entity_type, position, **properties):
        """Initialize the pooled entity"""
        self.type = entity_type
        self.position = position
        self.properties = properties
        self.components = {}
        self.id = str(uuid.uuid4())
        self.active = True
    
    def cleanup(self):
        """Clean up the entity for reuse"""
        self.reset()
    
    def reset(self):
        """Reset entity to default state"""
        self.type = None
        self.position = (0, 0)
        self.properties = {}
        self.components = {}
        self.id = None
        self.active = False

# Usage
entity_pool = ObjectPool(PooledEntity, 100)

def create_entity_optimized(entity_type, position, **properties):
    """Create entity using object pool"""
    entity = entity_pool.acquire(entity_type, position, **properties)
    return entity

def destroy_entity_optimized(entity):
    """Destroy entity and return to pool"""
    entity_pool.release(entity)
```

This advanced usage guide provides powerful patterns for building complex, high-performance space simulation systems. The examples show how to extend the basic Solar Factions system with sophisticated features while maintaining good performance and code organization.