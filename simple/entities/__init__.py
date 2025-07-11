# entities/__init__.py - Entity system module
"""
Solar Factions Simplified Entity System

This module provides a component-based entity system that replaces
complex inheritance hierarchies with flexible composition.
"""

from .entity import Entity, EntityFactory, ComponentTemplates, create_basic_templates

__all__ = ['Entity', 'EntityFactory', 'ComponentTemplates', 'create_basic_templates']
