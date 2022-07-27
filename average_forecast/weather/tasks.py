from requests import request
from celery import shared_task

RAPID_API_KEY = 'fcccdcec54mshd8de1f4afd9c04cp1bd53fjsn8fbc05589296'


def run_tasks_to_request_forcasts(city):
    forecasters = [
        # request_open_weather_map,
        request_yahoo_weather,
        request_weatherapi,
    ]
    
    task_ids = []
    for forecaster in forecasters:
        task = forecaster.delay(city)
        task_ids.append(task.id)
    return task_ids

@shared_task
def request_weatherapi(city):
    url = "https://weatherapi-com.p.rapidapi.com/current.json"
    querystring = {"q": city}
    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": "weatherapi-com.p.rapidapi.com"
    }

    data_json = request("GET", url, headers=headers, params=querystring)
    data = data_json.json()
    current_weather = data['current']
    return {
        'source': 'weatherapi',
        'temp': current_weather['temp_c'],
        'condition': current_weather['condition']['text'],
        'wind_direction': current_weather['wind_degree'],
        'wind_speed': current_weather['wind_kph'],
        'humidity': current_weather['humidity'],
        'pressure': current_weather['pressure_mb'],
        'precip': current_weather['precip_mm']         
    }

@shared_task
def request_open_weather_map(city):
    url = "https://community-open-weather-map.p.rapidapi.com/forecast"
    querystring = {"q": city, "units": "metric"}
    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": "community-open-weather-map.p.rapidapi.com",
    }
    data_json = request("GET", url, headers=headers, params=querystring)
    data = data_json.json()
    current_weather = {

    }
    return current_weather

@shared_task
def request_yahoo_weather(city="Moscow"):
    url = "https://yahoo-weather5.p.rapidapi.com/weather"
    querystring = {"location": city, "format":"json", "u":"c"}
    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": "yahoo-weather5.p.rapidapi.com"
    }
    data_json = request("GET", url, headers=headers, params=querystring)
    data = data_json.json()
    current_weather = data['current_observation']

    return {
        'source': 'yahoo_weather',
        'temp': current_weather['condition']['temperature'],
        'condition': current_weather['condition']['text'],
        'wind_direction': current_weather['wind']['direction'],
        'wind_speed': current_weather['wind']['speed'],
        'humidity': current_weather['atmosphere']['humidity'],
        'pressure': current_weather['atmosphere']['pressure']            
    }