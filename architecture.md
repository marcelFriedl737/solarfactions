# Solar Factions - Architecture Document

## Overview
This document outlines the technical architecture for Solar Factions, designed to start simple with standalone proof-of-concepts while maintaining clear paths for future scalability and integration.

## Core Architecture Principles

### 1. Modular Design
- **Separation of Concerns**: Each system (world map, data schema, behavior scripting) as independent modules
- **Loose Coupling**: Modules communicate through well-defined interfaces
- **Plugin Architecture**: Easy to add new components without modifying existing code

### 2. Data-First Approach
- **Schema-Driven**: All game logic derived from data definitions
- **Serializable State**: Game world can be saved/loaded at any point
- **Configuration-Based**: Behavior and rules defined in external files

### 3. Object-Oriented Entity System
- **Inheritance Hierarchy**: Clean class-based structure for all entities
- **Polymorphism**: Common interfaces for similar entity types
- **Composition**: Modular components for behaviors and capabilities

### 3. Incremental Complexity
- **Start Simple**: Begin with file-based storage and single-threaded execution
- **Clear Upgrade Paths**: Each component designed with future scaling in mind
- **Backward Compatibility**: New features don't break existing functionality

## Phase 1: Foundation (Proof of Concepts)

### 1.1 World Map Generator (POC 1)
**Purpose**: Create and visualize the 2D space map with basic entities

**Technology Stack**:
- **Core**: Python 3.11+
- **Visualization**: pygame for 2D rendering
- **Data Storage**: JSON files for map definitions
- **Coordinates**: Simple 2D coordinate system (x, y)

**Components**:
```
world_map/
├── generator.py          # Map generation algorithms
├── renderer.py           # Visual representation
├── entities/
│   ├── __init__.py
│   ├── base.py           # Base Entity class
│   ├── objects.py        # SpaceObject hierarchy
│   ├── vessels.py        # Vessel hierarchy
│   ├── structures.py     # Station/structure hierarchy
│   └── resources.py      # Asteroid/resource hierarchy
├── coordinates.py        # 2D coordinate system
└── data/
    ├── map_templates.json
    ├── entity_types.json
    └── generated_maps/
```

**Key Features**:
- Procedural map generation
- Entity placement algorithms
- Basic collision detection
- Export to various formats (JSON, image)

### 1.2 Data Schema Framework (POC 2)
**Purpose**: Define and validate all game data structures

**Technology Stack**:
- **Validation**: Pydantic for data models and validation
- **Storage**: JSON files with schema validation
- **Configuration**: YAML for human-readable configs

**Components**:
```
data_schema/
├── models/
│   ├── base/
│   │   ├── entity.py     # Base Entity class
│   │   └── mixins.py     # Shared functionality mixins
│   ├── entities/
│   │   ├── objects.py    # SpaceObject → Vessel → Ship → ShipClass
│   │   ├── vessels.py    # Vessel types and hierarchies
│   │   ├── structures.py # Station → StationType hierarchy
│   │   └── resources.py  # Asteroid → ResourceType hierarchy
│   ├── actors.py         # AI actor definitions
│   ├── economy.py        # Trade, production models
│   └── world.py          # Map, region models
├── validators.py         # Data validation logic
├── serializers.py        # JSON/YAML serialization
└── schemas/
    ├── entities.json
    ├── actors.json
    └── world.json
```

**Key Features**:
- Type-safe data models
- Automatic validation
- Schema evolution support
- Export/import functionality

### 1.2.1 Entity Inheritance Hierarchy
**Design Philosophy**: Clean object-oriented design with logical inheritance chains

**Base Entity Structure**:
```python
Entity (Abstract Base Class)
├── id: UUID
├── position: Coordinates
├── created_at: datetime
├── updated_at: datetime
├── metadata: Dict
└── methods: update(), serialize(), validate()
```

**Inheritance Chains**:

