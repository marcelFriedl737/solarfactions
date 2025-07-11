# simple/__init__.py - Simplified Solar Factions package
"""
Simplified Solar Factions - A streamlined space map generation system.

This package provides an easy-to-use interface for generating, managing,
and visualizing space maps with entities like stars, planets, ships, and stations.

Key features:
- Simple entity system using tuples for positions
- Template-based map generation
- Easy data persistence
- Interactive visualization with pygame
- Comprehensive test coverage

Main components:
- entities.entity: Core entity system
- data_manager: Data loading/saving
- generator: Map generation
- renderer: Visual display
- main: Entry point and CLI

Example usage:
    from simple.generator import SimpleMapGenerator
    from simple.renderer import SimpleRenderer
    
    generator = SimpleMapGenerator()
    entities = generator.generate_map('basic')
    
    renderer = SimpleRenderer()
    renderer.run(entities)
"""

from .entities.entity import Entity, EntityFactory
from .data_manager import DataManager
from .generator import SimpleMapGenerator
from .renderer import SimpleRenderer

__version__ = '1.0.0'
__author__ = 'Solar Factions Team'

__all__ = [
    'Entity',
    'EntityFactory', 
    'DataManager',
    'SimpleMapGenerator',
    'SimpleRenderer'
]
