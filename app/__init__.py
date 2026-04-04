from dotenv import load_dotenv
from flask import Flask, jsonify

from app.database import init_db
from app.routes import register_routes


def create_app(test_config=None):
    load_dotenv()

    app = Flask(__name__)
    
    if test_config:
        app.config.update(test_config)

    init_db(app)

    from app import models  # noqa: F401 - registers models with Peewee

    register_routes(app)

    @app.route("/health")
    def health():
        return jsonify(status="ok")

    @app.errorhandler(404)
    def resource_not_found(e):
        return jsonify(error="Resource not found", details=str(e)), 404

    @app.errorhandler(Exception)
    def internal_server_error(e):
        return jsonify(error="Internal server error", details=str(e)), 500

    return app
