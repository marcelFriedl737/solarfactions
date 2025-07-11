# simple_generator.py - Simplified Map Generator
"""
Simplified map generator focusing on core functionality.
Replaces complex generation logic with straightforward, data-driven approach.
"""

import random
import math
from typing import List, Dict, Any, Tuple, Optional
from entities.simple import Entity, EntityFactory
from data_manager import DataManager


class SimpleMapGenerator:
    """
    Simplified map generator with focus on:
    - Easy to understand generation logic
    - Template-based entity creation
    - Configurable but not complex
    - Fast iteration for testing
    """
    
    def __init__(self, data_manager: Optional[DataManager] = None):
        self.data_manager = data_manager or DataManager()
        self.entity_factory = self.data_manager.get_entity_factory()
        self.last_seed = None
    
    def generate_map(self, template_name: str = "basic", seed: Optional[int] = None) -> List[Entity]:
        """
        Generate a map using a template.
        
        Args:
            template_name: Name of the template to use
            seed: Random seed for reproducible generation
            
        Returns:
            List of generated entities
        """
        # Set random seed if provided
        if seed is not None:
            random.seed(seed)
            self.last_seed = seed
        
        # Load template
        template = self.data_manager.load_template(template_name)
        
        # Generate entities
        entities = []
        entity_configs = template.get('entities', [])
        
        for config in entity_configs:
            generated_entities = self._generate_entity_group(config, template)
            entities.extend(generated_entities)
        
        # Apply post-generation rules
        entities = self._apply_post_generation_rules(entities, template)
        
        return entities
    
    def _generate_entity_group(self, config: Dict[str, Any], template: Dict[str, Any]) -> List[Entity]:
        """Generate a group of entities from a configuration"""
        entities = []
        entity_type = config.get('type', 'unknown')
        count = config.get('count', 1)
        
        # Generation parameters
        bounds = config.get('bounds', template.get('bounds', {'x': [0, 1000], 'y': [0, 800]}))
        properties = config.get('properties', {})
        spacing = config.get('spacing', None)
        distribution = config.get('distribution', 'random')
        
        # Generate positions
        positions = self._generate_positions(count, bounds, spacing, distribution)
        
        # Create entities
        for i, position in enumerate(positions):
            # Create entity properties with variations
            entity_properties = self._create_entity_properties(properties, i, count)
            
            # Create entity
            entity = self.entity_factory.create_entity(
                entity_type, 
                position, 
                **entity_properties
            )
            
            entities.append(entity)
        
        return entities
    
    def _generate_positions(self, count: int, bounds: Dict[str, List[float]], 
                           spacing: Optional[float], distribution: str) -> List[Tuple[float, float]]:
        """Generate positions for entities"""
        positions = []
        
        x_min, x_max = bounds['x']
        y_min, y_max = bounds['y']
        
        if distribution == 'random':
            # Simple random distribution
            for _ in range(count):
                x = random.uniform(x_min, x_max)
                y = random.uniform(y_min, y_max)
                positions.append((x, y))
        
        elif distribution == 'grid':
            # Grid-based distribution
            positions = self._generate_grid_positions(count, bounds)
        
        elif distribution == 'cluster':
            # Clustered distribution
            positions = self._generate_clustered_positions(count, bounds)
        
        elif distribution == 'orbital':
            # Orbital distribution around center
            positions = self._generate_orbital_positions(count, bounds)
        
        else:
            # Default to random
            positions = self._generate_positions(count, bounds, spacing, 'random')
        
        # Apply spacing if specified
        if spacing is not None:
            positions = self._apply_spacing(positions, spacing)
        
        return positions
    
    def _generate_grid_positions(self, count: int, bounds: Dict[str, List[float]]) -> List[Tuple[float, float]]:
        """Generate positions in a grid pattern"""
        positions = []
        x_min, x_max = bounds['x']
        y_min, y_max = bounds['y']
        
        # Calculate grid dimensions
        grid_size = math.ceil(math.sqrt(count))
        x_step = (x_max - x_min) / grid_size
        y_step = (y_max - y_min) / grid_size
        
        for i in range(count):
            grid_x = i % grid_size
            grid_y = i // grid_size
            
            x = x_min + (grid_x + 0.5) * x_step
            y = y_min + (grid_y + 0.5) * y_step
            
            # Add some randomness
            x += random.uniform(-x_step * 0.3, x_step * 0.3)
            y += random.uniform(-y_step * 0.3, y_step * 0.3)
            
            positions.append((x, y))
        
        return positions
    
    def _generate_clustered_positions(self, count: int, bounds: Dict[str, List[float]]) -> List[Tuple[float, float]]:
        """Generate positions in clusters"""
        positions = []
        x_min, x_max = bounds['x']
        y_min, y_max = bounds['y']
        
        # Create 2-4 cluster centers
        num_clusters = random.randint(2, 4)
        cluster_centers = []
        
        for _ in range(num_clusters):
            center_x = random.uniform(x_min, x_max)
            center_y = random.uniform(y_min, y_max)
            cluster_centers.append((center_x, center_y))
        
        # Distribute entities among clusters
        for i in range(count):
            cluster_center = cluster_centers[i % num_clusters]
            
            # Add random offset from cluster center
            cluster_radius = min(x_max - x_min, y_max - y_min) * 0.15
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0, cluster_radius)
            
            x = cluster_center[0] + distance * math.cos(angle)
            y = cluster_center[1] + distance * math.sin(angle)
            
            # Keep within bounds
            x = max(x_min, min(x_max, x))
            y = max(y_min, min(y_max, y))
            
            positions.append((x, y))
        
        return positions
    
    def _generate_orbital_positions(self, count: int, bounds: Dict[str, List[float]]) -> List[Tuple[float, float]]:
        """Generate positions in orbital pattern around center"""
        positions = []
        x_min, x_max = bounds['x']
        y_min, y_max = bounds['y']
        
        center_x = (x_min + x_max) / 2
        center_y = (y_min + y_max) / 2
        max_radius = min(x_max - center_x, y_max - center_y) * 0.8
        
        for i in range(count):
            # Different orbital radii
            radius = random.uniform(max_radius * 0.3, max_radius)
            
            # Angle with some randomness
            base_angle = (i / count) * 2 * math.pi
            angle = base_angle + random.uniform(-0.5, 0.5)
            
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            
            positions.append((x, y))
        
        return positions
    
    def _apply_spacing(self, positions: List[Tuple[float, float]], min_spacing: float) -> List[Tuple[float, float]]:
        """Apply minimum spacing between positions"""
        if len(positions) <= 1:
            return positions
        
        adjusted_positions = [positions[0]]
        
        for pos in positions[1:]:
            # Check distance to all existing positions
            valid_position = True
            for existing_pos in adjusted_positions:
                distance = math.sqrt((pos[0] - existing_pos[0])**2 + (pos[1] - existing_pos[1])**2)
                if distance < min_spacing:
                    valid_position = False
                    break
            
            if valid_position:
                adjusted_positions.append(pos)
            else:
                # Try to find a nearby valid position
                for attempt in range(10):
                    offset_x = random.uniform(-min_spacing, min_spacing)
                    offset_y = random.uniform(-min_spacing, min_spacing)
                    new_pos = (pos[0] + offset_x, pos[1] + offset_y)
                    
                    valid = True
                    for existing_pos in adjusted_positions:
                        distance = math.sqrt((new_pos[0] - existing_pos[0])**2 + (new_pos[1] - existing_pos[1])**2)
                        if distance < min_spacing:
                            valid = False
                            break
                    
                    if valid:
                        adjusted_positions.append(new_pos)
                        break
        
        return adjusted_positions
    
    def _create_entity_properties(self, base_properties: Dict[str, Any], index: int, total_count: int) -> Dict[str, Any]:
        """Create properties for an entity with variations"""
        properties = base_properties.copy()
        
        # Add variations to properties
        for key, value in properties.items():
            if key == 'name' and isinstance(value, str):
                # Add number to name if multiple entities
                if total_count > 1:
                    properties[key] = f"{value} {index + 1}"
            
            elif key == 'temperature' and isinstance(value, (int, float)):
                # Add temperature variation
                variation = random.uniform(-0.1, 0.1)
                properties[key] = int(value * (1 + variation))
            
            elif key == 'size' and isinstance(value, str):
                # Randomly vary size
                sizes = ['small', 'medium', 'large']
                if value in sizes:
                    current_index = sizes.index(value)
                    # Sometimes use adjacent sizes
                    if random.random() < 0.3:
                        new_index = max(0, min(len(sizes) - 1, current_index + random.choice([-1, 1])))
                        properties[key] = sizes[new_index]
            
            elif key == 'resources' and isinstance(value, list):
                # Sometimes add or remove resources
                if random.random() < 0.3:
                    available_resources = ['iron', 'nickel', 'copper', 'platinum', 'gold', 'uranium']
                    new_resources = value.copy()
                    if random.random() < 0.5 and len(new_resources) > 1:
                        # Remove a resource
                        new_resources.remove(random.choice(new_resources))
                    else:
                        # Add a resource
                        possible_additions = [r for r in available_resources if r not in new_resources]
                        if possible_additions:
                            new_resources.append(random.choice(possible_additions))
                    properties[key] = new_resources
        
        return properties
    
    def _apply_post_generation_rules(self, entities: List[Entity], template: Dict[str, Any]) -> List[Entity]:
        """Apply rules after all entities are generated"""
        rules = template.get('post_generation_rules', [])
        
        for rule in rules:
            rule_type = rule.get('type', '')
            
            if rule_type == 'avoid_star_overlap':
                entities = self._avoid_star_overlap(entities, rule.get('min_distance', 100))
            
            elif rule_type == 'orbital_alignment':
                entities = self._align_planets_to_star(entities, rule.get('star_types', ['star']))
            
            elif rule_type == 'trade_routes':
                entities = self._create_trade_routes(entities, rule.get('station_types', ['space_station']))
        
        return entities
    
    def _avoid_star_overlap(self, entities: List[Entity], min_distance: float) -> List[Entity]:
        """Ensure stars don't overlap with each other"""
        stars = [e for e in entities if e.type == 'star']
        
        for i, star1 in enumerate(stars):
            for j, star2 in enumerate(stars[i+1:], i+1):
                distance = math.sqrt((star1.position[0] - star2.position[0])**2 + 
                                   (star1.position[1] - star2.position[1])**2)
                
                if distance < min_distance:
                    # Move star2 away from star1
                    angle = math.atan2(star2.position[1] - star1.position[1], 
                                     star2.position[0] - star1.position[0])
                    new_x = star1.position[0] + min_distance * math.cos(angle)
                    new_y = star1.position[1] + min_distance * math.sin(angle)
                    star2.position = (new_x, new_y)
        
        return entities
    
    def _align_planets_to_star(self, entities: List[Entity], star_types: List[str]) -> List[Entity]:
        """Align planets in orbital patterns around stars"""
        stars = [e for e in entities if e.type in star_types]
        planets = [e for e in entities if e.type == 'planet']
        
        if not stars or not planets:
            return entities
        
        # For each planet, find the closest star and adjust position
        for planet in planets:
            closest_star = min(stars, key=lambda s: math.sqrt(
                (planet.position[0] - s.position[0])**2 + 
                (planet.position[1] - s.position[1])**2
            ))
            
            # Calculate orbital distance
            distance = math.sqrt((planet.position[0] - closest_star.position[0])**2 + 
                               (planet.position[1] - closest_star.position[1])**2)
            
            # Ensure minimum orbital distance
            min_orbital_distance = 80
            if distance < min_orbital_distance:
                angle = math.atan2(planet.position[1] - closest_star.position[1], 
                                 planet.position[0] - closest_star.position[0])
                new_x = closest_star.position[0] + min_orbital_distance * math.cos(angle)
                new_y = closest_star.position[1] + min_orbital_distance * math.sin(angle)
                planet.position = (new_x, new_y)
        
        return entities
    
    def _create_trade_routes(self, entities: List[Entity], station_types: List[str]) -> List[Entity]:
        """Create trade route connections between stations"""
        stations = [e for e in entities if e.type in station_types]
        
        if len(stations) < 2:
            return entities
        
        # Add trade route component to stations
        for station in stations:
            if not station.has_component('trade_routes'):
                station.add_component('trade_routes', {'connected_stations': []})
            
            # Connect to nearest stations
            other_stations = [s for s in stations if s != station]
            distances = []
            
            for other_station in other_stations:
                distance = math.sqrt((station.position[0] - other_station.position[0])**2 + 
                                   (station.position[1] - other_station.position[1])**2)
                distances.append((distance, other_station))
            
            # Connect to 1-3 nearest stations
            distances.sort()
            max_connections = min(3, len(distances))
            
            trade_routes = station.get_component('trade_routes')
            for i in range(max_connections):
                _, connected_station = distances[i]
                if connected_station.id not in trade_routes['connected_stations']:
                    trade_routes['connected_stations'].append(connected_station.id)
        
        return entities
    
    def get_generation_stats(self, entities: List[Entity]) -> Dict[str, Any]:
        """Get statistics about the generated map"""
        stats = {
            'total_entities': len(entities),
            'entity_types': {},
            'average_position': [0, 0],
            'bounds': {'x': [float('inf'), float('-inf')], 'y': [float('inf'), float('-inf')]},
            'seed_used': self.last_seed
        }
        
        if not entities:
            return stats
        
        # Calculate statistics
        total_x, total_y = 0, 0
        
        for entity in entities:
            # Count types
            entity_type = entity.type
            stats['entity_types'][entity_type] = stats['entity_types'].get(entity_type, 0) + 1
            
            # Calculate bounds and averages
            x, y = entity.position
            total_x += x
            total_y += y
            
            stats['bounds']['x'][0] = min(stats['bounds']['x'][0], x)
            stats['bounds']['x'][1] = max(stats['bounds']['x'][1], x)
            stats['bounds']['y'][0] = min(stats['bounds']['y'][0], y)
            stats['bounds']['y'][1] = max(stats['bounds']['y'][1], y)
        
        stats['average_position'] = [total_x / len(entities), total_y / len(entities)]
        
        return stats


# Example usage and testing
if __name__ == "__main__":
    # Create generator
    generator = SimpleMapGenerator()
    
    # Generate different types of maps
    templates = ['basic', 'frontier', 'warzone']
    
    for template in templates:
        print(f"\nGenerating {template} map...")
        entities = generator.generate_map(template, seed=42)
        
        stats = generator.get_generation_stats(entities)
        print(f"Generated {stats['total_entities']} entities")
        print(f"Entity types: {stats['entity_types']}")
        print(f"Map bounds: {stats['bounds']}")
        
        # Save the map
        generator.data_manager.save_entities(entities, f"example_{template}")
        print(f"Saved as example_{template}.json")
