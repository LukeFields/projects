import psycopg
from util.db_util import get_conn_params
from pathlib import Path
from psycopg import sql

root = Path(__file__).parent.parent

class WeatherDAO:
    def __init__(self):
        self.schema_file = Path(root) / "sql/weather_insert.sql"
        self.schema_file.resolve()
        self.conn_string = get_conn_params()


    def dump_to_db(self, rec_list):
        with open(self.schema_file, "r") as f:
            query = sql.SQL(f.read())
            
        with psycopg.connect(self.conn_string) as conn:
            with conn.cursor() as cur:
                cur.executemany(query, rec_list)