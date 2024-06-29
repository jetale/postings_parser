import logging
import multiprocessing
import time

import pkg_resources
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from postings_parser.backend.static_scraper.lever_scraper.spiders.lever_scraper_spider import \
    LeverSpider
from postings_parser.utils.database_connector import Connector


class StartSpiders:
    def __init__(self):
        self.url_file_path = pkg_resources.resource_filename(
            "postings_parser", "input/cleaned_lever_urls.txt"
        )
        self.logger = logging.getLogger("logger")
        self.url_batches = self.get_url_batches()
        self.connector = Connector()

    def start_multiprocess(self):
        process = []
        total_batches = len(self.get_url_batches())
        for index, batch in enumerate(self.url_batches):
            time.sleep(20)
            print(f"Starting process for batch {index} of {total_batches}")
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
            if (
                "lever" in url
            ):  # This is for sanity check only. All urls should be for lever.co only
                spider_process.crawl(LeverSpider, url=url)
        spider_process.start()

    def get_url_batches(self):
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
        select_query = """
                SELECT url FROM site_urls
                WHERE url_domain='lever';
                """
        rows = self.conn.execute_select_query(select_query)
        if rows:
            return rows
        else:
            raise RuntimeError(f"{select_query} did not return any rows")


if __name__ == "__main__":
    lever_parser_obj = StartSpiders()
    lever_parser_obj.start_multiprocess()
