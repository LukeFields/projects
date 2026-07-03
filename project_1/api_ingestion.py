import httpx
import pandas as pd
from getcities import GetCityData

cities = ["San Francisco", "Los Angeles", "Weed"]
city_df = GetCityData(cities)


url = "https://archive-api.open-meteo.com/v1/archive"
params = {
	"latitude": city_df["latitude"].tolist(),
	"longitude": city_df["longitude"].tolist(),
	"start_date": "2016-01-01",
	"end_date": "2025-12-31",
	"daily": [
        "temperature_2m_min",
        "temperature_2m_max",
        "temperature_2m_mean",
        "precipitation_sum",
        "precipitation_hours",
        "wind_speed_10m_min",
        "wind_speed_10m_max",
        "wind_speed_10m_mean"
    ],
	"timezone": "America/Los_Angeles",
}


with httpx.Client() as client:
    responses = client.get(url, params=params) # will be cached

locations = []

for response in responses.json():
    print(f"\nCoordinates: {response["latitude"]}°N {response["longitude"]}°E")
    
    daily = response["daily"]

    daily_data = {
        "date": [pd.to_datetime(t, format="ISO8601") for t in daily["time"]],
        "temperature_2m_max": daily["temperature_2m_max"],
        "temperature_2m_min": daily["temperature_2m_min"],
        "temperature_2m_mean": daily["temperature_2m_mean"],
        "precipitation_sum": daily["precipitation_sum"],
        "precipitation_hours": daily["precipitation_hours"],
        "wind_speed_10m_min": daily["wind_speed_10m_min"],
        "wind_speed_10m_max": daily["wind_speed_10m_max"],
        "wind_speed_10m_mean": daily["wind_speed_10m_mean"],
    }

    locations.append(pd.DataFrame(data = daily_data))

for loc in locations:
    print(loc)