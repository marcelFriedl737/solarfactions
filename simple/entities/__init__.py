# entities/__init__.py - Entity system module
"""
Solar Factions Simplified Entity System

This module provides a component-based entity system that replaces
complex inheritance hierarchies with flexible composition.

Components are now configurable and extendable through JSON files.
"""

from .entity import (
    Entity, EntityFactory, 
    component_registry, 
    get_available_components, 
    get_component_info,
    create_component,
    load_custom_components,
    register_component,
    create_basic_templates,
    ComponentTemplates  # For backward compatibility
)

__all__ = [
    'Entity', 
    'EntityFactory',
    'component_registry',
    'get_available_components',
    'get_component_info', 
    'create_component',
    'load_custom_components',
    'register_component',
    'create_basic_templates',
    'ComponentTemplates'
]
