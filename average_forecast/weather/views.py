from django.views.generic import TemplateView
from django.http import JsonResponse
from weather.tasks import create_task, run_tasks_to_request_forcasts
from django.views.decorators.csrf import csrf_exempt
from celery.result import AsyncResult


class Index(TemplateView):
    template_name = 'weather/index.html'


@csrf_exempt
def get_forecasts_for_city(request):
    if request.POST:
        city = request.POST.get('city')
        task_ids = run_tasks_to_request_forcasts(city)
        return JsonResponse({"task_ids": task_ids}, status=202)


def get_forecast_status(request):
    if request.POST:
        task_ids = request.POST.get('task_ids')
        results = []
        for task_id in task_ids:
            task_result = AsyncResult(task_id)
            results.append = ({
                "task_id": task_id,
                "task_status": task_result.status,
                "task_result": task_result.result
            })
            



###########################################################################
# TRAINING TASKS
###########################################################################

@csrf_exempt
def run_task(request):
    if request.POST:
        task_type = request.POST.get("type")
        task = create_task.delay(int(task_type))
        return JsonResponse({"task_id": task.id}, status=202)

@csrf_exempt
def get_status(request, task_id):
    task_result = AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result
    }
    return JsonResponse(result, status=200)