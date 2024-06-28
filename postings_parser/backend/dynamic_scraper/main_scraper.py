import logging
from importlib.resources import files

from tqdm import tqdm 

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

from postings_parser.backend.dynamic_scraper.workday.workday_scraper import WorkdayScraper
from postings_parser.utils.database_connector import Connector, ExecutionType


# right now i want to parse all postings. After that we can modify to check for previous posting and then notify only about new ones
class RunBatches:
    def __init__(self)->None:
        self.input_path = files("postings_parser.input").joinpath(
            "input_urls.txt"
        )  
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
        self.scraper = WorkdayScraper(self.driver, self.wait)

    def load_urls_from_file(self):
        urls = []
        with open (self.input_path, "r") as f:
            for url in f:
                urls.append(url)
        return urls

    def load_urls_from_db(self):
        rows = self.select_query()
        urls = []
        for row in rows:
            urls.append(row[0])
        return urls

    def parse(self, url)->None: 
        postings_list = self.scraper.scrape(url)
        self.insert_rows(postings_list)

    def main_executor(self):
        urls = self.load_urls_from_file()
        for url in tqdm(urls, "Scraping Progress"):
            self.parse(url)
        self.conn.close_all_connections()
        self.driver.quit()

    def insert_rows(self, data):
        insert_query = """
                    INSERT INTO postings(job_id,
                                        job_title,
                                        company,
                                        work_location,
                                        posting_date,
                                        posting_url,
                                        parsed_date,
                                        parsed_time )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (job_id) DO NOTHING;
                    """
        self.conn.execute_insert_query(insert_query, data, type_execute=ExecutionType.MANY)

    def select_query(self):
        select_query = """
                SELECT url FROM site_urls
                WHERE url_domain='workday';
                """
        rows = self.conn.execute_select_query(select_query)
        if rows:
            return rows
        else:
            raise RuntimeError(f"{select_query} did not return any rows")
     

if __name__ == "__main__":
    main = RunBatches()
    main.main_executor()
