import logging
from pythonjsonlogger import jsonlogger
import psutil
import json
import os
import uuid

from dotenv import load_dotenv
from flask import Flask, jsonify, request, g, has_request_context

from app.database import init_db
from app.routes import register_routes

class ContextFilter(logging.Filter):
    def filter(self, record):
        # Safely tag EVERY log with the current request trace if inside a request loop
        if has_request_context():
            record.correlation_id = getattr(g, 'request_id', 'system_event')
        else:
            record.correlation_id = 'system_boot'
            
        record.replica_id = os.environ.get("HOSTNAME", "standalone")
        return True


def create_app(test_config=None):
    load_dotenv()

    app = Flask(__name__)
    
    if test_config:
        app.config.update(test_config)

    init_db(app)

    # Ensure unified log directory exists natively to share across Web 1 and Web 2
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Safely configure JSON Structured Telemetry 
    log_handler = logging.FileHandler('logs/app.jsonl')
    formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(replica_id)s %(correlation_id)s %(name)s %(message)s')
    log_handler.setFormatter(formatter)
    
    # Attach our context filter mapping the UUIDs
    log_handler.addFilter(ContextFilter())
    
    app.logger.addHandler(log_handler)
    app.logger.setLevel(logging.INFO)
    
    app.logger.info("Watchtower Framework Initialized", extra={"component": "system"})

    from app import models  # noqa: F401 - registers models with Peewee

    register_routes(app)
    
    @app.before_request
    def attach_correlation_id():
        # Assign incoming header or generate brand new UUID natively securely
        g.request_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))

    @app.route("/health")
    def health():
        return jsonify(status="ok")

    @app.route("/metrics")
    def metrics():
        return jsonify({
            "replica_id": os.environ.get("HOSTNAME", "standalone"),
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "ram_percent": psutil.virtual_memory().percent,
            "ram_used_mb": round(psutil.virtual_memory().used / (1024 * 1024), 2)
        })

    @app.route("/logs")
    def view_logs():
        try:
            with open("logs/app.jsonl", "r") as f:
                lines = f.readlines()[-100:]
            return jsonify([json.loads(l) for l in lines if l.strip()])
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.errorhandler(404)
    def resource_not_found(e):
        return jsonify(error="Resource not found", details=str(e)), 404

    @app.errorhandler(Exception)
    def internal_server_error(e):
        return jsonify(error="Internal server error", details=str(e)), 500

    return app
