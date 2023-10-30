from cabeceras import *
import aiohttp
import asyncio
import os  # Import the os module

API_KEY = os.environ.get("API_KEY")
BASE_URL = "http://dev.virtualearth.net/REST/v1/Locations"

async def geocode_address_bing_async(session, address):
    try:
        params = {
            "q": address,
            "key": API_KEY
        }
        async with session.get(BASE_URL, params=params) as response:
            data = await response.json()

            if data.get('resourceSets') and data['resourceSets'][0].get('resources'):
                resource = data['resourceSets'][0]['resources'][0]
                coordinates = resource['point']['coordinates']
                return coordinates[0], coordinates[1]
            else:
                return None, None
    except Exception as e:
        print(f"Error geocoding address: {e}")
        return None, None

async def geocode_dataframe_addresses(df):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for index, row in df.iterrows():

            tipo_via = row[LUGAR_HECHO_TIPO_VIA]
            via = row[LUGAR_HECHO_VIA]
            municipio = row[LUGAR_HECHO_MUNICIPIO]
            provincia = row[LUGAR_HECHO_PROVINCIA]

            address = f"{tipo_via} {via}, {municipio}, {provincia}"
            tasks.append(geocode_address_bing_async(session, address))
        geocoded_results = await asyncio.gather(*tasks)
        return geocoded_results
