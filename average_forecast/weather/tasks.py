import time
from requests import request

from celery import shared_task
import time


API_KEY = 'fcccdcec54mshd8de1f4afd9c04cp1bd53fjsn8fbc05589296'


def run_tasks_to_request_forcasts(city):
    forecasters = [
        # request_open_weather_map,
        request_yahoo_weather,
    ]
    
    task_ids = []
    for forecaster in forecasters:
        task = forecaster.delay(city)
        task_ids.append(task.id)

    return task_ids


@shared_task
def request_open_weather_map(city):
    # url = "https://community-open-weather-map.p.rapidapi.com/forecast"
    querystring = {"q": city, "units": "metric"}
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "community-open-weather-map.p.rapidapi.com",
    }
    data = request("GET", url, headers=headers, params=querystring)
    return 'Mi poluchili datu.'


@shared_task
def request_yahoo_weather(city="Moscow"):
    url = "https://yahoo-weather5.p.rapidapi.com/weather"
    # url = "htttps://yandex.ru"
    querystring = {"location": city, "format":"json","u":"c"}

    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "yahoo-weather5.p.rapidapi.com"
    }

    data_json = request("GET", url, headers=headers, params=querystring)
    data = data_json.json()
    current_weather = {
        'source': 'yahoo_weather',
        'temp': data['current_observation']['condition']['temperature'],
        'condition': data['current_observation']['condition']['text'],
        'wind_direction': data['current_observation']['wind']['direction'],
        'wind_speed': data['current_observation']['wind']['speed'],
        'humidity': data['current_observation']['atmosphere']['humidity'],
        'pressure': data['current_observation']['atmosphere']['pressure']            
    }
    return current_weather

# def test_f(city):
#     url = "https://yahoo-weather5.p.rapidapi.com/weather"
#     # url = "htttps://yandex.ru"
#     querystring = {"location": city, "format":"json","u":"c"}

#     headers = {
#         "X-RapidAPI-Key": API_KEY,
#         "X-RapidAPI-Host": "yahoo-weather5.p.rapidapi.com"
#     }

#     data_json = request("GET", url, headers=headers, params=querystring)
#     data = data_json.json()
#     print(data)