```
Entity
├── SpaceObject
│   ├── Vessel
│   │   ├── Ship
│   │   │   ├── CargoShip
│   │   │   │   ├── FreighterClass
│   │   │   │   ├── TankerClass
│   │   │   │   └── ContainerClass
│   │   │   ├── CombatShip
│   │   │   │   ├── FighterClass
│   │   │   │   ├── CruiserClass
│   │   │   │   └── BattleshipClass
│   │   │   ├── UtilityShip
│   │   │   │   ├── MiningShip
│   │   │   │   ├── ExplorationShip
│   │   │   │   └── RepairShip
│   │   │   └── SpecialtyShip
│   │   │       ├── DiplomaticShip
│   │   │       └── ResearchShip
│   │   └── Drone
│   │       ├── MiningDrone
│   │       ├── CombatDrone
│   │       └── ScoutDrone
│   ├── Structure
│   │   ├── Station
│   │   │   ├── TradingStation
│   │   │   │   ├── TradingPost
│   │   │   │   ├── CommercialHub
│   │   │   │   └── MarketCenter
│   │   │   ├── IndustrialStation
│   │   │   │   ├── Factory
│   │   │   │   ├── Refinery
│   │   │   │   └── Shipyard
│   │   │   ├── MilitaryStation
│   │   │   │   ├── Fortress
│   │   │   │   ├── NavalBase
│   │   │   │   └── Outpost
│   │   │   └── CivilianStation
│   │   │       ├── ResearchLab
│   │   │       ├── Colony
│   │   │       └── Habitat
│   │   └── Installation
│   │       ├── JumpGate
│   │       ├── Beacon
│   │       └── Sensor Array
│   └── NaturalObject
│       ├── Asteroid
│       │   ├── MetallicAsteroid
│       │   ├── CarbonaceousAsteroid
│       │   ├── SilicateAsteroid
│       │   └── IceAsteroid
│       ├── Comet
│       └── Nebula
└── Actor (AI Entity)
    ├── Individual
    │   ├── ShipCaptain
    │   ├── StationCommander
    │   └── Agent
    └── Organization
        ├── Faction
        ├── Corporation
        └── Guild
```

**Class Responsibilities**:
- **Entity**: Base functionality, serialization, identification
- **SpaceObject**: Physical presence, coordinates, collision
- **Vessel**: Movement, crew, cargo capacity
- **Ship**: Combat capabilities, upgrade slots, maintenance
- **ShipClass**: Specific stats, hardpoints, role optimization
- **Structure**: Fixed position, production, services
- **Station**: Complex operations, multiple modules
- **NaturalObject**: Resource content, environmental effects

### 1.3 Behavior Scripting Engine (POC 3)
**Purpose**: Configuration-driven AI actor behaviors with minimal code changes

**Technology Stack**:
- **Configuration**: YAML/JSON for behavior definitions
- **Behavior Trees**: Configuration-based tree construction
- **Decision Making**: Rule-based system with weighted choices
- **Runtime Loading**: Hot-reload of behavior configurations
- **Validation**: Schema validation for behavior configs

**Components**:
```
behavior_engine/
├── core/
│   ├── behavior_loader.py     # Configuration file loader
│   ├── behavior_validator.py  # Schema validation
│   ├── behavior_interpreter.py # Config-to-behavior translation
│   └── hot_reload.py          # Runtime configuration updates
├── actors/
│   ├── base_actor.py          # Abstract actor class
│   ├── config_driven_actor.py # Configuration-based actor
│   └── actor_factory.py       # Actor creation from configs
├── primitives/
│   ├── conditions.py          # Configurable condition checks
│   ├── actions.py             # Configurable action library
│   ├── selectors.py           # Behavior tree selectors
│   └── decorators.py          # Behavior modifiers
├── templates/
│   ├── ship_templates.yml     # Ship behavior templates
│   ├── station_templates.yml  # Station behavior templates
│   └── faction_templates.yml  # Faction behavior templates
└── configs/
    ├── entities/
    │   ├── ships/
    │   │   ├── cargo_ship.yml
    │   │   ├── combat_ship.yml
    │   │   └── mining_ship.yml
    │   ├── stations/
    │   │   ├── trading_station.yml
    │   │   ├── factory.yml
    │   │   └── military_base.yml
    │   └── factions/
    │       ├── traders_guild.yml
    │       ├── mining_corp.yml
    │       └── pirates.yml
    ├── behaviors/
    │   ├── trading.yml
    │   ├── combat.yml
    │   ├── exploration.yml
    │   └── production.yml
    └── schemas/
        ├── behavior_schema.json
        ├── condition_schema.json
        └── action_schema.json
```
│   ├── combat.py         # Combat behaviors
│   ├── exploration.py    # Exploration patterns
│   └── production.py     # Production management
├── decision_engine.py    # Core decision logic
└── scripts/
    ├── trader_behaviors.yml
    ├── combat_tactics.yml
    └── exploration_patterns.yml
