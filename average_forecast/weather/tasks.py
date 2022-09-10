from django.core.exceptions import ObjectDoesNotExist
from requests import request
from celery import shared_task
import json
import os


RAPID_API_KEY = os.getenv('RAPID_API_KEY')


def run_tasks_to_request_forcasts(coords): # ToDo: add type checking
    """
    This function takes coords name as an argument and creates tasks requesting
    weather forecasters, and returns a list of task ids.
    """
    return [
        {
            'forecaster_id': forecaster['id'], 
            'task_id': forecaster['request_func'].delay(coords).id
        } 
        for forecaster in FORECASTERS
    ]

@shared_task
def get_weatherapi(coords):
    url = "https://weatherapi-com.p.rapidapi.com/current.json"
    querystring = {"q": f"{coords['lat']},{coords['lng']}"}
    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": "weatherapi-com.p.rapidapi.com"
    }

    data_json = request("GET", url, headers=headers, params=querystring)
    data = data_json.json()
    current_weather = data['current']
    
    return {
        'source': 'weatherapi',
        'temp': current_weather.get('temp_c'),
        'condition': current_weather.get('condition', {}).get('text'),
        'wind_direction': current_weather.get('wind_degree'),
        'wind_speed': current_weather.get('wind_kph'),
        'humidity': current_weather.get('humidity'),
        'pressure': current_weather.get('pressure_mb'),
        'precip': current_weather.get('precip_mm')         
    }

@shared_task
def get_yahoo_weather(coords):
    url = "https://yahoo-weather5.p.rapidapi.com/weather"
    querystring = {"lat": coords['lat'], "long": coords['lng'],"format":"json","u":"c"}
    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": "yahoo-weather5.p.rapidapi.com"
    }
    data_json = request("GET", url, headers=headers, params=querystring)
    data = data_json.json()
    current_weather = data['current_observation']

    return {
        'source': 'yahoo_weather',
        'temp': current_weather.get('condition', {}).get('temperature'),
        'condition': current_weather.get('condition', {}).get('text'),
        'wind_direction': current_weather.get('wind', {}).get('direction'),
        'wind_speed': current_weather.get('wind', {}).get('speed'),
        'humidity': current_weather.get('atmosphere', {}).get('humidity'),
        'pressure': current_weather.get('atmosphere', {}).get('pressure')
    }

@shared_task
def get_aeris_weather(coords):
    url = f"https://aerisweather1.p.rapidapi.com/observations/{coords['lat']},{coords['lng']}"

    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": "aerisweather1.p.rapidapi.com"
    }
    data_json = request("GET", url, headers=headers)
    data = data_json.json()
    if 'error' in data and 'no results available' in data['error']['description'].lower():
        raise ObjectDoesNotExist(data['error']['description'])

    current_weather = data['response']['ob']

    return {
        'source': 'aeris_weather',
        'temp': current_weather.get('tempC'),
        'condition': current_weather.get('weather'),
        'wind_direction': current_weather.get('windDirDEG'),
        'wind_speed': current_weather.get('windSpeedKPH'),
        'humidity': current_weather.get('humidity'),
        'pressure': current_weather.get('pressureMB')            
    }

@shared_task
def get_foreca_weather(coords):
    url = f"https://foreca-weather.p.rapidapi.com/current/{coords['lat']},{coords['lng']}"

    querystring = {"alt":"0","tempunit":"C","windunit":"kph","tz":"Europe/London","lang":"en"}

    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": "foreca-weather.p.rapidapi.com"
    }

    req = request("GET", url, headers=headers, params=querystring)
    data = json.loads(req.text)
    current_weather = data['current']

    return {
        'source': 'foreca_weather',
        'temp': current_weather.get('temperature'),
        'condition': current_weather.get('symbolPhrase'),
        'wind_direction': current_weather.get('windDir'),
        'wind_speed': current_weather.get('windSpeed'),
        'humidity': current_weather.get('relHumidity'),
        'pressure': current_weather.get('pressure'),
        'precip': current_weather.get('precipRate')
    }

