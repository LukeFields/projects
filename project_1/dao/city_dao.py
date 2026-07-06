import psycopg
from psycopg.rows import dict_row
from util.db_util import get_conn_params

class CityDAO:
    def __init__(self):
        self.conn_string = get_conn_params()
        self.insert_statement = """
                                    INSERT INTO weather_proj_lf.city
                                    VALUES (%s, %s, %s, %s)
                                """

    def dump_to_db(self, rec_list):
        with psycopg.connect(self.conn_string) as conn:
            with conn.cursor() as cur:
                cur.executemany(self.insert_statement, rec_list)