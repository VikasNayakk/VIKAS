"""
Web-based GUI Dashboard for AI-Agent-OS
Access at: http://localhost:5000
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import logging
from datetime import datetime
import threading

logger = logging.getLogger(__name__)


class DashboardServer:
    """Web dashboard for AI-Agent-OS"""
    
    def __init__(self, ai_system=None, command_queue=None):
        import os
        
        # Get absolute paths
        ui_dir = os.path.dirname(os.path.abspath(__file__))
        template_dir = os.path.join(ui_dir, 'templates')
        static_dir = os.path.join(ui_dir, 'static')
        
        self.app = Flask(__name__, 
                        template_folder=template_dir,
                        static_folder=static_dir)
        CORS(self.app)
        self.ai_system = ai_system
        self.command_history = []
        self.command_queue = command_queue  # Use provided queue
        
        # Setup error handlers
        @self.app.errorhandler(404)
        def not_found(e):
            return jsonify({"error": "Not found"}), 404
        
        @self.app.errorhandler(500)
        def internal_error(e):
            logger.error(f"Internal error: {e}")
            return jsonify({"error": "Internal server error", "details": str(e)}), 500
        
        # Setup routes
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup API routes"""
        
        @self.app.route('/')
        def index():
            try:
                return render_template('dashboard.html')
            except Exception as e:
                logger.error(f"Template error: {e}")
                # Fallback HTML
                return """
                <html>
                <head><title>AI-Agent-OS</title></head>
                <body style="background:#0a0e27; color:#e0e6ff; font-family:Arial; padding:20px">
                    <h1>🤖 AI-Agent-OS Dashboard</h1>
                    <p>Status: System Online ✅</p>
                    <details>
                        <summary>Error Details</summary>
                        <p style="color:red">Template loading error: {}</p>
                        <p>Make sure ui/templates/dashboard.html exists</p>
                    </details>
                </body>
                </html>
                """.format(str(e))
        
        @self.app.route('/api/test')
        def api_test():
            """Test endpoint"""
            return jsonify({"status": "ok", "message": "API working!"})
        
        @self.app.route('/api/status')
        def api_status():
            """Get system status"""
            try:
                if not self.ai_system:
                    return jsonify({"error": "System not initialized"}), 503
                
                return jsonify({
                    "status": "online",
                    "kernel": {
                        "running": self.ai_system.kernel._running,
                        "version": "1.0.0"
                    },
                    "agents": {
                        "total": 4,
                        "active": [
                            {"name": "Coordinator", "status": "active"},
                            {"name": "Executor", "status": "active"},
                            {"name": "Planner", "status": "active"},
                            {"name": "Monitor", "status": "active"}
                        ]
                    },
                    "metrics": {
                        "cpu_percent": 0,
                        "memory_percent": 0
                    }
                })
            except Exception as e:
                logger.error(f"Status error: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/command', methods=['POST'])
        def api_command():
            """Execute command"""
            try:
                if not self.ai_system:
                    return jsonify({"error": "System not initialized"}), 503
                
                data = request.json
                command = data.get('command', '').strip()
                
                if not command:
                    return jsonify({"error": "Empty command"}), 400
                
                # Store in history
                self.command_history.append({
                    "command": command,
                    "timestamp": datetime.now().isoformat(),
                    "status": "processing"
                })
                
                # Queue command for processing by main event loop
                if self.command_queue:
                    self.command_queue.put(command)
                
                return jsonify({
                    "success": True,
                    "command": command,
                    "message": "Command queued"
                })
            
            except Exception as e:
                logger.error(f"Error executing command: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/history')
        def api_history():
            """Get command history"""
            try:
                return jsonify({
                    "history": self.command_history[-20:]  # Last 20 commands
                })
            except Exception as e:
                logger.error(f"History error: {e}")
                return jsonify({"history": []}), 200
        
        @self.app.route('/api/metrics')
        def api_metrics():
            """Get system metrics"""
            try:
                import psutil
                return jsonify({
                    "cpu_percent": psutil.cpu_percent(interval=1),
                    "memory_percent": psutil.virtual_memory().percent,
                    "disk_usage": psutil.disk_usage('/').percent,
                    "uptime": 0  # TODO: implement uptime tracking
                })
            except Exception as e:
                logger.error(f"Metrics error: {e}")
                return jsonify({
                    "cpu_percent": 0,
                    "memory_percent": 0,
                    "disk_usage": 0,
                    "uptime": 0
                }), 200
        
        @self.app.route('/api/help')
        def api_help():
            """Get help information"""
            try:
                return jsonify({
                    "commands": {
                        "messaging": [
                            {"command": "send hello to [name]", "description": "Send message"},
                            {"command": "message [name] [text]", "description": "Message someone"},
                            {"command": "teams [message] to [name]", "description": "Send Teams DM"}
                        ],
                        "apps": [
                            {"command": "open [app]", "description": "Open application"},
                            {"command": "close [app]", "description": "Close application"}
                        ],
                        "ui": [
                            {"command": "type [text]", "description": "Type text"},
                            {"command": "click [x,y]", "description": "Click position"},
                            {"command": "take screenshot", "description": "Capture screen"}
                        ],
                        "system": [
                            {"command": "status", "description": "Show system status"},
                            {"command": "help", "description": "Show this help"},
                            {"command": "exit", "description": "Stop system"}
                        ]
                    }
                })
            except Exception as e:
                logger.error(f"Help error: {e}")
                return jsonify({"error": str(e)}), 500
    
    def run(self, host='localhost', port=5000, debug=False):
        """Run dashboard server"""
        # Suppress Flask logging
        import logging as builtin_logging
        log = builtin_logging.getLogger('werkzeug')
        log.setLevel(builtin_logging.ERROR)
        
        logger.info(f"Dashboard running at http://{host}:{port}")
        self.app.run(host=host, port=port, debug=debug, use_reloader=False)
