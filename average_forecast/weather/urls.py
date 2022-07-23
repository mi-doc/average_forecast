from django.urls import path

from . import views

app_name = 'weather'

urlpatterns = [
    path('index/', views.Index.as_view()),
]