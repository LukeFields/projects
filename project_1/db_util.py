import os
from dotenv import load_dotenv
import psycopg

load_dotenv()

def get_conn_params() -> str:
    """
    returns string with db connection info
        DB_HOST
        DB_NAME
        DB_USER
        DB_PASSWORD
        DB_PORT
    """
    valid = bool(
        os.environ.get('DB_HOST') and
        os.environ.get('DB_NAME') and
        os.environ.get('DB_USER') and
        os.environ.get('DB_PASSWORD') and
        os.environ.get('DB_PORT')
    )

    if not valid:
        raise EnvironmentError("one or more .env variables missing")
    
    return (
        f"host={os.environ.get('DB_HOST')} "
        f"dbname={os.environ.get('DB_NAME')} "
        f"user={os.environ.get('DB_USER')} "
        f"password={os.environ.get('DB_PASSWORD')} "
        f"port={os.environ.get('DB_PORT')}"
    )

def del_schema():
    with psycopg.connect(get_conn_params()) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                DROP SCHEMA IF EXISTS weather_proj_lf CASCADE;
                """
            )


def init_db():
    with psycopg.connect(get_conn_params()) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE SCHEMA IF NOT EXISTS weather_proj_lf;

                CREATE TABLE IF NOT EXISTS city (
                    city_id INT PRIMARY KEY,
                    city_name VARCHAR(32) UNIQUE NOT NULL,
                    lat NUMERIC NOT NULL,
                    long NUMERIC NOT NULL
                );

                CREATE TABLE IF NOT EXISTS observations (
                    observation_id INT PRIMARY KEY,
                    city_id INT NOT NULL,
                    observation_date DATE NOT NULL,
                    temp_2m_min NUMERIC(3,1),
                    temp_2m_max NUMERIC(3,1),
                    temp_2m_mean NUMERIC(3,1),
                    precip_sum NUMERIC(5,1),
                    precip_hours NUMERIC(3,1),
                    windspeed_min NUMERIC(4,1),
                    windspeed_max NUMERIC(4,1),
                    windspeed_mean NUMERIC(4,1),
                    CONSTRAINT city_id_fk FOREIGN KEY (city_id) REFERENCES weather_proj_lf.city(city_id)
                );
                """
            )

if __name__ == "__main__":
    print(get_conn_params())

    init_db()