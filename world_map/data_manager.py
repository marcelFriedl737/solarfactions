# data_manager.py - Simplified Data Management
"""
Simplified data management without complex validation.
Focuses on core functionality: load, save, and basic templates.
"""

import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from entities.simple import Entity, EntityFactory, create_basic_templates


class DataManager:
    """
    Simplified data management focusing on core functionality.
    
    Handles:
    - Loading and saving entity data
    - Template management
    - Basic file operations
    - Simple backup/versioning
    """
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.generated_dir = os.path.join(data_dir, "generated_maps")
        self.templates_dir = os.path.join(data_dir, "templates")
        self.backups_dir = os.path.join(data_dir, "backups")
        
        # Create directories if they don't exist
        for directory in [self.data_dir, self.generated_dir, self.templates_dir, self.backups_dir]:
            os.makedirs(directory, exist_ok=True)
        
        # Initialize entity factory
        self.entity_factory = EntityFactory()
        self._load_default_templates()
    
    def _load_default_templates(self):
        """Load default entity templates"""
        templates = create_basic_templates()
        for entity_type, template in templates.items():
            self.entity_factory.register_template(entity_type, template)
    
    def load_template(self, template_name: str) -> Dict[str, Any]:
        """Load a map generation template"""
        template_path = os.path.join(self.templates_dir, f"{template_name}.json")
        
        if not os.path.exists(template_path):
            # Return a default template if file doesn't exist
            return self._create_default_template(template_name)
        
        try:
            with open(template_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading template {template_name}: {e}")
            return self._create_default_template(template_name)
    
    def save_template(self, template_name: str, template_data: Dict[str, Any]):
        """Save a map generation template"""
        template_path = os.path.join(self.templates_dir, f"{template_name}.json")
        
        try:
            with open(template_path, 'w') as f:
                json.dump(template_data, f, indent=2)
        except IOError as e:
            print(f"Error saving template {template_name}: {e}")
    
    def save_entities(self, entities: List[Entity], filename: str, backup: bool = True):
        """Save entities to file with optional backup"""
        filepath = os.path.join(self.generated_dir, f"{filename}.json")
        
        # Create backup if requested and file exists
        if backup and os.path.exists(filepath):
            self._create_backup(filepath)
        
        # Convert entities to dictionaries
        data = {
            'metadata': {
                'created_at': datetime.now().isoformat(),
                'entity_count': len(entities),
                'filename': filename
            },
            'entities': [entity.to_dict() for entity in entities]
        }
        
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        except IOError as e:
            print(f"Error saving entities to {filename}: {e}")
            raise
    
    def load_entities(self, filename: str) -> List[Entity]:
        """Load entities from file"""
        filepath = os.path.join(self.generated_dir, f"{filename}.json")
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Entity file not found: {filename}")
        
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Handle both old and new format
            if 'entities' in data:
                entity_data = data['entities']
            else:
                entity_data = data  # Old format
            
            return [Entity.from_dict(item) for item in entity_data]
        
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading entities from {filename}: {e}")
            raise
    
    def list_saved_maps(self) -> List[str]:
        """List all saved maps"""
        try:
            files = os.listdir(self.generated_dir)
            return [f[:-5] for f in files if f.endswith('.json')]  # Remove .json extension
        except OSError:
            return []
    
    def list_templates(self) -> List[str]:
        """List all available templates"""
        try:
            files = os.listdir(self.templates_dir)
            return [f[:-5] for f in files if f.endswith('.json')]  # Remove .json extension
        except OSError:
            return []
    
    def delete_saved_map(self, filename: str, backup: bool = True):
        """Delete a saved map with optional backup"""
        filepath = os.path.join(self.generated_dir, f"{filename}.json")
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Map file not found: {filename}")
        
        if backup:
            self._create_backup(filepath)
        
        try:
            os.remove(filepath)
        except OSError as e:
            print(f"Error deleting map {filename}: {e}")
            raise
    
    def get_entity_factory(self) -> EntityFactory:
        """Get the entity factory for creating entities"""
        return self.entity_factory
    
    def _create_backup(self, filepath: str):
        """Create a backup of a file"""
        if not os.path.exists(filepath):
            return
        
        filename = os.path.basename(filepath)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{timestamp}_{filename}"
        backup_path = os.path.join(self.backups_dir, backup_name)
        
        try:
            import shutil
            shutil.copy2(filepath, backup_path)
        except IOError as e:
            print(f"Warning: Could not create backup of {filename}: {e}")
    
    def _create_default_template(self, template_name: str) -> Dict[str, Any]:
        """Create a default template for testing"""
        templates = {
            'basic': {
                'name': 'Basic System',
                'description': 'A simple star system with planets and asteroids',
                'bounds': {'x': [0, 1000], 'y': [0, 800]},
                'entities': [
                    {
                        'type': 'star',
                        'count': 1,
                        'bounds': {'x': [450, 550], 'y': [350, 450]},
                        'properties': {'name': 'Central Star', 'temperature': 5778}
                    },
                    {
                        'type': 'planet',
                        'count': 3,
                        'bounds': {'x': [100, 900], 'y': [100, 700]},
                        'properties': {'habitable': True}
                    },
                    {
                        'type': 'asteroid',
                        'count': 15,
                        'bounds': {'x': [0, 1000], 'y': [0, 800]},
                        'properties': {'resources': ['iron', 'nickel']}
                    },
                    {
                        'type': 'space_station',
                        'count': 2,
                        'bounds': {'x': [200, 800], 'y': [200, 600]},
                        'properties': {'services': ['trading', 'repair']}
                    }
                ]
            },
            'frontier': {
                'name': 'Frontier System',
                'description': 'A remote system with mining operations',
                'bounds': {'x': [0, 1200], 'y': [0, 1000]},
                'entities': [
                    {
                        'type': 'star',
                        'count': 1,
                        'bounds': {'x': [550, 650], 'y': [450, 550]},
                        'properties': {'name': 'Frontier Star', 'temperature': 4500}
                    },
                    {
                        'type': 'asteroid',
                        'count': 25,
                        'bounds': {'x': [0, 1200], 'y': [0, 1000]},
                        'properties': {'resources': ['iron', 'nickel', 'platinum']}
                    },
                    {
                        'type': 'mining_ship',
                        'count': 5,
                        'bounds': {'x': [100, 1100], 'y': [100, 900]},
                        'properties': {'crew': 3}
                    },
                    {
                        'type': 'space_station',
                        'count': 1,
                        'bounds': {'x': [300, 900], 'y': [300, 700]},
                        'properties': {'services': ['trading', 'repair', 'refuel']}
                    }
                ]
            },
            'warzone': {
                'name': 'Contested System',
                'description': 'A system with active combat operations',
                'bounds': {'x': [0, 1500], 'y': [0, 1200]},
                'entities': [
                    {
                        'type': 'star',
                        'count': 1,
                        'bounds': {'x': [700, 800], 'y': [550, 650]},
                        'properties': {'name': 'Contested Star', 'temperature': 6000}
                    },
                    {
                        'type': 'planet',
                        'count': 2,
                        'bounds': {'x': [200, 1300], 'y': [200, 1000]},
                        'properties': {'habitable': False}
                    },
                    {
                        'type': 'fighter',
                        'count': 10,
                        'bounds': {'x': [100, 1400], 'y': [100, 1100]},
                        'properties': {'crew': 1}
                    },
                    {
                        'type': 'cargo_ship',
                        'count': 3,
                        'bounds': {'x': [200, 1300], 'y': [200, 1000]},
                        'properties': {'crew': 5}
                    }
                ]
            }
        }
        
        return templates.get(template_name, templates['basic'])
    
    def export_statistics(self, entities: List[Entity]) -> Dict[str, Any]:
        """Export basic statistics about entities"""
        stats = {
            'total_entities': len(entities),
            'entity_types': {},
            'components_used': set(),
            'timestamp': datetime.now().isoformat()
        }
        
        for entity in entities:
            # Count entity types
            entity_type = entity.type
            stats['entity_types'][entity_type] = stats['entity_types'].get(entity_type, 0) + 1
            
            # Track components
            for component_name in entity.components.keys():
                stats['components_used'].add(component_name)
        
        # Convert set to list for JSON serialization
        stats['components_used'] = list(stats['components_used'])
        
        return stats


# Example usage and testing
if __name__ == "__main__":
    # Create data manager
    dm = DataManager()
    
    # Create some test entities
    factory = dm.get_entity_factory()
    
    entities = [
        factory.create_entity('star', (500, 400), name='Test Star'),
        factory.create_entity('planet', (300, 400), name='Test Planet'),
        factory.create_entity('cargo_ship', (100, 200), name='Test Ship')
    ]
    
    # Save entities
    dm.save_entities(entities, 'test_map')
    print("Entities saved")
    
    # Load entities back
    loaded_entities = dm.load_entities('test_map')
    print(f"Loaded {len(loaded_entities)} entities")
    
    # Show statistics
    stats = dm.export_statistics(loaded_entities)
    print(f"Statistics: {stats}")
    
    # List saved maps
    maps = dm.list_saved_maps()
    print(f"Available maps: {maps}")
    
    # Test template loading
    template = dm.load_template('basic')
    print(f"Template loaded: {template['name']}")
