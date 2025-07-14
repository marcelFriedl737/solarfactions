# Solar Factions Documentation

## Overview

Solar Factions is a modular, tick-based space simulation system with JSON-configurable behaviors and components. This documentation provides comprehensive coverage of all systems, from basic usage to advanced customization.

## Documentation Structure

### Core Documentation
- **[README.md](README.md)** - Quick start guide and basic usage
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Comprehensive system architecture overview
- **[GAME_SYSTEMS.md](GAME_SYSTEMS.md)** - Game loop, movement, and AI systems
- **[COMPONENTS.md](COMPONENTS.md)** - JSON-based component system
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common issues and solutions
- **[ADVANCED_USAGE.md](ADVANCED_USAGE.md)** - Advanced patterns and optimization

### Quick Navigation

#### Getting Started
- [Installation and Setup](README.md#dependencies)
- [Your First Map](README.md#generate-and-display-a-map)
- [Command Line Interface](README.md#command-line-interface)
- [Interactive Mode](README.md#interactive-mode)

#### Core Systems
- [Game Loop System](GAME_SYSTEMS.md#game-loop-system)
- [Movement System](GAME_SYSTEMS.md#movement-system)
- [AI System](GAME_SYSTEMS.md#ai-system)
- [Component System](COMPONENTS.md#overview)
- [Game Manager](GAME_SYSTEMS.md#game-manager)

#### Configuration
- [Movement Behaviors](GAME_SYSTEMS.md#movement-system)
- [AI Behaviors](GAME_SYSTEMS.md#ai-system)
- [Component Definitions](COMPONENTS.md#component-definition-format)
- [Map Templates](README.md#available-templates)

#### Advanced Topics
- [Custom AI Behaviors](ADVANCED_USAGE.md#complex-ai-behaviors)
- [Custom Movement Patterns](ADVANCED_USAGE.md#custom-movement-patterns)
- [Performance Optimization](ADVANCED_USAGE.md#performance-optimization)
- [System Extensions](ADVANCED_USAGE.md#system-extensions)

## System Architecture

```
Solar Factions Architecture
├── Game Manager (Coordinator)
│   ├── Game Loop (Timing & Control)
│   │   ├── Update Thread (Game Logic)
│   │   └── Render Thread (Visual Updates)
│   ├── Movement System (Entity Movement)
│   ├── AI System (Intelligent Behavior)
│   └── Renderer (Visual Display)
├── Data Layer
│   ├── Data Manager (Persistence)
│   ├── Generator (Map Creation)
│   └── Component System (JSON Configuration)
└── Entity System
    ├── Entity (Core Entity Class)
    ├── Entity Factory (Entity Creation)
    └── Components (Modular Functionality)
```

## Key Features

### ✅ Tick-Based Game Loop
- Consistent timing at configurable TPS (Ticks Per Second)
- Frame-rate independent rendering
- Speed controls (0.1x - 10.0x)
- Pause/resume functionality
- Performance monitoring

### ✅ JSON-Configurable Systems
- **Movement Behaviors**: Linear, circular, patrol, orbit, wander, seek
- **AI Behaviors**: Idle, patrol, hunt, flee, guard, trade
- **Components**: Health, movement, combat, cargo, AI, and more
- **Map Templates**: Customizable map generation

### ✅ Component-Based Architecture
- Modular entity composition
- JSON-based component definitions
- Runtime component loading
- Automatic validation

### ✅ Performance Optimized
- Spatial partitioning for efficient entity lookups
- Object pooling for memory management
- Configurable update frequencies
- Comprehensive profiling tools

## Common Use Cases

### 1. Simple Space Simulation
```bash
# Generate and display a basic map
python main.py --template basic

# Run interactive game mode
python main.py --game
```

### 2. AI Behavior Testing
```bash
# Run headless simulation
python main.py --simulate 30

# Run behavior demo
python game_demo.py behavior
```

### 3. Custom Map Creation
```python
from game_manager import GameManager

game_manager = GameManager()
game_manager.generate_map("frontier", seed=42)
game_manager.save_map("my_custom_map")
```

### 4. Component Customization
```python
# Add custom component
entity.add_component('shield_generator', {
    'shield_capacity': 1000,
    'recharge_rate': 50.0
})
```

## File Structure

```
simple/
├── docs/                    # Documentation (this directory)
├── main.py                  # Main entry point
├── game_manager.py          # Game coordination
├── game_loop.py             # Tick-based timing
├── movement_system.py       # Movement behaviors
├── ai_system.py             # AI behaviors
├── renderer.py              # Visual display
├── entities/                # Entity system
│   └── entity.py           # Core entity class
├── data/                    # Configuration and data
│   ├── behaviors/          # AI and movement configs
│   ├── components/         # Component definitions
│   ├── templates/          # Map generation templates
│   ├── generated_maps/     # Generated maps
│   └── backups/            # Backup files
└── tests/                   # Test suite
```

## API Reference

### Core Classes

#### GameManager
```python
class GameManager:
    def __init__(data_path="data")
    def generate_map(template_name, seed=None)
    def load_map(map_name)
    def save_map(map_name)
    def run_interactive()
    def run_headless(duration)
    def start_game_loop()
    def pause_game()
    def resume_game()
    def set_game_speed(speed)
```

#### GameLoop
```python
class GameLoop:
    def __init__(target_tps=20, target_fps=60)
    def start()
    def stop()
    def pause()
    def resume()
    def set_speed(multiplier)
    def get_stats()
```

#### Entity
```python
class Entity:
    def __init__(entity_type, position, **properties)
    def add_component(component_type, **data)
    def get_component(component_type)
    def has_component(component_type)
    def set_property(key, value)
    def get_property(key, default=None)
```

### System APIs

#### Movement System
```python
movement_system.assign_behavior(entity_id, behavior_name)
movement_system.set_target(entity_id, target_position)
movement_system.get_movement_data(entity_id)
movement_system.load_config(config_path)
```

#### AI System
```python
ai_system.assign_ai_to_entity(entity, behavior_name)
ai_system.get_ai_state(entity_id)
ai_system.set_behavior(entity_id, behavior_name)
ai_system.load_config(config_path)
```

## Configuration Reference

### Movement Behaviors
```json
{
    "behaviors": [
        {
            "name": "patrol_route",
            "type": "patrol",
            "waypoints": [[100, 100], [200, 200]],
            "speed": 50.0,
            "arrival_tolerance": 10.0,
            "enabled": true
        }
    ]
}
```

### AI Behaviors
```json
{
    "behaviors": [
        {
            "name": "hunter_ai",
            "type": "hunt",
            "priority": 30,
            "detection_range": 150.0,
            "target_types": ["cargo_ship"],
            "energy_cost": 8.0,
            "enabled": true
        }
    ]
}
```

### Component Definitions
```json
{
    "health": {
        "description": "Health and damage system",
        "properties": {
            "max_health": {"type": "integer", "default": 100},
            "current_health": {"type": "integer", "default": 100},
            "shields": {"type": "integer", "default": 0}
        }
    }
}
```

## Performance Guidelines

### Recommended Settings
- **Small simulations**: 10-20 TPS, 30-60 FPS, <100 entities
- **Medium simulations**: 15-25 TPS, 30-60 FPS, 100-500 entities
- **Large simulations**: 10-20 TPS, 30 FPS, 500-1000 entities

### Optimization Tips
1. **Reduce Detection Ranges**: Lower AI detection ranges for better performance
2. **Use Spatial Partitioning**: Enable for large entity counts
3. **Optimize Behaviors**: Prefer simple behaviors over complex ones
4. **Monitor Performance**: Use built-in statistics and profiling
5. **Batch Operations**: Process entities in groups when possible

## Best Practices

### Code Organization
- Keep systems focused on single responsibilities
- Use JSON configuration for behavior parameters
- Implement proper error handling and validation
- Write tests for custom behaviors and components
- Document custom extensions

### Configuration Management
- Use version control for configuration files
- Keep backups of working configurations
- Test configuration changes incrementally
- Document custom behaviors and components
- Use meaningful names for behaviors and components

### Performance Monitoring
- Monitor TPS and FPS regularly
- Profile custom behaviors for performance
- Use spatial partitioning for large maps
- Implement object pooling for high-frequency objects
- Set appropriate memory limits

## Common Patterns

### Creating Custom Entities
```python
# Create entity with multiple components
ship = Entity('battleship', (400, 300), name='Defender')
ship.add_component('movement', max_speed=150.0)
ship.add_component('health', max_health=200, shields=100)
ship.add_component('combat', weapon_damage=25)
ship.add_component('ai', ai_type='aggressive')
```

### Implementing Custom Behaviors
```python
class CustomAI(AIBehavior):
    def _can_execute(self, entity, ai_state, entities):
        return True
    
    def _execute(self, entity, ai_state, entities, dt):
        # Custom behavior logic
        pass

ai_system.add_behavior('custom', CustomAI(config))
```

### Building Interactive Scenarios
```python
game_manager = GameManager()
game_manager.generate_map("warzone", seed=42)
game_manager.start_game_loop()
game_manager.run_interactive()
```

## Troubleshooting Quick Reference

### Common Issues
- **pygame not found**: Install with `pip install pygame`
- **Entities not moving**: Check if game loop is running and not paused
- **AI not working**: Verify AI configuration and behavior assignment
- **Performance issues**: Reduce entity count or behavior complexity
- **Configuration errors**: Validate JSON syntax and required fields

### Debug Tools
- **Debug mode**: Press 'D' in interactive mode
- **Performance stats**: `game_manager.game_loop.get_stats()`
- **Entity inspection**: `game_manager.get_entity_info(entity_id)`
- **System health**: Check [troubleshooting guide](TROUBLESHOOTING.md#system-health-check)

## Contributing

### Adding New Features
1. Follow existing code patterns
2. Write comprehensive tests
3. Update documentation
4. Add configuration examples
5. Consider performance impact

### Extending Systems
1. Inherit from base classes
2. Register new behaviors/components
3. Provide JSON configuration
4. Add validation logic
5. Document usage patterns

## Version History

### Current Version Features
- ✅ Tick-based game loop with timing controls
- ✅ JSON-configurable movement and AI systems
- ✅ Component-based entity architecture
- ✅ Interactive and headless operation modes
- ✅ Performance optimization tools
- ✅ Comprehensive documentation and examples

### Planned Features
- [ ] Network multiplayer support
- [ ] Advanced physics simulation
- [ ] Scripting system integration
- [ ] Enhanced visual effects
- [ ] Modding framework

## Resources

### Documentation
- [Architecture Guide](ARCHITECTURE.md) - System design and integration
- [Troubleshooting](TROUBLESHOOTING.md) - Common issues and solutions
- [Advanced Usage](ADVANCED_USAGE.md) - Complex patterns and optimization

### Examples
- [Basic Usage](README.md#examples) - Simple examples and patterns
- [Demo Scripts](../game_demo.py) - Interactive demonstrations
- [Test Suite](../tests/) - Comprehensive test examples

### Tools
- [Component Manager](../component_manager.py) - Component management utility
- [Demo Scripts](../demo_visual.py) - Visual demonstrations
- [Test Runner](../tests/test_system.py) - System validation

## Support

For questions, issues, or contributions:
1. Check the [troubleshooting guide](TROUBLESHOOTING.md)
2. Review existing [documentation](.)
3. Run the test suite to verify system health
4. Check the examples and demo scripts

This documentation provides comprehensive coverage of the Solar Factions system. Start with the [README](README.md) for basic usage, then explore the specific system documentation based on your needs.