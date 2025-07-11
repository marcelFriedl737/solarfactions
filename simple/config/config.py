# config.py - Configuration for the simplified system
"""
Configuration settings for the simplified Solar Factions system.
"""

# Default map generation settings
DEFAULT_MAP_SIZE = (1000, 1000)
DEFAULT_ENTITY_COUNT = 50
DEFAULT_SEED = None

# Entity generation bounds
ENTITY_BOUNDS = {
    'star': {'min_count': 1, 'max_count': 3},
    'planet': {'min_count': 2, 'max_count': 8},
    'asteroid': {'min_count': 5, 'max_count': 20},
    'space_station': {'min_count': 1, 'max_count': 5},
    'cargo_ship': {'min_count': 3, 'max_count': 10},
    'fighter': {'min_count': 1, 'max_count': 8},
    'mining_ship': {'min_count': 1, 'max_count': 5}
}

# Renderer settings
RENDERER_SETTINGS = {
    'width': 1200,
    'height': 800,
    'fps': 60,
    'background_color': (10, 10, 30),
    'grid_color': (30, 30, 50),
    'grid_size': 50
}

# Data storage settings
DATA_PATHS = {
    'saves': 'data/saved_maps',
    'templates': 'data/templates',
    'generated': 'data/generated_maps',
    'backups': 'data/backups'
}

# File extensions
FILE_EXTENSIONS = {
    'map': '.json',
    'template': '.json',
    'backup': '.json'
}

# Template names
AVAILABLE_TEMPLATES = ['basic', 'frontier', 'warzone', 'trading_hub', 'mining_sector']

# Entity colors for rendering
ENTITY_COLORS = {
    'star': (255, 255, 100),      # Yellow
    'planet': (100, 200, 100),    # Green
    'asteroid': (150, 150, 150),  # Gray
    'space_station': (100, 100, 255),  # Blue
    'cargo_ship': (200, 200, 100),     # Light yellow
    'fighter': (255, 100, 100),        # Red
    'mining_ship': (150, 100, 200),    # Purple
    'default': (255, 255, 255)         # White
}

# Entity sizes for rendering
ENTITY_SIZES = {
    'star': 20,
    'planet': 15,
    'asteroid': 8,
    'space_station': 12,
    'cargo_ship': 6,
    'fighter': 4,
    'mining_ship': 7,
    'default': 5
}
