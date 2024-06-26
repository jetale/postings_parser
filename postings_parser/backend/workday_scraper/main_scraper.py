import logging
from datetime import date, datetime
from importlib.resources import files

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

from postings_parser.backend.workday_scraper.scrape_postings import PageScraper
from postings_parser.utils.database_connector import Connector


# right now i want to parse all postings. After that we can modify to check for previous posting and then notify only about new ones
class RunBatches:
    def __init__(self)->None:
        self.input_path = files("postings_parser.input").joinpath(
            "urls.txt"
        )  # ('postings_parser', 'input/urls.txt')
        # self.input_path = "input/urls.txt"
        self.logger = logging.getLogger("logger")
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--remote-debugging-pipe")
        chrome_options.experimental_options['prefs'] = {
            'profile.managed_default_content_settings.images': 2
        }
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)  # Adjust the timeout as needed
        self.conn = Connector()
        

        self.scraper = PageScraper(self.driver, self.wait)

    def load_urls(self):
        rows = self.select_query()
        for row in rows:
            url = row[0]
            yield "https://boeing.wd1.myworkdayjobs.com/EXTERNAL_CAREERS/"

    def parse(self, url)->None: 
        postings_list = self.scraper.scrape(url)
        self.insert_query(postings_list)

    def main_executor(self):
        loader = self.load_urls()
        for url in loader:
            self.parse(url)
        
        self.conn.close_all_connections()
        self.driver.quit()


    def close_connection(self)->None:
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def get_date_time(self):
        current_date = date.today()
        current_time = datetime.now().time()
        formatted_date = current_date.strftime("%Y-%m-%d")
        formatted_time = current_time.strftime("%H:%M:%S.%f")
        return (formatted_date, formatted_time)
    
    def insert_query(self, postings_list):
        insert_query = """
                    INSERT INTO postings(job_id,
                                        job_title,
                                        company,
                                        work_location,
                                        posting_date,
                                        posting_url,
                                        parsed_date,
                                        parsed_time )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                    """
        try:
            connection = self.conn.get_conn()
            cursor = connection.cursor()
            cursor.executemany(insert_query, postings_list)
            connection.commit()
        except Exception as e:
            print(f"An error occurred: {e}")
            connection.rollback()
        finally:
            self.conn.release_conn(connection)

    def select_query(self):
        select_query = """
                SELECT url FROM site_urls
                WHERE url_domain='workday';
                """
        try:
            connection = self.conn.get_conn()
            cursor = connection.cursor()
            cursor.execute(select_query)
            rows = cursor.fetchall()
            
        except Exception as e:
            print(f"An error occurred: {e}")
            connection.rollback()
        finally:
            self.conn.release_conn(connection)
        
        if rows:
            return rows
        else:
            raise RuntimeError(f"{select_query} did not return any rows")
     

if __name__ == "__main__":
    main = RunBatches()
    main.main_executor()
