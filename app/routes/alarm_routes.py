from flask import Blueprint, render_template
from app.extensions import socketio  # Import socketio from extensions
from ..services.alarm_service import set_alarm, clear_alarm

alarm_routes = Blueprint('alarm_routes', __name__)

@alarm_routes.route('/alarm', methods=['GET'])
def alarm():
    return render_template('alarm.html')

@socketio.on('set_alarm')
def handle_set_alarm(data):
    set_alarm(data.get("alarm_time"))

@socketio.on('clear_alarm')
def handle_clear_alarm():
    clear_alarm()
