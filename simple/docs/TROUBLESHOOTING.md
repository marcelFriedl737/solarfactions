# Solar Factions Troubleshooting Guide

## Table of Contents
1. [Common Issues](#common-issues)
2. [Performance Problems](#performance-problems)
3. [Configuration Issues](#configuration-issues)
4. [System Integration Problems](#system-integration-problems)
5. [Development and Testing Issues](#development-and-testing-issues)
6. [Debugging Tools](#debugging-tools)
7. [Error Messages](#error-messages)
8. [FAQ](#faq)

## Common Issues

### pygame Not Found

**Symptom:**
```
ModuleNotFoundError: No module named 'pygame'
```

**Solution:**
```bash
# Install pygame
pip install pygame

# Or for development
pip install pygame>=2.0
```

**Alternative Solution:**
Use headless mode to avoid pygame dependency:
```bash
# Run without renderer
python main.py --no-render

# Run headless simulation
python main.py --simulate 10

# Run game in headless mode
python game_demo.py headless
```

### Entity Not Moving

**Symptom:**
- Entities appear static in renderer
- AI behaviors seem inactive
- Movement system not responding

**Diagnosis:**
```python
# Check if game loop is running
game_manager = GameManager()
game_manager.generate_map("basic")
stats = game_manager.game_loop.get_stats()
print(f"Running: {stats['is_running']}")
print(f"Paused: {stats['is_paused']}")
```

**Solutions:**
1. **Start the game loop:**
```python
game_manager.start_game_loop()
```

2. **Check if paused:**
```python
if game_manager.game_loop.state.is_paused:
    game_manager.resume_game()
```

3. **Verify system registration:**
```python
# Check if systems are registered
loop_stats = game_manager.game_loop.get_stats()
print(f"Update systems: {loop_stats['update_systems']}")
print(f"Render systems: {loop_stats['render_systems']}")
```

### AI Behaviors Not Working

**Symptom:**
- Entities not following AI patterns
- AI energy not changing
- Behavior assignments not taking effect

**Diagnosis:**
```python
# Check AI system status
for entity in entities:
    if hasattr(entity, 'id'):
        ai_state = game_manager.ai_system.get_ai_state(entity.id)
        if ai_state:
            print(f"Entity {entity.id}: {ai_state.behavior_name}")
            print(f"  Energy: {ai_state.energy}")
            print(f"  Alertness: {ai_state.alertness}")
```

**Solutions:**
1. **Verify AI configuration:**
```python
# Check if AI config file exists
import os
ai_config_path = "data/behaviors/ai.json"
if not os.path.exists(ai_config_path):
    game_manager.ai_system.create_default_config(ai_config_path)
```

2. **Check behavior assignment:**
```python
# Manually assign AI behavior
game_manager.ai_system.assign_ai_to_entity(entity, 'default_idle')
```

3. **Verify component integration:**
```python
# Check if entity has AI component
if entity.has_component('ai'):
    ai_comp = entity.get_component('ai')
    print(f"AI Type: {ai_comp.get('ai_type')}")
    print(f"Current Goal: {ai_comp.get('current_goal')}")
```

### Map Generation Failures

**Symptom:**
```
Error generating map: Template 'template_name' not found
```

**Diagnosis:**
```python
# List available templates
generator = SimpleMapGenerator()
templates = generator.list_templates()
print(f"Available templates: {templates}")
```

**Solutions:**
1. **Use existing templates:**
```python
# Use basic template
entities = generator.generate_map('basic')

# Or frontier template
entities = generator.generate_map('frontier')
```

2. **Check template directory:**
```bash
ls -la data/templates/
```

3. **Create missing template:**
```python
# Create basic template if missing
template_data = {
    "name": "basic",
    "description": "Basic solar system",
    "entities": [
        {
            "type": "star",
            "count": 1,
            "properties": {"name": "Sol"}
        }
    ]
}
generator.data_manager.save_template('basic', template_data)
```

### Component Errors

**Symptom:**
```
KeyError: 'component_name'
AttributeError: 'Entity' object has no attribute 'components'
```

**Diagnosis:**
```python
# Check available components
from entities.entity import get_available_components
available = get_available_components()
print(f"Available components: {list(available.keys())}")
```

**Solutions:**
1. **Initialize component system:**
```python
# Ensure components are loaded
from entities.entity import load_components
load_components()
```

2. **Check component definitions:**
```python
# Verify component file exists
import os
component_file = "data/components/components.json"
if not os.path.exists(component_file):
    print(f"Component file missing: {component_file}")
```

3. **Create missing components:**
```python
# Create component safely
if 'movement' in get_available_components():
    entity.add_component('movement', max_speed=100.0)
else:
    print("Movement component not available")
```

## Performance Problems

### Low Frame Rate

**Symptom:**
- Choppy visual rendering
- FPS significantly below target
- Laggy user interactions

**Diagnosis:**
```python
# Check performance statistics
stats = game_manager.game_loop.get_stats()
print(f"Target FPS: {stats['target_fps']}")
print(f"Actual FPS: {stats['actual_fps']:.1f}")
print(f"Target TPS: {stats['target_tps']}")
print(f"Actual TPS: {stats['actual_tps']:.1f}")
```

**Solutions:**
1. **Reduce entity count:**
```python
# Generate smaller maps
entities = generator.generate_map('basic', seed=42)
print(f"Generated {len(entities)} entities")
```

2. **Lower target rates:**
```python
# Reduce TPS for better performance
game_loop = GameLoop(target_tps=15, target_fps=30)
```

3. **Optimize render frequency:**
```python
# Skip frames if needed
if stats['actual_fps'] < stats['target_fps'] * 0.8:
    # Reduce rendering complexity
    pass
```

### Memory Usage Issues

**Symptom:**
- Increasing memory consumption
- Eventual system slowdown
- Out of memory errors

**Diagnosis:**
```python
import psutil
import os

# Check memory usage
process = psutil.Process(os.getpid())
memory_info = process.memory_info()
print(f"Memory usage: {memory_info.rss / 1024 / 1024:.1f} MB")
```

**Solutions:**
1. **Clean up entity data:**
```python
# Clear unused entities
entities = [e for e in entities if hasattr(e, 'id')]
```

2. **Limit behavior memory:**
```python
# Clear old AI memory
for entity in entities:
    if hasattr(entity, 'id'):
        ai_state = game_manager.ai_system.get_ai_state(entity.id)
        if ai_state:
            ai_state.memory.clear_old_data(max_age=30.0)
```

3. **Optimize component data:**
```python
# Remove unnecessary component data
for entity in entities:
    if entity.has_component('movement'):
        # Clear old position history
        movement_comp = entity.get_component('movement')
        if 'position_history' in movement_comp:
            movement_comp['position_history'] = []
```

### Slow AI Processing

**Symptom:**
- Low TPS (ticks per second)
- Delayed AI responses
- Choppy entity behavior

**Diagnosis:**
```python
# Profile AI system performance
import time

start_time = time.time()
game_manager.ai_system.update(entities, 0.05)
ai_time = time.time() - start_time
print(f"AI update time: {ai_time:.3f}s")
```

**Solutions:**
1. **Reduce AI complexity:**
```python
# Use simpler AI behaviors
for entity in entities:
    if entity.type == 'cargo_ship':
        # Switch to idle instead of complex trading
        game_manager.ai_system.assign_ai_to_entity(entity, 'default_idle')
```

2. **Optimize behavior execution:**
```python
# Reduce AI update frequency for some entities
class OptimizedAISystem(AISystem):
    def update(self, entities, dt):
        # Update only half the entities each frame
        for i, entity in enumerate(entities):
            if i % 2 == self.frame_count % 2:
                super().update_entity(entity, dt)
        self.frame_count += 1
```

3. **Limit behavior ranges:**
```python
# Reduce detection ranges in AI config
ai_config = {
    "behaviors": [
        {
            "name": "efficient_hunt",
            "type": "hunt",
            "detection_range": 100.0,  # Reduced from 150.0
            "memory_duration": 10.0    # Reduced from 20.0
        }
    ]
}
```

## Configuration Issues

### Invalid JSON Configuration

**Symptom:**
```
JSONDecodeError: Expecting ',' delimiter: line 15 column 9
```

**Diagnosis:**
```python
import json

# Validate JSON file
try:
    with open("data/behaviors/ai.json", 'r') as f:
        config = json.load(f)
    print("JSON is valid")
except json.JSONDecodeError as e:
    print(f"JSON error: {e}")
```

**Solutions:**
1. **Use JSON validator:**
```bash
# Use online JSON validator or
python -m json.tool data/behaviors/ai.json
```

2. **Regenerate default config:**
```python
# Create fresh default configuration
game_manager.ai_system.create_default_config("data/behaviors/ai.json")
```

3. **Check common JSON errors:**
```json
{
    "behaviors": [
        {
            "name": "test_behavior",
            "type": "idle",
            "enabled": true  // Remove this comment
        }  // Remove trailing comma
    ]
}
```

### Missing Configuration Files

**Symptom:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'data/behaviors/movement.json'
```

**Solutions:**
1. **Create default configurations:**
```python
# Create all default config files
game_manager = GameManager()  # This creates missing configs
```

2. **Manual creation:**
```python
# Create movement config
movement_system = MovementSystem()
movement_system.create_default_config("data/behaviors/movement.json")

# Create AI config
ai_system = AISystem()
ai_system.create_default_config("data/behaviors/ai.json")
```

3. **Check directory structure:**
```bash
mkdir -p data/behaviors
mkdir -p data/components
mkdir -p data/templates
```

### Invalid Behavior Configuration

**Symptom:**
- Behaviors not executing
- Configuration validation errors
- Unexpected behavior patterns

**Diagnosis:**
```python
# Validate behavior configuration
movement_system = MovementSystem()
movement_system.load_config("data/behaviors/movement.json")

# Check loaded behaviors
for name, behavior in movement_system.behaviors.items():
    print(f"Behavior: {name}, Type: {behavior.behavior_type}")
```

**Solutions:**
1. **Verify required fields:**
```json
{
    "behaviors": [
        {
            "name": "required_field",
            "type": "required_field",
            "enabled": true
        }
    ]
}
```

2. **Check behavior parameters:**
```python
# Validate behavior parameters
behavior_config = {
    "name": "test_patrol",
    "type": "patrol",
    "waypoints": [[100, 100], [200, 200]],  # Required for patrol
    "speed": 50.0,
    "enabled": true
}
```

## System Integration Problems

### Systems Not Communicating

**Symptom:**
- AI sets targets but movement doesn't respond
- Movement updates don't reflect in AI
- Systems seem to work independently

**Diagnosis:**
```python
# Check system synchronization
entity_id = entities[0].id
ai_state = game_manager.ai_system.get_ai_state(entity_id)
movement_data = game_manager.movement_system.get_movement_data(entity_id)

print(f"AI target: {ai_state.memory.goal_data.get('target_position')}")
print(f"Movement target: {movement_data.target_position}")
```

**Solutions:**
1. **Verify sync method:**
```python
# Check if sync is being called
def debug_sync_ai_with_movement(self):
    for entity in self.entities:
        if hasattr(entity, 'id'):
            entity_id = entity.id
            ai_state = self.ai_system.get_ai_state(entity_id)
            if ai_state and 'target_position' in ai_state.memory.goal_data:
                target_pos = ai_state.memory.goal_data['target_position']
                print(f"Setting target for {entity_id}: {target_pos}")
                self.movement_system.set_target(entity_id, target_pos)
```

2. **Check system registration:**
```python
# Ensure systems are registered correctly
game_manager.game_loop.add_update_system(game_manager._update_game_logic)
```

### Component Synchronization Issues

**Symptom:**
- Component data not updating
- Changes not persisting
- Inconsistent component states

**Solutions:**
1. **Force component sync:**
```python
# Manually sync component data
for entity in entities:
    if entity.has_component('ai'):
        ai_comp = entity.get_component('ai')
        ai_state = game_manager.ai_system.get_ai_state(entity.id)
        if ai_state:
            ai_comp['current_goal'] = ai_state.memory.current_goal
            ai_comp['memory'] = ai_state.memory.to_dict()
```

2. **Verify component updates:**
```python
# Check if components are being updated
original_data = entity.get_component('ai').copy()
# ... run simulation ...
current_data = entity.get_component('ai')
print(f"Component changed: {original_data != current_data}")
```

## Development and Testing Issues

### Testing Framework Problems

**Symptom:**
- Tests fail unexpectedly
- Inconsistent test results
- Test environment issues

**Solutions:**
1. **Use isolated test environment:**
```python
# Create clean test environment
import tempfile
import os

test_dir = tempfile.mkdtemp()
os.chdir(test_dir)

# Create minimal test structure
os.makedirs("data/behaviors", exist_ok=True)
os.makedirs("data/components", exist_ok=True)
```

2. **Reset systems between tests:**
```python
def setUp(self):
    # Clean system state
    self.game_manager = GameManager()
    self.game_manager.entities = []
    self.game_manager.ai_system.entity_states = {}
    self.game_manager.movement_system.entity_behaviors = {}
```

### Development Environment Issues

**Symptom:**
- Import errors
- Module not found errors
- Path issues

**Solutions:**
1. **Set up proper Python path:**
```python
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
```

2. **Use relative imports:**
```python
# Instead of absolute imports
from entities.entity import Entity
from data_manager import DataManager
```

## Debugging Tools

### Performance Profiling

```python
import cProfile
import pstats

def profile_system():
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Run system
    game_manager.run_headless(5.0)
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)
```

### Entity State Inspection

```python
def inspect_entity_state(entity_id):
    """Comprehensive entity state inspection"""
    entity = None
    for e in entities:
        if hasattr(e, 'id') and e.id == entity_id:
            entity = e
            break
    
    if not entity:
        print(f"Entity {entity_id} not found")
        return
    
    print(f"=== Entity {entity_id} State ===")
    print(f"Type: {entity.type}")
    print(f"Position: {entity.position}")
    print(f"Properties: {entity.properties}")
    print(f"Components: {list(entity.components.keys())}")
    
    # AI state
    ai_state = game_manager.ai_system.get_ai_state(entity_id)
    if ai_state:
        print(f"AI Behavior: {ai_state.behavior_name}")
        print(f"AI Energy: {ai_state.energy}")
        print(f"AI Alertness: {ai_state.alertness}")
        print(f"AI Goal: {ai_state.memory.current_goal}")
        print(f"AI Target: {ai_state.memory.current_target}")
    
    # Movement state
    movement_data = game_manager.movement_system.get_movement_data(entity_id)
    if movement_data:
        print(f"Movement Behavior: {movement_data.behavior_name}")
        print(f"Velocity: {movement_data.velocity}")
        print(f"Target: {movement_data.target_position}")
```

### System Health Check

```python
def system_health_check():
    """Check overall system health"""
    print("=== System Health Check ===")
    
    # Game loop health
    stats = game_manager.game_loop.get_stats()
    print(f"Game Loop: {'OK' if stats['is_running'] else 'STOPPED'}")
    print(f"TPS: {stats['actual_tps']:.1f}/{stats['target_tps']}")
    print(f"FPS: {stats['actual_fps']:.1f}/{stats['target_fps']}")
    
    # System counts
    print(f"Entities: {len(entities)}")
    print(f"AI States: {len(game_manager.ai_system.entity_states)}")
    print(f"Movement Behaviors: {len(game_manager.movement_system.entity_behaviors)}")
    
    # Configuration health
    config_files = [
        "data/behaviors/movement.json",
        "data/behaviors/ai.json",
        "data/components/components.json"
    ]
    
    for config_file in config_files:
        if os.path.exists(config_file):
            print(f"Config {config_file}: OK")
        else:
            print(f"Config {config_file}: MISSING")
```

## Error Messages

### Common Error Messages and Solutions

#### "Entity has no attribute 'id'"
```python
# Solution: Ensure entity has ID
if not hasattr(entity, 'id'):
    entity.id = str(uuid.uuid4())
```

#### "Behavior 'name' not found"
```python
# Solution: Check available behaviors
available_behaviors = list(game_manager.ai_system.behaviors.keys())
print(f"Available behaviors: {available_behaviors}")
```

#### "Component 'name' not registered"
```python
# Solution: Load components
from entities.entity import load_components
load_components()
```

#### "Game loop not running"
```python
# Solution: Start game loop
game_manager.start_game_loop()
```

## FAQ

### Q: Why are my entities not moving?
A: Check if the game loop is running and not paused. Ensure movement behaviors are assigned and the movement system is registered.

### Q: How do I add custom AI behaviors?
A: Create a new behavior class inheriting from AIBehavior and register it with the AI system, or modify the ai.json configuration file.

### Q: Can I run the system without pygame?
A: Yes, use headless mode or the --no-render flag to avoid pygame dependency.

### Q: How do I optimize performance for large numbers of entities?
A: Reduce TPS, use simpler behaviors, implement spatial partitioning, and limit AI detection ranges.

### Q: Why are my configuration changes not taking effect?
A: Ensure the JSON is valid, restart the system, or call reload_config() on the relevant system.

### Q: How do I backup my game state?
A: Use the save_map() function or manually copy files from the data/generated_maps directory.

### Q: Can I extend the component system?
A: Yes, add new component definitions to custom_components.json or use the component_manager.py utility.

### Q: How do I debug AI behavior issues?
A: Use the debug mode (press D), inspect AI state with get_ai_state(), and check the AI configuration file.

### Q: What's the maximum number of entities the system can handle?
A: Typically 500-1000 entities at 60 FPS, but this depends on behavior complexity and hardware.

### Q: How do I create custom map templates?
A: Create JSON files in data/templates/ following the existing template format, or use the generator programmatically.

This troubleshooting guide should help resolve most common issues. For additional help, check the system logs and use the debugging tools provided.