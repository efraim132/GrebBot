from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_socketio import SocketIO, emit
import asyncio
import threading
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here')
socketio = SocketIO(app, cors_allowed_origins="*")

# Global variable to store bot instance
bot_instance = None

class BotWebInterface:
    def __init__(self, bot):
        global bot_instance
        bot_instance = bot
        self.bot = bot
        self.logs = []

    def add_log(self, message, level="INFO"):
        """Add a log entry"""
        log_entry = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'level': level,
            'message': message
        }
        self.logs.append(log_entry)
        if len(self.logs) > 100:  # Keep only last 100 logs
            self.logs.pop(0)

        # Emit to connected clients
        socketio.emit('new_log', log_entry)

# Initialize web interface instance
web_interface = None

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/bot/status')
def bot_status():
    """Get bot status information"""
    if not bot_instance:
        return jsonify({'status': 'offline', 'error': 'Bot not initialized'})

    try:
        guilds = bot_instance.guilds
        total_members = sum(guild.member_count for guild in guilds)

        return jsonify({
            'status': 'online' if bot_instance.is_ready() else 'offline',
            'username': str(bot_instance.user) if bot_instance.user else 'Unknown',
            'user_id': bot_instance.user.id if bot_instance.user else None,
            'guild_count': len(guilds),
            'total_members': total_members,
            'latency': round(bot_instance.latency * 1000, 2),
            'guilds': [{'name': guild.name, 'member_count': guild.member_count, 'id': guild.id} for guild in guilds]
        })
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)})

@app.route('/api/bot/commands')
def bot_commands():
    """Get list of bot commands"""
    if not bot_instance:
        return jsonify({'error': 'Bot not initialized'})

    commands = []
    for command in bot_instance.commands:
        commands.append({
            'name': command.name,
            'description': command.help or 'No description available',
            'cog': command.cog.qualified_name if command.cog else 'No Cog'
        })

    return jsonify({'commands': commands})

@app.route('/api/logs')
def get_logs():
    """Get bot logs"""
    if web_interface:
        return jsonify({'logs': web_interface.logs})
    return jsonify({'logs': []})

@app.route('/guilds')
def guilds():
    """Guild management page"""
    return render_template('guilds.html')

@app.route('/commands')
def commands():
    """Commands overview page"""
    return render_template('commands.html')

@app.route('/logs')
def logs():
    """Logs page"""
    return render_template('logs.html')

@app.route('/settings')
def settings():
    """Settings page"""
    return render_template('settings.html')

@app.route('/api/settings')
def get_settings():
    """Get current settings"""
    return jsonify({
        'debug_mode': os.getenv('DEBUG_MODE', 'False').lower() in ['true', '1', 'yes'],
        'bot_status': os.getenv('bot_status', 'playing with <code>'),
        'version': os.getenv('VERSION', 'Unknown')
    })

@app.route('/api/settings', methods=['POST'])
def update_settings():
    """Update settings"""
    data = request.get_json()

    # This is a basic implementation - in production you'd want to update the .env file
    # and possibly restart the bot with new settings

    return jsonify({'success': True, 'message': 'Settings updated (restart required)'})

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    emit('connected', {'data': 'Connected to GrebBot Web Interface'})

def run_web_interface(host='127.0.0.1', port=5000, debug=False):
    """Run the Flask web interface"""
    print(f"🌐 Starting web interface at http://{host}:{port}")
    socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)

if __name__ == '__main__':
    run_web_interface(debug=True)
