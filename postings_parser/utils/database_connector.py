import psycopg2
from psycopg2 import pool
import logging
from dotenv import load_dotenv
import os

logger = logging.getLogger("logger")

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
        self.connection_pool = pool.SimpleConnectionPool(
                            minconn=1,
                            maxconn=60,
                            database=self.db_params['dbname'],
                            user=self.db_params['user'],
                            password=self.db_params['password'],
                            host=self.db_params['host'],
                            port=self.db_params['port']
                        )
        
        self._initialized = True


    def get_conn(self):
        return self.connection_pool.getconn()
    
    def release_conn(self, connection):
        return self.connection_pool.putconn(connection)
    
    def connect(self):
        try:
            conn = psycopg2.connect(**self.db_params)
            logger.info("Database connection successful")
        except psycopg2.OperationalError as e:
            print(f"Error: {e}")
            exit(1)

        cur = conn.cursor()
        return conn, cur


