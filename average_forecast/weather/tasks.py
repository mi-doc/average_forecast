from requests import request
from celery import shared_task

RAPID_API_KEY = 'fcccdcec54mshd8de1f4afd9c04cp1bd53fjsn8fbc05589296'


def run_tasks_to_request_forcasts(city): # ToDo: add type checking
    """
    This function takes city name as an argument and creates tasks requesting
    weather forecasters, and returns a list of task ids.
    """
    # Below is the list of wether forecast APIs we want to request
    forecasters = [
        # get_open_weather_map,
        get_yahoo_weather,
        get_weatherapi,
        get_aeris_weather
    ]
    
    task_ids = []
    for forecaster in forecasters:
        task = forecaster.delay(city)
        task_ids.append(task.id)
    return task_ids

@shared_task
def get_weatherapi(city):
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
def get_open_weather_map(city):
    url = "https://community-open-weather-map.p.rapidapi.com/forecast"
    querystring = {"q": city, "units": "metric"}
    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": "community-open-weather-map.p.rapidapi.com",
    }
    data_json = request("GET", url, headers=headers, params=querystring)
    data = data_json.json()
    current_weather = {
        # ToDo: figure out if this API works
    }
    return current_weather

@shared_task
def get_yahoo_weather(city="Moscow"):
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

@shared_task
def get_aeris_weather(city):
    url = f"https://aerisweather1.p.rapidapi.com/observations/{city},ru"

    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": "aerisweather1.p.rapidapi.com"
    }
    data_json = request("GET", url, headers=headers)
    data = data_json.json()
    current_weather = data['response']['ob']

    return {
        'source': 'aeris_weather',
        'temp': current_weather['tempC'],
        'condition': current_weather['weather'],
        'wind_direction': current_weather['windDirDEG'],
        'wind_speed': current_weather['windSpeedKPH'],
        'humidity': current_weather['humidity'],
        'pressure': current_weather['pressureMB']            
    }




    
