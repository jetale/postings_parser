
import time
import pkg_resources
import multiprocessing
from scrapy.crawler import CrawlerProcess

from postings_parser.backend.lever_scraper.lever_scraper.spiders.lever_scraper_spider import LeverSpider




def main():
    url_file_path =  pkg_resources.resource_filename('postings_parser', 'input/urls.txt')
    url_batches = get_url_batches(url_file_path=url_file_path)





def start_multiprocess(url_batches):
    process = []
    for index, batch in enumerate(url_batches):
        time.sleep(30)
        p = multiprocessing.Process(target=run_spiders, args=(batch))
        process.append(p)
        p.start()

    for p in process:
        time.sleep(30)
        p.join()



def run_spiders(url_batch):
    spider_process = CrawlerProcess()
    for url in url_batch:
        if "lever" in url: # This is for sanity check only. All urls should be for lever.co only
            spider_process.crawl(LeverSpider)

    spider_process.start()




def get_url_batches(url_file_path):
    main_list = []
    batch_list = []
    with open(url_file_path, "r") as input_f:
        for line in input_f:
            line = line.strip()
            batch_list.append(line)
            if len(batch_list) == 6:
                main_list.append(batch_list)
                batch_list = []

    return main_list








if __name__ == "__main__":
    main()