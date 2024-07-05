from typing import Any, Generator
from parsel.selector import SelectorList
import scrapy
from scrapy.selector import Selector

from postings_parser.backend.static_scraper.lever_scraper.spiders import BaseSpider
from postings_parser.backend.static_scraper.lever_scraper.items import JobItem


class LeverSpider(BaseSpider):
    name: str= "lever_postings"
    allowed_domains: list[str] = ["jobs.lever.co"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.spider_id = kwargs.pop("spider_id", 3)

    def parse(self, response) -> Generator[Any, Any, None]:
        parsed_date, parsed_time = self.__class__.get_date_time()
        company_name, postings_groups = self.get_data_from_response(response)
        self.logger.info(f"Parsing {company_name}")

        for index, postings_group in enumerate(postings_groups):
            stratified_selector = Selector(text=postings_group.get(), type="html")
            departments = self.get_department(stratified_selector, index)            
            job_openings = stratified_selector.xpath("//a[@class='posting-title']")
            for _, opening in enumerate(job_openings):
                opening_data_tuple = self.parse_posting_info(opening, company_name, parsed_date, parsed_time)
                yield opening_data_tuple

    def get_data_from_response(self, response)-> tuple[Any, SelectorList[Selector]]:
        response_html = response.text
        url = response.request.url
        company_name = url.split(".")[-1].split("/")[-1]
        selector = Selector(text=response_html, type="html")
        postings_groups: SelectorList[Selector] = selector.xpath('//div[@class="postings-group"]')
        return company_name, postings_groups

    def parse_posting_info(self, opening, company_name, parsed_date, parsed_time):
        job_href = opening.xpath("./@href").get()
        job_title = opening.xpath(".//h5/text()").get()
        job_id = self.__class__.generate_unique_id(job_title, company_name, job_href)
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
        return item

    def get_department(self, stratified_selector, index) -> Any:
        potential_primary_department = stratified_selector.xpath(
                f"//div[contains(@class, 'large-category-header')]/text()"
            )
        label_department = stratified_selector.xpath(
            f"//div[contains(@class, 'large-category-label')]/text()"
        )
        if index == 0:
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

        return departments

    def start_requests(self):
        yield scrapy.Request(url=self.url, callback=self.parse)

    