```

**Key Features**:
- Configuration-driven behavior trees
- Hot-reload capability for runtime changes
- Schema validation for behavior configs
- Template-based behavior inheritance
- Visual behavior tree editor (future)
- No-code behavior modification

### 1.3.1 Configuration-Driven Behavior System
**Design Philosophy**: Behaviors defined in configuration files, not code

**Configuration-Based Behavior Trees**:
```yaml
# Example: cargo_ship_trading.yml
behavior_name: "Cargo Ship Trading"
entity_types: ["CargoShip", "FreighterClass"]
priority: 100

behavior_tree:
  type: "selector"  # Try each child until one succeeds
  children:
    - type: "sequence"  # All must succeed
      name: "Emergency Actions"
      children:
        - type: "condition"
          condition: "hull_integrity < 0.3"
        - type: "action"
          action: "seek_repair_station"
          parameters:
            max_distance: 50
            urgency: "high"
    
    - type: "sequence"
      name: "Trading Sequence"
      children:
        - type: "condition"
          condition: "cargo_space_available > 0.1"
        - type: "selector"
          children:
            - type: "sequence"
              name: "Fulfill Contract"
              children:
                - type: "condition"
                  condition: "has_active_contract"
                - type: "action"
                  action: "navigate_to_delivery"
            - type: "sequence"
              name: "Find New Trade"
              children:
                - type: "action"
                  action: "scan_nearby_markets"
                  parameters:
                    scan_radius: 25
                    commodity_filter: ["metals", "food", "technology"]
                - type: "condition"
                  condition: "profitable_trade_found"
                - type: "action"
                  action: "execute_trade"
                  parameters:
                    profit_margin_min: 0.15
                    risk_tolerance: 0.3

personality_modifiers:
  risk_tolerance: 0.4    # Affects decision weights
  profit_focus: 0.8      # Prioritizes profitable actions
  loyalty: 0.6           # Affects faction-related decisions
```

**Condition Library Configuration**:
```yaml
# conditions.yml - Reusable condition definitions
conditions:
  hull_integrity:
    type: "entity_property"
    property: "hull.integrity"
    comparison: "numeric"
    
  cargo_space_available:
    type: "calculated"
    formula: "(cargo.max_capacity - cargo.current_load) / cargo.max_capacity"
    
  has_active_contract:
    type: "entity_state"
    state: "contracts"
    check: "has_active"
    
  profitable_trade_found:
    type: "market_analysis"
    analysis: "trade_opportunities"
    threshold: "profit_margin > personality.profit_focus * 0.1"
    
  enemy_ships_nearby:
    type: "proximity"
    entities: "combat_ships"
    faction_relation: "hostile"
    distance: 15
```

**Action Library Configuration**:
```yaml
# actions.yml - Reusable action definitions
actions:
  seek_repair_station:
    type: "navigation"
    target_type: "station"
    target_filter:
      services: ["repair"]
      faction_relation: ["friendly", "neutral"]
    parameters:
      - name: "max_distance"
        type: "float"
        default: 100
      - name: "urgency"
        type: "enum"
        values: ["low", "medium", "high"]
        default: "medium"
        
  scan_nearby_markets:
    type: "information_gathering"
    scan_type: "market_data"
    parameters:
      - name: "scan_radius"
        type: "float"
        default: 20
      - name: "commodity_filter"
        type: "array"
        default: ["all"]
        
  execute_trade:
    type: "economic"
    action: "trade_execution"
    parameters:
      - name: "profit_margin_min"
        type: "float"
        default: 0.1
      - name: "risk_tolerance"
        type: "float"
        default: 0.5
