from typing import Any, Generator

import scrapy
from parsel.selector import SelectorList
from scrapy.selector import Selector

from postings_parser.backend.static_scraper.lever_scraper.items import DeleteItem
from postings_parser.backend.static_scraper.lever_scraper.spiders.base_spider import \
    BaseSpider


class LeverDeleterSpider(BaseSpider):
    name: str = "lever_deleter"
    allowed_domains: list[str] = ["jobs.lever.co"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.spider_id = kwargs.pop("spider_id", 3)

    def parse(self, response):
        response_html = response.text
        url = response.request.url
        result_tuple: tuple[bool, str] = (False, url )
        selector = Selector(text=response_html, type="html")
        try:
            error: SelectorList[Selector] = selector.xpath(
                '//body[@class="404"]'
            )
            if error:
                # ---- Mark for deletion
                result_tuple[0] = True
        except:
            # -------- Posting still exists do nothing -------
            self.logger.info(f"Posting still exists for job {url}")

        yield DeleteItem(
            removed = result_tuple[0],
            removed_url = result_tuple[1]
        )



    def start_requests(self):
        yield scrapy.Request(url=self.url, callback=self.parse)
