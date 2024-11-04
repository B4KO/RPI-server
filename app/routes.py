# app/routes.py
from flask import Blueprint, request, render_template, jsonify
from .models import db, Humidity, Temperature, Pressure
from sqlalchemy import func
from flask_socketio import SocketIO
from datetime import datetime, date

socketio = SocketIO()
routes = Blueprint('routes', __name__)

@routes.route('/', methods=['GET'])
def home():
    return render_template('index.html')

# Monitoring pages route
@routes.route('/<sensor_type>', methods=['GET'])
def monitoring_page(sensor_type):
    templates = {
        'pressure': 'pressure.html',
        'temperature': 'temperature.html',
        'humidity': 'humidity.html'
    }
    return render_template(templates.get(sensor_type, 'index.html'))

# API route to receive sensor data
@routes.route('/api/sensor_data', methods=['POST'])
def receive_sensor_data():
    data = request.json
    if not data:
        return jsonify({'status': 'No data received'}), 400

    try:
        add_sensor_records(data)
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'Failed to add data', 'error': str(e)}), 500

    # Emit the latest sensor data to the client
    emit_sensor_data()
    return jsonify({'status': 'Data received and processed successfully'}), 200

# API route to retrieve data for a specific sensor type
@routes.route('/api/<sensor_type>_data', methods=['GET'])
def get_sensor_data_api(sensor_type):
    models = {'pressure': Pressure, 'temperature': Temperature, 'humidity': Humidity}
    ranges = {'pressure': (900, 1100), 'temperature': (15, 25), 'humidity': (30, 60)}

    model = models.get(sensor_type)
    current_range = ranges.get(sensor_type)

    if model and current_range:
        data = get_sensor_data(model, sensor_type, current_range)
        return jsonify({sensor_type: data})

    return jsonify({'status': 'Invalid sensor type'}), 400

# API route to reset data
@routes.route('/reset', methods=['POST'])
def reset_data():
    try:
        rows_deleted = db.session.query(Temperature).delete() + \
                       db.session.query(Humidity).delete() + \
                       db.session.query(Pressure).delete()
        db.session.commit()
        socketio.emit('dataReset', {'status': 'Data has been reset'})
        return jsonify({'status': f'{rows_deleted} rows deleted'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'Failed to reset data', 'error': str(e)}), 500

# Helper function to add sensor records
def add_sensor_records(data, timestamp=datetime.utcnow().isoformat()):
    records = [
        Humidity(humidity=data.get('humidity'), timestamp=timestamp),
        Temperature(temperature=data.get('temperature'), timestamp=timestamp),
        Pressure(pressure=data.get('pressure'), timestamp=timestamp)
    ]
    db.session.add_all(records)
    db.session.commit()

# Helper function to get sensor data
def get_sensor_data(model, attribute, current_range, today=date.today().isoformat()):
    current_record = db.session.query(getattr(model, attribute)).order_by(model.id.desc()).first()
    current_value = parse_value(current_record)

    min_value = db.session.query(func.min(getattr(model, attribute))).filter(func.date(model.timestamp) == today).scalar()
    max_value = db.session.query(func.max(getattr(model, attribute))).filter(func.date(model.timestamp) == today).scalar()

    status = 'No Data Available' if current_value is None else 'Normal' if current_range[0] <= current_value <= current_range[1] else 'Abnormal'

    history_records = model.query.order_by(model.id.desc()).limit(10).all()
    history = [record_to_dict(record, attribute) for record in history_records]

    return {
        'current': current_value,
        'min': min_value,
        'max': max_value,
        'status': status,
        'history': history
    }

# Helper function to parse a value from a record
def parse_value(record):
    if record and record[0] is not None:
        try:
            return float(record[0])
        except ValueError:
            return None
    return None

# Helper function to convert a record to a dictionary
def record_to_dict(record, attribute):
    timestamp = record.timestamp.isoformat() if hasattr(record.timestamp, 'isoformat') else record.timestamp
    return {
        'id': record.id,
        'timestamp': timestamp,
        attribute: getattr(record, attribute)
    }

# Helper function to emit the latest sensor data to clients
def emit_sensor_data():
    pressure_data = get_sensor_data(Pressure, "pressure", current_range=(900, 1100))
    temperature_data = get_sensor_data(Temperature, "temperature", current_range=(15, 25))
    humidity_data = get_sensor_data(Humidity, "humidity", current_range=(30, 60))

    socketio.emit('sensor_update', {
        'pressure': pressure_data,
        'temperature': temperature_data,
        'humidity': humidity_data,
    })
