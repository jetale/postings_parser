import logging
import multiprocessing
import time
import argparse
from enum import Enum

import pkg_resources
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from postings_parser.backend.static_scraper.lever_scraper.spiders.lever_scraper_spider import \
    LeverSpider
from postings_parser.backend.static_scraper.lever_scraper.spiders.lever_deleter_spider import \
    LeverDeleterSpider
from postings_parser.backend.static_scraper.lever_scraper.spiders.workday_deleter_spider import \
    WorkdayDeleterSpider
from postings_parser.utils.database_connector import Connector


class ActionType(Enum):
    SCRAPER = "scraper"
    LEVER_DELETER = "ldeleter"
    WORKDAY_DELETER = "wdeleter"


class ScraperAction:
    def __init__(self) -> None:
        self.spider = LeverSpider
        self.query: str = """
                    SELECT url FROM site_urls
                    WHERE url_domain='lever';
                    """
        self.sleep_time: int = 20


class LeverDeleterAction:
    def __init__(self) -> None:
        self.spider = LeverDeleterSpider
        self.query: str = """
                    SELECT posting_url FROM postings_new
                    """
        self.sleep_time: int = 10

class WorkdayDeleterAction:
    def __init__(self) -> None:
        self.spider = WorkdayDeleterSpider
        self.query: str = """
                    SELECT posting_url FROM postings
                    """
        self.sleep_time: int = 20

class ScraperSpiders:
    def __init__(self, action) -> None:
        self.url_file_path = pkg_resources.resource_filename(
            "postings_parser", "input/cleaned_lever_urls.txt"
        )
        self.action = action
        self.logger = logging.getLogger("logger")
        self.connector = Connector()
        self.spider = action.spider
        
    def start_multiprocess(self):
        process = []
        url_batches = self.get_url_batches_from_db()
        total_batches = len(url_batches)
        for index, batch in enumerate(url_batches):
            time.sleep(self.action.sleep_time)
            self.logger.info(f"Starting process for batch {index} of {total_batches}")
            p = multiprocessing.Process(target=self.run_spiders, args=(batch,))
            process.append(p)
            p.start()

        for p in process:
            p.join()

        # close all connections
        self.connector.close_all_connections()

    def run_spiders(self, url_batch: list):
        spider_process = CrawlerProcess(get_project_settings())
        for url in url_batch:
            self.logger.info(f"Starting process for {url}")
            spider_process.crawl(self.spider, url=url)
        spider_process.start()

    def get_url_batches_from_file(self):
        main_list = []
        batch_list = []
        with open(self.url_file_path, "r") as input_f:
            for line in input_f:
                line = line.strip()
                batch_list.append(line)
                if len(batch_list) == 50:
                    main_list.append(batch_list)
                    batch_list = []
        return main_list

    def get_url_batches_from_db(self):
        rows = self.execute_select_query()
        main_list = []
        batch_list = []
        for line in rows:
            line = line[0].strip()
            batch_list.append(line)
            if len(batch_list) == 50:
                main_list.append(batch_list)
                batch_list = []
        return main_list

    def execute_select_query(self):
        select_query = self.action.query
        rows = self.connector.execute_select_query(query=select_query)
        if rows:
            return rows
        else:
            raise RuntimeError(f"{select_query} did not return any rows")




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run scrapy scraper or deleter')
    parser.add_argument('--action_type', type=str, help="Run either scraper or deleter. Enter 'deleter' or 'scraper'")
    args = parser.parse_args()
    action_type = ActionType(args.action_type)

    if action_type == ActionType.SCRAPER:
        action_obj = ScraperAction()
    elif action_type == ActionType.LEVER_DELETER:
        action_obj = LeverDeleterAction()
    elif action_type == ActionType.WORKDAY_DELETER:
        action_obj = WorkdayDeleterAction()

    ScraperSpiders(action=action_obj).start_multiprocess()
    

