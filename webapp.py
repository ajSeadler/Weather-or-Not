from flask import Flask, render_template, request
import requests
from datetime import datetime
import pytz  # for CT time zone
from geopy.geocoders import Nominatim
import ssl

# in the future i will find a way to make this code more managable but here it is for now. 

# Disable SSL certificate verification for Geopy - I would never do this in the real world. Plus this site will never be live. 
ssl._create_default_https_context = ssl._create_unverified_context

app = Flask(__name__)



def kelvin_to_celsius(kelvin):
    return kelvin - 273.15

def kelvin_to_fahrenheit(kelvin):
    return (kelvin - 273.15) * 9/5 + 32

def mps_to_mph(mps):
    return round(mps * 2.23694, 1)



def get_location_time_zone(city, state):
    geolocator = Nominatim(user_agent="your_app_name")
    location = geolocator.geocode(f"{city}, {state}")

    if location:
        return pytz.timezone(location.raw['timezone'])
    else:
        # Default to UTC if the location can't be determined
        return pytz.utc

def get_current_weather():
    api_key = '4633100f3428272436e88b4f6a488c7f'
    base_url = 'http://api.openweathermap.org/data/2.5/weather'

    
    city = 'Oklahoma City'
    state = 'Oklahoma'
    coordinates = '35.4676,-97.5164' 

    params = {
        'q': f'{city},{state}',
        'appid': api_key,
    }

    response = requests.get(base_url, params=params)
    data = response.json()

    if response.status_code == 200:
        temperature_k = data['main']['temp']
        temperature_f = round(kelvin_to_fahrenheit(temperature_k))
        current_time = datetime.now().strftime('%I:%M %p')  # Get the current time

        return {
            'city': city,
            'state': state,
            'temperature_f': temperature_f,
            'current_time': current_time,          }

    return None

# Import necessary libraries
from datetime import datetime

def get_8_day_forecast(city, state):
    api_key = '4633100f3428272436e88b4f6a488c7f'
    base_url = 'http://api.openweathermap.org/data/2.5/forecast'

    params = {
        'q': f'{city},{state}',
        'appid': api_key,
    }

    response = requests.get(base_url, params=params)
    data = response.json()

    if response.status_code == 200:
        forecast_data = []
        unique_dates = set()

        for item in data.get('list', []):
            timestamp = item['dt']
            forecast_utc = datetime.utcfromtimestamp(timestamp)
            
            # Extracting day of the week, month, and date
            formatted_day = forecast_utc.strftime('%A, %b %d')

            # Only include data for the next 8 unique dates
            if formatted_day not in unique_dates and len(forecast_data) < 8:
                temperature_k = item['main']['temp']
                temperature_f = round(kelvin_to_fahrenheit(temperature_k))
                weather_description = item['weather'][0]['description'].title()

                # Append forecast data to the list
                forecast_data.append({
                    'formatted_day': formatted_day,
                    'temperature_f': temperature_f,
                    'weather_description': weather_description,
                })

                # Add the formatted day to the set of unique dates
                unique_dates.add(formatted_day)

        return forecast_data
    else:
        # Handle API errors
        error_message = f'Error: {response.status_code}, {data.get("message", "No message provided")}'
        raise Exception(error_message)

# hard coded forecast location for now
@app.route('/forecast')
def forecast():
    city = 'Oklahoma City' 
    state = 'Oklahoma'      

    try:
        forecast_data = get_8_day_forecast(city, state)
        return render_template('forecast.html', city=city, state=state, forecast_data=forecast_data)
    except Exception as e:
        error_message = "Error fetching forecast. Please try again later."
        return render_template('index.html', error_message=error_message)

    

@app.route('/')
def index():
    current_weather = get_current_weather()
    return render_template('index.html', current_weather=current_weather)

@app.route('/about')
def about():
    return render_template('about.html')

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

    

# THE Weather function.
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
        # Check if the response contains weather data
        if 'weather' in data and 'main' in data:
            weather = data['weather'][0]['description'].title()
            temperature_k = data['main']['temp']
            temperature_f = round(kelvin_to_fahrenheit(temperature_k))
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
            # No weather data found
            raise Exception("Invalid city or state.")
    else:
        # Handle API errors
        error_message = f'Error: {response.status_code}, {data.get("message", "No message provided")}'
        raise Exception(error_message)
    
    

if __name__ == '__main__':
    app.run(debug=True)
