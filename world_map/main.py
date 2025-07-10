# main.py
import sys
import argparse
from typing import List
from generator import MapGenerator
from renderer import MapRenderer
from entities.base import Entity

def main():
    parser = argparse.ArgumentParser(description='Solar Factions World Map Generator')
    parser.add_argument('--template', default='basic_sector', help='Map template to use')
    parser.add_argument('--seed', type=int, default=None, help='Random seed for generation')
    parser.add_argument('--export', help='Export map to file (without extension)')
    parser.add_argument('--no-render', action='store_true', help='Skip rendering')
    
    args = parser.parse_args()
    
    # Generate map
    print(f"Generating map using template: {args.template}")
    generator = MapGenerator()
    entities = generator.generate_map(args.template, args.seed)
    
    print(f"Generated {len(entities)} entities")
    
    # Export if requested
    if args.export:
        generator.export_map(entities, args.export)
        print(f"Map exported to: data/generated_maps/{args.export}.json")
    
    # Render if not skipped
    if not args.no_render:
        renderer = MapRenderer()
        renderer.run(entities)

if __name__ == "__main__":
    main()