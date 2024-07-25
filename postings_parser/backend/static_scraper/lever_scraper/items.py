# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class JobItem(scrapy.Item):
    job_title = scrapy.Field()
    work_location = scrapy.Field()
    workplace_type = scrapy.Field()
    company_name = scrapy.Field()
    parsed_date = scrapy.Field()
    parsed_time = scrapy.Field()
    job_href = scrapy.Field()
    posting_date = scrapy.Field()
    commitment = scrapy.Field()


class DeleteItem(scrapy.Item):
    removed = scrapy.Field()
    removed_url = scrapy.Field()