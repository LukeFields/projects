import pandas as pd
import psycopg
from db_util import get_conn_params

class WeatherDAO:
    def __init__(self):
        self.connect_string = get_conn_params()

    