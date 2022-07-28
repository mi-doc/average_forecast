from django.db import models


class Source(models.Model):
    name = models.CharField(("Source_name"), max_length=64, blank=True, null=True)
    url = models.URLField(("Source API url"))

    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)
  
    def __str__(self):
        return "Forecast source"


class Place(models.Model):
    name = models.CharField(("Name of place"), max_length=30)
    # coordinates ?
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)


class Weather(models.Model):

    place = models.ForeignKey(Place, on_delete=models.CASCADE)
    source = models.ForeignKey(Source, models.CASCADE)
    date = models.DateTimeField(("Date of forecast"))
    temperature = models.IntegerField(("Air temperature (C)"), blank=True, null=True)
    condition = models.CharField(("Weather condition"), max_length=30, blank=True, null=True)
    wind_direction = models.IntegerField(("Wind direction"), blank=True, null=True)
    wind_speed = models.IntegerField(("Wind speed (m/s)"), blank=True, null=True)
    humidity = models.IntegerField(("Humidity"), blank=True, null=True)
    pressure = models.IntegerField(("Pressure"), blank=True, null=True)

    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return "Weather forecast"
