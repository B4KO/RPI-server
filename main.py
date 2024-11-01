from flask import Flask, request, render_template, jsonify
from datetime import datetime

app = Flask(__name__)

# List to store received data
received_data = []

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/reset', methods=['POST'])
def reset_data():
    global received_data
    received_data = []
    return jsonify({'status': 'Data reset'}), 200


@app.route('/receive', methods=['POST'])
def receive():
    global received_data
    new_data = request.json  # Expecting JSON data
    if new_data:
        # Add a timestamp to the data
        new_data['timestamp'] = datetime.utcnow().isoformat()
        received_data.append(new_data)
        return jsonify({'status': 'Data received'}), 200
    else:
        return jsonify({'status': 'No data received'}), 400

@app.route('/data', methods=['GET'])
def get_data():
    # Return the received data as JSON
    return jsonify(received_data)

@app.errorhandler(404)
def page_not_found(e):
    return jsonify({'error': 'Not Found'}), 404

@app.errorhandler(500)
def internal_server_error(e):
    return jsonify({'error': 'Internal Server Error'}), 500



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
