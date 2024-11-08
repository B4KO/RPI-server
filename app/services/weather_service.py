import requests
from datetime import datetime
from ..helpers.icon_mapper import map_icon

WEATHER_API_KEY = 'your_api_key_here'
WEATHER_API_URL = 'https://api.openweathermap.org/data/3.0/onecall'


LATITUDE = 58.1467
LONGITUDE = 7.9956

def fetch_weather_data():
    """
    Fetches weather data from the OpenWeatherMap API for the specified latitude and longitude.
    Returns a dictionary containing today's weather data and a 7-day forecast.
    """
    # Build the request URL
    url = f"{WEATHER_API_URL}?lat={LATITUDE}&lon={LONGITUDE}&exclude=minutely&appid={WEATHER_API_KEY}&units=metric"
    
    try:
        # Make the API request
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        
        # Parse the JSON response
        data = response.json()
        
        # Validate necessary fields in the API response
        if "current" not in data or "daily" not in data:
            print("Error: Missing expected data keys in the API response.")
            return {}, {}

        # Process today's data
        current = data["current"]
        today_data = {
            "today_temp": current.get("temp", "N/A"),
            "today_desc": current.get("weather", [{"description": "N/A"}])[0]["description"].capitalize(),
            "today_icon": f"fas fa-{map_icon(current['weather'][0]['icon'])}" if "weather" in current else "fas fa-cloud",
            "humidity": current.get("humidity", "N/A"),
            "wind_speed": current.get("wind_speed", "N/A"),
            "sunrise": datetime.fromtimestamp(current.get("sunrise", 0)).strftime("%H:%M") if "sunrise" in current else "N/A",
            "sunset": datetime.fromtimestamp(current.get("sunset", 0)).strftime("%H:%M") if "sunset" in current else "N/A",
        }

        # Process 7-day forecast data
        forecast_data = {}
        for day in data.get("daily", [])[:7]:  # Limit to 7 days
            day_name = datetime.fromtimestamp(day["dt"]).strftime("%A")
            forecast_data[day_name] = {
                "temp": day["temp"].get("day", "N/A"),
                "min_temp": day["temp"].get("min", "N/A"),
                "max_temp": day["temp"].get("max", "N/A"),
                "desc": day["weather"][0]["description"].capitalize() if "weather" in day else "N/A",
                "icon": f"fas fa-{map_icon(day['weather'][0]['icon'])}" if "weather" in day else "fas fa-cloud",
            }

        return today_data, forecast_data

    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return {}, {}
