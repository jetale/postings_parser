import logging
import json
import argparse
from importlib.resources import files

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from tqdm import tqdm

from postings_parser.backend.dynamic_scraper.workday.workday_scraper import \
    WorkdayScraper
from postings_parser.utils.database_connector import Connector, ExecutionType

# right now i want to parse all postings. After that we can modify to check for previous posting and then notify only about new ones
class RunBatches:
    def __init__(self) -> None:
        self.input_path = files("postings_parser.input").joinpath("input_urls.txt")
        self.logger = logging.getLogger("logger")
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--remote-debugging-pipe")
        chrome_options.experimental_options["prefs"] = {
            "profile.managed_default_content_settings.images": 2
        }
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(driver=self.driver, timeout=20)  # Adjust the timeout as needed
        self.conn = Connector()
        self.scraper = WorkdayScraper(self.driver, self.wait)

    def load_urls_from_file(self):
        urls = []
        with open(self.input_path, "r") as f:
            for url in f:
                urls.append(url)
        return urls

    def load_urls_from_db(self):
        rows = self.get_urls()
        urls = []
        for row in rows:
            urls.append(row[0])
        return urls
    
    def get_pages(self, url: str, date_parse: str, s3_bucket_name: str, only_html: bool)-> None:
        """
        Only gets page's html and uploads json to s3
        """
        company_name: str
        postings_pages_dict: dict
        company_name, postings_pages_dict = self.scraper.scrape(url=url, only_html=only_html)

        if company_name and  postings_pages_dict:
            json_data: str = json.dumps(postings_pages_dict)
            s3_dest_path: str = "postings"+ "/" + date_parse + "/" + company_name + ".json"
            self.boto_conn.upload_json_to_s3(json_data=json_data, bucket_name=s3_bucket_name, s3_dest_path=s3_dest_path)


    def parse(self, url: str, only_html: bool)-> None:
        """
        Gets page using selenium -> parses it and returns row to be inserted in db
        """
        postings_list = self.scraper.scrape(url=url, only_html=only_html)
        self.insert_rows(postings_list)


    def main_executor(self, s3_bucket_name=None, date_parse=None, only_html=False,) -> None:
        #urls: list = self.load_urls_from_file()
        urls: list = self.load_urls_from_db()
        for url in tqdm(urls, "Scraping Progress"):
            if only_html:
                from postings_parser.utils.boto_connector import BotoConnector
                self.boto_conn = BotoConnector()
                self.get_pages(url=url, date_parse=date_parse, s3_bucket_name=s3_bucket_name, only_html=only_html)
            else:
                self.parse(url=url, only_html=only_html)
        self.conn.close_all_connections()
        self.driver.quit()

    def insert_rows(self, data):
        insert_query = """
                    SELECT insert_into_posting(
                        %s, %s, %s, %s, %s, %s, %s, %s
                    );
                    """
        self.conn.execute_insert_query(
            insert_query, data, type_execute=ExecutionType.MANY, new_conn=True
        )

    def get_urls(self):
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
    parser = argparse.ArgumentParser(description='Run the dynamic parser using selenium')
    parser.add_argument('--s3_bucket_name', type=str, help='Name of the S3 bucket')
    parser.add_argument('--date_parse', type=str, help='Date of parsing')
    parser.add_argument('--only_html', type=lambda x: x.lower() == 'true', help='Get only html pages or full parsing', required=True)

    args = parser.parse_args()

    main = RunBatches()
    main.main_executor(s3_bucket_name=args.s3_bucket_name, date_parse=args.date_parse, only_html=args.only_html)
