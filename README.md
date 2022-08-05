# Emarket
## Table of contents
* [General info](#general-info)
* [Technologies](#technologies)
* [Setup](#setup)

## General info
This application collects current weather data for a requested location from a number of weather forecasters 
for diversity and calculates average numbers.

## Technologies
- Python 3.9
- Django 4.0
- Javascript, jquery
- HTML, css
- Docker-compose

## Setup
1. Install [docker-compose](https://docs.docker.com/compose/install/)
2. ```git clone https://github.com/mi-doc/average_forecast.git && cd average_forecast```
3. ```cat .env.sample >> .env ```
4. Subscribe to the listed weather services on rapidapi site and enter the API TOKEN in the .env file. 
5. ```docker-compose -f docker-compose.prod.yml build```
6. ```docker-compose -f docker-compose.prod.yml up ```