```

### 1.4 Game Loop & Time Management (POC 4)
**Purpose**: Tick-based simulation engine

**Technology Stack**:
- **Core**: Python asyncio for concurrent processing
- **Scheduling**: Custom tick scheduler
- **Event System**: Observer pattern for entity communication

**Components**:
```
simulation/
├── tick_engine.py        # Main simulation loop
├── scheduler.py          # Event scheduling
├── world_state.py        # Game state management
├── events.py             # Event system
└── processors/
    ├── movement.py       # Entity movement
    ├── economics.py      # Trade processing
    ├── combat.py         # Combat resolution
    └── production.py     # Production cycles
```

**Key Features**:
- Deterministic tick processing
- Event-driven updates
- State persistence
- Performance monitoring

## Phase 2: Integration & Enhancement

### 2.1 Unified Game Engine
**Purpose**: Combine all POCs into cohesive game engine

**Architecture**:
```
solar_factions/
├── core/
│   ├── engine.py         # Main game engine
│   ├── world.py          # Unified world representation
│   └── config.py         # Configuration management
├── systems/              # Integrated from POCs
│   ├── world_map/
│   ├── data_schema/
│   ├── behavior_engine/
│   └── simulation/
├── ui/
│   ├── pygame_ui.py      # Basic UI implementation
│   ├── terminal_ui.py    # Text-based interface
│   └── web_ui/ (future)  # Web-based UI preparation
└── data/
    ├── worlds/
    ├── saves/
    └── configs/
