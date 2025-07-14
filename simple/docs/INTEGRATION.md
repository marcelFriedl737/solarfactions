# Integration Guide

## Overview

This guide demonstrates how to integrate Solar Factions with external systems, extend its functionality, and build custom applications on top of the framework.

## Table of Contents

1. [Web Integration](#web-integration)
2. [Database Integration](#database-integration)
3. [Network Integration](#network-integration)
4. [External API Integration](#external-api-integration)
5. [Plugin System](#plugin-system)
6. [Custom User Interfaces](#custom-user-interfaces)
7. [Data Export/Import](#data-exportimport)
8. [Real-time Communication](#real-time-communication)
9. [Testing Integration](#testing-integration)
10. [Deployment Strategies](#deployment-strategies)

## Web Integration

### Flask Web Server

Create a web interface for Solar Factions:

```python
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import json
import threading
from game_manager import GameManager

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

class WebGameManager:
    def __init__(self):
        self.game_manager = GameManager()
        self.is_running = False
        self.web_clients = set()
    
    def start_web_game(self, template_name="basic", seed=None):
        """Start a game session for web clients"""
        if not self.is_running:
            self.game_manager.generate_map(template_name, seed)
            self.game_manager.start_game_loop()
            self.is_running = True
            
            # Start update thread for web clients
            self.update_thread = threading.Thread(target=self.web_update_loop)
            self.update_thread.daemon = True
            self.update_thread.start()
    
    def web_update_loop(self):
        """Send updates to web clients"""
        import time
        while self.is_running:
            if self.web_clients:
                # Get current game state
                game_state = self.get_game_state()
                
                # Send to all connected clients
                socketio.emit('game_update', game_state, broadcast=True)
            
            time.sleep(0.1)  # 10 FPS for web updates
    
    def get_game_state(self):
        """Get current game state for web clients"""
        entities_data = []
        for entity in self.game_manager.entities:
            if hasattr(entity, 'id'):
                entity_data = {
                    'id': entity.id,
                    'type': entity.type,
                    'position': entity.position,
                    'properties': entity.properties
                }
                
                # Add AI state if available
                ai_state = self.game_manager.ai_system.get_ai_state(entity.id)
                if ai_state:
                    entity_data['ai'] = {
                        'behavior': ai_state.behavior_name,
                        'energy': ai_state.energy,
                        'target': ai_state.memory.current_target
                    }
                
                entities_data.append(entity_data)
        
        # Get system statistics
        stats = self.game_manager.game_loop.get_stats()
        
        return {
            'entities': entities_data,
            'statistics': stats,
            'timestamp': time.time()
        }

# Global web game manager
web_game = WebGameManager()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/start_game', methods=['POST'])
def start_game():
    data = request.json
    template = data.get('template', 'basic')
    seed = data.get('seed', None)
    
    web_game.start_web_game(template, seed)
    return jsonify({'status': 'started', 'template': template})

@app.route('/api/game_state')
def get_game_state():
    return jsonify(web_game.get_game_state())

@app.route('/api/control/<action>')
def game_control(action):
    if action == 'pause':
        web_game.game_manager.pause_game()
    elif action == 'resume':
        web_game.game_manager.resume_game()
    elif action == 'speed_up':
        current_speed = web_game.game_manager.game_loop.state.speed_multiplier
        web_game.game_manager.set_game_speed(min(5.0, current_speed * 1.5))
    elif action == 'slow_down':
        current_speed = web_game.game_manager.game_loop.state.speed_multiplier
        web_game.game_manager.set_game_speed(max(0.1, current_speed / 1.5))
    
    return jsonify({'status': 'ok', 'action': action})

@socketio.on('connect')
def handle_connect():
    web_game.web_clients.add(request.sid)
    emit('connected', {'status': 'connected'})

@socketio.on('disconnect')
def handle_disconnect():
    web_game.web_clients.discard(request.sid)

# HTML Template (templates/index.html)
html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Solar Factions Web Interface</title>
    <script src="https://cdn.socket.io/4.0.0/socket.io.min.js"></script>
    <style>
        #canvas { border: 1px solid #ccc; }
        #controls { margin: 10px 0; }
        #stats { font-family: monospace; }
    </style>
</head>
<body>
    <h1>Solar Factions Web Interface</h1>
    <div id="controls">
        <button onclick="startGame()">Start Game</button>
        <button onclick="pauseGame()">Pause</button>
        <button onclick="resumeGame()">Resume</button>
        <button onclick="speedUp()">Speed Up</button>
        <button onclick="slowDown()">Slow Down</button>
    </div>
    <canvas id="canvas" width="800" height="600"></canvas>
    <div id="stats"></div>
    
    <script>
        const socket = io();
        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');
        
        let gameState = null;
        
        socket.on('game_update', function(data) {
            gameState = data;
            render();
            updateStats();
        });
        
        function startGame() {
            fetch('/api/start_game', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({template: 'basic', seed: 42})
            });
        }
        
        function pauseGame() { fetch('/api/control/pause'); }
        function resumeGame() { fetch('/api/control/resume'); }
        function speedUp() { fetch('/api/control/speed_up'); }
        function slowDown() { fetch('/api/control/slow_down'); }
        
        function render() {
            if (!gameState) return;
            
            // Clear canvas
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // Draw entities
            gameState.entities.forEach(entity => {
                const x = entity.position[0] * 0.4; // Scale to canvas
                const y = entity.position[1] * 0.4;
                
                // Color by type
                const colors = {
                    'star': '#ffff00',
                    'planet': '#00ff00',
                    'fighter': '#ff0000',
                    'cargo_ship': '#0000ff',
                    'space_station': '#808080'
                };
                
                ctx.fillStyle = colors[entity.type] || '#ffffff';
                ctx.fillRect(x-2, y-2, 4, 4);
                
                // Draw name
                ctx.fillStyle = '#000000';
                ctx.font = '8px Arial';
                ctx.fillText(entity.properties.name || entity.type, x+5, y);
            });
        }
        
        function updateStats() {
            if (!gameState) return;
            
            const stats = gameState.statistics;
            document.getElementById('stats').innerHTML = `
                <h3>Statistics</h3>
                <p>Tick: ${stats.tick}</p>
                <p>Game Time: ${stats.game_time.toFixed(1)}s</p>
                <p>TPS: ${stats.actual_tps.toFixed(1)}/${stats.target_tps}</p>
                <p>Entities: ${gameState.entities.length}</p>
                <p>Status: ${stats.is_running ? 'Running' : 'Stopped'}</p>
                <p>Paused: ${stats.is_paused ? 'Yes' : 'No'}</p>
            `;
        }
    </script>
</body>
</html>
"""

# Save template
import os
os.makedirs('templates', exist_ok=True)
with open('templates/index.html', 'w') as f:
    f.write(html_template)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
```

### REST API

Create a REST API for Solar Factions:

```python
from flask import Flask, jsonify, request
from flask_restful import Api, Resource
import uuid

app = Flask(__name__)
api = Api(app)

class GameSessionManager:
    def __init__(self):
        self.sessions = {}
    
    def create_session(self, template="basic", seed=None):
        session_id = str(uuid.uuid4())
        game_manager = GameManager()
        game_manager.generate_map(template, seed)
        
        self.sessions[session_id] = {
            'game_manager': game_manager,
            'created_at': time.time(),
            'template': template,
            'seed': seed
        }
        
        return session_id
    
    def get_session(self, session_id):
        return self.sessions.get(session_id)
    
    def delete_session(self, session_id):
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session['game_manager'].stop_game_loop()
            del self.sessions[session_id]
            return True
        return False

session_manager = GameSessionManager()

class GameSession(Resource):
    def post(self):
        """Create a new game session"""
        data = request.json or {}
        template = data.get('template', 'basic')
        seed = data.get('seed', None)
        
        session_id = session_manager.create_session(template, seed)
        return {'session_id': session_id, 'template': template}, 201
    
    def get(self, session_id):
        """Get game session state"""
        session = session_manager.get_session(session_id)
        if not session:
            return {'error': 'Session not found'}, 404
        
        game_manager = session['game_manager']
        entities_data = []
        
        for entity in game_manager.entities:
            if hasattr(entity, 'id'):
                entities_data.append({
                    'id': entity.id,
                    'type': entity.type,
                    'position': entity.position,
                    'properties': entity.properties
                })
        
        stats = game_manager.game_loop.get_stats()
        
        return {
            'session_id': session_id,
            'entities': entities_data,
            'statistics': stats,
            'created_at': session['created_at']
        }
    
    def delete(self, session_id):
        """Delete game session"""
        if session_manager.delete_session(session_id):
            return {'message': 'Session deleted'}, 200
        return {'error': 'Session not found'}, 404

class GameControl(Resource):
    def post(self, session_id, action):
        """Control game session"""
        session = session_manager.get_session(session_id)
        if not session:
            return {'error': 'Session not found'}, 404
        
        game_manager = session['game_manager']
        
        if action == 'start':
            game_manager.start_game_loop()
        elif action == 'pause':
            game_manager.pause_game()
        elif action == 'resume':
            game_manager.resume_game()
        elif action == 'stop':
            game_manager.stop_game_loop()
        else:
            return {'error': 'Invalid action'}, 400
        
        return {'message': f'Action {action} executed'}, 200

api.add_resource(GameSession, '/api/sessions', '/api/sessions/<session_id>')
api.add_resource(GameControl, '/api/sessions/<session_id>/control/<action>')

if __name__ == '__main__':
    app.run(debug=True)
```

## Database Integration

### SQLAlchemy Integration

Store game data in a database:

```python
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json
import datetime

Base = declarative_base()

class GameSession(Base):
    __tablename__ = 'game_sessions'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(36), unique=True, nullable=False)
    template = Column(String(50), nullable=False)
    seed = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)
    is_active = Column(Boolean, default=True)
    game_state = Column(Text)  # JSON blob

class EntitySnapshot(Base):
    __tablename__ = 'entity_snapshots'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(36), nullable=False)
    entity_id = Column(String(36), nullable=False)
    entity_type = Column(String(50), nullable=False)
    position_x = Column(Float, nullable=False)
    position_y = Column(Float, nullable=False)
    properties = Column(Text)  # JSON blob
    components = Column(Text)  # JSON blob
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class GameEvent(Base):
    __tablename__ = 'game_events'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(36), nullable=False)
    event_type = Column(String(50), nullable=False)
    event_data = Column(Text)  # JSON blob
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class DatabaseGameManager:
    def __init__(self, database_url="sqlite:///solarfactions.db"):
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.db_session = Session()
        
        self.game_manager = GameManager()
        self.session_id = None
    
    def create_session(self, template="basic", seed=None):
        """Create a new database-backed game session"""
        self.session_id = str(uuid.uuid4())
        
        # Generate map
        self.game_manager.generate_map(template, seed)
        
        # Create database record
        db_session = GameSession(
            session_id=self.session_id,
            template=template,
            seed=seed,
            game_state=json.dumps(self.serialize_game_state())
        )
        
        self.db_session.add(db_session)
        self.db_session.commit()
        
        # Log creation event
        self.log_event('session_created', {
            'template': template,
            'seed': seed,
            'entity_count': len(self.game_manager.entities)
        })
        
        return self.session_id
    
    def save_snapshot(self):
        """Save current game state to database"""
        if not self.session_id:
            return
        
        # Save entity snapshots
        for entity in self.game_manager.entities:
            if hasattr(entity, 'id'):
                snapshot = EntitySnapshot(
                    session_id=self.session_id,
                    entity_id=entity.id,
                    entity_type=entity.type,
                    position_x=entity.position[0],
                    position_y=entity.position[1],
                    properties=json.dumps(entity.properties),
                    components=json.dumps(entity.components) if hasattr(entity, 'components') else '{}'
                )
                self.db_session.add(snapshot)
        
        # Update session record
        session = self.db_session.query(GameSession).filter_by(session_id=self.session_id).first()
        if session:
            session.last_updated = datetime.datetime.utcnow()
            session.game_state = json.dumps(self.serialize_game_state())
        
        self.db_session.commit()
    
    def load_session(self, session_id):
        """Load game session from database"""
        session = self.db_session.query(GameSession).filter_by(session_id=session_id).first()
        if not session:
            return False
        
        self.session_id = session_id
        
        # Load game state
        game_state = json.loads(session.game_state)
        self.deserialize_game_state(game_state)
        
        self.log_event('session_loaded', {'session_id': session_id})
        return True
    
    def serialize_game_state(self):
        """Serialize game state for database storage"""
        return {
            'entities': [self.serialize_entity(e) for e in self.game_manager.entities],
            'statistics': self.game_manager.game_loop.get_stats(),
            'timestamp': time.time()
        }
    
    def serialize_entity(self, entity):
        """Serialize a single entity"""
        return {
            'id': getattr(entity, 'id', None),
            'type': entity.type,
            'position': entity.position,
            'properties': entity.properties,
            'components': getattr(entity, 'components', {})
        }
    
    def deserialize_game_state(self, game_state):
        """Deserialize game state from database"""
        from entities.entity import Entity
        
        entities = []
        for entity_data in game_state['entities']:
            entity = Entity(
                entity_data['type'],
                entity_data['position'],
                **entity_data['properties']
            )
            
            # Restore ID and components
            if entity_data.get('id'):
                entity.id = entity_data['id']
            
            if entity_data.get('components'):
                entity.components = entity_data['components']
            
            entities.append(entity)
        
        self.game_manager.entities = entities
        self.game_manager._assign_behaviors_to_entities()
    
    def log_event(self, event_type, event_data):
        """Log a game event"""
        if not self.session_id:
            return
        
        event = GameEvent(
            session_id=self.session_id,
            event_type=event_type,
            event_data=json.dumps(event_data)
        )
        
        self.db_session.add(event)
        self.db_session.commit()
    
    def get_session_history(self, session_id):
        """Get history of a game session"""
        events = self.db_session.query(GameEvent).filter_by(session_id=session_id).order_by(GameEvent.timestamp).all()
        
        return [{
            'event_type': event.event_type,
            'event_data': json.loads(event.event_data),
            'timestamp': event.timestamp.isoformat()
        } for event in events]
    
    def get_entity_timeline(self, session_id, entity_id):
        """Get timeline of an entity's states"""
        snapshots = self.db_session.query(EntitySnapshot).filter_by(
            session_id=session_id,
            entity_id=entity_id
        ).order_by(EntitySnapshot.timestamp).all()
        
        return [{
            'position': [snapshot.position_x, snapshot.position_y],
            'properties': json.loads(snapshot.properties),
            'components': json.loads(snapshot.components),
            'timestamp': snapshot.timestamp.isoformat()
        } for snapshot in snapshots]

# Usage example
db_manager = DatabaseGameManager()

# Create session
session_id = db_manager.create_session("frontier", seed=42)

# Start game and save snapshots periodically
db_manager.game_manager.start_game_loop()

# Save snapshot every 5 seconds
import time
import threading

def snapshot_thread():
    while True:
        time.sleep(5)
        db_manager.save_snapshot()
        db_manager.log_event('snapshot_saved', {'tick': db_manager.game_manager.game_loop.state.tick})

snapshot_thread = threading.Thread(target=snapshot_thread, daemon=True)
snapshot_thread.start()
```

## Network Integration

### WebSocket Communication

Real-time communication with clients:

```python
import asyncio
import websockets
import json
import threading
from game_manager import GameManager

class NetworkGameManager:
    def __init__(self):
        self.game_manager = GameManager()
        self.connected_clients = set()
        self.game_thread = None
        self.is_running = False
    
    async def register_client(self, websocket):
        """Register a new client"""
        self.connected_clients.add(websocket)
        
        # Send initial game state
        await self.send_to_client(websocket, {
            'type': 'game_state',
            'data': self.get_game_state()
        })
        
        print(f"Client connected. Total clients: {len(self.connected_clients)}")
    
    async def unregister_client(self, websocket):
        """Unregister a client"""
        self.connected_clients.discard(websocket)
        print(f"Client disconnected. Total clients: {len(self.connected_clients)}")
    
    async def send_to_client(self, websocket, message):
        """Send message to a specific client"""
        try:
            await websocket.send(json.dumps(message))
        except websockets.exceptions.ConnectionClosed:
            self.connected_clients.discard(websocket)
    
    async def broadcast_to_clients(self, message):
        """Broadcast message to all clients"""
        if self.connected_clients:
            await asyncio.gather(
                *[self.send_to_client(client, message) for client in self.connected_clients],
                return_exceptions=True
            )
    
    async def handle_client_message(self, websocket, message):
        """Handle message from client"""
        try:
            data = json.loads(message)
            message_type = data.get('type')
            
            if message_type == 'start_game':
                await self.start_game(data.get('template', 'basic'), data.get('seed'))
            elif message_type == 'pause_game':
                self.game_manager.pause_game()
            elif message_type == 'resume_game':
                self.game_manager.resume_game()
            elif message_type == 'set_speed':
                self.game_manager.set_game_speed(data.get('speed', 1.0))
            elif message_type == 'get_entity_info':
                entity_info = self.game_manager.get_entity_info(data.get('entity_id'))
                await self.send_to_client(websocket, {
                    'type': 'entity_info',
                    'data': entity_info
                })
            
        except json.JSONDecodeError:
            await self.send_to_client(websocket, {
                'type': 'error',
                'message': 'Invalid JSON'
            })
    
    async def start_game(self, template="basic", seed=None):
        """Start the game"""
        if not self.is_running:
            self.game_manager.generate_map(template, seed)
            self.game_manager.start_game_loop()
            self.is_running = True
            
            # Start update broadcast thread
            self.game_thread = threading.Thread(target=self.game_update_loop, daemon=True)
            self.game_thread.start()
            
            await self.broadcast_to_clients({
                'type': 'game_started',
                'data': {'template': template, 'seed': seed}
            })
    
    def game_update_loop(self):
        """Send periodic updates to clients"""
        import time
        while self.is_running:
            if self.connected_clients:
                game_state = self.get_game_state()
                
                # Use asyncio to send updates
                asyncio.run_coroutine_threadsafe(
                    self.broadcast_to_clients({
                        'type': 'game_update',
                        'data': game_state
                    }),
                    asyncio.get_event_loop()
                )
            
            time.sleep(0.1)  # 10 updates per second
    
    def get_game_state(self):
        """Get current game state"""
        entities_data = []
        for entity in self.game_manager.entities:
            if hasattr(entity, 'id'):
                entities_data.append({
                    'id': entity.id,
                    'type': entity.type,
                    'position': entity.position,
                    'properties': entity.properties
                })
        
        return {
            'entities': entities_data,
            'statistics': self.game_manager.game_loop.get_stats(),
            'timestamp': time.time()
        }

# WebSocket server
network_manager = NetworkGameManager()

async def handle_client(websocket, path):
    """Handle WebSocket client connection"""
    await network_manager.register_client(websocket)
    
    try:
        async for message in websocket:
            await network_manager.handle_client_message(websocket, message)
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        await network_manager.unregister_client(websocket)

# Start WebSocket server
async def start_server():
    print("Starting WebSocket server on ws://localhost:8765")
    server = await websockets.serve(handle_client, "localhost", 8765)
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(start_server())
```

### Client Example

JavaScript client for WebSocket communication:

```javascript
class SolarFactionsClient {
    constructor(serverUrl = 'ws://localhost:8765') {
        this.serverUrl = serverUrl;
        this.websocket = null;
        this.gameState = null;
        this.callbacks = {};
    }
    
    connect() {
        this.websocket = new WebSocket(this.serverUrl);
        
        this.websocket.onopen = (event) => {
            console.log('Connected to Solar Factions server');
            this.trigger('connected', event);
        };
        
        this.websocket.onmessage = (event) => {
            const message = JSON.parse(event.data);
            this.handleMessage(message);
        };
        
        this.websocket.onclose = (event) => {
            console.log('Disconnected from server');
            this.trigger('disconnected', event);
        };
        
        this.websocket.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.trigger('error', error);
        };
    }
    
    handleMessage(message) {
        switch (message.type) {
            case 'game_state':
            case 'game_update':
                this.gameState = message.data;
                this.trigger('gameUpdate', this.gameState);
                break;
            case 'game_started':
                this.trigger('gameStarted', message.data);
                break;
            case 'entity_info':
                this.trigger('entityInfo', message.data);
                break;
            case 'error':
                this.trigger('error', message.message);
                break;
        }
    }
    
    send(messageType, data = {}) {
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            this.websocket.send(JSON.stringify({
                type: messageType,
                ...data
            }));
        }
    }
    
    startGame(template = 'basic', seed = null) {
        this.send('start_game', { template, seed });
    }
    
    pauseGame() {
        this.send('pause_game');
    }
    
    resumeGame() {
        this.send('resume_game');
    }
    
    setSpeed(speed) {
        this.send('set_speed', { speed });
    }
    
    getEntityInfo(entityId) {
        this.send('get_entity_info', { entity_id: entityId });
    }
    
    on(event, callback) {
        if (!this.callbacks[event]) {
            this.callbacks[event] = [];
        }
        this.callbacks[event].push(callback);
    }
    
    trigger(event, data) {
        if (this.callbacks[event]) {
            this.callbacks[event].forEach(callback => callback(data));
        }
    }
}

// Usage example
const client = new SolarFactionsClient();

client.on('connected', () => {
    console.log('Connected to server');
    client.startGame('frontier', 42);
});

client.on('gameUpdate', (gameState) => {
    console.log(`Game update: ${gameState.entities.length} entities`);
    // Update UI with game state
});

client.on('gameStarted', (data) => {
    console.log(`Game started with template: ${data.template}`);
});

client.connect();
```

## Plugin System

Create an extensible plugin system:

```python
import importlib
import inspect
from abc import ABC, abstractmethod

class Plugin(ABC):
    """Base class for all plugins"""
    
    @abstractmethod
    def get_name(self):
        """Return plugin name"""
        pass
    
    @abstractmethod
    def get_version(self):
        """Return plugin version"""
        pass
    
    @abstractmethod
    def initialize(self, game_manager):
        """Initialize plugin with game manager"""
        pass
    
    @abstractmethod
    def shutdown(self):
        """Shutdown plugin"""
        pass

class PluginManager:
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.plugins = {}
        self.plugin_directory = "plugins"
    
    def load_plugin(self, plugin_path):
        """Load a plugin from a Python file"""
        try:
            spec = importlib.util.spec_from_file_location("plugin", plugin_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find plugin class
            plugin_class = None
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and issubclass(obj, Plugin) and obj != Plugin:
                    plugin_class = obj
                    break
            
            if plugin_class:
                plugin_instance = plugin_class()
                plugin_instance.initialize(self.game_manager)
                
                plugin_name = plugin_instance.get_name()
                self.plugins[plugin_name] = plugin_instance
                
                print(f"Loaded plugin: {plugin_name} v{plugin_instance.get_version()}")
                return True
            else:
                print(f"No plugin class found in {plugin_path}")
                return False
                
        except Exception as e:
            print(f"Error loading plugin {plugin_path}: {e}")
            return False
    
    def unload_plugin(self, plugin_name):
        """Unload a plugin"""
        if plugin_name in self.plugins:
            try:
                self.plugins[plugin_name].shutdown()
                del self.plugins[plugin_name]
                print(f"Unloaded plugin: {plugin_name}")
                return True
            except Exception as e:
                print(f"Error unloading plugin {plugin_name}: {e}")
                return False
        return False
    
    def get_plugin(self, plugin_name):
        """Get a loaded plugin"""
        return self.plugins.get(plugin_name)
    
    def list_plugins(self):
        """List all loaded plugins"""
        return list(self.plugins.keys())
    
    def shutdown_all(self):
        """Shutdown all plugins"""
        for plugin_name in list(self.plugins.keys()):
            self.unload_plugin(plugin_name)

# Example plugin: Statistics Logger
class StatisticsLoggerPlugin(Plugin):
    def __init__(self):
        self.game_manager = None
        self.log_file = None
        self.update_interval = 1.0
        self.last_update = 0
    
    def get_name(self):
        return "Statistics Logger"
    
    def get_version(self):
        return "1.0.0"
    
    def initialize(self, game_manager):
        self.game_manager = game_manager
        self.log_file = open("game_statistics.log", "w")
        
        # Add update system
        game_manager.game_loop.add_update_system(self.update_statistics)
        
        print("Statistics Logger initialized")
    
    def shutdown(self):
        if self.log_file:
            self.log_file.close()
        print("Statistics Logger shutdown")
    
    def update_statistics(self, dt):
        self.last_update += dt
        
        if self.last_update >= self.update_interval:
            stats = self.game_manager.game_loop.get_stats()
            
            log_line = f"Tick: {stats['tick']}, TPS: {stats['actual_tps']:.1f}, Entities: {len(self.game_manager.entities)}\n"
            self.log_file.write(log_line)
            self.log_file.flush()
            
            self.last_update = 0

# Usage
plugin_manager = PluginManager(game_manager)

# Load plugins
plugin_manager.load_plugin("plugins/statistics_logger.py")

# Use plugin system
print("Loaded plugins:", plugin_manager.list_plugins())

# Shutdown
plugin_manager.shutdown_all()
```

## Testing Integration

### Automated Testing Framework

Create automated tests for integrations:

```python
import unittest
import tempfile
import os
import json
import time
from game_manager import GameManager

class IntegrationTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)
        
        # Create test data directory
        os.makedirs("data/behaviors", exist_ok=True)
        os.makedirs("data/components", exist_ok=True)
        os.makedirs("data/templates", exist_ok=True)
        
        self.game_manager = GameManager()
    
    def tearDown(self):
        """Clean up test environment"""
        self.game_manager.stop_game_loop()
        os.chdir(self.original_dir)
        # Clean up temp directory
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_web_integration(self):
        """Test web integration"""
        from integration_examples import WebGameManager
        
        web_game = WebGameManager()
        web_game.start_web_game("basic", seed=42)
        
        # Test game state retrieval
        game_state = web_game.get_game_state()
        self.assertIn('entities', game_state)
        self.assertIn('statistics', game_state)
        self.assertGreater(len(game_state['entities']), 0)
    
    def test_database_integration(self):
        """Test database integration"""
        from integration_examples import DatabaseGameManager
        
        db_manager = DatabaseGameManager("sqlite:///test.db")
        session_id = db_manager.create_session("basic", seed=42)
        
        # Test session creation
        self.assertIsNotNone(session_id)
        
        # Test snapshot saving
        db_manager.save_snapshot()
        
        # Test session loading
        db_manager2 = DatabaseGameManager("sqlite:///test.db")
        self.assertTrue(db_manager2.load_session(session_id))
    
    def test_network_integration(self):
        """Test network integration"""
        import asyncio
        from integration_examples import NetworkGameManager
        
        async def test_network():
            network_manager = NetworkGameManager()
            await network_manager.start_game("basic", seed=42)
            
            # Test game state
            game_state = network_manager.get_game_state()
            self.assertIn('entities', game_state)
            self.assertGreater(len(game_state['entities']), 0)
        
        # Run async test
        asyncio.run(test_network())
    
    def test_plugin_system(self):
        """Test plugin system"""
        from integration_examples import PluginManager, StatisticsLoggerPlugin
        
        plugin_manager = PluginManager(self.game_manager)
        
        # Create test plugin
        plugin = StatisticsLoggerPlugin()
        plugin.initialize(self.game_manager)
        
        # Test plugin functionality
        self.assertEqual(plugin.get_name(), "Statistics Logger")
        self.assertEqual(plugin.get_version(), "1.0.0")
        
        # Test shutdown
        plugin.shutdown()

class PerformanceTestCase(unittest.TestCase):
    def test_web_performance(self):
        """Test web integration performance"""
        from integration_examples import WebGameManager
        
        web_game = WebGameManager()
        web_game.start_web_game("warzone", seed=42)
        
        # Measure game state retrieval time
        start_time = time.time()
        for _ in range(100):
            game_state = web_game.get_game_state()
        end_time = time.time()
        
        avg_time = (end_time - start_time) / 100
        self.assertLess(avg_time, 0.01)  # Should be under 10ms
    
    def test_database_performance(self):
        """Test database integration performance"""
        from integration_examples import DatabaseGameManager
        
        db_manager = DatabaseGameManager("sqlite:///perf_test.db")
        session_id = db_manager.create_session("warzone", seed=42)
        
        # Measure snapshot saving time
        start_time = time.time()
        for _ in range(10):
            db_manager.save_snapshot()
        end_time = time.time()
        
        avg_time = (end_time - start_time) / 10
        self.assertLess(avg_time, 0.1)  # Should be under 100ms

if __name__ == '__main__':
    unittest.main()
```

This integration guide provides comprehensive examples for extending Solar Factions with external systems. The patterns shown can be adapted for various integration scenarios while maintaining system performance and reliability.