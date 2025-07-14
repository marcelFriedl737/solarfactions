# Demo System Guide

## Overview

The Solar Factions demo system provides interactive demonstrations of the game systems in action. This guide covers all available demo modes and how to use them effectively.

## Demo Modes

### 1. Interactive Demo (`interactive`)

**Purpose**: Visual demonstration with full user interaction

**Command**: 
```bash
python game_demo.py interactive
```

**Features**:
- Full visual rendering with pygame
- Real-time game system interactions
- Interactive controls for game speed, pause/resume
- Entity selection and inspection
- Debug information overlay

**Controls**:
- **SPACE**: Pause/Resume simulation
- **+/-**: Increase/Decrease game speed
- **S**: Single step when paused
- **D**: Toggle debug information
- **ESC**: Exit demo
- **Mouse**: Pan view and select entities
- **Mouse wheel**: Zoom in/out

**What You'll See**:
- Entities moving according to their assigned behaviors
- AI decision-making in real-time
- System performance metrics
- Component interactions

### 2. Headless Demo (`headless`)

**Purpose**: Non-visual simulation for testing and analysis

**Command**: 
```bash
python game_demo.py headless
```

**Features**:
- No graphics dependency (no pygame required)
- Comprehensive statistics output
- Performance benchmarking
- Automated testing scenarios

**Output Example**:
```
=== Solar Factions Headless Demo ===
Running simulation without graphics...
Generating demo map...
Generated map with template 'warzone' (45 entities)

Initial state:
=== Game Statistics ===
--- Game Loop Statistics ---
Tick: 0
Game Time: 0.00s
...

Running simulation for 15 seconds...
--- Game Loop Statistics ---
Tick: 150
Game Time: 15.02s
Actual TPS: 20.1 / 20
...
```

### 3. System Showcase (`showcase`)

**Purpose**: Demonstrate individual system features

**Command**: 
```bash
python game_demo.py showcase
```

**Features**:
- Speed control demonstration
- System performance testing
- Entity behavior analysis
- Pause/resume functionality

**Demonstration Sequence**:
1. **Speed Testing**: Runs at 0.5x, 1.0x, 2.0x, 4.0x speeds
2. **Entity Analysis**: Shows detailed entity information
3. **Pause/Resume**: Demonstrates pause functionality
4. **Step-by-Step**: Shows single-step execution
5. **Statistics**: Displays comprehensive system metrics

### 4. Behavior Demo (`behavior`)

**Purpose**: Show AI and movement behavior configuration

**Command**: 
```bash
python game_demo.py behavior
```

**Features**:
- Initial behavior assignment display
- Dynamic behavior changes
- Behavior performance analysis
- Real-time behavior monitoring

**Demonstration Flow**:
1. Shows initial behavior assignments
2. Runs simulation with default behaviors
3. Dynamically changes behaviors mid-simulation
4. Shows impact of behavior changes
5. Displays final behavior statistics

## Demo Scripts

### Main Demo Script (`game_demo.py`)

The main demo script provides a command-line interface for all demo modes:

```python
# Run interactive demo
python game_demo.py interactive

# Run headless demo
python game_demo.py headless

# Run system showcase
python game_demo.py showcase

# Run behavior demo
python game_demo.py behavior
```

### Visual Demo Script (`demo_visual.py`)

Focused on visual demonstration with custom entity setup:

```bash
python demo_visual.py
```

**Features**:
- Custom entity generation with interesting properties
- Component demonstration
- Map saving and statistics
- Visual renderer with detailed controls

## Using Demos for Development

### Testing New Features

```bash
# Test new AI behaviors
python game_demo.py behavior

# Test performance changes
python game_demo.py headless

# Test visual changes
python game_demo.py interactive
```

### Debugging Issues

```bash
# Debug with visual feedback
python game_demo.py interactive

# Debug performance issues
python game_demo.py showcase

# Debug without graphics
python game_demo.py headless
```

### Benchmarking Performance

```bash
# Headless performance test
python game_demo.py headless

# Interactive performance test
python game_demo.py showcase
```

