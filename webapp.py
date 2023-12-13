from flask import Flask, render_template, request
import requests
from datetime import datetime
import pytz  #for CT time zone
from geopy.geocoders import Nominatim

app = Flask(__name__)

def kelvin_to_celsius(kelvin):
    return kelvin - 273.15

def kelvin_to_fahrenheit(kelvin):
    return (kelvin - 273.15) * 9/5 + 32

def mps_to_mph(mps):
    return round(mps * 2.23694, 1)

def get_current_weather():
    api_key = '4633100f3428272436e88b4f6a488c7f'
    base_url = 'http://api.openweathermap.org/data/2.5/weather'

    # Provide coordinates for Oklahoma City, Oklahoma
    city = 'Oklahoma City'
    state = 'Oklahoma'
    coordinates = '35.4676,-97.5164'  # Latitude, Longitude

    params = {
        'q': f'{city},{state}',
        'appid': api_key,
    }

    response = requests.get(base_url, params=params)
    data = response.json()

    if response.status_code == 200:
        temperature_k = data['main']['temp']
        temperature_f = kelvin_to_fahrenheit(temperature_k)
        return {
            'city': city,
            'state': state,
            'temperature_f': temperature_f,
        }

    return None


@app.route('/')
def index():
    current_weather = get_current_weather()
    return render_template('index.html', current_weather=current_weather)


@app.route('/weather', methods=['POST'])
def weather():
    city = request.form['city']
    state = request.form['state']
    
    try:
        weather_data = get_weather(city, state)
        return render_template('weather.html', city=city, state=state, **weather_data, error_message=None)
    except Exception as e:
        error_message = "Please enter a valid city and state."
        return render_template('index.html', error_message=error_message)

#THE Weather function.

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
        precipitation_rain = data.get('rain', {}).get('1h', 0)
        precipitation_snow = data.get('snow', {}).get('1h', 0)
        sunrise_timestamp = data['sys']['sunrise']
        sunset_timestamp = data['sys']['sunset']
        wind_speed = data['wind']['speed']
        wind_direction = data['wind']['deg']

        central_time = pytz.timezone('US/Central')
        sunrise_utc = datetime.utcfromtimestamp(sunrise_timestamp)
        sunset_utc = datetime.utcfromtimestamp(sunset_timestamp)

        sunrise_local = sunrise_utc.replace(tzinfo=pytz.utc).astimezone(central_time)
        sunset_local = sunset_utc.replace(tzinfo=pytz.utc).astimezone(central_time)

        sunrise_time = sunrise_local.strftime('%I:%M %p')
        sunset_time = sunset_local.strftime('%I:%M %p')
        wind_speed_mph = mps_to_mph(wind_speed)

        return {
            'weather': weather,
            'temperature_f': temperature_f,
            'precipitation_rain': precipitation_rain,
            'precipitation_snow': precipitation_snow,
            'sunrise_time': sunrise_time,
            'sunset_time': sunset_time,
            'wind_speed': wind_speed,
            'wind_direction': wind_direction,
            'wind_speed_mph': wind_speed_mph
        }
    else:
        raise Exception(f'Error: {response.status_code}, {data.get("message", "No message provided")}')


if __name__ == '__main__':
    app.run(debug=True)
