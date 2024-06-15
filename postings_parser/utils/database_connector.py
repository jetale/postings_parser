import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os




class Connector:
    def __init__(self):
        load_dotenv()
        print(os.getenv("DB_PASSWORD"))
        self.db_params = {
                            'dbname': 'postgres',
                            'user': 'dev',
                            'password': os.getenv('DB_PASSWORD'),
                            'host': 'localhost',  # e.g., 'localhost' or '127.0.0.1'
                            'port': '5432'  # e.g., '5432'
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