## Demo Configuration

### Customizing Demo Maps

The demos use predefined map templates. You can customize them:

```python
# In game_demo.py, modify the map generation:
game_manager.generate_map("custom_template", seed=42)
```

### Available Demo Templates

- **basic**: Standard solar system (used in showcase)
- **frontier**: Mining-focused system (used in interactive)
- **warzone**: Military conflict zone (used in headless and behavior)

### Creating Custom Demo Scenarios

```python
def custom_demo_scenario():
    """Create a custom demo scenario"""
    game_manager = GameManager()
    
    # Generate specific map
    game_manager.generate_map("frontier", seed=123)
    
    # Customize entity behaviors
    for entity in game_manager.entities:
        if entity.type == 'fighter':
            game_manager.ai_system.assign_ai_to_entity(entity, 'aggressive_patrol')
    
    # Run custom scenario
    game_manager.run_interactive()
```

## Demo Output Analysis

### Understanding Statistics

```
--- Game Loop Statistics ---
Tick: 300                    # Total ticks executed
Game Time: 15.02s           # Total game time
Real Time: 15.12s           # Total real time
Time Ratio: 0.99            # Game time / Real time
Status: Running             # Current status
Paused: No                  # Pause state
Speed: 1.0x                 # Speed multiplier
TPS: 20.1 / 20             # Actual/Target TPS
FPS: 59.8 / 60             # Actual/Target FPS
Systems: 1 update, 1 render # System count
```

### Entity Statistics

```
--- Entity Counts ---
cargo_ship: 8               # Number of cargo ships
fighter: 12                 # Number of fighters
mining_ship: 6              # Number of mining ships
space_station: 3            # Number of stations
star: 1                     # Number of stars
planet: 4                   # Number of planets
```

### AI Behavior Statistics

```
--- AI Behavior Counts ---
default_idle: 5             # Entities with idle behavior
pirate_hunter: 8            # Entities with hunter behavior
resource_hunter: 6          # Entities with resource behavior
station_defender: 3         # Entities with defender behavior
trade_circuit: 8            # Entities with trade behavior
```

## Troubleshooting Demos

### Common Issues

#### pygame Import Error
```
ImportError: No module named 'pygame'
```
**Solution**: Install pygame or use headless mode:
```bash
pip install pygame
# OR
python game_demo.py headless
```

#### Demo Crashes
```
AttributeError: 'NoneType' object has no attribute 'position'
```
**Solution**: Ensure proper entity initialization:
```python
# Check entity validity before use
if entity and hasattr(entity, 'position'):
    # Use entity safely
```

#### Performance Issues
```
Low FPS or TPS in demos
```
**Solution**: Reduce entity count or use headless mode:
```python
# Generate smaller maps
game_manager.generate_map("basic", seed=42)  # Smaller than warzone
```

### Debug Mode

Enable debug mode in interactive demo:
- Press **D** to toggle debug information
- Shows real-time system statistics
- Displays entity counts and behaviors
- Shows performance metrics

### Custom Debug Output

Add custom debug output to demos:

```python
def debug_entity_states(game_manager):
    """Debug helper for entity states"""
    for entity in game_manager.entities:
        if hasattr(entity, 'id'):
            ai_state = game_manager.ai_system.get_ai_state(entity.id)
            movement_data = game_manager.movement_system.get_movement_data(entity.id)
            
            print(f"Entity {entity.id}:")
            print(f"  Type: {entity.type}")
            print(f"  Position: {entity.position}")
            
            if ai_state:
                print(f"  AI: {ai_state.behavior_name} (Energy: {ai_state.energy:.1f})")
            
            if movement_data:
                print(f"  Movement: {movement_data.behavior_name}")
```

## Advanced Demo Usage

### Scripted Demonstrations

Create scripted demonstrations for presentations:

