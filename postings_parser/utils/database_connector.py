import psycopg2
from dotenv import load_dotenv
import os


class Connector:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Connector, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialized = False
        return cls._instance
        
    def __init__(self):
        if self._initialized:
            return 
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
        self._initialized = True

    def connect(self):
        try:
            conn = psycopg2.connect(**self.db_params)
            print("Database connection successful")
        except psycopg2.OperationalError as e:
            print(f"Error: {e}")
            exit(1)

        cur = conn.cursor()
        return conn, cur


