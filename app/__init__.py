# app/helpers.py
from flask import Flask
from .config import Config
from .models import db
from .routes import routes, socketio
from .errors import errors

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*", async_mode="threading")

    app.register_blueprint(routes)
    app.register_blueprint(errors)

    return app, socketio
