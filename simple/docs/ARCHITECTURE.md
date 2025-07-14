# Solar Factions Architecture Overview

## Table of Contents
1. [System Overview](#system-overview)
2. [Core Architecture](#core-architecture)
3. [Data Flow](#data-flow)
4. [System Integration](#system-integration)
5. [Component Architecture](#component-architecture)
6. [Configuration System](#configuration-system)
7. [Threading Model](#threading-model)
8. [Performance Considerations](#performance-considerations)

## System Overview

Solar Factions is a modular space simulation system built around a tick-based game loop with JSON-configurable behaviors. The architecture emphasizes simplicity, modularity, and extensibility while maintaining high performance.

### Key Design Principles

1. **Separation of Concerns**: Each system has a single, well-defined responsibility
2. **JSON Configuration**: Behaviors and components are configurable without code changes
3. **Tick-Based Timing**: Consistent, predictable game logic execution
4. **Component-Based Entities**: Modular entity composition through JSON components
5. **Thread Safety**: Proper synchronization for concurrent operations

### System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                        Game Manager                              │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                   Game Loop                                 │ │
│  │  ┌─────────────────┐  ┌─────────────────┐                  │ │
│  │  │  Update Thread  │  │  Render Thread  │                  │ │
│  │  │                 │  │                 │                  │ │
│  │  │  ┌───────────┐  │  │  ┌───────────┐  │                  │ │
│  │  │  │AI System  │  │  │  │ Renderer  │  │                  │ │
│  │  │  └───────────┘  │  │  └───────────┘  │                  │ │
│  │  │  ┌───────────┐  │  │                 │                  │ │
│  │  │  │Movement   │  │  │                 │                  │ │
│  │  │  │System     │  │  │                 │                  │ │
│  │  │  └───────────┘  │  │                 │                  │ │
│  │  └─────────────────┘  └─────────────────┘                  │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      Data Layer                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │  Data Manager   │  │   Generator     │  │   Components    │ │
│  │                 │  │                 │  │                 │ │
│  │  ┌───────────┐  │  │  ┌───────────┐  │  │  ┌───────────┐  │ │
│  │  │Persistence│  │  │  │Templates  │  │  │  │JSON Defs  │  │ │
│  │  └───────────┘  │  │  └───────────┘  │  │  └───────────┘  │ │
│  │  ┌───────────┐  │  │  ┌───────────┐  │  │  ┌───────────┐  │ │
│  │  │Statistics │  │  │  │Algorithms │  │  │  │Validation │  │ │
│  │  └───────────┘  │  │  └───────────┘  │  │  └───────────┘  │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      Entity System                               │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │     Entity      │  │  Entity Factory │  │  Entity Store   │ │
│  │                 │  │                 │  │                 │ │
│  │  ┌───────────┐  │  │  ┌───────────┐  │  │  ┌───────────┐  │ │
│  │  │Properties │  │  │  │Templates  │  │  │  │Collections│  │ │
│  │  └───────────┘  │  │  └───────────┘  │  │  └───────────┘  │ │
│  │  ┌───────────┐  │  │  ┌───────────┐  │  │  ┌───────────┐  │ │
│  │  │Components │  │  │  │Factories  │  │  │  │Indexing   │  │ │
│  │  └───────────┘  │  │  └───────────┘  │  │  └───────────┘  │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Core Architecture

### Game Loop (game_loop.py)
The heart of the system providing precise timing and system coordination.

**Key Features:**
- Tick-based updates at configurable TPS (Ticks Per Second)
- Frame-rate independent rendering
- Speed controls (0.1x - 10.0x)
- Pause/resume functionality
- Threading separation for logic and rendering

**Architecture:**
```python
class GameLoop:
    - state: GameState          # Current game state
    - update_systems: List      # Game logic systems
    - render_systems: List      # Rendering systems
    - game_thread: Thread       # Logic thread
    - render_thread: Thread     # Render thread
```

### Movement System (movement_system.py)
Handles entity movement with JSON-configurable behaviors.

**Behavior Types:**
- Linear: Simple velocity-based movement
- Circular: Circular motion around a center
- Orbit: Orbit around other entities
- Patrol: Waypoint-based movement
- Wander: Random exploration
- Seek: Target-directed movement

**Configuration Format:**
```json
{
    "behaviors": [
        {
            "name": "fast_patrol",
            "type": "linear",
            "max_speed": 80.0,
            "enabled": true
        }
    ]
}
```

### AI System (ai_system.py)
Provides intelligent behavior with memory and priority systems.

**Behavior Types:**
- Idle: Default resting behavior
- Patrol: Area monitoring
- Hunt: Target pursuit
- Flee: Threat avoidance
- Guard: Area/entity protection
- Trade: Commerce routes

**Memory System:**
- Target tracking with timestamps
- Goal persistence
- Blackboard for general data
- Configurable memory duration

### Component System (entities/entity.py)
JSON-based modular entity composition.

**Core Components:**
- Movement: Speed, acceleration, fuel
- Health: Hit points, shields, armor
- Cargo: Storage and inventory
- Combat: Weapons and defense
- AI: Behavior and intelligence
- Trading: Economic interactions

## Data Flow

### Game Update Cycle

```
┌─────────────────────────────────────────────────────────────────┐
│                     Game Update Cycle                            │
│                                                                 │
│  1. Game Loop Tick                                              │
│     ┌─────────────────────────────────────────────────────────┐ │
│     │ Calculate Delta Time                                    │ │
│     │ Check Pause State                                       │ │
│     │ Apply Speed Multiplier                                  │ │
│     └─────────────────────────────────────────────────────────┘ │
│                             │                                   │
│                             ▼                                   │
│  2. AI System Update                                            │
│     ┌─────────────────────────────────────────────────────────┐ │
│     │ For Each Entity with AI:                                │ │
│     │   • Update AI State                                     │ │
│     │   • Process Memory                                      │ │
│     │   • Evaluate Behaviors                                  │ │
│     │   • Execute Highest Priority Behavior                  │ │
│     │   • Update Component Data                               │ │
│     └─────────────────────────────────────────────────────────┘ │
│                             │                                   │
│                             ▼                                   │
│  3. Movement System Update                                      │
│     ┌─────────────────────────────────────────────────────────┐ │
│     │ For Each Entity with Movement:                          │ │
│     │   • Process Movement Behavior                           │ │
│     │   • Update Position                                     │ │
│     │   • Handle Collisions                                   │ │
│     │   • Update Velocity                                     │ │
│     │   • Sync with Components                                │ │
│     └─────────────────────────────────────────────────────────┘ │
│                             │                                   │
│                             ▼                                   │
│  4. System Synchronization                                      │
│     ┌─────────────────────────────────────────────────────────┐ │
│     │ • Sync AI targets with Movement                         │ │
│     │ • Update Component data                                 │ │
│     │ • Process inter-entity interactions                     │ │
│     │ • Handle system events                                  │ │
│     └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Data Persistence Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                   Data Persistence Flow                          │
│                                                                 │
│  Entities ──────────────────────────────────────────────────────┐ │
│     │                                                           │ │
│     ▼                                                           │ │
│  Entity.to_dict()                                               │ │
│     │                                                           │ │
│     ▼                                                           │ │
│  JSON Serialization                                             │ │
│     │                                                           │ │
│     ▼                                                           │ │
│  File System Storage                                            │ │
│     │                                                           │ │
│     ▼                                                           │ │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │ │
│  │  Generated Maps │  │   Saved Maps    │  │    Backups     │ │ │
│  │                 │  │                 │  │                 │ │ │
│  │  • Test maps    │  │  • User saves   │  │  • Timestamped │ │ │
│  │  • Temp files   │  │  • Named saves  │  │  • Automatic   │ │ │
│  │  • Demos        │  │  • Checkpoints  │  │  • Manual      │ │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │ │
│                                                                 │ │
│  Loading Process (Reverse)                                      │ │
│     │                                                           │ │
│     ▼                                                           │ │
│  File System Read                                               │ │
│     │                                                           │ │
│     ▼                                                           │ │
│  JSON Deserialization                                           │ │
│     │                                                           │ │
│     ▼                                                           │ │
│  Entity.from_dict()                                             │ │
│     │                                                           │ │
│     ▼                                                           │ │
│  Entities ──────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## System Integration

### Game Manager Integration

The Game Manager serves as the central coordinator, integrating all systems:

```python
class GameManager:
    def __init__(self):
        # Core systems
        self.game_loop = GameLoop(target_tps=20, target_fps=60)
        self.movement_system = MovementSystem()
        self.ai_system = AISystem()
        self.data_manager = DataManager()
        self.generator = SimpleMapGenerator()
        self.renderer = SimpleRenderer()
        
        # Register systems with game loop
        self.game_loop.add_update_system(self._update_game_logic)
        self.game_loop.add_render_system(self._update_rendering)
```

### System Communication

Systems communicate through well-defined interfaces:

1. **Game Manager → Systems**: Configuration and control
2. **AI System → Movement System**: Target positions and movement goals
3. **Movement System → Entities**: Position and velocity updates
4. **All Systems → Components**: State persistence and data sharing

### Configuration Integration

All systems share a common configuration approach:

```
data/
├── behaviors/
│   ├── movement.json    # Movement behavior definitions
│   └── ai.json          # AI behavior definitions
├── components/
│   ├── components.json  # Core component definitions
│   └── custom_components.json  # User-defined components
└── templates/
    ├── basic.json       # Map generation templates
    ├── frontier.json
    └── warzone.json
```

## Component Architecture

### Entity Structure

```python
class Entity:
    def __init__(self, entity_type, position, **properties):
        self.type = entity_type
        self.position = position
        self.properties = properties
        self.components = {}        # JSON-based components
        self.id = generate_id()     # Unique identifier
```

### Component Definition Format

```json
{
    "component_name": {
        "description": "Component description",
        "properties": {
            "property_name": {
                "type": "type_name",
                "default": "default_value",
                "description": "Property description"
            }
        }
    }
}
```

### Component Integration

Components integrate with systems through:

1. **Auto-detection**: Systems automatically find relevant components
2. **Data binding**: Component data is synchronized with system state
3. **Validation**: Components validate data types and constraints
4. **Persistence**: Components are automatically saved/loaded

## Configuration System

### Configuration Loading Priority

1. **System Defaults**: Built-in sensible defaults
2. **Default Config Files**: Generated default configurations
3. **User Config Files**: User-modified configurations
4. **Runtime Overrides**: Programmatic configuration changes

### Configuration Validation

All configurations are validated for:
- JSON syntax correctness
- Required field presence
- Type consistency
- Value range validation
- Reference integrity

### Hot Reloading

Systems support configuration hot reloading:

```python
# Reload movement behaviors
movement_system.reload_config()

# Reload AI behaviors
ai_system.reload_config()
```

## Threading Model

### Thread Architecture

```
Main Thread
├── Event Processing
├── User Interface
└── System Control

Game Thread (Update)
├── AI System Updates
├── Movement System Updates
├── Physics Processing
└── State Synchronization

Render Thread
├── Visual Rendering
├── UI Updates
└── Frame Management
```

### Thread Synchronization

- **Thread Lock**: Protects shared entity data
- **Atomic Operations**: For simple state changes
- **Message Queues**: For inter-thread communication
- **State Snapshots**: For consistent rendering

### Thread Safety Guidelines

1. **Entity Access**: Always acquire lock before modifying entities
2. **System Updates**: Systems are single-threaded within their domain
3. **Configuration Changes**: Apply during synchronized periods
4. **Resource Cleanup**: Ensure proper cleanup on thread termination

## Performance Considerations

### Optimization Strategies

1. **Spatial Partitioning**: Optimize entity lookups and interactions
2. **Behavior Caching**: Cache frequently accessed behavior data
3. **Update Filtering**: Skip unnecessary updates for inactive entities
4. **Memory Pooling**: Reuse objects to reduce garbage collection
5. **Batch Processing**: Process entities in batches for better cache performance

### Performance Monitoring

Built-in performance monitoring tracks:
- Tick rate (TPS) and frame rate (FPS)
- System update times
- Memory usage
- Entity counts
- Behavior execution times

### Scalability Limits

Typical performance characteristics:
- **Entities**: 500-1000 active entities at 60 FPS
- **Behaviors**: 10-20 behavior types per system
- **Components**: 20-50 component types
- **Map Size**: 2000x2000 units effective area

### Performance Tuning

Key tuning parameters:
- **TPS**: Lower for strategy games (10-20), higher for action (30-60)
- **Update Frequency**: Balance between responsiveness and performance
- **Memory Limits**: Set appropriate limits for entity and component data
- **Spatial Granularity**: Optimize spatial partitioning cell size

## Best Practices

### System Design

1. **Single Responsibility**: Each system has one clear purpose
2. **Loose Coupling**: Systems communicate through well-defined interfaces
3. **Configuration Driven**: Behavior controlled through JSON files
4. **Fail Gracefully**: Handle errors without crashing the system
5. **Monitor Performance**: Track metrics and optimize bottlenecks

### Code Organization

1. **Consistent Naming**: Use clear, descriptive names
2. **Proper Documentation**: Document all public interfaces
3. **Error Handling**: Comprehensive error handling and logging
4. **Testing**: Unit tests for all core functionality
5. **Version Control**: Track configuration changes

### Configuration Management

1. **Default Values**: Always provide sensible defaults
2. **Validation**: Validate all configuration inputs
3. **Documentation**: Document all configuration options
4. **Backup**: Keep backups of working configurations
5. **Incremental Changes**: Make small, testable changes

This architecture provides a solid foundation for building complex space simulation games while maintaining simplicity and extensibility.