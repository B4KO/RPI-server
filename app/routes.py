from flask import Blueprint
from flask_socketio import SocketIO

# Initialize SocketIO and the main Blueprint
socketio = SocketIO()
routes = Blueprint('routes', __name__)

# Import individual route blueprints and register them
from .routes.home_routes import home_routes
from .routes.weather_routes import weather_routes
from .routes.calendar_routes import calendar_routes
from .routes.sensor_routes import sensor_routes
from .routes.alarm_routes import alarm_routes
from .routes.error_routes import error_routes


# Register blueprints for each route
routes.register_blueprint(home_routes)
routes.register_blueprint(weather_routes)
routes.register_blueprint(calendar_routes)
routes.register_blueprint(sensor_routes)
routes.register_blueprint(alarm_routes)
