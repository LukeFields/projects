import pandas as pd
import pathlib
from api_ingestion import get_weather_data, get_city_data

weather_file = "weather_data.csv"
data_path = pathlib.Path(__file__).parent / "data"

weather_path = pathlib.Path(data_path) / weather_file
weather_path.resolve()

cities = ["San Francisco", "Los Angeles", "Weed"]
city_df = get_weather_data()
weather_df = get_weather_data()

weather_df["observation_date"] = pd.to_datetime(weather_df["observation_date"], format="ISO8601")

print(f"\nShape: {weather_df.shape[0]} rows x {weather_df.shape[1]} columns")
print("\nColumn names")
print(weather_df.columns.tolist())

print("\nFirst 5 rows")
print(weather_df.head())

print("\nLast 5 rows")
print(weather_df.tail())

print("\nData types:")
print(weather_df.dtypes)

print("\nBasic statistics (numeric columns):")
print(weather_df.describe())

print("\nMissing values per column:")
print(weather_df.isnull().sum())

print(f"\nDuplicate rows: {weather_df.duplicated().sum()}")
print(f"\nMissing Values: {weather_df.isnull().sum().sum()}")