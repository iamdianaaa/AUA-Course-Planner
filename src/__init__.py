from flask import Flask

def create_app():
    app = Flask(__name__)

    from src.controllers.planner import planner_bp
    app.register_blueprint(planner_bp, url_prefix='/api')

    return app
