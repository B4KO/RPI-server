from flask import Flask, request, render_template, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from datetime import datetime
import random

app = Flask(__name__)

# Configuring the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Database model
class Humidity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    humidity = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.String(100), nullable=False)

class Temperature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    temperature = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.String(100), nullable=False)

# Create database tables
with app.app_context():
    db.create_all()
    print("Database tables created successfully.")

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/reset', methods=['POST'])
def reset_data():
    # Delete all data from the database
    try:
        num_rows_deleted_temp = db.session.query(Temperature).delete()
        num_rows_deleted_hum = db.session.query(Humidity).delete()
        db.session.commit()
        socketio.emit('dataReset', {'status': 'Data has been reset'})
        return jsonify({'status': f'{num_rows_deleted_temp + num_rows_deleted_hum} rows deleted'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'Failed to reset data', 'error': str(e)}), 500

@app.route('/receive', methods=['POST'])
def receive():
    new_data = request.json  # Expecting JSON data
    if new_data:
        # Add a timestamp to the data
        timestamp = datetime.utcnow().isoformat()
        humidity_data = Humidity(humidity=new_data['humidity'], timestamp=timestamp)
        temperature_data = Temperature(temperature=str(new_data['temperature']), timestamp=timestamp)
        try:
            db.session.add(temperature_data)
            db.session.add(humidity_data)
            db.session.commit()
            socketio.emit('dataUpdate', {
                'temperature': {'id': temperature_data.id, 'value': temperature_data.temperature, 'timestamp': temperature_data.timestamp},
                'humidity': {'id': humidity_data.id, 'value': humidity_data.humidity, 'timestamp': humidity_data.timestamp}
            })
            return jsonify({'status': 'Data received'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'status': 'Failed to add data', 'error': str(e)}), 500
    else:
        return jsonify({'status': 'No data received'}), 400

@app.route('/data', methods=['GET'])
def get_data():
    try:
        # Query temperature and humidity data from the database
        temperature_all = Temperature.query.all()
        humidity_all = Humidity.query.all()

        # Organize data into the expected structure
        data = {
            'temperature': [{'id': temp.id, 'value': temp.temperature, 'timestamp': temp.timestamp} for temp in temperature_all],
            'humidity': [{'id': hum.id, 'value': hum.humidity, 'timestamp': hum.timestamp} for hum in humidity_all]
        }
        return jsonify(data)
    except Exception as e:
        return jsonify({'status': 'Failed to retrieve data', 'error': str(e)}), 500


@app.route('/generate_random_data', methods=['POST'])
def generate_random_data():
    # Generate random temperature and humidity data
    try:
        timestamp = datetime.utcnow().isoformat()
        temperature_value = round(random.uniform(15.0, 35.0), 2)
        humidity_value = round(random.uniform(30.0, 90.0), 2)
        temperature_data = Temperature(temperature=str(temperature_value), timestamp=timestamp)
        humidity_data = Humidity(humidity=str(humidity_value), timestamp=timestamp)
        db.session.add(temperature_data)
        db.session.add(humidity_data)
        db.session.commit()
        socketio.emit('dataUpdate', {
            'temperature': {'id': temperature_data.id, 'value': temperature_data.temperature, 'timestamp': temperature_data.timestamp},
            'humidity': {'id': humidity_data.id, 'value': humidity_data.humidity, 'timestamp': humidity_data.timestamp}
        })
        return jsonify({'status': 'Random data generated'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'Failed to generate data', 'error': str(e)}), 500

@app.route('/next_page', methods=['GET'])
def next_page():
    return render_template('next_page.html')

@app.errorhandler(404)
def page_not_found(e):
    return jsonify({'error': 'Not Found'}), 404

@app.errorhandler(500)
def internal_server_error(e):
    return jsonify({'error': 'Internal Server Error'}), 500

# Run the app
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=80, debug=True)

# Additional fix: Add a compatible version of Werkzeug to avoid ImportError
# Update requirements.txt file to include Werkzeug version
# Werkzeug==2.0.3
