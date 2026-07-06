import httpx
import pandas as pd
import pathlib

city_file = "city_data.csv"
weather_file = "weather_data.csv"
data_path = pathlib.Path(__file__).parent.parent / "data"

def get_city_data(cities) -> pd.DataFrame:

    city_path = pathlib.Path(data_path) / city_file
    city_path.resolve()

    if city_path.is_file():
        try:
            print(f'city data found in {city_file}, reading from local storage')
            df = pd.read_csv(city_path)
            return df
        except Exception as e:
            raise e
    
    url = "https://geocoding-api.open-meteo.com/v1/search"
    
    params = {
        "name": "",
        "count": 10,
        "countryCode": "US"
    }

    responses = []
    with httpx.Client() as client:
        for city in cities:
            params["name"] = city
            r = client.get(url, params=params)
            responses.append(r)

    city_data = {
        "city_name":[],
        "latitude":[],
        "longitude":[]
    }

    for response in responses:
        for entry in response.json()["results"]:
            if entry["admin1"].lower() == "California".lower():
                city_data["city_name"].append(entry["name"])
                city_data["latitude"].append(entry["latitude"])
                city_data["longitude"].append(entry["longitude"])

    df = pd.DataFrame(data=city_data)
    df.rename_axis('city_id', inplace=True)
    df.reset_index(inplace=True)
    df.to_csv(city_path, index=False)

    return df

def get_weather_data():

    weather_path = pathlib.Path(data_path) / weather_file
    weather_path.resolve()

    if weather_path.is_file():
        try:
            print(f'weather data found in {weather_file}, reading from local storage')
            df = pd.read_csv(weather_path)
            return df
        except Exception as e:
            raise e
        
    cities = ["San Francisco", "Los Angeles", "Weed"]
    try:
        city_df = get_city_data(cities)
    except Exception as e:
        raise e

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
        responses = client.get(url, params=params)

    daily_data = {
        "city_id": [],
        "observation_date": [],
        "temperature_2m_min": [],
        "temperature_2m_max": [],
        "temperature_2m_mean": [],
        "precipitation_sum": [],
        "precipitation_hours": [],
        "wind_speed_10m_min": [],
        "wind_speed_10m_max": [],
        "wind_speed_10m_mean": [],
    }

    for idx, response in enumerate(responses.json()):
        daily = response["daily"]

        daily_data["city_id"] += [idx]*len(daily["time"])
        daily_data["observation_date"] += daily["time"]
        daily_data["temperature_2m_max"] += daily["temperature_2m_max"]
        daily_data["temperature_2m_min"] += daily["temperature_2m_min"]
        daily_data["temperature_2m_mean"] += daily["temperature_2m_mean"]
        daily_data["precipitation_sum"] += daily["precipitation_sum"]
        daily_data["precipitation_hours"] += daily["precipitation_hours"]
        daily_data["wind_speed_10m_min"] += daily["wind_speed_10m_min"]
        daily_data["wind_speed_10m_max"] += daily["wind_speed_10m_max"]
        daily_data["wind_speed_10m_mean"] += daily["wind_speed_10m_mean"]

    df = pd.DataFrame(data = daily_data)
    df.rename_axis('observation_id', inplace=True)
    df.reset_index(inplace=True)
    df.to_csv(weather_path, index=False)

    return df

if __name__ == '__main__':
    cities = ["San Francisco", "Los Angeles", "Weed"]
    # print(get_city_data(cities))

    print(get_weather_data())