```python
class ScriptedDemo:
    def __init__(self):
        self.game_manager = GameManager()
        self.script_steps = []
        self.current_step = 0
    
    def add_step(self, duration, action, description):
        """Add a scripted step"""
        self.script_steps.append({
            'duration': duration,
            'action': action,
            'description': description
        })
    
    def run_script(self):
        """Run the scripted demonstration"""
        for step in self.script_steps:
            print(f"Step {self.current_step + 1}: {step['description']}")
            step['action']()
            time.sleep(step['duration'])
            self.current_step += 1
    
    def demo_ai_behaviors(self):
        """Demonstrate AI behavior changes"""
        # Step 1: Show initial state
        self.add_step(3, lambda: print("Initial AI behaviors..."), 
                     "Showing initial AI behavior assignments")
        
        # Step 2: Change behaviors
        self.add_step(5, self.change_behaviors,
                     "Changing AI behaviors dynamically")
        
        # Step 3: Show results
        self.add_step(3, self.show_results,
                     "Showing behavior change results")
    
    def change_behaviors(self):
        """Change entity behaviors"""
        fighters = [e for e in self.game_manager.entities if e.type == 'fighter']
        if fighters:
            fighter = fighters[0]
            self.game_manager.ai_system.assign_ai_to_entity(fighter, 'aggressive_patrol')
            print(f"Changed {fighter.id} to aggressive_patrol")
    
    def show_results(self):
        """Show behavior change results"""
        self.game_manager.print_statistics()

# Usage
demo = ScriptedDemo()
demo.game_manager.generate_map("frontier", seed=42)
demo.demo_ai_behaviors()
demo.run_script()
```

### Performance Profiling

Use demos for performance profiling:

```python
import cProfile
import pstats

def profile_demo():
    """Profile a demo for performance analysis"""
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Run demo
    game_manager = GameManager()
    game_manager.generate_map("warzone", seed=42)
    game_manager.run_headless(10.0)
    
    profiler.disable()
    
    # Analyze results
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)  # Top 20 functions

# Run profiling
profile_demo()
```

### Automated Testing

Use demos for automated testing:

```python
def automated_test_suite():
    """Run automated tests using demo framework"""
    test_results = []
    
    # Test 1: Basic functionality
    try:
        game_manager = GameManager()
        game_manager.generate_map("basic", seed=42)
        game_manager.run_headless(1.0)
        test_results.append("Basic functionality: PASS")
    except Exception as e:
        test_results.append(f"Basic functionality: FAIL - {e}")
    
    # Test 2: Performance test
    try:
        game_manager = GameManager()
        game_manager.generate_map("warzone", seed=42)
        start_time = time.time()
        game_manager.run_headless(5.0)
        duration = time.time() - start_time
        
        if duration < 7.0:  # Should complete in reasonable time
            test_results.append("Performance test: PASS")
        else:
            test_results.append(f"Performance test: FAIL - took {duration:.1f}s")
    except Exception as e:
        test_results.append(f"Performance test: FAIL - {e}")
    
    # Report results
    print("\n=== Automated Test Results ===")
    for result in test_results:
        print(result)
    
    return all("PASS" in result for result in test_results)

# Run automated tests
success = automated_test_suite()
print(f"\nOverall result: {'PASS' if success else 'FAIL'}")
```

## Best Practices

### Running Demos

1. **Start Simple**: Begin with headless demo to verify basic functionality
2. **Use Interactive**: Use interactive mode for visual verification
3. **Test Scenarios**: Use behavior demo to test AI configurations
4. **Monitor Performance**: Use showcase mode for performance analysis

### Creating Custom Demos

1. **Clear Purpose**: Each demo should have a clear objective
2. **Appropriate Duration**: Keep demos short and focused
3. **Error Handling**: Include proper error handling and cleanup
4. **Documentation**: Document what each demo demonstrates

### Demo Integration

1. **CI/CD Integration**: Use headless demos in continuous integration
2. **Performance Baselines**: Establish performance baselines with demos
3. **Regression Testing**: Use demos to catch regressions
4. **User Training**: Use interactive demos for user training

The demo system provides a powerful way to showcase, test, and develop Solar Factions functionality. Use the appropriate demo mode for your specific needs, and consider creating custom demos for specialized scenarios.