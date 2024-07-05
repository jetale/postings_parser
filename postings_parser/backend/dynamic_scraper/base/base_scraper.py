import hashlib
import logging
from abc import abstractmethod
from datetime import date, datetime


class BaseScraper:
    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait
        self.logger = logging.getLogger("logger")

    @staticmethod
    def get_date_time():
        current_date = date.today()
        current_time = datetime.now().time()
        formatted_date = current_date.strftime("%Y-%m-%d")
        formatted_time = current_time.strftime("%H:%M:%S.%f")
        return (formatted_date, formatted_time)

    @staticmethod
    def generate_unique_id(job_title, company_name, job_href):
        composite_key = f"{job_title}-{company_name}-{job_href}"
        return hashlib.md5(composite_key.encode()).hexdigest()

    @abstractmethod
    def get_posting_date(self):
        pass

    @abstractmethod
    def scrape(self):
        pass

    @abstractmethod
    def get_jobid_and_posted_on(self):
        pass

    @abstractmethod
    def get_location(self):
        pass
