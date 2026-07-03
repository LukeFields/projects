import httpx
import pandas as pd
import pathlib

path = pathlib.Path(__file__).parent / "data/cities.csv"
path.resolve()

def GetCityData(cities) -> pd.DataFrame:
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
        "name":[],
        "latitude":[],
        "longitude":[]
    }

    for response in responses:
        for entry in response.json()["results"]:
            if entry["admin1"].lower() == "California".lower():
                city_data["name"].append(entry["name"])
                city_data["latitude"].append(entry["latitude"])
                city_data["longitude"].append(entry["longitude"])

    df = pd.DataFrame(data=city_data)
    df.to_csv(path)
    return df