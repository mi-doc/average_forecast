from celery.result import AsyncResult
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

import geocoder
from weather.tasks import FORECASTERS, run_tasks_to_request_forcasts


class Index(TemplateView):
    template_name = 'weather/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['forecasters'] = FORECASTERS 
        return context


@csrf_exempt
def get_forecasts_for_city(request):
    if request.POST:
        city = request.POST.get('city')

        # Here we find out the coordinates of the city requested by user,
        # since some weather forecasters don't accept a city name,
        # only latitude and longitude of the place
        g = geocoder.osm(city)
        response = {}

        # TODO: improve status checking
        if 'max retries exceeded with url' in g.status.lower():
            response["error"] = "Geolocation service is not responding. Try later."
            status = 503
        elif 'error - no results found' in g.status.lower():
            response["error"] = f'The place "{city}" wasn\'t found'
            status=404
        else:
            city_data = g.geojson['features'][0]['properties']
            coords = {
                'lat': city_data['lat'], 
                'lng': city_data['lng']
            }
            tasks = run_tasks_to_request_forcasts(coords)
            response.update({"tasks": tasks, "address": city_data['address']})
            status = 202

        return JsonResponse(response, status=status)

EXCEPTION_MESSAGES = {
    'ConnectionError': 'Failed to establish a connection with the server',
    'ConnectTimeout': 'The server hasn\'t responded (timeout exceeded)',
    'ObjectDoesNotExist': 'No data for this location',
}

@csrf_exempt
def get_forecast_statuses(request):
    if request.POST:
        task_ids = request.POST.get('task_ids').split(',')
        results = []
        for task_id in task_ids:
            task_data = AsyncResult(task_id)
            task_result = task_data.result

            if task_data.status == 'FAILURE':
                task_result = EXCEPTION_MESSAGES.get(
                    type(task_result).__name__, "Some unrecognized error occured"
                    )

            results.append({
                "task_id": task_id,
                "task_status": task_data.status,
                "task_result": task_result
            })
        
        return JsonResponse({'results': results}, status=200) 
