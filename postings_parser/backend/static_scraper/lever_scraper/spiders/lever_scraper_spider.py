import hashlib
from datetime import date, datetime, time, timedelta

import scrapy
from scrapy.selector import Selector

from postings_parser.backend.static_scraper.lever_scraper.items import JobItem


class LeverSpider(scrapy.Spider):
    name = "lever_postings"
    allowed_domains = ["jobs.lever.co"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.spider_id = kwargs.pop("spider_id", 3)

    def parse(self, response):
        response_html = response.text
        url = response.request.url
        company_name = url.split(".")[-1].split("/")[-1]
        selector = Selector(text=response_html, type="html")
        postings_groups = selector.xpath('//div[@class="postings-group"]')

        parsed_date, parsed_time = self.get_date_time()

        for i, postings_group in enumerate(postings_groups):
            stratified_selector = Selector(text=postings_group.get(), type="html")
            potential_primary_department = stratified_selector.xpath(
                f"//div[contains(@class, 'large-category-header')]/text()"
            )
            label_department = stratified_selector.xpath(
                f"//div[contains(@class, 'large-category-label')]/text()"
            )

            if i == 0:
                if len(potential_primary_department) == 0:
                    secondary_string = "label"
                    primary_department = label_department.get()
                else:
                    secondary_string = "header"
                    primary_department = potential_primary_department.get()
            if secondary_string == "header":
                if len(potential_primary_department) != 0:
                    primary_department = potential_primary_department.get()
                departments = primary_department + " – " + label_department.get()
            else:
                departments = label_department.get()

            job_openings = stratified_selector.xpath("//a[@class='posting-title']")

            for j, opening in enumerate(job_openings):
                self.logger.info(f"Parsing row {i+1}, {company_name}")
                job_href = opening.xpath("./@href").get()
                job_title = opening.xpath(".//h5/text()").get()
                job_id = self.generate_unique_id(job_title, company_name, job_href)
                workplace_type = opening.xpath(
                    ".//span[contains(@class, 'workplaceTypes')]/text()"
                ).get()
                commitment = opening.xpath(
                    ".//span[contains(@class, 'commitment')]/text()"
                ).get()
                location = opening.xpath(
                    ".//span[contains(@class, 'location')]/text()"
                ).get()
                item = JobItem(
                    job_id=job_id,
                    job_title=job_title,
                    company_name=company_name,
                    work_location=location,
                    workplace_type=workplace_type,
                    parsed_date=parsed_date,
                    parsed_time=parsed_time,
                    job_href=job_href,
                    posting_date=None,
                    commitment=commitment,
                )
                yield item

    def start_requests(self):
        yield scrapy.Request(url=self.url, callback=self.parse)

    def generate_unique_id(self, job_title, company_name, job_href):
        composite_key = f"{job_title}-{company_name}-{job_href}"
        return hashlib.md5(composite_key.encode()).hexdigest()

    def get_date_time(self):
        current_date = date.today()
        current_time = datetime.now().time()
        formatted_date = current_date.strftime("%Y-%m-%d")
        formatted_time = current_time.strftime("%H:%M:%S.%f")
        return (formatted_date, formatted_time)
