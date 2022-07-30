from celery.result import AsyncResult
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

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
        city = request.POST.get('type')
        tasks = run_tasks_to_request_forcasts(city)
        return JsonResponse({"tasks": tasks}, status=202)


@csrf_exempt
def get_forecast_statuses(request):
    if request.POST:
        task_ids = request.POST.get('task_ids').split(',')
        results = []
        for task_id in task_ids:
            task_data = AsyncResult(task_id)

            task_result = task_data.result
            if task_data.status == 'FAILURE':
                # Because error classes are not serializeable, we take only text message of the error 
                task_result = str(task_result)

            results.append({
                "task_id": task_id,
                "task_status": task_data.status,
                "task_result": task_result
            })
        
        return JsonResponse({'results': results}, status=200) 
