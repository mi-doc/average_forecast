from django.test import TestCase
from unittest.mock import Mock, patch
import requests
from django.core import exceptions
from weather import tasks
import django


class TasksTestCase(TestCase):
    keys = { 
        'source', 'temp', 'condition', 'wind_direction', 
        'wind_speed', 'humidity', 'pressure', 'precip'
         }
    
    def test_get_weatherapi(self):
        mock_response = {
            'temp_c': 123,
            'condition': {'text': 'bad'},
            'wind_degree': 100,
            "wind_kph": 14,
            "humidity": 55,
            "pressure_mb": 200,
            'precip_mm': 12
        }
        mock_json = Mock()
        mock_json.json.return_value = {'current': mock_response}
        with patch('weather.tasks.request') as mock_request:
            mock_request.return_value = mock_json
            res = tasks.get_weatherapi({'lat':123, 'lng':321})
            assert set(res.keys()) == self.keys
            assert res['condition'] == 'bad'
            assert res['pressure'] == 200
        
        # Without one of the parameters
        mock_response = {
            'temp_c': 123,
            # 'condition': {'text': 'bad'},
            # 'wind_degree': 100,
            "wind_kph": 14,
            "humidity": 55,
            # "pressure_mb": 200,
            'precip_mm': 12
        }
        mock_json = Mock()
        mock_json.json.return_value = {'current': mock_response}
        with patch('weather.tasks.request') as mock_request:
            mock_request.return_value = mock_json
            res = tasks.get_weatherapi({'lat':123, 'lng':321})
            assert set(res.keys()) == self.keys
            assert res['source'] == 'weatherapi'
            assert res['wind_speed'] == 14
            assert res['wind_direction'] == res['pressure'] == res['condition'] == None

    def test_yahoo_weather(self):
        mock_response = {
            'condition': {'temperature': 123, 'text': 'bad'},
            'wind': {'direction': 123, 'speed': 22},
            'atmosphere': {"humidity": 55, "pressure": 200},
        }
        mock_json = Mock()
        mock_json.json.return_value = {'current_observation': mock_response}
        with patch('weather.tasks.request') as mock_request:
            mock_request.return_value = mock_json
            res = tasks.get_yahoo_weather({'lat':123, 'lng':321})

            # The response shoudn't contain "pressure"
            assert set(res.keys()) == self.keys.difference({'precip'})
            assert res['source'] == 'yahoo_weather'
            assert res['condition'] == 'bad'
            assert res['wind_speed'] == 22

        # Without one of the params
        mock_response = {
            'condition': {'temperature': 123, 'text': 'bad'},
            # 'wind': {'direction': 123, 'speed': 22},
            'atmosphere': {"humidity": 55} #, "pressure": 200},
        }
        mock_json = Mock()
        mock_json.json.return_value = {'current_observation': mock_response}
        with patch('weather.tasks.request') as mock_request:
            mock_request.return_value = mock_json
            res = tasks.get_yahoo_weather({'lat':123, 'lng':321})

            # The response shoudn't contain "pressure"
            assert set(res.keys()) == self.keys.difference({'precip'})
            assert res['source'] == 'yahoo_weather'
            assert res['condition'] == 'bad'
            assert res['wind_direction'] == res['pressure'] == None
    
    def test_aeris_weather(self):
        mock_response = {
            'tempC': 123,
            'weather': 'sunny',
            'windDirDEG': 100,
            "windSpeedKPH": 14,
            "humidity": 55,
            "pressureMB": 200,
        }
        mock_json = Mock()
        mock_json.json.return_value = {'response': {'ob': mock_response}}
        with patch('weather.tasks.request') as mock_request:
            mock_request.return_value = mock_json
            res = tasks.get_aeris_weather({'lat':123, 'lng':321})

            # The response shoudn't contain "prcipitations"
            # because aeris weather doesn't procide it
            assert set(res.keys()) == self.keys.difference({'precip'})
            assert res['source'] == 'aeris_weather'
            assert res['condition'] == 'sunny'
            assert res['wind_speed'] == 14
    
        mock_response = {
            # 'tempC': 123,
            # 'weather': 'sunny',
            'windDirDEG': 100,
            # "windSpeedKPH": 14,
            "humidity": 55,
            "pressureMB": 200,
        }
        mock_json = Mock()
        mock_json.json.return_value = {'response': {'ob': mock_response}}
        with patch('weather.tasks.request') as mock_request:
            mock_request.return_value = mock_json
            res = tasks.get_aeris_weather({'lat':123, 'lng':321})

            # The response shoudn't contain "pressure"
            assert set(res.keys()) == self.keys.difference({'precip'})
            assert res['source'] == 'aeris_weather'
            assert res['condition'] == res['wind_speed'] == res['temp'] == None
            assert res['humidity'] == 55

        # Test exception
        with self.assertRaises(exceptions.ObjectDoesNotExist) as e:
            with patch('weather.tasks.request') as mock_request:
                mock_json = Mock()
                mock_json.json.return_value = {'error': {'description': '..no results available...'}}
                mock_request.return_value = mock_json
                res = tasks.get_aeris_weather({'lat':123, 'lng':321})
            assert 'no results available' in e.exception.args[0]
        
        # Test other error doesn't raise exception
        with patch('weather.tasks.request') as mock_request:
            mock_response = {
                'windDirDEG': 100,
                "humidity": 55,
                "pressureMB": 200,
            }
            mock_json = Mock()
            mock_json.json.return_value = {'response': {'ob': mock_response},'error': {'description': '..other exception...'}}
            mock_request.return_value = mock_json
            res = tasks.get_aeris_weather({'lat':123, 'lng':321})
            assert type(res) == dict
            assert set(res.keys()) == self.keys.difference({'precip'})
            assert res['humidity'] == 55
