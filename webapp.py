from flask import Flask, render_template, request
import requests
from datetime import datetime
import pytz  # Import the pytz module

app = Flask(__name__)

def kelvin_to_celsius(kelvin):
    return kelvin - 273.15

def kelvin_to_fahrenheit(kelvin):
    return (kelvin - 273.15) * 9/5 + 32

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/weather', methods=['POST'])
def weather():
    city = request.form['city']
    state = request.form['state']
    try:
        weather_data = get_weather(city, state)
        return render_template('weather.html', city=city, state=state, **weather_data)
    except Exception as e:
        return render_template('error.html', error=str(e))

# ... (your existing code)

def get_weather(city, state):
    api_key = '4633100f3428272436e88b4f6a488c7f'
    base_url = 'http://api.openweathermap.org/data/2.5/weather'

    params = {
        'q': f'{city},{state}',
        'appid': api_key,
    }

    response = requests.get(base_url, params=params)
    data = response.json()

    if response.status_code == 200:
        weather = data['weather'][0]['description']
        temperature_k = data['main']['temp']
        temperature_f = kelvin_to_fahrenheit(temperature_k)
        precipitation_rain = data.get('rain', {}).get('1h', 0)  # 1-hour precipitation in mm
        precipitation_snow = data.get('snow', {}).get('1h', 0)  # 1-hour snowfall in mm
        sunrise_timestamp = data['sys']['sunrise']
        sunset_timestamp = data['sys']['sunset']

        # Convert timestamps to readable time format in Central Time Zone
        central_time = pytz.timezone('US/Central')
        sunrise_utc = datetime.utcfromtimestamp(sunrise_timestamp)
        sunset_utc = datetime.utcfromtimestamp(sunset_timestamp)

        sunrise_local = sunrise_utc.replace(tzinfo=pytz.utc).astimezone(central_time)
        sunset_local = sunset_utc.replace(tzinfo=pytz.utc).astimezone(central_time)

        sunrise_time = sunrise_local.strftime('%I:%M %p')
        sunset_time = sunset_local.strftime('%I:%M %p')

        return {
            'weather': weather,
            'temperature_f': temperature_f,
            'precipitation_rain': precipitation_rain,
            'precipitation_snow': precipitation_snow,
            'sunrise_time': sunrise_time,
            'sunset_time': sunset_time
        }
    else:
        raise Exception(f'Error: {response.status_code}, {data.get("message", "No message provided")}')


if __name__ == '__main__':
    app.run(debug=True)
