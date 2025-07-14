# game_loop.py - Tick-based game loop with time controls
"""
Tick-based game loop system for Solar Factions.
Provides precise timing, speed controls, and frame-rate independent updates.
"""

import time
import threading
from typing import List, Callable, Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class GameState:
    """Current state of the game"""
    tick: int = 0
    game_time: float = 0.0  # Total game time in seconds
    real_time: float = 0.0  # Real time elapsed
    is_running: bool = False
    is_paused: bool = False
    speed_multiplier: float = 1.0
    
    # Statistics
    target_fps: int = 60
    actual_fps: float = 0.0
    target_tps: int = 20  # Ticks per second
    actual_tps: float = 0.0


class GameLoop:
    """
    Tick-based game loop with time controls.
    Separates rendering from game logic updates.
    """
    
    def __init__(self, target_tps: int = 20, target_fps: int = 60):
        self.state = GameState(target_tps=target_tps, target_fps=target_fps)
        
        # Timing
        self.tick_interval = 1.0 / target_tps
        self.frame_interval = 1.0 / target_fps
        self.last_tick_time = 0.0
        self.last_frame_time = 0.0
        self.start_time = 0.0
        
        # System callbacks
        self.update_systems: List[Callable[[float], None]] = []
        self.render_systems: List[Callable[[float], None]] = []
        
        # Threading
        self.game_thread: Optional[threading.Thread] = None
        self.render_thread: Optional[threading.Thread] = None
        self.thread_lock = threading.Lock()
        
        # Statistics tracking
        self.tick_times: List[float] = []
        self.frame_times: List[float] = []
        self.max_stat_samples = 100
        
    def add_update_system(self, system: Callable[[float], None]):
        """Add a system that runs on game ticks"""
        self.update_systems.append(system)
        
    def add_render_system(self, system: Callable[[float], None]):
        """Add a system that runs on render frames"""
        self.render_systems.append(system)
        
    def remove_update_system(self, system: Callable[[float], None]):
        """Remove an update system"""
        if system in self.update_systems:
            self.update_systems.remove(system)
            
    def remove_render_system(self, system: Callable[[float], None]):
        """Remove a render system"""
        if system in self.render_systems:
            self.render_systems.remove(system)
    
    def start(self):
        """Start the game loop"""
        if self.state.is_running:
            return
            
        self.state.is_running = True
        self.state.is_paused = False
        self.start_time = time.time()
        self.last_tick_time = self.start_time
        self.last_frame_time = self.start_time
        
        # Start game thread (for game logic)
        self.game_thread = threading.Thread(target=self._game_loop, daemon=True)
        self.game_thread.start()
        
        # Start render thread (for rendering)
        self.render_thread = threading.Thread(target=self._render_loop, daemon=True)
        self.render_thread.start()
        
    def stop(self):
        """Stop the game loop"""
        self.state.is_running = False
        
        # Wait for threads to finish
        if self.game_thread and self.game_thread.is_alive():
            self.game_thread.join(timeout=1.0)
        if self.render_thread and self.render_thread.is_alive():
            self.render_thread.join(timeout=1.0)
    
    def pause(self):
        """Pause the game loop"""
        self.state.is_paused = True
        
    def resume(self):
        """Resume the game loop"""
        self.state.is_paused = False
        
    def set_speed(self, multiplier: float):
        """Set game speed multiplier (1.0 = normal speed)"""
        self.state.speed_multiplier = max(0.1, min(10.0, multiplier))
        
    def step(self):
        """Execute one game tick (useful for debugging)"""
        if not self.state.is_running:
            return
            
        current_time = time.time()
        dt = self.tick_interval * self.state.speed_multiplier
        
        self._update_game_logic(dt)
        self.state.tick += 1
        self.state.game_time += dt
        
    def _game_loop(self):
        """Main game logic loop (runs in separate thread)"""
        while self.state.is_running:
            current_time = time.time()
            
            if not self.state.is_paused:
                # Calculate time since last tick
                time_since_last_tick = current_time - self.last_tick_time
                
                # Check if it's time for a tick
                adjusted_interval = self.tick_interval / self.state.speed_multiplier
                if time_since_last_tick >= adjusted_interval:
                    # Calculate delta time
                    dt = self.tick_interval * self.state.speed_multiplier
                    
                    # Update game logic
                    self._update_game_logic(dt)
                    
                    # Update state
                    self.state.tick += 1
                    self.state.game_time += dt
                    self.state.real_time = current_time - self.start_time
                    
                    # Track performance
                    self.tick_times.append(time_since_last_tick)
                    if len(self.tick_times) > self.max_stat_samples:
                        self.tick_times.pop(0)
                    
                    # Update TPS
                    if self.tick_times:
                        avg_tick_time = sum(self.tick_times) / len(self.tick_times)
                        self.state.actual_tps = 1.0 / avg_tick_time if avg_tick_time > 0 else 0
                    
                    self.last_tick_time = current_time
            
            # Small sleep to prevent CPU spinning
            time.sleep(0.001)
    
    def _render_loop(self):
        """Main render loop (runs in separate thread)"""
        while self.state.is_running:
            current_time = time.time()
            
            # Calculate time since last frame
            time_since_last_frame = current_time - self.last_frame_time
            
            # Check if it's time for a frame
            if time_since_last_frame >= self.frame_interval:
                # Calculate delta time for rendering
                dt = time_since_last_frame
                
                # Update render systems
                self._update_render_systems(dt)
                
                # Track performance
                self.frame_times.append(time_since_last_frame)
                if len(self.frame_times) > self.max_stat_samples:
                    self.frame_times.pop(0)
                
                # Update FPS
                if self.frame_times:
                    avg_frame_time = sum(self.frame_times) / len(self.frame_times)
                    self.state.actual_fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0
                
                self.last_frame_time = current_time
            
            # Small sleep to prevent CPU spinning
            time.sleep(0.001)
    
    def _update_game_logic(self, dt: float):
        """Update all game logic systems"""
        with self.thread_lock:
            for system in self.update_systems:
                try:
                    system(dt)
                except Exception as e:
                    print(f"Error in update system: {e}")
    
    def _update_render_systems(self, dt: float):
        """Update all render systems"""
        with self.thread_lock:
            for system in self.render_systems:
                try:
                    system(dt)
                except Exception as e:
                    print(f"Error in render system: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current performance statistics"""
        return {
            'tick': self.state.tick,
            'game_time': self.state.game_time,
            'real_time': self.state.real_time,
            'time_ratio': self.state.game_time / self.state.real_time if self.state.real_time > 0 else 0,
            'is_running': self.state.is_running,
            'is_paused': self.state.is_paused,
            'speed_multiplier': self.state.speed_multiplier,
            'target_tps': self.state.target_tps,
            'actual_tps': self.state.actual_tps,
            'target_fps': self.state.target_fps,
            'actual_fps': self.state.actual_fps,
            'update_systems': len(self.update_systems),
            'render_systems': len(self.render_systems)
        }
    
    def print_stats(self):
        """Print current performance statistics"""
        stats = self.get_stats()
        print(f"\n--- Game Loop Statistics ---")
        print(f"Tick: {stats['tick']}")
        print(f"Game Time: {stats['game_time']:.2f}s")
        print(f"Real Time: {stats['real_time']:.2f}s")
        print(f"Time Ratio: {stats['time_ratio']:.2f}")
        print(f"Status: {'Running' if stats['is_running'] else 'Stopped'}")
        print(f"Paused: {'Yes' if stats['is_paused'] else 'No'}")
        print(f"Speed: {stats['speed_multiplier']:.1f}x")
        print(f"TPS: {stats['actual_tps']:.1f} / {stats['target_tps']}")
        print(f"FPS: {stats['actual_fps']:.1f} / {stats['target_fps']}")
        print(f"Systems: {stats['update_systems']} update, {stats['render_systems']} render")
