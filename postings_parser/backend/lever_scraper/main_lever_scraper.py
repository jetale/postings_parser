import time
import logging
import pkg_resources
import multiprocessing
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from postings_parser.backend.lever_scraper.lever_scraper.spiders.lever_scraper_spider import LeverSpider
#from postings_parser.backend.lever_scraper.lever_scraper.spiders.workday_spider import WorkdaySpider


class StartSpiders:

    def __init__(self):
        self.url_file_path = pkg_resources.resource_filename('postings_parser', 'input/cleaned_lever_urls.txt')
        self.logger = logging.getLogger("logger")
        self.url_batches = self.get_url_batches()


    def start_multiprocess(self):
        process = []
        for index, batch in enumerate(self.url_batches):
            time.sleep(30)
            p = multiprocessing.Process(target=self.run_spiders, args=(batch,))
            process.append(p)
            p.start()

        for p in process:
            time.sleep(30)
            p.join()



    def run_spiders(self, url_batch:list):
        spider_process = CrawlerProcess(get_project_settings())
        for url in url_batch:
            self.logger.info(f"Starting process for {url}")
            if "lever" in url: # This is for sanity check only. All urls should be for lever.co only
                spider_process.crawl(LeverSpider, url=url)
        spider_process.start()




    def get_url_batches(self):
        main_list = []
        batch_list = []
        with open(self.url_file_path, "r") as input_f:
            for line in input_f:
                line = line.strip()
                batch_list.append(line)
                if len(batch_list) == 6:
                    main_list.append(batch_list)
                    batch_list = []
        #return [['https://jobs.lever.co/rover']]
        return main_list


if __name__ == "__main__":
    lever_parser_obj = StartSpiders()
    lever_parser_obj.start_multiprocess()