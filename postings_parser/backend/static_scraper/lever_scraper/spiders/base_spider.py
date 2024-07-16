import hashlib
from abc import abstractmethod
from datetime import date, datetime

import scrapy


class BaseSpider(scrapy.Spider):
    @abstractmethod
    def parse(self):
        pass

    @abstractmethod
    def start_requests(self):
        pass

    @staticmethod
    def generate_unique_id(job_title, company_name, job_href):
        composite_key = f"{job_title}-{company_name}-{job_href}"
        return hashlib.md5(composite_key.encode()).hexdigest()

    @staticmethod
    def get_date_time():
        current_date = date.today()
        current_time = datetime.now().time()
        formatted_date = current_date.strftime("%Y-%m-%d")
        formatted_time = current_time.strftime("%H:%M:%S.%f")
        return (formatted_date, formatted_time)
