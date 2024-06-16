import csv 
import pickle
from datetime import datetime, date
import pkg_resources
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import uuid

from postings_parser.utils.database_connector import Connector
from postings_parser.backend.scrape_postings import PageScraper



# right now i want to parse all postings. After that we can modify to check for previous posting and then notify only about new ones
class ParsePostings:

    def __init__(self):
        self.input_path = pkg_resources.resource_filename('postings_parser', 'input/urls.txt')
        #self.input_path = "input/urls.txt"
        chrome_options = Options()
        chrome_options.add_argument('--headless')
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
            if ".lever." not in url: # Temporary measure while I sort out the scrapy situation
                postings_list = self.scraper.scrape(url=url)
                self.insert_query(postings_list)
                time.sleep(10)
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
        try:
            self.cursor.executemany(insert_query, postings_list)
            self.connection.commit()
        except Exception as e:
            print(f"An error occurred: {e}")
            self.connection.rollback()

    def parse_postings(self, url):
        posting_dict = {"job_id":"", "job_title":"", "company":"", \
                        "parsed_date":"", "parsed_time":"", "posting_url":""}
        postings_list = []
        company_name = url.split(".")[0].split(":")[1].replace("/","")
        parsed_date, parsed_time = self.get_date_time()
        print(url)
        self.driver.get(url)
        seturl = url
        page = 1
        try:       
            while page < 2:
                # Wait for job elements to load
                self.wait.until(EC.presence_of_element_located((By.XPATH, '//li[@class="css-1q2dra3"]')))
                job_elements = self.driver.find_elements(By.XPATH, '//li[@class="css-1q2dra3"]')

                for job_element in job_elements:
                    job_title_element = job_element.find_element(By.XPATH, './/h3/a')
                    job_id_element = job_element.find_element(By.XPATH, './/ul[@data-automation-id="subtitle"]/li')
                    job_id = job_id_element.text.strip()
                    job_href = job_title_element.get_attribute('href')
                    job_title = job_title_element.text.strip()
                    posted_on_element = job_element.find_element(By.XPATH, './/dd[@class="css-129m7dg"][preceding-sibling::dt[contains(text(),"posted on")]]')
                    posted_on = posted_on_element.text
                    
                    print(posted_on)
                    temp_dict = dict(
                        job_id=job_id, job_title=job_title, \
                        company=company_name, \
                        parsed_date=parsed_date, \
                        parsed_time=parsed_time, \
                        posting_url=job_href
                    )

                    temp_tuple = (
                        job_id, job_title, \
                        company_name, \
                        parsed_date, \
                        parsed_time, \
                        job_href
                    )
                    postings_list.append(temp_tuple)

                print(f"Page {page} - Total jobs parsed from {company_name}")

                # Check if there's a next page button
                next_button = self.driver.find_element(By.XPATH, '//button[@data-uxi-element-id="next"]')
                if "disabled" in next_button.get_attribute("class"):
                    break  # exit loop if the "next" button is disabled
                
                # Click on the next page button
                next_button.click()
                page += 1
                time.sleep(5)  # Adjust this delay as needed for page loading

        except Exception as e:
            print(f"An error occurred while processing {company_name}: {str(e)}")


        return postings_list





if __name__ == "__main__":
    main = ParsePostings()
    main.parse()