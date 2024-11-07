# app/routes.py
import collections
import threading

from flask import Blueprint, request, render_template, jsonify
from .models import db, Humidity, Temperature, Pressure
from sqlalchemy import func
from flask_socketio import SocketIO
from datetime import datetime, date, time, timedelta, timezone
from ics import Calendar
import time
import requests



#TODO
#Implement alarm
#Implement calendar


socketio = SocketIO()
routes = Blueprint('routes', __name__)


alarm_time = None
WEATHER_API_KEY = 'e2e8c192678f006be42e65394b03204e'
WEATHER_API_URL = 'http://api.openweathermap.org/data/2.5/onecall'


def fetch_weather_data():
    url = "https://api.openweathermap.org/data/3.0/onecall?lat=58.1467&lon=7.9956&exclude=minutely&appid=e2e8c192678f006be42e65394b03204e&units=metric"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Error: Unable to fetch weather data. Status code {response.status_code}")
        return {}, {}

    data = response.json()

    if "current" not in data or "daily" not in data:
        print("Error: Missing expected data keys in the API response.")
        return {}, {}

    # Today's data
    current = data["current"]
    today_data = {
        "today_temp": current.get("temp", "N/A"),
        "today_desc": current.get("weather", [{"description": "N/A"}])[0]["description"].capitalize(),
        "today_icon": f"fas fa-{map_icon(current['weather'][0]['icon'])}" if "weather" in current else "fas fa-cloud",
        "humidity": current.get("humidity", "N/A"),
        "wind_speed": current.get("wind_speed", "N/A"),
        "sunrise": datetime.fromtimestamp(current.get("sunrise", 0)).strftime(
            "%H:%M") if "sunrise" in current else "N/A",
        "sunset": datetime.fromtimestamp(current.get("sunset", 0)).strftime("%H:%M") if "sunset" in current else "N/A",
    }

    # 7-day forecast data
    forecast_data = {}
    for day in data.get("daily", [])[:7]:  # Limit to 7 days
        day_name = datetime.fromtimestamp(day["dt"]).strftime("%a")
        forecast_data[day_name] = {
            "temp": day["temp"].get("day", "N/A"),
            "min_temp": day["temp"].get("min", "N/A"),
            "max_temp": day["temp"].get("max", "N/A"),
            "desc": day["weather"][0]["description"].capitalize() if "weather" in day else "N/A",
            "icon": f"fas fa-{map_icon(day['weather'][0]['icon'])}" if "weather" in day else "fas fa-cloud",
        }

    return today_data, forecast_data


def map_icon(icon_code):
    icon_map = {
        "01d": "sun", "01n": "moon",
        "02d": "cloud-sun", "02n": "cloud-moon",
        "03d": "cloud", "03n": "cloud",
        "04d": "cloud-meatball", "04n": "cloud-meatball",
        "09d": "cloud-showers-heavy", "09n": "cloud-showers-heavy",
        "10d": "cloud-sun-rain", "10n": "cloud-moon-rain",
        "11d": "bolt", "11n": "bolt",
        "13d": "snowflake", "13n": "snowflake",
        "50d": "smog", "50n": "smog",
    }
    return icon_map.get(icon_code, "cloud")

@routes.route('/', methods=['GET'])
def home():
    return render_template('index.html')

# Path to the in-memory .ics file on the server
ICS_FILE_PATH = 'calendar.ics'

# Route to display the calendar events
@routes.route('/calendar')
def daily_calendar():
    # Load the sample .ics file
    with open("calendar.ics", "r") as f:
        calendar = Calendar(f.read())

    # Get today's date in UTC
    today = datetime.now(timezone.utc).date()

    # Filter events to include only today's events
    today_events = []
    for event in calendar.events:
        event_start = event.begin.datetime.date()
        if event_start == today:
            today_events.append(event)

    # Pass today's events to the template
    return render_template("calendar.html", today_events=today_events, current_date=today)





@routes.route('/weather', methods=['GET'])
def weather():
        today_data, forecast_data = fetch_weather_data()
        return render_template('weather.html', **today_data, forecast=forecast_data)


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


@routes.route('/alarm', methods=['GET'])
def alarm():
    return render_template('alarm.html')

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

@socketio.on('set_alarm')
def handle_set_alarm(data):
    global alarm_time
    alarm_time = data.get("alarm_time")
    print(f"Alarm set for {alarm_time}")

    # Start a background thread to monitor the alarm time
    def check_alarm():
        global alarm_time
        while alarm_time:
            now = datetime.now().strftime("%H:%M")
            if now == alarm_time:
                socketio.emit('trigger_alarm', {'message': "Time's up! Your alarm is ringing!"})
                alarm_time = None
                break
            time.sleep(1)

    # Start background thread only if there's no alarm thread already running
    threading.Thread(target=check_alarm).start()

@socketio.on('clear_alarm')
def handle_clear_alarm():
    global alarm_time
    alarm_time = None
    print("Alarm cleared")