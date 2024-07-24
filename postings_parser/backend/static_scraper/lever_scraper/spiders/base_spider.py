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
    def get_date_time() -> tuple[str, str]:
        current_date = date.today()
        current_time = datetime.now().time()
        formatted_date: str = current_date.strftime("%Y-%m-%d")
        formatted_time: str = current_time.strftime("%H:%M:%S.%f")
        return (formatted_date, formatted_time)
