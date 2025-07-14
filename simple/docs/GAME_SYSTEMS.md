# Game Systems Documentation

## Overview

Solar Factions now includes advanced game systems that provide tick-based gameplay, configurable movement behaviors, and intelligent AI systems. These systems work together to create dynamic, interactive gameplay while remaining highly configurable through JSON files.

## Table of Contents

1. [Game Loop System](#game-loop-system)
2. [Movement System](#movement-system)
3. [AI System](#ai-system)
4. [Game Manager](#game-manager)
5. [Configuration](#configuration)
6. [Examples](#examples)

## Game Loop System

The game loop system provides precise tick-based timing with frame-rate independent updates.

### Features

- **Tick-based updates**: Game logic runs at consistent intervals (default 20 TPS)
- **Frame-rate independent rendering**: Visual updates can run at different rates (default 60 FPS)
- **Speed control**: Adjust game speed from 0.1x to 10x
- **Pause/Resume**: Full control over game execution
- **Threading**: Separate threads for game logic and rendering
- **Statistics**: Real-time performance monitoring

### Usage

```python
from game_loop import GameLoop

# Create game loop
game_loop = GameLoop(target_tps=20, target_fps=60)

# Add systems
game_loop.add_update_system(my_update_function)
game_loop.add_render_system(my_render_function)

# Control execution
game_loop.start()
game_loop.set_speed(2.0)  # 2x speed
game_loop.pause()
game_loop.resume()
game_loop.stop()
```

### API Reference

#### GameLoop Class

- `GameLoop(target_tps, target_fps)`: Initialize game loop
- `start()`: Start the game loop
- `stop()`: Stop the game loop
- `pause()`: Pause game execution
- `resume()`: Resume game execution
- `set_speed(multiplier)`: Set game speed (0.1-10.0)
- `step()`: Execute single tick (for debugging)
- `get_stats()`: Get performance statistics

## Movement System

The movement system provides configurable movement behaviors for entities.

### Built-in Behaviors

1. **Linear Movement**: Simple velocity-based movement
2. **Circular Movement**: Circular motion around a center point
3. **Orbit Movement**: Orbit around another entity
4. **Patrol Movement**: Move between waypoints
5. **Wander Movement**: Random exploration
6. **Seek Movement**: Move toward a target position

### Configuration

Movement behaviors are configured in `data/behaviors/movement.json`:

```json
{
    "behaviors": [
        {
            "name": "fast_patrol",
            "type": "linear",
            "max_speed": 80.0,
            "enabled": true
        },
        {
            "name": "security_patrol",
            "type": "patrol",
            "waypoints": [
                [150.0, 150.0],
                [250.0, 150.0],
                [250.0, 250.0],
                [150.0, 250.0]
            ],
            "speed": 35.0,
            "arrival_tolerance": 12.0,
            "enabled": true
        }
    ]
}
```

### Usage

```python
from movement_system import MovementSystem

# Create movement system
movement_system = MovementSystem("data/behaviors/movement.json")

# Assign behavior to entity
movement_system.assign_behavior("entity_id", "fast_patrol")

# Set target position
movement_system.set_target("entity_id", (100.0, 100.0))

# Update all entities
movement_system.update(entities, delta_time)
```

### Creating Custom Behaviors

```python
from movement_system import MovementBehavior

class CustomMovement(MovementBehavior):
    def _update_movement(self, entity, dt, movement_data):
        # Custom movement logic here
        pass

# Register custom behavior
movement_system.add_behavior("custom", CustomMovement(config))
```

## AI System

The AI system provides intelligent behavior for entities through configurable AI behaviors.

### Built-in Behaviors

1. **Idle**: Default resting behavior with energy recovery
2. **Patrol**: Move between waypoints
3. **Hunt**: Search for and pursue targets
4. **Flee**: Escape from threats
5. **Guard**: Protect an area or entity
6. **Trade**: Move between trade points

### Configuration

AI behaviors are configured in `data/behaviors/ai.json`:

```json
{
    "behaviors": [
        {
            "name": "pirate_hunter",
            "type": "hunt",
            "priority": 25,
            "detection_range": 150.0,
            "target_types": ["cargo_ship", "mining_ship"],
            "memory_duration": 20.0,
            "energy_cost": 8.0,
            "enabled": true
        },
        {
            "name": "merchant_escape",
            "type": "flee",
            "priority": 35,
            "detection_range": 120.0,
            "threat_types": ["fighter"],
            "flee_range": 200.0,
            "energy_cost": 12.0,
            "enabled": true
        }
    ]
}
```

### Priority System

AI behaviors have priority levels. Higher priority behaviors will override lower priority ones when their conditions are met.

### Memory System

AI entities have memory that persists information about:
- Last seen targets and their positions
- Current goals and objectives
- General purpose data storage (blackboard)

### Usage

```python
from ai_system import AISystem

# Create AI system
ai_system = AISystem("data/behaviors/ai.json")

# Assign AI to entity
ai_system.assign_ai("entity_id", "pirate_hunter")

# Update all entities
ai_system.update(entities, delta_time)

# Get AI state
ai_state = ai_system.get_ai_state("entity_id")
print(f"Energy: {ai_state.energy}")
print(f"Behavior: {ai_state.behavior_name}")
```

### Creating Custom AI Behaviors

```python
from ai_system import AIBehavior

class CustomAI(AIBehavior):
    def _can_execute(self, entity, ai_state, entities):
        # Return True if behavior can execute
        return True
    
    def _execute(self, entity, ai_state, entities, dt):
        # Custom AI logic here
        pass

# Register custom behavior
ai_system.add_behavior("custom", CustomAI(config))
```

## AI-Component Integration

The AI system is fully integrated with the JSON-based component system, providing persistent AI behavior and configuration.

### AI Component Structure

The AI component stores persistent AI data:

```json
{
  "ai_type": "aggressive",
  "current_goal": "hunt_targets",
  "memory": {
    "last_seen_targets": {},
    "last_seen_times": {},
    "current_target": null,
    "goal_data": {},
    "blackboard": {}
  },
  "aggression_level": 0.8,
  "intelligence_level": 75
}
```

### AI Types

AI components support different types that determine default behaviors:

- **aggressive**: Defaults to hunt behaviors, high alertness
- **defensive**: Defaults to guard behaviors, balanced energy
- **merchant**: Defaults to trade behaviors, low aggression
- **basic**: Defaults to idle behaviors, standard settings

### Integration Features

#### Auto-Assignment
Entities with AI components automatically get AI behaviors assigned based on their component data:

```python
# AI system automatically detects and assigns AI from components
ai_system.auto_assign_ai_from_components(entities)
```

#### Real-time Synchronization
AI state is continuously synchronized with component data:

```python
# AI memory, goals, and state are saved to components
ai_system.update(entities, dt)  # Automatically syncs with components
```

#### Component-Based Configuration
AI behavior is modified by component properties:

```python
# High aggression increases alertness
entity.get_component('ai')['aggression_level'] = 0.9

# Intelligence affects behavior complexity
entity.get_component('ai')['intelligence_level'] = 85
```

#### Memory Persistence
AI memory is stored in components and persists across game sessions:

```python
# Memory data is automatically saved to component
ai_component = entity.get_component('ai')
memory = ai_component['memory']
# Contains last_seen_targets, goal_data, blackboard, etc.
```

### Usage Examples

#### Creating AI Entities
```python
from entities.entity import Entity, create_component

# Create entity with AI component
fighter = Entity('fighter', (100, 100), name='Hunter')
ai_component = create_component('ai',
                              ai_type='aggressive',
                              current_goal='patrol_sector',
                              aggression_level=0.8,
                              intelligence_level=70)
fighter.add_component('ai', **ai_component)

# AI system will automatically assign appropriate behavior
```

#### Direct AI Assignment with Components
```python
# Assign AI and create component simultaneously
ai_system.assign_ai_to_entity(entity, 'pirate_hunter',
                             aggression_level=0.9,
                             intelligence_level=85)
```

#### Dynamic AI Modification
```python
# Change AI behavior through component
ai_comp = entity.get_component('ai')
ai_comp['ai_type'] = 'defensive'
ai_comp['current_goal'] = 'defend_base'
ai_comp['aggression_level'] = 0.4

# Changes take effect on next update
```

### Benefits

1. **Persistence**: AI state survives game restarts
2. **Configuration**: Easy to modify AI through JSON/components
3. **Modularity**: AI behavior separated from entity logic
4. **Flexibility**: Mix and match AI types with entity types
5. **Debugging**: AI state visible in component data
6. **Extensibility**: New AI types can be added easily

## Game Manager

The Game Manager coordinates all systems and provides a high-level interface.

### Features

- **System Integration**: Coordinates game loop, movement, and AI systems
- **Map Management**: Generate and load maps
- **Interactive Mode**: Visual interface with controls
- **Headless Mode**: Non-visual simulation
- **Statistics**: Comprehensive performance and entity statistics

### Usage

```python
from game_manager import GameManager

# Create game manager
game_manager = GameManager()

# Generate map
game_manager.generate_map("frontier", seed=42)

# Run interactive mode
game_manager.run_interactive()

# Or run headless simulation
game_manager.run_headless(duration=10.0)
```

### Interactive Controls

- **SPACE**: Pause/Resume
- **+/-**: Increase/Decrease speed
- **S**: Single step (when paused)
- **D**: Toggle debug information
- **ESC**: Exit
- **Mouse**: Pan view and select entities
- **Mouse wheel**: Zoom

## Configuration

### Directory Structure

```
data/
├── behaviors/
│   ├── movement.json    # Movement behavior configurations
│   └── ai.json          # AI behavior configurations
├── components/
│   ├── components.json  # Core components
│   └── custom_components.json  # Custom components
└── templates/
    ├── basic.json       # Basic map template
    ├── frontier.json    # Frontier map template
    └── warzone.json     # Warzone map template
```

### Default Configuration Generation

Both movement and AI systems can generate default configurations:

```python
# Generate default movement config
movement_system.create_default_config("data/behaviors/movement.json")

# Generate default AI config
ai_system.create_default_config("data/behaviors/ai.json")
```

## Examples

### Basic Usage

```python
from game_manager import GameManager

# Create and run a simple simulation
game_manager = GameManager()
game_manager.generate_map("basic", seed=42)
game_manager.run_interactive()
```

### Custom Behavior Assignment

```python
# Create game manager
game_manager = GameManager()
game_manager.generate_map("frontier", seed=42)

# Find entities and assign custom behaviors
entities = game_manager.list_entities()
for entity_info in entities:
    if entity_info['type'] == 'fighter':
        # Make fighters more aggressive
        game_manager.ai_system.assign_ai(entity_info['id'], 'pirate_hunter')
        game_manager.movement_system.assign_behavior(entity_info['id'], 'fast_patrol')
```

### Performance Monitoring

```python
# Get comprehensive statistics
game_manager.print_statistics()

# Get game loop performance
stats = game_manager.game_loop.get_stats()
print(f"TPS: {stats['actual_tps']:.1f}")
print(f"FPS: {stats['actual_fps']:.1f}")
```

### Headless Simulation

```python
# Run automated simulation
game_manager = GameManager()
game_manager.generate_map("warzone", seed=123)
game_manager.run_headless(duration=30.0)  # Run for 30 seconds
```

## Best Practices

1. **Performance**: Keep behavior update logic efficient
2. **Configuration**: Use JSON files for easy behavior tuning
3. **Modularity**: Create reusable behavior components
4. **Testing**: Use headless mode for automated testing
5. **Debugging**: Use debug mode and single-step functionality
6. **Memory Management**: Clear unused entity data periodically

## Troubleshooting

### Common Issues

1. **Low Performance**: Reduce number of entities or behavior complexity
2. **Erratic Behavior**: Check behavior priority conflicts
3. **Memory Leaks**: Ensure proper cleanup of entity data
4. **Configuration Errors**: Validate JSON syntax and required fields

### Debug Information

Enable debug mode to see:
- Current tick and game time
- System performance metrics
- Entity counts and behaviors
- Memory usage statistics

### Performance Optimization

- Use appropriate tick rates (10-30 TPS for most games)
- Optimize behavior update loops
- Consider spatial partitioning for large entity counts
- Profile behavior execution times
