from re import T
from telnetlib import Telnet
from django.db import models


class Weather(models.Model):

    date = models.DateTimeField(_("Date of forecast"))
    temperature = models.IntegerField(_("Air temperature (C)"), max=99, blank=True, null=True)
    condition = models.CharField(_("Weather condition"), max_length=30, blank=True, null=True)
    wind_direction = models.IntegerField(_("Wind direction"), max=360, min=0, blank=True, null=True)
    wind_speed = models.IntegerField(_("Wind speed"), max=999, min=0, blank=True, null=True)
    humidity = models.IntegerField(_("Humidity"), max=999, min=0, blank=True, null=True)
    pressure = models.IntegerField(_("Pressure"), max=999, min=0, blank=True, null=True)

    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "Weather forecast"

class Source(models.Model):
    name = models.CharField(_("Source_name"), max_length=64, blank=True, null=True)
    url = models.URLField(_("Source API url"))

    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)
  
    def __str__(self):
        return "Forecast source"