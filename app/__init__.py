from flask import Flask
from .routes import routes, socketio

def create_app():
    app = Flask(__name__)
    
    # Register the main routes blueprint
    app.register_blueprint(routes)
    
    # Initialize SocketIO with the app
    socketio.init_app(app)
    
    return app
