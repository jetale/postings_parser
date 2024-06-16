
from datetime import datetime, date, timedelta
import time
import uuid

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

import scrapy
from scrapy.crawler import CrawlerRunner
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerProcess
from scrapy.signalmanager import dispatcher
from scrapy import signals

from postings_parser.backend.lever_scraper.spiders.lever_scraper_spider import LeverSpider


class ItemCollector:
    def __init__(self):
        self.items = []

    def collect_item(self, item, response, spider):
        self.items.append(item)

    def clear_items(self):
        self.items = []

class PageScraper:
    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait
        self.collector = ItemCollector()
        

    def scrape(self, url):
        # Add conditions based on url and which scraper to use. Eg. workday, lever etc.
        if "lever" in url:
            postings_list = self.scrape_lever(url)
        else:
            postings_list = self.scrape_workday(url)
        return postings_list
    
    def get_date_time(self):
        current_date = date.today()
        current_time = datetime.now().time()
        formatted_date = current_date.strftime('%Y-%m-%d')
        formatted_time = current_time.strftime('%H:%M:%S.%f')
        return (formatted_date, formatted_time)
    
    def get_posting_date(self, posted_on):
        current_date = date.today()
        ret_val = None

        if "+" in posted_on:
            ret_val = None
        elif "Today" in posted_on:
            ret_val = current_date.strftime('%Y-%m-%d')
        elif "Yesterday" in posted_on:
            one_day_ago = current_date - timedelta(days=1)
            ret_val = one_day_ago.strftime('%Y-%m-%d')
        else:
            try:
                n_days_ago = int(posted_on.split(" ")[1].strip())
                n_days_ago_date = current_date - timedelta(days=n_days_ago)
                ret_val = n_days_ago_date.strftime('%Y-%m-%d')
            except:
                ret_val = None
            
        return ret_val

    def scrape_workday(self,url):
        posting_dict = {"job_id":"", "job_title":"", "company":"", \
                        "parsed_date":"", "parsed_time":"", "posting_url":""}
        postings_list = []
        company_name = url.split(".")[0].split(":")[1].replace("/","")
        parsed_date, parsed_time = self.get_date_time()
        print(url)
        self.driver.get(url)
        seturl = url
        page = 1
        try:       
            while page < 10:
                # Wait for job elements to load
                self.wait.until(EC.presence_of_element_located((By.XPATH, '//li[@class="css-1q2dra3"]')))
                job_elements = self.driver.find_elements(By.XPATH, '//li[@class="css-1q2dra3"]')

                for job_element in job_elements:
                    job_title_element = job_element.find_element(By.XPATH, './/h3/a')
                    job_id_element = job_element.find_element(By.XPATH, './/ul[@data-automation-id="subtitle"]/li')
                    job_id = job_id_element.text.strip()
                    job_href = job_title_element.get_attribute('href')
                    job_title = job_title_element.text.strip()
                    posted_on_element = job_element.find_element(By.XPATH, './/dd[@class="css-129m7dg"][preceding-sibling::dt[contains(text(),"posted on")]]')
                    posted_on = posted_on_element.text
                    
                    posted_on_date = self.get_posting_date(posted_on)
                    #print(posted_on)
                    temp_dict = dict(
                        job_id=job_id, job_title=job_title, \
                        company=company_name, \
                        parsed_date=parsed_date, \
                        parsed_time=parsed_time, \
                        posting_url=job_href
                    )

                    temp_tuple = (
                        job_id, 
                        job_title, 
                        company_name, 
                        parsed_date, 
                        parsed_time, 
                        job_href,
                        posted_on_date
                    )
                    postings_list.append(temp_tuple)

                #print(f"Page {page} - Total jobs parsed from {company_name}")

                try:
                    # Check if there's a next page button
                    next_button = self.driver.find_element(By.XPATH, '//button[@data-uxi-element-id="next"]')
                    if "disabled" in next_button.get_attribute("class"):
                        break  # exit loop if the "next" button is disabled
                    next_button.click()
                except Exception as e:
                    print("Reached at the end of all listings")
                page += 1
                time.sleep(5)  # Adjust this delay as needed for page loading

        except Exception as e:
            print(f"An error occurred while processing {company_name}: {str(e)}")


        return postings_list
    
        
    @defer.inlineCallbacks
    def crawl(self, url):
        self.collector.clear_items()
        dispatcher.connect(self.collector.collect_item, signal=signals.item_scraped)
        runner = CrawlerRunner()
        yield runner.crawl(LeverSpider, url=url)
        reactor.callLater(0, reactor.stop)

    """
    def scrape_lever(self, url):
        dispatcher.connect(collector.collect_item, signal=signals.item_scraped)
        process = CrawlerProcess()
        process.crawl(LeverSpider, url=url)
        process.start()
        return self.convert_to_tuple(collector.items)
    """

    def scrape_lever(self, url):
        deferred = self.crawl(url)
        deferred.addCallback(lambda _: self.convert_to_tuple(self.collector.items))
        reactor.run()  # This will block until crawling is finished
        return deferred.result  # Return the result after the reactor stops
    

    def convert_to_tuple(self, list_of_dicts):
        keys_order = ['job_id', 'job_title', 'company_name',  'parsed_date', 'parsed_time', 'job_href', 'posting_date' ]
        list_of_tuples_ordered = [tuple(d[key] for key in keys_order) for d in list_of_dicts]
        return list_of_tuples_ordered