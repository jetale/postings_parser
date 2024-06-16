import scrapy

class JobItem(scrapy.Item):
    job_id = scrapy.Field()
    job_title = scrapy.Field()
    company_name = scrapy.Field()
    parsed_date = scrapy.Field()
    parsed_time = scrapy.Field()
    job_href = scrapy.Field()
    posting_date = scrapy.Field()  # Add any additional fields as needed
