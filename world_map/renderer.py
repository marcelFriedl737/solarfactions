# renderer.py
import pygame
import sys
from typing import List, Tuple, Optional
from entities.base import Entity
from coordinates import Coordinates

class MapRenderer:
    """Pygame-based map visualization"""
    
    def __init__(self, width: int = 1200, height: int = 800, title: str = "Solar Factions - World Map"):
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
        
        # View settings
        self.view_offset = Coordinates(0, 0)
        self.zoom_level = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 5.0
        
        # Selection
        self.selected_entity = None
        self.show_labels = True
        self.show_grid = True
    
    def world_to_screen(self, world_pos: Coordinates) -> Tuple[int, int]:
        """Convert world coordinates to screen coordinates"""
        screen_x = int((world_pos.x - self.view_offset.x) * self.zoom_level + self.width / 2)
        screen_y = int((world_pos.y - self.view_offset.y) * self.zoom_level + self.height / 2)
        return (screen_x, screen_y)
    
    def screen_to_world(self, screen_pos: Tuple[int, int]) -> Coordinates:
        """Convert screen coordinates to world coordinates"""
        world_x = (screen_pos[0] - self.width / 2) / self.zoom_level + self.view_offset.x
        world_y = (screen_pos[1] - self.height / 2) / self.zoom_level + self.view_offset.y
        return Coordinates(world_x, world_y)
    
    def draw_grid(self) -> None:
        """Draw background grid"""
        if not self.show_grid:
            return
        
        grid_spacing = int(self.grid_size * self.zoom_level)
        if grid_spacing < 10:  # Don't draw if too small
            return
        
        # Calculate grid offset
        offset_x = int((-self.view_offset.x * self.zoom_level + self.width / 2) % grid_spacing)
        offset_y = int((-self.view_offset.y * self.zoom_level + self.height / 2) % grid_spacing)
        
        # Draw vertical lines
        for x in range(offset_x, self.width, grid_spacing):
            pygame.draw.line(self.screen, self.grid_color, (x, 0), (x, self.height))
        
        # Draw horizontal lines
        for y in range(offset_y, self.height, grid_spacing):
            pygame.draw.line(self.screen, self.grid_color, (0, y), (self.width, y))
    
    def draw_entity(self, entity: Entity) -> None:
        """Draw a single entity"""
        screen_pos = self.world_to_screen(entity.position)
        
        # Skip if off-screen
        if (screen_pos[0] < -50 or screen_pos[0] > self.width + 50 or
            screen_pos[1] < -50 or screen_pos[1] > self.height + 50):
            return
        
        # Get entity rendering properties
        color = entity.get_render_color()
        size = max(1, int(entity.get_render_size() * self.zoom_level))
        
        # Draw entity
        pygame.draw.circle(self.screen, color, screen_pos, size)
        
        # Draw selection highlight
        if entity == self.selected_entity:
            pygame.draw.circle(self.screen, (255, 255, 255), screen_pos, size + 3, 2)
        
        # Draw label if enabled and zoomed in enough
        if self.show_labels and self.zoom_level > 0.5:
            label = entity.get_display_name()
            text_surface = self.font.render(label, True, (200, 200, 200))
            text_rect = text_surface.get_rect()
            text_rect.center = (screen_pos[0], screen_pos[1] - size - 15)
            self.screen.blit(text_surface, text_rect)
    
    def draw_entities(self, entities: List[Entity]) -> None:
        """Draw all entities"""
        for entity in entities:
            self.draw_entity(entity)
    
    def draw_ui(self, entities: List[Entity]) -> None:
        """Draw UI elements"""
        # Entity count
        count_text = f"Entities: {len(entities)}"
        count_surface = self.font.render(count_text, True, (255, 255, 255))
        self.screen.blit(count_surface, (10, 10))
        
        # Zoom level
        zoom_text = f"Zoom: {self.zoom_level:.2f}x"
        zoom_surface = self.font.render(zoom_text, True, (255, 255, 255))
        self.screen.blit(zoom_surface, (10, 35))
        
        # View position
        pos_text = f"View: ({self.view_offset.x:.1f}, {self.view_offset.y:.1f})"
        pos_surface = self.font.render(pos_text, True, (255, 255, 255))
        self.screen.blit(pos_surface, (10, 60))
        
        # Selected entity info
        if self.selected_entity:
            info_lines = [
                f"Selected: {self.selected_entity.get_display_name()}",
                f"Type: {self.selected_entity.__class__.__name__}",
                f"Position: ({self.selected_entity.position.x:.1f}, {self.selected_entity.position.y:.1f})"
            ]
            
            for i, line in enumerate(info_lines):
                info_surface = self.font.render(line, True, (255, 255, 255))
                self.screen.blit(info_surface, (10, self.height - 90 + i * 25))
        
        # Controls
        controls = [
            "Controls:",
            "WASD - Move view",
            "Mouse wheel - Zoom",
            "Click - Select entity",
            "G - Toggle grid",
            "L - Toggle labels",
            "ESC - Exit"
        ]
        
        for i, control in enumerate(controls):
            control_surface = self.font.render(control, True, (150, 150, 150))
            self.screen.blit(control_surface, (self.width - 200, 10 + i * 20))
    
    def find_entity_at_position(self, entities: List[Entity], screen_pos: Tuple[int, int]) -> Optional[Entity]:
        """Find entity at screen position"""
        world_pos = self.screen_to_world(screen_pos)
        
        for entity in entities:
            distance = world_pos.distance_to(entity.position)
            if distance <= entity.get_render_size() / self.zoom_level:
                return entity
        
        return None
    
    def handle_input(self, entities: List[Entity]) -> bool:
        """Handle pygame input events"""
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
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.selected_entity = self.find_entity_at_position(entities, event.pos)
                elif event.button == 4:  # Mouse wheel up
                    self.zoom_level = min(self.max_zoom, self.zoom_level * 1.2)
                elif event.button == 5:  # Mouse wheel down
                    self.zoom_level = max(self.min_zoom, self.zoom_level / 1.2)
        
        # Handle continuous key presses
        keys = pygame.key.get_pressed()
        move_speed = 10 / self.zoom_level
        
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.view_offset.y -= move_speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.view_offset.y += move_speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.view_offset.x -= move_speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.view_offset.x += move_speed
        
        return True
    
    def render_frame(self, entities: List[Entity]) -> None:
        """Render a single frame"""
        self.screen.fill(self.background_color)
        
        self.draw_grid()
        self.draw_entities(entities)
        self.draw_ui(entities)
        
        pygame.display.flip()
        self.clock.tick(60)
    
    def run(self, entities: List[Entity]) -> None:
        """Main rendering loop"""
        running = True
        
        while running:
            running = self.handle_input(entities)
            self.render_frame(entities)
        
        pygame.quit()
    
    def export_screenshot(self, entities: List[Entity], filename: str) -> None:
        """Export current view as image"""
        self.render_frame(entities)
        pygame.image.save(self.screen, f"data/generated_maps/{filename}.png")