from flask_socketio import emit
from ..models import db, Humidity, Temperature, Pressure
from sqlalchemy import func
from datetime import datetime, date

def add_sensor_records(data):
    """
    Adds sensor data records for humidity, temperature, and pressure to the database.
    """
    timestamp = datetime.utcnow()
    records = [
        Humidity(humidity=data.get('humidity'), timestamp=timestamp),
        Temperature(temperature=data.get('temperature'), timestamp=timestamp),
        Pressure(pressure=data.get('pressure'), timestamp=timestamp)
    ]
    db.session.add_all(records)
    db.session.commit()

def get_sensor_data(sensor_type):
    """
    Retrieves the current, min, max, and historical data for the specified sensor type.
    """
    model_map = {'pressure': Pressure, 'temperature': Temperature, 'humidity': Humidity}
    ranges = {'pressure': (900, 1100), 'temperature': (15, 25), 'humidity': (30, 60)}
    
    model = model_map.get(sensor_type)
    current_range = ranges.get(sensor_type)

    if not model or not current_range:
        return {'status': 'Invalid sensor type'}

    # Get current value
    current_record = db.session.query(model).order_by(model.id.desc()).first()
    current_value = current_record.pressure if sensor_type == 'pressure' else \
                    current_record.temperature if sensor_type == 'temperature' else \
                    current_record.humidity

    # Get min and max values for today
    today = date.today()
    min_value = db.session.query(func.min(getattr(model, sensor_type))).filter(func.date(model.timestamp) == today).scalar()
    max_value = db.session.query(func.max(getattr(model, sensor_type))).filter(func.date(model.timestamp) == today).scalar()

    # Determine the status based on current value
    status = 'Normal' if current_value and current_range[0] <= current_value <= current_range[1] else 'Abnormal'

    # Get recent history (last 10 records)
    history_records = model.query.order_by(model.id.desc()).limit(10).all()
    history = [{"id": record.id, "timestamp": record.timestamp.isoformat(), sensor_type: getattr(record, sensor_type)} for record in history_records]

    return {
        'current': current_value,
        'min': min_value,
        'max': max_value,
        'status': status,
        'history': history
    }

def reset_sensor_data():
    """
    Deletes all records from the humidity, temperature, and pressure tables and emits a reset event.
    """
    try:
        rows_deleted = db.session.query(Temperature).delete() + \
                       db.session.query(Humidity).delete() + \
                       db.session.query(Pressure).delete()
        db.session.commit()
        emit('dataReset', {'status': 'Data has been reset'})
        return {'status': f'{rows_deleted} rows deleted'}
    except Exception as e:
        db.session.rollback()
        return {'status': 'Failed to reset data', 'error': str(e)}

def emit_sensor_data():
    """
    Emits the latest sensor data for pressure, temperature, and humidity to all connected clients.
    """
    pressure_data = get_sensor_data('pressure')
    temperature_data = get_sensor_data('temperature')
    humidity_data = get_sensor_data('humidity')

    emit('sensor_update', {
        'pressure': pressure_data,
        'temperature': temperature_data,
        'humidity': humidity_data,
    }, broadcast=True)
