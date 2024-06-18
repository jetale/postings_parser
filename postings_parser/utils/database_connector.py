import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os


class Connector:
    def __init__(self):
        load_dotenv()
        """
        self.db_params = {
                            'dbname': 'postgres',
                            'user': 'dev',
                            'password': 'abcd', #os.getenv('DB_PASSWORD'),
                            'host': 'host.docker.internal',  # e.g., 'localhost' or '127.0.0.1','host.docker.internal'
                            'port': '5432'  # e.g., '5432'
                        }
        """
        self.db_params = {
                            'dbname':  os.getenv('PGDATABASE'),
                            'user': os.getenv('PGUSER'),
                            'password': os.getenv('PGPASSWORD'),
                            'host': os.getenv('PGHOST'),
                            'port': os.getenv('PGPORT', 5432),
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