```

### 2.2 Enhanced User Interface
**Technology Options**:
- **Immediate**: pygame for desktop application
- **Near-term**: Terminal/CLI interface for debugging
- **Future**: Web-based UI (Flask/FastAPI + React/Vue)

### 2.3 Advanced AI & Economics
- **Machine Learning**: Simple ML models for market prediction
- **Complex Behaviors**: Multi-layered decision trees
- **Emergent Gameplay**: Faction relationship dynamics

## Phase 3: Scalability Preparation

### 3.1 Database Integration
**Migration Path**:
1. **File-based → SQLite**: Local database for complex queries
2. **SQLite → PostgreSQL**: Production-ready database
3. **Add Redis**: Caching and session management

**Database Schema**:
```sql
-- Core tables with inheritance support
entities (
    id UUID PRIMARY KEY,
    entity_type VARCHAR(50) NOT NULL,  -- 'Ship', 'Station', 'Asteroid', etc.
    entity_class VARCHAR(50),          -- 'CargoShip', 'TradingStation', etc.
    position_x FLOAT,
    position_y FLOAT,
    base_data JSONB,                   -- Common entity properties
    specific_data JSONB,               -- Class-specific properties
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Inheritance relationships
entity_hierarchy (
    child_type VARCHAR(50) PRIMARY KEY,
    parent_type VARCHAR(50) REFERENCES entity_hierarchy(child_type),
    inheritance_level INTEGER
);

-- Polymorphic relationships
actors (
    id UUID PRIMARY KEY,
    entity_id UUID REFERENCES entities(id),
    actor_type VARCHAR(50),            -- 'ShipCaptain', 'StationManager', etc.
    faction_id UUID,
    behavior_data JSONB,
    personality_traits JSONB
);

-- World state with entity polymorphism
world_state (
    tick BIGINT,
    timestamp TIMESTAMP,
    entity_states JSONB               -- Serialized entity states by type
);
```

### 3.2 Client-Server Architecture
**Preparation Steps**:
1. **API Layer**: FastAPI/Flask for game state access
2. **Message Queue**: Redis/RabbitMQ for real-time updates
3. **WebSocket**: Real-time client communication
4. **Authentication**: JWT-based user management

**Architecture**:
```
Client Layer (Multiple)
├── Desktop (pygame)
├── Web (React/Vue)
└── Mobile (future)

API Layer
├── FastAPI/Flask
├── WebSocket handlers
└── Authentication

Game Engine (Server)
├── Core simulation
├── Data persistence
└── Multi-client management

Database Layer
├── PostgreSQL
├── Redis cache
└── File storage
```

### 3.3 Multiplayer Support
**Implementation Strategy**:
1. **Shared World**: All players in same simulation
2. **Player Factions**: Each player controls a faction
3. **Real-time Updates**: WebSocket-based synchronization
4. **Conflict Resolution**: Server-authoritative decisions

## Technology Stack Evolution

### Phase 1 (Current)
- **Language**: Python 3.11+
- **UI**: pygame/matplotlib
- **Data**: JSON/YAML files
- **Validation**: Pydantic
- **Concurrency**: asyncio

### Phase 2 (Near-term)
- **Database**: SQLite
- **Web UI**: Flask + basic HTML/CSS
- **APIs**: Flask-RESTful
- **Caching**: In-memory Python dicts

### Phase 3 (Future)
- **Database**: PostgreSQL
- **Backend**: FastAPI
- **Frontend**: React/Vue.js
- **Cache**: Redis
- **Message Queue**: RabbitMQ
- **Deployment**: Docker + Kubernetes

## Development Workflow

### POC Development
1. **Isolated Development**: Each POC in separate directory
2. **Independent Testing**: Unit tests for each component
3. **Documentation**: README and examples for each POC
4. **Integration Points**: Clear interfaces for future integration

### Integration Strategy
1. **Gradual Merge**: Combine POCs one at a time
2. **Regression Testing**: Ensure existing functionality remains
3. **Performance Monitoring**: Track performance impacts
4. **User Testing**: Validate gameplay experience

### Deployment Pipeline
1. **Local Development**: File-based, single-player
2. **Local Server**: SQLite, web UI, single-player
3. **Cloud Development**: PostgreSQL, Redis, multi-player
4. **Production**: Full stack with monitoring and scaling

## File Structure (Final Vision)

```
solar_factions/
├── core/                 # Core game engine
├── systems/              # Game systems (from POCs)
├── ui/                   # User interfaces
├── api/                  # Web API (future)
├── data/                 # Data files and schemas
├── tests/                # Test suites
├── docs/                 # Documentation
├── scripts/              # Utility scripts
├── deploy/               # Deployment configurations
└── examples/             # Example configurations
```

## Key Benefits of This Architecture

1. **Incremental Development**: Each POC provides immediate value
2. **Low Risk**: Failures in one POC don't affect others
3. **Clear Upgrade Path**: Each phase builds naturally on previous
4. **Technology Flexibility**: Can swap components as needed
5. **Team Scalability**: Different developers can work on different POCs
6. **Learning Opportunities**: Each POC teaches different aspects

## Success Metrics

### POC Success Criteria
- **World Map**: Can generate and visualize game world
- **Data Schema**: All game entities properly validated
- **Behavior Engine**: AI actors make believable decisions
- **Game Loop**: Simulation runs smoothly with consistent timing

### Integration Success Criteria
- **Performance**: Maintains 60+ ticks per second
- **Stability**: Runs for hours without crashes
- **Extensibility**: New features can be added easily
- **User Experience**: Intuitive and responsive interface

This architecture provides a solid foundation for starting simple while keeping all doors open for future growth and scalability.

**Station Behavior Configuration Example**:
```yaml
# trading_station.yml
behavior_name: "Trading Station Operations"
entity_types: ["TradingStation", "TradingPost", "CommercialHub"]
priority: 90

behavior_tree:
  type: "parallel"  # Execute multiple branches simultaneously
  children:
    - type: "sequence"
      name: "Market Management"
      children:
        - type: "action"
          action: "update_market_prices"
          frequency: "every_tick"
        - type: "condition"
          condition: "market_volatility > 0.5"
        - type: "action"
          action: "adjust_trade_margins"
          parameters:
            volatility_factor: 1.2
    
    - type: "sequence"
      name: "Resource Management"
      children:
        - type: "condition"
          condition: "storage_capacity_used > 0.8"
        - type: "action"
          action: "liquidate_excess_inventory"
          parameters:
            target_capacity: 0.6
            price_discount: 0.1
    
    - type: "sequence"
      name: "Ship Services"
      children:
        - type: "condition"
          condition: "docked_ships_present"
        - type: "action"
          action: "process_trade_requests"
        - type: "action"
          action: "offer_station_services"
          parameters:
            services: ["refuel", "repair", "restock"]

events:
  on_ship_dock:
    - type: "action"
      action: "send_welcome_message"
    - type: "action"
      action: "offer_trade_catalog"
  
  on_market_crash:
    - type: "action"
      action: "emergency_price_stabilization"
    - type: "action"
      action: "contact_faction_headquarters"
```

**Faction-Level Behavior Configuration**:
```yaml
# traders_guild.yml
behavior_name: "Traders Guild Strategy"
entity_types: ["Faction"]
faction_id: "traders_guild"
priority: 50

behavior_tree:
  type: "selector"
  children:
    - type: "sequence"
      name: "Crisis Management"
      children:
        - type: "condition"
          condition: "faction_reputation < 0.3"
        - type: "action"
          action: "implement_reputation_recovery"
          parameters:
            strategy: "charitable_trades"
            duration: 30  # ticks
    
    - type: "sequence"
      name: "Expansion Strategy"
      children:
        - type: "condition"
          condition: "faction_wealth > expansion_threshold"
        - type: "action"
          action: "identify_expansion_opportunities"
        - type: "condition"
          condition: "suitable_location_found"
        - type: "action"
          action: "establish_new_trading_post"
    
    - type: "sequence"
      name: "Daily Operations"
      children:
        - type: "action"
          action: "analyze_market_trends"
        - type: "action"
          action: "adjust_faction_policies"
        - type: "action"
          action: "manage_fleet_assignments"

diplomatic_rules:
  - condition: "other_faction.type == 'pirates'"
    action: "hostile_stance"
  - condition: "other_faction.type == 'mining_corp'"
    action: "seek_trade_agreement"
  - condition: "trade_route_blocked"
    action: "negotiate_passage_rights"
```

**Behavior Template System**:
```yaml
# templates/trading_template.yml
template_name: "basic_trading"
description: "Standard trading behavior for commercial entities"
applicable_types: ["Ship", "Station"]

template_behavior:
  type: "selector"
  children:
    - type: "sequence"
      name: "Emergency Response"
      children:
        - type: "condition"
          condition: "health_critical"
        - type: "action"
          action: "emergency_actions"
    
    - type: "sequence"
      name: "Trading Logic"
      children:
        - type: "action"
          action: "analyze_market"
        - type: "condition"
          condition: "opportunity_exists"
        - type: "action"
          action: "execute_trade"

customization_points:
  - name: "risk_tolerance"
    type: "float"
    description: "How much risk the entity is willing to take"
    default: 0.5
  - name: "profit_margin"
    type: "float"
    description: "Minimum profit margin required"
    default: 0.15
  - name: "trade_commodities"
    type: "array"
    description: "Preferred commodities to trade"
    default: ["all"]
```

**Runtime Behavior System**:
```python
# Core implementation concept (minimal game code changes)
class ConfigurableBehaviorEngine:
    def __init__(self):
        self.behavior_loader = BehaviorLoader()
        self.behavior_cache = {}
        self.file_watcher = FileWatcher()  # For hot-reload
        
    def load_behaviors(self, config_path: str):
        """Load all behavior configurations from path"""
        behaviors = self.behavior_loader.load_from_directory(config_path)
        self.behavior_cache.update(behaviors)
        self.file_watcher.watch_directory(config_path, self.reload_behavior)
    
    def get_behavior(self, entity: Entity) -> BehaviorTree:
        """Get behavior tree for entity based on its type"""
        entity_type = entity.__class__.__name__
        if entity_type in self.behavior_cache:
            return self.behavior_cache[entity_type]
        return self.get_default_behavior(entity_type)
    
    def reload_behavior(self, file_path: str):
        """Hot-reload behavior when config file changes"""
        behavior = self.behavior_loader.load_from_file(file_path)
        self.behavior_cache.update(behavior)
        print(f"Reloaded behavior from {file_path}")
```

**Benefits of Configuration-Driven Approach**:
1. **No Code Changes**: Modify AI behavior without touching Python code
2. **Hot Reload**: Changes take effect immediately during gameplay
3. **Non-Technical Editing**: Game designers can modify behaviors
4. **Version Control**: Behavior changes tracked in config files
5. **A/B Testing**: Easy to test different behavior configurations
6. **Modding Support**: Players can create custom behaviors
7. **Rapid Iteration**: Quick experimentation with different strategies
8. **Template System**: Reusable behavior patterns
9. **Validation**: Schema validation prevents invalid configurations
10. **Debugging**: Clear behavior tree visualization and logging
````