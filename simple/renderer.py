# renderer.py - Simplified renderer for the new entity system
"""
Simple pygame renderer that works with the simplified entity system.
Uses tuples for positions instead of Coordinates objects.
"""

import pygame
import sys
from typing import List, Tuple, Optional, Dict, Any
from entities.entity import Entity

class SimpleRenderer:
    """Simple pygame-based map visualization for the simplified entity system"""
    
    def __init__(self, width: int = 1200, height: int = 800, title: str = "Solar Factions - Simplified"):
        self.width = width
        self.height = height
        self.title = title
        
        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()
        
        # Rendering settings
        self.background_color = (10, 10, 30)  # Dark space blue
        self.grid_color = (30, 30, 50)
        self.grid_size = 50
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # View settings
        self.view_offset = (0, 0)  # Use tuples instead of Coordinates
        self.zoom_level = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 5.0
        
        # Selection and interaction
        self.selected_entity = None
        self.show_labels = True
        self.show_grid = True
        self.show_info = True
        
        # Mouse interaction
        self.mouse_dragging = False
        self.last_mouse_pos = None
        
        # Entity display settings
        self.entity_colors = {
            'star': (255, 255, 100),      # Yellow
            'planet': (100, 200, 100),    # Green
            'asteroid': (150, 150, 150),  # Gray
            'space_station': (100, 100, 255),  # Blue
            'cargo_ship': (200, 200, 100),     # Light yellow
            'fighter': (255, 100, 100),        # Red
            'mining_ship': (150, 100, 200),    # Purple
            'default': (255, 255, 255)         # White
        }
        
        self.entity_sizes = {
            'star': 20,
            'planet': 15,
            'asteroid': 8,
            'space_station': 12,
            'cargo_ship': 6,
            'fighter': 4,
            'mining_ship': 7,
            'default': 5
        }
    
    def world_to_screen(self, world_pos: Tuple[float, float]) -> Tuple[int, int]:
        """Convert world coordinates to screen coordinates"""
        world_x, world_y = world_pos
        screen_x = int((world_x - self.view_offset[0]) * self.zoom_level + self.width / 2)
        screen_y = int((world_y - self.view_offset[1]) * self.zoom_level + self.height / 2)
        return (screen_x, screen_y)
    
    def screen_to_world(self, screen_pos: Tuple[int, int]) -> Tuple[float, float]:
        """Convert screen coordinates to world coordinates"""
        screen_x, screen_y = screen_pos
        world_x = (screen_x - self.width / 2) / self.zoom_level + self.view_offset[0]
        world_y = (screen_y - self.height / 2) / self.zoom_level + self.view_offset[1]
        return (world_x, world_y)
    
    def draw_grid(self):
        """Draw background grid"""
        if not self.show_grid:
            return
        
        # Calculate grid spacing in screen coordinates
        grid_spacing = int(self.grid_size * self.zoom_level)
        
        if grid_spacing < 10:  # Don't draw grid if too small
            return
        
        # Calculate grid offset
        offset_x = int(self.view_offset[0] * self.zoom_level) % grid_spacing
        offset_y = int(self.view_offset[1] * self.zoom_level) % grid_spacing
        
        # Draw vertical lines
        for x in range(-offset_x, self.width + grid_spacing, grid_spacing):
            pygame.draw.line(self.screen, self.grid_color, (x, 0), (x, self.height))
        
        # Draw horizontal lines
        for y in range(-offset_y, self.height + grid_spacing, grid_spacing):
            pygame.draw.line(self.screen, self.grid_color, (0, y), (self.width, y))
    
    def draw_entity(self, entity: Entity):
        """Draw a single entity"""
        screen_pos = self.world_to_screen(entity.position)
        
        # Skip if entity is off-screen
        if (screen_pos[0] < -50 or screen_pos[0] > self.width + 50 or
            screen_pos[1] < -50 or screen_pos[1] > self.height + 50):
            return
        
        # Get entity display properties
        color = self.entity_colors.get(entity.type, self.entity_colors['default'])
        base_size = self.entity_sizes.get(entity.type, self.entity_sizes['default'])
        size = max(2, int(base_size * self.zoom_level))
        
        # Highlight selected entity
        if entity == self.selected_entity:
            # Draw selection circle
            pygame.draw.circle(self.screen, (255, 255, 255), screen_pos, size + 5, 2)
            color = tuple(min(255, c + 50) for c in color)  # Brighten color
        
        # Draw entity based on type
        if entity.type == 'star':
            # Draw star with glow effect
            for i in range(3):
                alpha_color = (*color, 100 - i * 30)
                glow_size = size + (3 - i) * 2
                pygame.draw.circle(self.screen, color, screen_pos, glow_size - i)
            pygame.draw.circle(self.screen, (255, 255, 255), screen_pos, size // 2)
        
        elif entity.type == 'planet':
            # Draw planet
            pygame.draw.circle(self.screen, color, screen_pos, size)
            pygame.draw.circle(self.screen, (255, 255, 255), screen_pos, size, 1)
        
        elif entity.type == 'asteroid':
            # Draw asteroid as rough circle
            points = []
            import math
            for i in range(6):
                angle = (i * 60) * math.pi / 180
                radius = size + (i % 2) * 2
                x = screen_pos[0] + radius * math.cos(angle)
                y = screen_pos[1] + radius * math.sin(angle)
                points.append((x, y))
            pygame.draw.polygon(self.screen, color, points)
        
        elif entity.type == 'space_station':
            # Draw space station as square
            rect = pygame.Rect(screen_pos[0] - size, screen_pos[1] - size, size * 2, size * 2)
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, (255, 255, 255), rect, 1)
        
        elif entity.type in ['cargo_ship', 'fighter', 'mining_ship']:
            # Draw ships as triangles
            points = [
                (screen_pos[0], screen_pos[1] - size),
                (screen_pos[0] - size, screen_pos[1] + size),
                (screen_pos[0] + size, screen_pos[1] + size)
            ]
            pygame.draw.polygon(self.screen, color, points)
        
        else:
            # Default: draw as circle
            pygame.draw.circle(self.screen, color, screen_pos, size)
        
        # Draw label if enabled and zoom level is sufficient
        if self.show_labels and self.zoom_level > 0.5:
            name = entity.get_property('name', entity.type)
            if len(name) > 20:
                name = name[:17] + "..."
            
            text = self.small_font.render(name, True, (200, 200, 200))
            text_rect = text.get_rect()
            text_rect.center = (screen_pos[0], screen_pos[1] + size + 15)
            self.screen.blit(text, text_rect)
    
    def draw_info_panel(self, entities: List[Entity]):
        """Draw information panel"""
        if not self.show_info:
            return
        
        # Panel background
        panel_rect = pygame.Rect(10, 10, 300, 200)
        pygame.draw.rect(self.screen, (0, 0, 0, 180), panel_rect)
        pygame.draw.rect(self.screen, (100, 100, 100), panel_rect, 2)
        
        # Panel content
        y_offset = 25
        
        # General info
        info_lines = [
            f"Entities: {len(entities)}",
            f"Zoom: {self.zoom_level:.2f}x",
            f"View: ({self.view_offset[0]:.1f}, {self.view_offset[1]:.1f})",
            "",
            "Controls:",
            "  Mouse: Pan view",
            "  Wheel: Zoom",
            "  Click: Select entity",
            "  G: Toggle grid",
            "  L: Toggle labels",
            "  I: Toggle info panel",
            "  ESC: Exit"
        ]
        
        for line in info_lines:
            if line:
                text = self.small_font.render(line, True, (200, 200, 200))
                self.screen.blit(text, (20, y_offset))
            y_offset += 15
    
    def draw_entity_info(self, entity: Entity):
        """Draw detailed info about selected entity"""
        if not entity:
            return
        
        # Info panel
        panel_rect = pygame.Rect(self.width - 320, 10, 300, 400)
        pygame.draw.rect(self.screen, (0, 0, 0, 180), panel_rect)
        pygame.draw.rect(self.screen, (100, 100, 100), panel_rect, 2)
        
        y_offset = 25
        
        # Entity details
        info_lines = [
            f"Selected: {entity.get_property('name', entity.type)}",
            f"Type: {entity.type}",
            f"ID: {entity.id[:8]}...",
            f"Position: ({entity.position[0]:.1f}, {entity.position[1]:.1f})",
            "",
            "Properties:"
        ]
        
        # Add properties
        for key, value in entity.properties.items():
            if key != 'name':  # Already shown above
                info_lines.append(f"  {key}: {value}")
        
        # Add components
        if entity.components:
            info_lines.append("")
            info_lines.append("Components:")
            for component_name, component_data in entity.components.items():
                info_lines.append(f"  {component_name}:")
                for key, value in component_data.items():
                    info_lines.append(f"    {key}: {value}")
        
        # Draw info lines
        for line in info_lines:
            if y_offset > panel_rect.height - 20:
                break
            
            if line:
                text = self.small_font.render(line, True, (200, 200, 200))
                self.screen.blit(text, (self.width - 310, y_offset))
            y_offset += 15
    
    def find_entity_at_position(self, world_pos: Tuple[float, float], entities: List[Entity]) -> Optional[Entity]:
        """Find entity at given world position"""
        for entity in entities:
            dx = entity.position[0] - world_pos[0]
            dy = entity.position[1] - world_pos[1]
            distance = (dx * dx + dy * dy) ** 0.5
            
            # Check if click is within entity bounds
            entity_size = self.entity_sizes.get(entity.type, self.entity_sizes['default'])
            if distance <= entity_size:
                return entity
        
        return None
    
    def handle_events(self, entities: List[Entity]) -> bool:
        """Handle pygame events. Returns False if should quit."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_g:
                    self.show_grid = not self.show_grid
                elif event.key == pygame.K_l:
                    self.show_labels = not self.show_labels
                elif event.key == pygame.K_i:
                    self.show_info = not self.show_info
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    world_pos = self.screen_to_world(event.pos)
                    self.selected_entity = self.find_entity_at_position(world_pos, entities)
                    self.mouse_dragging = True
                    self.last_mouse_pos = event.pos
                
                elif event.button == 4:  # Mouse wheel up
                    self.zoom_level = min(self.max_zoom, self.zoom_level * 1.1)
                
                elif event.button == 5:  # Mouse wheel down
                    self.zoom_level = max(self.min_zoom, self.zoom_level / 1.1)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.mouse_dragging = False
            
            elif event.type == pygame.MOUSEMOTION:
                if self.mouse_dragging and self.last_mouse_pos:
                    # Pan view
                    dx = (event.pos[0] - self.last_mouse_pos[0]) / self.zoom_level
                    dy = (event.pos[1] - self.last_mouse_pos[1]) / self.zoom_level
                    self.view_offset = (self.view_offset[0] - dx, self.view_offset[1] - dy)
                
                self.last_mouse_pos = event.pos
        
        return True
    
    def run(self, entities: List[Entity]):
        """Main rendering loop"""
        print(f"Starting renderer with {len(entities)} entities")
        print("Controls:")
        print("  Mouse: Click and drag to pan")
        print("  Mouse wheel: Zoom in/out")
        print("  Click on entities to select them")
        print("  G: Toggle grid")
        print("  L: Toggle labels")
        print("  I: Toggle info panel")
        print("  ESC: Exit")
        
        running = True
        while running:
            # Handle events
            running = self.handle_events(entities)
            
            # Clear screen
            self.screen.fill(self.background_color)
            
            # Draw grid
            self.draw_grid()
            
            # Draw entities
            for entity in entities:
                self.draw_entity(entity)
            
            # Draw UI
            self.draw_info_panel(entities)
            if self.selected_entity:
                self.draw_entity_info(self.selected_entity)
            
            # Update display
            pygame.display.flip()
            self.clock.tick(60)  # 60 FPS
        
        pygame.quit()


if __name__ == "__main__":
    # Create some test entities
    from entities.entity import Entity
    
    entities = [
        Entity('star', (500, 400), name='Central Star', temperature=5778),
        Entity('planet', (300, 400), name='Earth', habitable=True),
        Entity('planet', (700, 400), name='Mars', habitable=False),
        Entity('asteroid', (200, 300), name='Asteroid 1'),
        Entity('asteroid', (800, 500), name='Asteroid 2'),
        Entity('space_station', (400, 200), name='Station Alpha'),
        Entity('cargo_ship', (350, 350), name='Trader')
    ]
    
    # Add some components
    entities[-1].add_component('movement', {'speed': 50, 'fuel': 80})
    entities[-1].add_component('cargo', {'capacity': 100, 'current': 25})
    
    # Run renderer
    renderer = SimpleRenderer()
    renderer.run(entities)
