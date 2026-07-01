import httpx
import pandas as pd
import json

url = "https://archive-api.open-meteo.com/v1/archive"
params = {
    "latitude": [37.47, 34.04, 40.67],
    "longitude": [-122.25, -118.25, -73.94],
    "start_date": "2025-01-01",
    "end_date": "2025-01-01",
    "hourly": ["temperature_2m", "wind_speed_10m", "precipitation"],
    # "temperature_unit": "fahrenheit",
    "wind_speed_unit": "mph",
    "precipitation_unit": "inch",
}

with httpx.Client() as client:
    responses = client.get(url, params=params) # will be cached

hourly = responses.json()[0]["hourly"]
hourly_time = hourly["time"]
hourly_temp = hourly["temperature_2m"]
hourly_wind = hourly["wind_speed_10m"]
hourly_precip = hourly["precipitation"]

for response in responses.json():
    print(f"\nCoordinates: {response["latitude"]}°N {response["longitude"]}°E")
    
    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = response["hourly"]
    hourly_time = hourly["time"]
    hourly_temperature_2m = hourly["temperature_2m"]
    hourly_wind_speed_10m = hourly["wind_speed_10m"]
    hourly_precipitation = hourly["precipitation"]
    
    hourly_data = {
        "time": hourly["time"],
        "temperature_2m": hourly["temperature_2m"],
        "wind_speed_10m": hourly["wind_speed_10m"],
        "precipitation": hourly["precipitation"]
    }

    hourly_dataframe = pd.DataFrame(data = hourly_data)
    print("\nHourly data\n", hourly_dataframe)