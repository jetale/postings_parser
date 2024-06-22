import os

import psycopg2
from dotenv import load_dotenv
from psycopg2 import sql


class Connector:
    def __init__(self):
        load_dotenv()
        self.db_params = {
            "dbname": os.getenv("PGDATABASE"),
            "user": os.getenv("PGUSER"),
            "password": os.getenv("PGPASSWORD"),
            "host": os.getenv("PGHOST"),
            "port": os.getenv("PGPORT", 5432),
        }

    def connect(self):
        try:
            conn = psycopg2.connect(**self.db_params)
            print("Database connection successful")
        except psycopg2.OperationalError as e:
            print(f"Error: {e}")
            exit(1)

        # Create a cursor object
        cur = conn.cursor()
        return conn, cur


if __name__ == "__main__":
    cr = Connector()
    print(cr.connect())
