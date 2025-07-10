# generator.py
import json
import random
from datetime import datetime
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from coordinates import Coordinates, Region
from entities.base import Entity
from entities.vessels import FreighterClass, FighterClass
from entities.structures import TradingStation, IndustrialStation
from entities.resources import MetallicAsteroid, IceAsteroid

@dataclass
class MapTemplate:
    name: str
    description: str
    size: Dict[str, int]
    entity_counts: Dict[str, Dict[str, int]]
    placement_rules: Dict[str, Any]

class MapGenerator:
    """Procedural map generation engine"""
    
    def __init__(self, template_file: str = "data/map_templates.json"):
        self.templates = self._load_templates(template_file)
        self.entity_registry = {
            'trading_stations': TradingStation,
            'industrial_stations': IndustrialStation,
            'freighter_ships': FreighterClass,
            'fighter_ships': FighterClass,
            'metallic_asteroids': MetallicAsteroid,
            'ice_asteroids': IceAsteroid
        }
    
    def _load_templates(self, file_path: str) -> Dict[str, MapTemplate]:
        """Load map generation templates from JSON file"""
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        templates = {}
        for name, template_data in data['templates'].items():
            templates[name] = MapTemplate(
                name=template_data['name'],
                description=template_data['description'],
                size=template_data['size'],
                entity_counts=template_data['entity_counts'],
                placement_rules=template_data['placement_rules']
            )
        
        return templates
    
    def generate_map(self, template_name: str, seed: int = None) -> List[Entity]:
        """Generate a map using the specified template"""
        if seed is not None:
            random.seed(seed)
        
        template = self.templates[template_name]
        entities = []
        
        # Create map region
        region = Region(0, 0, template.size['width'], template.size['height'])
        
        # Generate entities by type
        for entity_type, count_range in template.entity_counts.items():
            count = random.randint(count_range['min'], count_range['max'])
            entity_class = self.entity_registry[entity_type]
            
            if entity_type.endswith('_stations'):
                entities.extend(self._generate_stations(entity_class, count, region, template))
            elif entity_type.endswith('_ships'):
                entities.extend(self._generate_ships(entity_class, count, region, template, entities))
            elif entity_type.endswith('_asteroids'):
                entities.extend(self._generate_asteroids(entity_class, count, region, template))
        
        return entities
    
    def _generate_stations(self, entity_class: type, count: int, region: Region, template: MapTemplate) -> List[Entity]:
        """Generate stations with placement rules"""
        entities = []
        placement_rules = template.placement_rules.get('stations', {})
        
        min_edge_distance = placement_rules.get('min_distance_from_edge', 50)
        min_between_distance = placement_rules.get('min_distance_between', 100)
        
        # Create valid placement region
        valid_region = Region(
            region.min_x + min_edge_distance,
            region.min_y + min_edge_distance,
            region.max_x - min_edge_distance,
            region.max_y - min_edge_distance
        )
        
        attempts = 0
        while len(entities) < count and attempts < count * 10:
            position = valid_region.random_point()
            
            # Check minimum distance from other stations
            valid_position = True
            for existing in entities:
                if position.distance_to(existing.position) < min_between_distance:
                    valid_position = False
                    break
            
            if valid_position:
                entities.append(entity_class(position=position))
            
            attempts += 1
        
        return entities
    
    def _generate_ships(self, entity_class: type, count: int, region: Region, template: MapTemplate, existing_entities: List[Entity]) -> List[Entity]:
        """Generate ships with placement rules"""
        entities = []
        placement_rules = template.placement_rules.get('ships', {})
        
        spawn_near_stations = placement_rules.get('spawn_near_stations', False)
        station_proximity = placement_rules.get('station_proximity', 50)
        
        # Find stations for proximity spawning
        stations = [e for e in existing_entities if 'Station' in e.__class__.__name__]
        
        for _ in range(count):
            if spawn_near_stations and stations:
                # Spawn near a random station
                station = random.choice(stations)
                angle = random.uniform(0, 2 * 3.14159)
                distance = random.uniform(10, station_proximity)
                
                position = Coordinates(
                    station.position.x + distance * random.uniform(-1, 1),
                    station.position.y + distance * random.uniform(-1, 1)
                )
                
                # Ensure position is within region
                position.x = max(region.min_x, min(region.max_x, position.x))
                position.y = max(region.min_y, min(region.max_y, position.y))
            else:
                position = region.random_point()
            
            entities.append(entity_class(position=position))
        
        return entities
    
    def _generate_asteroids(self, entity_class: type, count: int, region: Region, template: MapTemplate) -> List[Entity]:
        """Generate asteroids with clustering rules"""
        entities = []
        placement_rules = template.placement_rules.get('asteroids', {})
        
        cluster_probability = placement_rules.get('cluster_probability', 0.5)
        cluster_size_range = placement_rules.get('cluster_size', {'min': 3, 'max': 8})
        cluster_spread = placement_rules.get('cluster_spread', 30)
        
        remaining_count = count
        
        while remaining_count > 0:
            if random.random() < cluster_probability and remaining_count > 1:
                # Create cluster
                cluster_size = min(
                    random.randint(cluster_size_range['min'], cluster_size_range['max']),
                    remaining_count
                )
                
                # Cluster center
                center = region.random_point()
                
                for _ in range(cluster_size):
                    # Position within cluster
                    angle = random.uniform(0, 2 * 3.14159)
                    distance = random.uniform(0, cluster_spread)
                    
                    position = Coordinates(
                        center.x + distance * random.uniform(-1, 1),
                        center.y + distance * random.uniform(-1, 1)
                    )
                    
                    # Ensure position is within region
                    position.x = max(region.min_x, min(region.max_x, position.x))
                    position.y = max(region.min_y, min(region.max_y, position.y))
                    
                    entities.append(entity_class(position=position))
                
                remaining_count -= cluster_size
            else:
                # Create single asteroid
                position = region.random_point()
                entities.append(entity_class(position=position))
                remaining_count -= 1
        
        return entities
    
    def export_map(self, entities: List[Entity], filename: str) -> None:
        """Export generated map to JSON file"""
        map_data = {
            'generated_at': datetime.now().isoformat(),
            'entity_count': len(entities),
            'entities': [entity.to_dict() for entity in entities]
        }
        
        with open(f"data/generated_maps/{filename}.json", 'w') as f:
            json.dump(map_data, f, indent=2)