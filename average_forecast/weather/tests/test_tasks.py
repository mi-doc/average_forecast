from unittest import mock
from django.test import TestCase
from django.core import exceptions
from unittest.mock import Mock, patch
from weather import tasks
import json
import os


RAPID_API_KEY: str = os.getenv('RAPID_API_KEY')


class TasksTestCase(TestCase):
    weather_keys: dict = { 
        'source', 'temp', 'condition', 'wind_direction', 
        'wind_speed', 'humidity', 'pressure', 'precip'
         }

    def test_run_tasks_to_request_forcasts(self):
        mock_f, mock_f2 = Mock(), Mock()
        mock_f.delay.return_value.id = '222999'
        mock_f2.delay.return_value.id = '333444'
        mock_forecasters = [
            {'readable_name': 'Mock-service1', 'id': 'mock1', 'request_func':  mock_f },
            {'readable_name': 'service2', 'id': 'mocktwo', 'request_func': mock_f2}
        ]
        with patch('weather.tasks.FORECASTERS', mock_forecasters):
            res, res2 = tasks.run_tasks_to_request_forcasts({'lat': 123, 'lng': 222})
            assert res == {'forecaster_id': 'mock1', 'task_id': '222999'}
            assert res2 == {'forecaster_id': 'mocktwo', 'task_id': '333444'}
            
    def test_get_weatherapi(self):
        mock_weather = {
            'temp_c': 123,
            'condition': {'text': 'bad'},
            'wind_degree': 100,
            "wind_kph": 14,
            "humidity": 55,
            "pressure_mb": 200,
            'precip_mm': 12
        }
        mock_response = Mock()
        mock_response.json.return_value = {'current': mock_weather}
        with patch('weather.tasks.request', return_value = mock_response) as mock_req:
            res = tasks.get_weatherapi({'lat':123, 'lng':321})
            assert set(res.keys()) == self.weather_keys
            assert res['condition'] == 'bad'
            assert res['pressure'] == 200
            mock_req.assert_called_once_with(
                "GET", "https://weatherapi-com.p.rapidapi.com/current.json",
                headers={ "X-RapidAPI-Key": RAPID_API_KEY, "X-RapidAPI-Host": "weatherapi-com.p.rapidapi.com" },
                params={"q": "123,321"}
            )
        
        # Without one of the parameters
        mock_weather = {
            'temp_c': 123,
            # 'condition': {'text': 'bad'},
            # 'wind_degree': 100,
            "wind_kph": 14,
            "humidity": 55,
            # "pressure_mb": 200,
            'precip_mm': 12
        }
        mock_response = Mock()
        mock_response.json.return_value = {'current': mock_weather}
        with patch('weather.tasks.request', return_value = mock_response):
            
            res = tasks.get_weatherapi({'lat':123, 'lng':321})
            assert set(res.keys()) == self.weather_keys
            assert res['source'] == 'weatherapi'
            assert res['wind_speed'] == 14
            assert res['wind_direction'] == res['pressure'] == res['condition'] == None

    def test_yahoo_weather(self):
        mock_weather = {
            'condition': {'temperature': 123, 'text': 'bad'},
            'wind': {'direction': 123, 'speed': 22},
            'atmosphere': {"humidity": 55, "pressure": 200},
        }
        mock_response = Mock()
        mock_response.json.return_value = {'current_observation': mock_weather}
        with patch('weather.tasks.request', return_value = mock_response) as mock_req:
            res = tasks.get_yahoo_weather({'lat':123, 'lng':321})

            # The response shoudn't contain "pressure"
            assert set(res.keys()) == self.weather_keys.difference({'precip'})
            assert res['source'] == 'yahoo_weather'
            assert res['condition'] == 'bad'
            assert res['wind_speed'] == 22
            mock_req.assert_called_once_with(
                "GET", "https://yahoo-weather5.p.rapidapi.com/weather",
                headers={ "X-RapidAPI-Key": RAPID_API_KEY, "X-RapidAPI-Host": "yahoo-weather5.p.rapidapi.com" },
                params= {"lat": 123, "long": 321,"format":"json","u":"c"}
            )

        # Without one of the params
        mock_weather = {
            'condition': {'temperature': 123, 'text': 'bad'},
            # 'wind': {'direction': 123, 'speed': 22},
            'atmosphere': {"humidity": 55} #, "pressure": 200},
        }
        mock_response = Mock()
        mock_response.json.return_value = {'current_observation': mock_weather}
        with patch('weather.tasks.request', return_value = mock_response):
            res = tasks.get_yahoo_weather({'lat':123, 'lng':321})

            # The response shoudn't contain "pressure"
            assert set(res.keys()) == self.weather_keys.difference({'precip'})
            assert res['source'] == 'yahoo_weather'
            assert res['condition'] == 'bad'
            assert res['wind_direction'] == res['pressure'] == None
    
    def test_aeris_weather(self):
        mock_weather = {
            'tempC': 123,
            'weather': 'sunny',
            'windDirDEG': 100,
            "windSpeedKPH": 14,
            "humidity": 55,
            "pressureMB": 200,
        }
        mock_response = Mock()
        mock_response.json.return_value = {'response': {'ob': mock_weather}, 'error': None}
        with patch('weather.tasks.request', return_value = mock_response) as mock_req:
            res = tasks.get_aeris_weather({'lat':123, 'lng':321})

            # The response shoudn't contain "prcipitations"
            # because aeris weather doesn't procide it
            assert set(res.keys()) == self.weather_keys.difference({'precip'})
            assert res['source'] == 'aeris_weather'
            assert res['condition'] == 'sunny'
            assert res['wind_speed'] == 14
            mock_req.assert_called_once_with(
                'GET', "https://aerisweather1.p.rapidapi.com/observations/123,321",
                headers={ "X-RapidAPI-Key": RAPID_API_KEY, "X-RapidAPI-Host": "aerisweather1.p.rapidapi.com" }
            )
    
        mock_weather = {
            # 'tempC': 123,
            # 'weather': 'sunny',
            'windDirDEG': 100,
            # "windSpeedKPH": 14,
            "humidity": 55,
            "pressureMB": 200,
        }
        mock_response = Mock()
        mock_response.json.return_value = {'response': {'ob': mock_weather}, 'error': None}
        with patch('weather.tasks.request', return_value = mock_response):
            res = tasks.get_aeris_weather({'lat':123, 'lng':321})

            # The response shoudn't contain "pressure"
            assert set(res.keys()) == self.weather_keys.difference({'precip'})
            assert res['source'] == 'aeris_weather'
            assert res['condition'] == res['wind_speed'] == res['temp'] == None
            assert res['humidity'] == 55

        # Test exception
        with self.assertRaises(exceptions.ObjectDoesNotExist):
            with patch('weather.tasks.request') as mock_request:
                mock_request.return_value.json.return_value = {
                    'error': {'description': '..no results available...'}
                    }
                res = tasks.get_aeris_weather({'lat':123, 'lng':321})
        
        # Test other error doesn't raise exception
        with patch('weather.tasks.request') as mock_request:
            mock_weather = {
                'windDirDEG': 100,
                "humidity": 55,
                "pressureMB": 200,
            }
            mock_response = Mock()
            mock_response.json.return_value = {'response': {'ob': mock_weather},'error': {'description': '..other exception...'}}
            mock_request.return_value = mock_response
            res = tasks.get_aeris_weather({'lat':123, 'lng':321})
            assert type(res) == dict
            assert set(res.keys()) == self.weather_keys.difference({'precip'})
            assert res['humidity'] == 55

    def test_get_foreca_weather(self):
        mock_weather = {
            'temperature': 123,
            'symbolPhrase': 'cloudy',
            'windDir': 100,
            "windSpeed": 14,
            "relHumidity": 55,
            "pressure": 200,
            'precipRate': 12
        }
        mock_response = Mock()
        mock_response.text = json.dumps({'current': mock_weather})
        with patch('weather.tasks.request', return_value = mock_response) as mock_req:
            res = tasks.get_foreca_weather({'lat':123, 'lng':321})
            assert res['source'] == 'foreca_weather'
            assert set(res.keys()) == self.weather_keys
            assert res['condition'] == 'cloudy'
            assert res['pressure'] == 200
            mock_req.assert_called_once_with(
                'GET', "https://foreca-weather.p.rapidapi.com/current/123,321",
                headers={ "X-RapidAPI-Key": RAPID_API_KEY, "X-RapidAPI-Host": "foreca-weather.p.rapidapi.com" },
                params={"alt":"0","tempunit":"C","windunit":"kph","tz":"Europe/London","lang":"en"} 
            )

        # Without some parameters
        mock_weather = {
            'temperature': 123,
            'symbolPhrase': 'cloudy',
            # 'windDir': 100,
            "windSpeed": 14,
            "relHumidity": 55,
            "pressure": 200,
            # 'precipRate': 12
        }
        mock_response = Mock()
        mock_response.text = json.dumps({'current': mock_weather})
        with patch('weather.tasks.request', return_value = mock_response):
            res = tasks.get_foreca_weather({'lat':123, 'lng':321})
            assert res['source'] == 'foreca_weather'
            assert set(res.keys()) == self.weather_keys
            assert res['condition'] == 'cloudy'
            assert res['pressure'] == 200
            assert res['wind_direction'] == res['precip'] == None
        
    def test_get_weatherBit(self):
        mock_weather = {
            'temp': 123,
            'weather': {'description': 'just perfect'},
            'wind_dir': 100,
            "wind_spd": 14.3,
            "rh": 55,
            "pres": 200,
            'precip': 12
        }
        mock_response = Mock()
        mock_response.text = json.dumps({'data': [ mock_weather ]})
        with patch('weather.tasks.request', return_value = mock_response) as mock_req:
            res = tasks.get_weatherBit({'lat':123, 'lng':321})
            assert res['source'] == 'weatherBit'
            assert set(res.keys()) == self.weather_keys
            assert res['condition'] == 'just perfect'
            assert res['pressure'] == 200
            assert res['wind_speed'] == float(mock_weather['wind_spd']) * 3.6 # Calculate to kph
            mock_req.assert_called_once_with(
                'GET',
                "https://weatherbit-v1-mashape.p.rapidapi.com/current",
                headers={"X-RapidAPI-Key": RAPID_API_KEY, "X-RapidAPI-Host": "weatherbit-v1-mashape.p.rapidapi.com"},
                params={"lon": 321,"lat": 123},
            )
    
        mock_weather = {
            # 'temp': 123,
            'weather': {'description': 'just perfect'},
            'wind_dir': 100,
            # "wind_spd": 14,
            "rh": 55,
            "pres": 200,
            'precip': 12
        }
        mock_response = Mock()
        mock_response.text = json.dumps({'data': [ mock_weather ]})
        with patch('weather.tasks.request', return_value = mock_response):
            res = tasks.get_weatherBit({'lat':123, 'lng':321})
            assert res['source'] == 'weatherBit'
            assert set(res.keys()) == self.weather_keys
            assert res['condition'] == 'just perfect'
            assert res['temp'] == res['wind_speed'] == None
    
    def test_get_vc_weather(self):
        mock_weather = {
            'temp': 123,
            'wdir': 100,
            "wspd": 14.3,
            "humidity": 55,
            "sealevelpressure": 201,
            'precip': 12
        }
        mock_response = Mock()
        mock_response.text = json.dumps({ 'locations': { '123, 321': { 
                                    'values': [{'conditions': 'clear'}], 
                                    'currentConditions': mock_weather
                                    } } })
        with patch('weather.tasks.request', return_value = mock_response) as mock_req:
            res = tasks.get_vc_weather({'lat':123, 'lng':321})
            assert res['source'] == 'vc_weather'
            assert set(res.keys()) == self.weather_keys
            assert res['condition'] == 'clear'
            assert res['pressure'] == 201
            mock_req.assert_called_once_with(
                'GET', "https://visual-crossing-weather.p.rapidapi.com/forecast",
                headers={ "X-RapidAPI-Key": RAPID_API_KEY, "X-RapidAPI-Host": "visual-crossing-weather.p.rapidapi.com" },
                params={ "aggregateHours":"24", "location": "123, 321",
                            "contentType":"json", "unitGroup":"metric", "shortColumnNames":"0" }
            )

        mock_weather = {
            'temp': 123,
            # 'wdir': 100,
            "wspd": 14.3,
            # "humidity": 55,
            "sealevelpressure": 201,
            'precip': 12
        }
        mock_response = Mock()
        mock_response.text = json.dumps({ 'locations': { '123, 321': { 
                                    'currentConditions': mock_weather
                                    } } })
        with patch('weather.tasks.request', return_value = mock_response) as mock_req:
            res = tasks.get_vc_weather({'lat':123, 'lng':321})
            assert res['source'] == 'vc_weather'
            assert set(res.keys()) == self.weather_keys
            assert res['pressure'] == 201
            assert res['humidity'] == res['condition'] == res['wind_direction'] == None
    
    def test_get_accu_weather(self):
        mock_weather = {
            'Temperature': {'Metric': {'Value': 25}},
            'WeatherText': 'so cold!',
            'Wind': {
                    'Direction': {'Degrees': 222},
                    'Speed': {'Metric': {'Value': 12}}
                },
            "RelativeHumidity": 56,
            "Pressure": {'Metric': {'Value': 3}},
            'Precip1hr': {'Metric': {'Value': 10}}
        }

        def mock_response_func(method, url, params):
            text = {'Key': 'mock_location'}
            if url ==  f"http://dataservice.accuweather.com/currentconditions/v1/{text['Key']}":
                text = [mock_weather]
            mock_response = Mock()
            mock_response.text = json.dumps(text)
            return mock_response

        with patch('weather.tasks.request', side_effect=mock_response_func) as mock_req:
            res = tasks.get_accu_weather({'lat':123, 'lng':321})
            assert res['source'] == 'accu_weather'
            assert set(res.keys()) == self.weather_keys
            assert res['condition'] == 'so cold!'
            assert res['pressure'] == 3
            assert res['wind_speed'] == 12
            mock_req.assert_called_with(
                "GET",
                "http://dataservice.accuweather.com/currentconditions/v1/mock_location",
                params={"apikey": 'GfA1W3ZZr8lHUGCL3LGyV4UOEK80bGMI', 'details': 'true'}
            )

        # With missing params
        mock_weather = {
            # 'Temperature': {'Metric': {'Value': 25}},
            'WeatherText': 'so cold!',
            'Wind': {
                    'Direction': {'Degrees': 222},
                    # 'Speed': {'Metric': {'Value': 12}}
                },
            "RelativeHumidity": 56,
            # "Pressure": {'Metric': {'Value': 3}},
            'Precip1hr': {'Metric': {'Value': 10}}
        }

        with patch('weather.tasks.request', side_effect=mock_response_func) as mock_req:
            res = tasks.get_accu_weather({'lat':123, 'lng':321})
            assert res['source'] == 'accu_weather'
            assert set(res.keys()) == self.weather_keys
            assert res['wind_direction'] == 222
            assert res['precip'] == 10
            assert res['wind_speed'] == res['pressure'] == res['temp'] == None