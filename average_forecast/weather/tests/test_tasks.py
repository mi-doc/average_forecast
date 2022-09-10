from django.test import TestCase
from unittest.mock import Mock, patch
import requests
from django.core import exceptions
from weather import tasks


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