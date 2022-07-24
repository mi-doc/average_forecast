import aiohttp
import asyncio
import time

OPEN_WEATHER_MAP_API_KEY = 'fcccdcec54mshd8de1f4afd9c04cp1bd53fjsn8fbc05589296'


async def get_open_weather_map(session, city='Moscow'):
    url = "https://community-open-weather-map.p.rapidapi.com/forecast"
    querystring = {"q": city, "units": "metric"}
    headers = {
        "X-RapidAPI-Key": OPEN_WEATHER_MAP_API_KEY,
        "X-RapidAPI-Host": "community-open-weather-map.p.rapidapi.com",
    }

    async with session.get(url, headers=headers, params=querystring) as res:
        data = await res.json()
        return data

async def get_yahoo_weather(session, city="Moscow"):
    url = "https://yahoo-weather5.p.rapidapi.com/weather"

    querystring = {"location": city, "format":"json","u":"c"}

    headers = {
        "X-RapidAPI-Key": OPEN_WEATHER_MAP_API_KEY,
        "X-RapidAPI-Host": "yahoo-weather5.p.rapidapi.com"
    }

    async with session.get(url, headers=headers, params=querystring) as res:
        raw_data = await res.json()
        current_weather = {
            'source': 'yahoo_weather',
            'temp': raw_data['current_observation']['condition']['temperature'],
            'condition': raw_data['current_observation']['condition']['text'],
            'wind_direction': raw_data['current_observation']['wind']['direction'],
            'wind_speed': raw_data['current_observation']['wind']['speed'],
            'humidity': raw_data['current_observation']['atmosphere']['humidity'],
            'pressure': raw_data['current_observation']['atmosphere']['pressure']            
        }
        return current_weather

async def main():
    starting_time = time.time()

    async with aiohttp.ClientSession() as session:
        actions = [
            # asyncio.ensure_future(get_open_weather_map(session))
            asyncio.ensure_future(get_yahoo_weather(session))
        ]

        res = await asyncio.gather(*actions)

    total_time = time.time() - starting_time

    print(res, total_time, sep='\n')


if __name__ == '__main__':
    print('Starting')
    asyncio.run(main())