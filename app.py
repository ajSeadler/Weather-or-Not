# import requests

# def get_weather(city):
#     api_key = '4633100f3428272436e88b4f6a488c7f'
#     base_url = 'http://api.openweathermap.org/data/2.5/weather'

#     params = {
#         'q': city,
#         'appid': api_key,
#     }

#     response = requests.get(base_url, params=params)
#     data = response.json()

#     if response.status_code == 200:
#         weather = data['weather'][0]['description']
#         temperature = data['main']['temp']
#         print(f'The weather in {city} is {weather} with a temperature of {temperature}°C.')
#     else:
#         print(f'Error: {data["message"]}')

# if __name__ == '__main__':
#     city = input('Enter the city: ')
#     get_weather(city)
