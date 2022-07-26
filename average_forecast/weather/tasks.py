import time
from requests import request

from celery import shared_task
import time


API_KEY = 'fcccdcec54mshd8de1f4afd9c04cp1bd53fjsn8fbc05589296'


def run_tasks_to_request_forcasts(city):
    forecasters = [
        request_open_weather_map,
    ]

    task_ids = []
    for forecaster in forecasters:
        task = forecaster.delay(city)
        task_ids.append(task.id)
    
    return task_ids


@shared_task
def request_open_weather_map(city):
    url = "https://community-open-weather-map.p.rapidapi.com/forecast"
    querystring = {"q": city, "units": "metric"}
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "community-open-weather-map.p.rapidapi.com",
    }
    data = request("GET", url, headers=headers, params=querystring)
    return 'Mi poluchili datu.'




###########################################################################
# TRAINING TASKS
###########################################################################
@shared_task
def create_task(task_type):
    time.sleep(int(task_type) * 10)
    return True
