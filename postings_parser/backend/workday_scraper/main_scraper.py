import csv 
import pickle
from datetime import datetime, date
from importlib.resources import files
import time
import sys

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import uuid

from postings_parser.utils.database_connector import Connector
from postings_parser.backend.workday_scraper.scrape_postings import PageScraper



# right now i want to parse all postings. After that we can modify to check for previous posting and then notify only about new ones
class ParsePostings:

    def __init__(self):
        self.input_path = files('postings_parser.input').joinpath('urls.txt')  #('postings_parser', 'input/urls.txt')
        #self.input_path = "input/urls.txt"
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--remote-debugging-pipe')
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)  # Adjust the timeout as needed

        conn = Connector()
        self.connection, self.cursor = conn.connect()

        self.scraper = PageScraper(self.driver, self.wait)


    
    def load_url(self):
        with open(self.input_path, "r") as input_f:
            for line in input_f:
                line = line.strip()
                yield line


    def parse(self):

        loader = self.load_url()
        for url in loader:
            # Temporary measure while I sort out the scrapy situation
            postings_list = self.scraper.scrape(url=url)
            self.insert_query(postings_list)
            time.sleep(2)
            #print(postings_list)
            #exit()

        self.close_connection()
        self.driver.quit()
    
    def close_connection(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def get_date_time(self):
        current_date = date.today()
        current_time = datetime.now().time()
        formatted_date = current_date.strftime('%Y-%m-%d')
        formatted_time = current_time.strftime('%H:%M:%S.%f')
        return (formatted_date, formatted_time)


    def insert_query(self, postings_list):
        insert_query = \
                    """
                    INSERT INTO postings(job_id,  
                                        job_title,       
                                        company,         
                                        parsed_date,     
                                        parsed_time,     
                                        posting_url,
                                        posting_date )
                    VALUES (%s, %s, %s, %s, %s, %s, %s);
                    """
        print(postings_list)
        try:
            self.cursor.executemany(insert_query, postings_list)
            self.connection.commit()
        except Exception as e:
            print(f"An error occurred: {e}")
            self.connection.rollback()

   




if __name__ == "__main__":
    main = ParsePostings()
    main.parse()