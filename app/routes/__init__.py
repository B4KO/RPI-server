from flask import Blueprint
from app.extensions import socketio  # Import socketio from extensions

# Initialize the main Blueprint
routes = Blueprint('routes', __name__)

# Import individual route blueprints and register them
from .home_routes import home_routes
from .weather_routes import weather_routes
from .calendar_routes import calendar_routes
from .sensor_routes import sensor_routes
from .alarm_routes import alarm_routes

# Register blueprints for each route
routes.register_blueprint(home_routes)
routes.register_blueprint(weather_routes)
routes.register_blueprint(calendar_routes)
routes.register_blueprint(sensor_routes)
routes.register_blueprint(alarm_routes)
