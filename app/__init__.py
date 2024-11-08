from flask import Flask
from .extensions import socketio  # Import socketio from extensions
from .routes import routes

def create_app():
    app = Flask(__name__)
    app.register_blueprint(routes)
    socketio.init_app(app)  # Initialize socketio with the app
    return app
