from django.test import TestCase
from unittest.mock import Mock, patch
import requests
from django.core import exceptions


class IndexTestCase(TestCase):

    def test_view_url_exists_and_accessible(self):
        response = self.client.get('')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'weather/index.html')

    def test_context(self):
        mock_forecasters = [
            {'readable_name': 'test1', 'id': 123, 'request_func': None},
            {'readable_name': 'test2', 'id': 456, 'request_func': None},
        ]
        with patch('weather.views.FORECASTERS', mock_forecasters):
            response = self.client.get('')
            self.assertEqual(response.status_code, 200)
            assert response.context_data['forecasters'] == mock_forecasters

class GetForecastsForCityTestCase(TestCase):

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


class GetForecastStatusesTestCase(TestCase):

    def setUp(self) -> None:
        self.failure_status = 'FAILURE'
        self.success_status = 'SUCCESS'
        self.url = '/get_forecast_statuses/'
        return super().setUp()
    
    def get_result(self):
        resp = self.client.post(self.url, data={'task_ids': '123321'})
        self.assertEqual(resp.status_code, 200)

        data = resp.json()
        self.assertIn('results', data)
        results = data['results']
        self.assertIsInstance(results, list)
        r = results[0]
        self.assertEqual(len(r.keys()), 3)
        self.assertIn('task_id', r)
        self.assertIn('task_status', r)
        self.assertIn('task_result', r)
        return r

    def test_post_success(self):
        with patch('weather.views.AsyncResult') as task_res:
            res = Mock()
            res.status = self.success_status
            res.result = 'success weather data'
            task_res.return_value = res

            r = self.get_result()
            self.assertEqual(r['task_status'], self.success_status)
            self.assertEqual(r['task_result'], res.result)

    def test_post_connection_error(self):
        with patch('weather.views.AsyncResult') as task_res:
            res = Mock()
            res.status = self.failure_status
            res.result = requests.exceptions.ConnectionError()
            task_res.return_value = res

            r = self.get_result()
            self.assertEqual(r['task_status'], self.failure_status)
            self.assertEqual(r['task_result'], "Failed to establish a connection with the server")

    def test_post_connection_timeout(self):
        with patch('weather.views.AsyncResult') as task_res:
            res = Mock()
            res.status = self.failure_status
            res.result = requests.exceptions.ConnectTimeout()
            task_res.return_value = res

            r = self.get_result()
            self.assertEqual(r['task_status'], self.failure_status)
            self.assertEqual(r['task_result'], "The server hasn't responded (timeout exceeded)")

    def test_post_object_does_not_exist(self):
        with patch('weather.views.AsyncResult') as task_res:
            res = Mock()
            res.status = self.failure_status
            res.result = exceptions.ObjectDoesNotExist()
            task_res.return_value = res

            r = self.get_result()
            self.assertEqual(r['task_status'], self.failure_status)
            self.assertEqual(r['task_result'], "No data for this location")

    def test_post_unrecognized_error(self):
        with patch('weather.views.AsyncResult') as task_res:
            res = Mock()
            res.status = self.failure_status
            res.result = 'some error'
            task_res.return_value = res

            r = self.get_result()
            self.assertEqual(r['task_status'], self.failure_status)
            self.assertEqual(r['task_result'], "Some unrecognized error occured")
    
    def test_post_success_and_failure(self):
        def mock_async_result(taskid):
            res = Mock()
            if taskid == '123':
                res.status = self.success_status
                res.result = "success data"
            else:
                res.status = self.failure_status
                res.result = "error occured"
            return res

        with patch('weather.views.AsyncResult', side_effect=mock_async_result):
            resp = self.client.post(self.url, data={'task_ids': '123,321'})
            self.assertEqual(resp.status_code, 200)

            data = resp.json()
            self.assertIn('results', data)
            results = data['results']
            self.assertEqual(len(results), 2, "There should be two task results")

            for r in results:
                if r['task_id'] == '123':
                    self.assertEqual(r['task_status'], self.success_status)
                    self.assertEqual(r['task_result'], "success data")
                else:
                    self.assertEqual(r['task_status'], self.failure_status)
                    self.assertEqual(r['task_result'], "Some unrecognized error occured")
