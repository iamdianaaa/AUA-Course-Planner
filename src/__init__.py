from flask import Flask
from flask_cors import CORS


def create_app():
    app = Flask(__name__)

    CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

    from src.controllers.planner import planner_bp

    app.register_blueprint(planner_bp, url_prefix="/api")

    return app
