from flask import Blueprint, render_template
from ..services.weather_service import fetch_weather_data

weather_routes = Blueprint('weather_routes', __name__)

@weather_routes.route('/weather', methods=['GET'])
def weather():
    today_data, forecast_data = fetch_weather_data()
    return render_template('weather.html', **today_data, forecast=forecast_data)
