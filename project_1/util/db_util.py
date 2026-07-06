import os
from dotenv import load_dotenv
import psycopg
from psycopg import sql
from pathlib import Path

load_dotenv()
root = Path(__file__).parent.parent

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
    """delete the schema and all content"""
    with psycopg.connect(get_conn_params()) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                DROP SCHEMA IF EXISTS weather_proj_lf CASCADE;
                """
            )


def init_db():
    schema_file = Path(root) / "sql/create_schema.sql"
    schema_file.resolve()

    with open(schema_file, "r") as f:
        query = sql.SQL(f.read())

    with psycopg.connect(get_conn_params()) as conn:
        with conn.cursor() as cur:
            cur.execute(query)

if __name__ == "__main__":
    # init_db()
    
    # del_schema()
    pass