@shared_task
def get_weatherBit(coords):
    url = "https://weatherbit-v1-mashape.p.rapidapi.com/current"
    querystring = {"lon": coords['lng'],"lat": coords['lat']}
    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": "weatherbit-v1-mashape.p.rapidapi.com"
    }

    response = request("GET", url, headers=headers, params=querystring)
    data = json.loads(response.text)
    current_weather = data['data'][0]

    wind_spd = current_weather.get('wind_spd')
    if wind_spd != None:
        wind_spd = float(wind_spd) * 3.6
    return {
        'source': 'weatherBit',
        'temp': current_weather.get('temp'),
        'condition': current_weather.get('weather', {}).get('description'),
        'wind_direction': current_weather.get('wind_dir'),
        'wind_speed': wind_spd,
        'humidity': current_weather.get('rh'),
        'pressure': current_weather.get('pres'),
        'precip': current_weather.get('precip')
    } 

@shared_task
def get_vc_weather(coords):
    url = "https://visual-crossing-weather.p.rapidapi.com/forecast"
    querystring = {
        "aggregateHours":"24",
        "location": f"{coords['lat']}, {coords['lng']}",
        "contentType":"json",
        "unitGroup":"metric",
        "shortColumnNames":"0"
    }
    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": "visual-crossing-weather.p.rapidapi.com"
    }

    response = request("GET", url, headers=headers, params=querystring)
    data = json.loads(response.text)
    location_data = data['locations'][f"{coords['lat']}, {coords['lng']}"]
    current_weather = location_data['currentConditions']

    return {
        'source': 'weather',
        'temp': current_weather['temp'],
        'condition': location_data['values'][0]['conditions'],
        'wind_direction': current_weather['wdir'],
        'wind_speed': current_weather['wspd'],
        'humidity': current_weather['humidity'],
        'pressure': current_weather['sealevelpressure'],
        'precip': current_weather['precip']
    } 

@shared_task
def get_accu_weather(coords):
    url = 'http://dataservice.accuweather.com/locations/v1/cities/geoposition/search'

    # Getting "location key" of a place (required by accuweather)
    querystring = {
        "q": f"{coords['lat']},{coords['lng']}",
        "apikey": 'GfA1W3ZZr8lHUGCL3LGyV4UOEK80bGMI'
    }
    response = request("GET", url, params=querystring)
    location_key = json.loads(response.text)['Key']
    
    # Getting the forecast
    url = "http://dataservice.accuweather.com/currentconditions/v1/" + location_key
    querystring.pop('q')      # Don't need it here
    querystring['details'] = 'true'  # More detailed weather
    response = request("GET", url, params=querystring)
    data = json.loads(response.text)
    current_weather = data[0]

    return {
        'source': 'weather',
        'temp': current_weather['Temperature']['Metric']['Value'],
        'condition': current_weather['WeatherText'],
        'wind_direction': current_weather['Wind']['Direction']['Degrees'],
        'wind_speed': current_weather['Wind']['Speed']['Metric']['Value'],
        'humidity': current_weather['RelativeHumidity'],
        'pressure': current_weather['Pressure']['Metric']['Value'],
        'precip': current_weather['Precip1hr']['Metric']['Value']
    } 



FORECASTERS_LIST = [
    ('Yahoo weather', 'yahoo_weather', get_yahoo_weather),      # 1000 per month, 10 per minute
    ('Accu weather', 'accu_weather', get_accu_weather),         # 50 per day
    ('WeatherApi', 'weatherapi', get_weatherapi),                 # 1,000,000 requests per month
    ('Aeris weather', 'aeris_weather', get_aeris_weather),        # 100 per day
    # ('Foreca weather', 'foreca_weather', get_foreca_weather),    # 100 per month
    ('WeatherBit', 'weather', get_weatherBit),                           # 100 per day
    ('Visual crossing weather', 'vc_weather', get_vc_weather),      # 500 per month
]

FORECASTERS = [{'readable_name': t[0], 'id': t[1], 'request_func': t[2]} for t in FORECASTERS_LIST]


    
