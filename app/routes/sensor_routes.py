from flask import Blueprint, request, jsonify, render_template
from ..services.sensor_service import add_sensor_records, get_sensor_data, reset_sensor_data, emit_sensor_data

sensor_routes = Blueprint('sensor_routes', __name__)

@sensor_routes.route('/<sensor_type>', methods=['GET'])
def monitoring_page(sensor_type):
    templates = {
        'pressure': 'pressure.html',
        'temperature': 'temperature.html',
        'humidity': 'humidity.html'
    }
    return render_template(templates.get(sensor_type, 'index.html'))

@sensor_routes.route('/api/sensor_data', methods=['POST'])
def receive_sensor_data():
    data = request.json
    if not data:
        return jsonify({'status': 'No data received'}), 400
    try:
        add_sensor_records(data)
        emit_sensor_data()
        return jsonify({'status': 'Data received and processed successfully'}), 200
    except Exception as e:
        return jsonify({'status': 'Failed to add data', 'error': str(e)}), 500

@sensor_routes.route('/api/<sensor_type>_data', methods=['GET'])
def get_sensor_data_api(sensor_type):
    return get_sensor_data(sensor_type)

@sensor_routes.route('/reset', methods=['POST'])
def reset_data():
    return reset_sensor_data()
