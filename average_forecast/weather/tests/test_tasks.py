from unittest import mock
from django.test import TestCase
from django.core import exceptions
from unittest.mock import Mock, patch
from weather import tasks
import json
import os


RAPID_API_KEY = os.getenv('RAPID_API_KEY')


class TasksTestCase(TestCase):
    weather_keys = { 
        'source', 'temp', 'condition', 'wind_direction', 
        'wind_speed', 'humidity', 'pressure', 'precip'
         }
    
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
        mock_response.json.return_value = {'response': {'ob': mock_weather}}
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
        mock_response.json.return_value = {'response': {'ob': mock_weather}}
        with patch('weather.tasks.request', return_value = mock_response):
            res = tasks.get_aeris_weather({'lat':123, 'lng':321})

            # The response shoudn't contain "pressure"
            assert set(res.keys()) == self.weather_keys.difference({'precip'})
            assert res['source'] == 'aeris_weather'
            assert res['condition'] == res['wind_speed'] == res['temp'] == None
            assert res['humidity'] == 55

        # Test exception
        with self.assertRaises(exceptions.ObjectDoesNotExist) as e:
            with patch('weather.tasks.request') as mock_request:
                mock_response = Mock()
                mock_response.json.return_value = {'error': {'description': '..no results available...'}}
                mock_request.return_value = mock_response
                res = tasks.get_aeris_weather({'lat':123, 'lng':321})
            assert 'no results available' in e.exception.args[0]
        
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
        pass
