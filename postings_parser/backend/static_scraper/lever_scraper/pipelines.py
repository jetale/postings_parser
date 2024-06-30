# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import logging

from postings_parser.utils.database_connector import Connector, ExecutionType


class LeverScraperPipeline:
    def __init__(self):
        self.db_connector = Connector()

        self.logger = logging.getLogger("logger")
        self.hold_items_list = (
            []
        )  # Creating this list here because scrapy spider can only return one item. So will hold them here till all items are returned

    def open_spider(self, spider):
        self.logger.info("Opening Spider: {}".format(spider.name))

    def process_item(self, item, spider):
        self.logger.info(f"Received item with - {item}")
        self.hold_items_list.append(item)

    def convert_to_list(self):
        keys_order = [
            "job_id",
            "job_title",
            "company_name",
            "work_location",
            "workplace_type",
            "parsed_date",
            "parsed_time",
            "job_href",
            "posting_date",
            "commitment",
        ]
        list_ordered = [
            [sub_item[key] for key in keys_order] for sub_item in self.hold_items_list
        ]
        return list_ordered

    def insert_data(self, postings_list):
        self.logger.info("Inserting data into DB")
        insert_query = """
                    INSERT INTO postings_new(job_id,
                                            job_title,
                                            company,
                                            work_location,
                                            workplace_type,
                                            parsed_date,
                                            parsed_time,
                                            posting_url,
                                            posting_date,
                                            commitment )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                    """
        self.db_connector.execute_insert_query(insert_query, postings_list, type_execute=ExecutionType.MANY, new_conn=True)

    def close_spider(self, spider):
        item_list = self.convert_to_list()
        self.insert_data(item_list)
