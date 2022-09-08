from django.test import TestCase
from django.urls import reverse
from unittest.mock import MagicMock, patch


class TestIndexTestCase(TestCase):

    def test_view_url_exists_and_accessible(self):
        response = self.client.get('')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'weather/index.html')


class TestGetForecastsForCityTestCase(TestCase):

    def test_post_request_fail(self):
        with patch('geocoder.osm') as mock_request:
            mock_request.return_value.status = '...max retries exceeded with url...'
            resp = self.client.post('/get_forecasts/', data={'city': 'Moscow'})
            self.assertEqual(resp.status_code, 503)
            self.assertEqual(
                resp.json()['error'], 'Geolocation service is not responding. Try later.'
                )

    def test_post_request_no_results(self):
        with patch('geocoder.osm') as mock_request:
            mock_request.return_value.status = '...error - no results found...'
            resp = self.client.post('/get_forecasts/', data={'city': 'Moscow'})
            self.assertEqual(resp.status_code, 404)
            self.assertEqual(
                resp.json()['error'], 'The place "Moscow" wasn\'t found'
                )

    def test_post_request_success(self):
        with patch('weather.views.run_tasks_to_request_forcasts') as mock_func:
            mock_func.return_value = {'task1': 'id321', 'task2': 'id678'}
            resp = self.client.post('/get_forecasts/', data={'city': 'Vladivostok'})

            mock_func.assert_called_once()
            self.assertEqual(resp.status_code, 202)
            data = resp.json()
            self.assertEqual(mock_func.return_value, data['tasks'])
            self.assertIn("Владивосток", data['address'])
