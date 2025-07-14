#!/usr/bin/env python3
# component_manager.py - Utility for managing components
"""
Component management utility for the simplified Solar Factions system.
Allows users to view, create, and manage component definitions.
"""

import json
import os
import sys
from typing import Dict, Any, List

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from entities.entity import component_registry, get_available_components, get_component_info


def list_components():
    """List all available components"""
    print("Available Components:")
    print("=" * 50)
    
    components = get_available_components()
    for component_name in sorted(components):
        info = get_component_info(component_name)
        print(f"• {component_name}: {info['description']}")
    
    print(f"\nTotal: {len(components)} components")


def show_component_details(component_name: str):
    """Show detailed information about a component"""
    info = get_component_info(component_name)
    
    if not info['available']:
        print(f"Component '{component_name}' not found!")
        return
    
    print(f"Component: {component_name}")
    print("=" * 50)
    print(f"Description: {info['description']}")
    print(f"Properties:")
    
    for prop_name, prop_def in info['properties'].items():
        if isinstance(prop_def, dict):
            prop_type = prop_def.get('type', 'unknown')
            default_value = prop_def.get('default', 'none')
            description = prop_def.get('description', 'No description')
            print(f"  • {prop_name} ({prop_type}): {description}")
            print(f"    Default: {default_value}")
        else:
            print(f"  • {prop_name}: {prop_def}")


def create_component_template():
    """Interactive component creation"""
    print("Create New Component")
    print("=" * 50)
    
    name = input("Component name: ").strip()
    if not name:
        print("Component name is required!")
        return
    
    description = input("Description: ").strip()
    if not description:
        description = f"{name} component"
    
    component_def = {
        "description": description,
        "properties": {}
    }
    
    print("\nAdd properties (press Enter with empty name to finish):")
    while True:
        prop_name = input("Property name: ").strip()
        if not prop_name:
            break
        
        prop_type = input(f"Type for {prop_name} (integer/float/string/boolean/array/object): ").strip()
        if prop_type not in ['integer', 'float', 'string', 'boolean', 'array', 'object']:
            prop_type = 'string'
        
        prop_description = input(f"Description for {prop_name}: ").strip()
        if not prop_description:
            prop_description = f"{prop_name} property"
        
        default_value = input(f"Default value for {prop_name} (optional): ").strip()
        
        prop_def = {
            "type": prop_type,
            "description": prop_description
        }
        
        if default_value:
            # Try to parse the default value
            try:
                if prop_type == 'integer':
                    default_value = int(default_value)
                elif prop_type == 'float':
                    default_value = float(default_value)
                elif prop_type == 'boolean':
                    default_value = default_value.lower() in ['true', '1', 'yes', 'on']
                elif prop_type == 'array':
                    default_value = json.loads(default_value)
                elif prop_type == 'object':
                    default_value = json.loads(default_value)
                # string stays as string
                
                prop_def["default"] = default_value
            except (ValueError, json.JSONDecodeError):
                print(f"Warning: Could not parse default value '{default_value}', skipping")
        
        component_def["properties"][prop_name] = prop_def
    
    # Save to custom components file
    custom_components_path = os.path.join('data', 'components', 'custom_components.json')
    
    try:
        # Load existing custom components
        if os.path.exists(custom_components_path):
            with open(custom_components_path, 'r') as f:
                custom_components = json.load(f)
        else:
            custom_components = {}
        
        # Add new component
        custom_components[name] = component_def
        
        # Save back
        os.makedirs(os.path.dirname(custom_components_path), exist_ok=True)
        with open(custom_components_path, 'w') as f:
            json.dump(custom_components, f, indent=2)
        
        print(f"\nComponent '{name}' saved to {custom_components_path}")
        
        # Reload the component registry
        component_registry.load_components_from_file(custom_components_path)
        print(f"Component '{name}' is now available!")
        
    except Exception as e:
        print(f"Error saving component: {e}")


def validate_component_file(filepath: str):
    """Validate a component definition file"""
    try:
        with open(filepath, 'r') as f:
            components = json.load(f)
        
        if not isinstance(components, dict):
            print(f"Error: {filepath} should contain a JSON object")
            return False
        
        valid = True
        for component_name, component_def in components.items():
            print(f"Validating component: {component_name}")
            
            if not isinstance(component_def, dict):
                print(f"  Error: Component definition should be an object")
                valid = False
                continue
            
            if 'description' not in component_def:
                print(f"  Warning: No description provided")
            
            if 'properties' not in component_def:
                print(f"  Warning: No properties defined")
                continue
            
            properties = component_def['properties']
            if not isinstance(properties, dict):
                print(f"  Error: Properties should be an object")
                valid = False
                continue
            
            for prop_name, prop_def in properties.items():
                if isinstance(prop_def, dict):
                    if 'type' not in prop_def:
                        print(f"  Warning: Property {prop_name} has no type")
                    else:
                        prop_type = prop_def['type']
                        if prop_type not in ['integer', 'float', 'string', 'boolean', 'array', 'object', 'position']:
                            print(f"  Warning: Property {prop_name} has unknown type: {prop_type}")
            
            print(f"  ✓ Component {component_name} is valid")
        
        if valid:
            print(f"\n✓ {filepath} is valid!")
        else:
            print(f"\n✗ {filepath} has errors!")
        
        return valid
        
    except json.JSONDecodeError as e:
        print(f"Error: {filepath} is not valid JSON: {e}")
        return False
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return False


def main():
    """Main command-line interface"""
    if len(sys.argv) < 2:
        print("Component Manager for Solar Factions")
        print("Usage:")
        print("  python component_manager.py list                    - List all components")
        print("  python component_manager.py show <component_name>   - Show component details")
        print("  python component_manager.py create                  - Create new component")
        print("  python component_manager.py validate <file>         - Validate component file")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'list':
        list_components()
    
    elif command == 'show':
        if len(sys.argv) < 3:
            print("Usage: python component_manager.py show <component_name>")
            return
        show_component_details(sys.argv[2])
    
    elif command == 'create':
        create_component_template()
    
    elif command == 'validate':
        if len(sys.argv) < 3:
            print("Usage: python component_manager.py validate <file>")
            return
        validate_component_file(sys.argv[2])
    
    else:
        print(f"Unknown command: {command}")
        print("Available commands: list, show, create, validate")


if __name__ == "__main__":
    main()
