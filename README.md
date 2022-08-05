# Emarket
## Table of contents
* [General info](#general-info)
* [Technologies](#technologies)
* [Active weather forecasters](#weather-forecasters)
* [Setup](#setup)

## General info
This application collects current weather data for a requested location from a number of weather forecasters (for diversity) and calculates average numbers.

## Technologies
- Python 3.9
- Django 4.0
- Celery, Redis
- Geocoder (service to find a place by keyword)
- Javascript, jquery
- HTML, css
- Docker-compose

## Weather forecasters
These are weather services used in the app. Max request limit for free tier in brackets.
- Yahoo weather (1000 per month, 10 per minute)
- Accu weather  (50 per day)
- WeatherApi (1,000,000 per month)
- Aeris weather (100 per day)
- WeatherBit (100 per day)
- Visual crossing weather (500 per month)

More popular weahter services like yandex, gismeteo and other don't provide free access for 
their APIs that can be used in an app like this.

## Setup
1. Install [docker-compose](https://docs.docker.com/compose/install/)
2. ```git clone https://github.com/mi-doc/average_forecast.git && cd average_forecast```
3. ```cat .env.sample >> .env ```
4. Subscribe to the listed weather services on rapidapi site and enter the API TOKEN in the .env file. 
5. ```docker-compose -f docker-compose.prod.yml up ```