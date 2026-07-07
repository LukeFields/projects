import pandas as pd
import psycopg
from pathlib import Path
from util.api_ingestion import get_weather_data, get_city_data
from dao.city_dao import CityDAO
from dao.weather_dao import WeatherDAO
from util.db_util import init_db

weather_file = "weather_data.csv"
data_path = Path(__file__).parent / "data"

weather_path = Path(data_path) / weather_file
weather_path.resolve()

cities = ["San Francisco", "Los Angeles", "Weed"]
city_df = get_city_data(cities)
weather_df = get_weather_data()
city_dao = CityDAO()
weather_dao = WeatherDAO()

weather_df["observation_date"] = pd.to_datetime(weather_df["observation_date"], format="ISO8601")

# data integrity
print(f"\nShape: {weather_df.shape[0]} rows x {weather_df.shape[1]} columns")
print("\nColumn names")
print(weather_df.columns.tolist())

print("\nhead/tail basic structure")
print(weather_df.head())
print(weather_df.tail())

print("\nData types:")
print(weather_df.dtypes)

print("\nBasic statistics (numeric columns):")
print(weather_df.describe())

print("\nMissing values per column:")
print(weather_df.isnull().sum())

print(f"\nDuplicate rows: {weather_df.duplicated().sum()}")
print(f"\nMissing Values: {weather_df.isnull().sum().sum()}")

# db setup
init_db()
try:
    city_dao.dump_to_db(city_df.itertuples(index=False))
except psycopg.errors.UniqueViolation as e:
    print(f"city already exists {e}")
try:
    weather_dao.dump_to_db(weather_df.itertuples(index=False))
except psycopg.errors.UniqueViolation as e:
    print(f"observation already exists {e}")