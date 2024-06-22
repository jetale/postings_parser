import time
from datetime import date, datetime, timedelta

import scrapy
from scrapy.selector import Selector

from postings_parser.backend.lever_scraper.lever_scraper.items import JobItem


class WorkdaySpider(scrapy.Spider):
    name = "workday_spider"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.spider_id = kwargs.pop("spider_id", 3)
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.html_source = kwargs.pop("html_source", "default_source")
        self.company_name = kwargs.pop("company_name", "default_company")
        self.run_hash = kwargs.pop("run_hash", "default_run_hash")
        self.full_s3_html_path = kwargs.pop("full_s3_html_path", "default_path")
        self.existing_html_used = kwargs.pop("existing_html_used", False)
        self.logger.info(f"Initialized Spider, {self.html_source}")

    def parse(self, response):
        response_html = response.text
        url = response.request.url
        company_name = url.split(".")[-1].split("/")[-1]
        parsed_date, parsed_time = self.get_date_time()
        selector = Selector(text=response_html, type="html")
        job_elements = selector.xpath('//li[@class="css-1q2dra3"]')
        self.logger.info(job_elements)
        self.logger.info(response_html)

        for job_element in job_elements:
            job_title_element = job_element.xpath(".//h3/a")
            job_id_element = job_element.xpath(
                './/ul[@data-automation-id="subtitle"]/li'
            )
            job_id = job_id_element.xpath("text()").get().strip()
            job_href = job_title_element.xpath("@href").get()
            job_title = job_title_element.xpath("text()").get().strip()
            posted_on_element = job_element.xpath(
                './/dd[@class="css-129m7dg"][preceding-sibling::dt[contains(text(),"posted on")]]'
            )
            posted_on = posted_on_element.xpath("text()").get()

            posted_on_date = self.get_posting_date(posted_on)

            item = JobItem(
                job_id=None,
                job_title=job_title,
                company_name=company_name,
                parsed_date=parsed_date,
                parsed_time=parsed_time,
                job_href=job_href,
                posting_date=posted_on_date,
            )
            self.logger.info(item)
            yield item
        time.sleep(5)

        try:  # Check if there's a next page button
            next_button = response.xpath('//button[@data-uxi-element-id="next"]')
            if next_button and "disabled" not in next_button.xpath("@class").get():
                next_page_url = response.urljoin(next_button.xpath("@href").get())
                self.logger.info(f"Next Page URL - {next_page_url}")
                yield scrapy.Request(next_page_url, callback=self.parse)
            else:
                self.logger.info("Reached the end of all listings")
        except:
            print("Reached at the end of all listings")

    def start_requests(self):
        yield scrapy.Request(url=self.url, callback=self.parse)

    def get_date_time(self):
        current_date = date.today()
        current_time = datetime.now().time()
        formatted_date = current_date.strftime("%Y-%m-%d")
        formatted_time = current_time.strftime("%H:%M:%S.%f")
        return (formatted_date, formatted_time)

    def get_posting_date(self, posted_on):
        current_date = date.today()
        ret_val = None

        if "+" in posted_on:
            ret_val = None
        elif "Today" in posted_on:
            ret_val = current_date.strftime("%Y-%m-%d")
        elif "Yesterday" in posted_on:
            one_day_ago = current_date - timedelta(days=1)
            ret_val = one_day_ago.strftime("%Y-%m-%d")
        else:
            try:
                n_days_ago = int(posted_on.split(" ")[1].strip())
                n_days_ago_date = current_date - timedelta(days=n_days_ago)
                ret_val = n_days_ago_date.strftime("%Y-%m-%d")
            except:
                ret_val = None

        return ret_val
