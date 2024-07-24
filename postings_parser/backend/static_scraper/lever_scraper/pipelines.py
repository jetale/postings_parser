# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import logging

from postings_parser.utils.database_connector import Connector, ExecutionType


class LeverScraperPipeline:
    def __init__(self) -> None:
        self.db_connector = Connector()
        self.logger = logging.getLogger("logger")
        # Creating this list here because scrapy spider can only return one item. 
        # So will hold them here till all items are returned
        self.hold_items_list = []

    def open_spider(self, spider) -> None:
        self.logger.info("Opening Spider: {}".format(spider.name))

    def process_item(self, item, spider) -> None:
        self.logger.info(f"Received item with - {item}")
        self.hold_items_list.append(item)

    def convert_to_list(self) -> list[list]:
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

    def insert_data(self, postings_list) -> None:
        self.logger.info("Inserting data into DB")
        insert_query = """
                    SELECT insert_into_posting_new(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                    """
        self.db_connector.execute_insert_query(
            insert_query=insert_query, 
            data=postings_list, 
            type_execute=ExecutionType.MANY,
            new_conn=True
        )

    def close_spider(self, spider) -> None:
        item_list = self.convert_to_list()
        self.insert_data(item_list)



class LeverDeleterPipeline:
    def __init__(self) -> None:
        self.db_connector = Connector()
        self.logger = logging.getLogger("logger")

    def open_spider(self, spider) -> None:
        self.logger.info("Opening Spider: {}".format(spider.name))

    def process_item(self, item, spider) -> None:
        self.logger.info(f"Received item with - {item}")
        if item["removed"]:
            self.delete_marked(item["removed_url"])
        else:
            print(f"Not removing {item['removed_url']}")

    def delete_marked(self, url: str) -> None:
        self.logger.info("Deleting removed postings from DB")
        delete_query = """
                    DELETE FROM postings_new where posting_url=%s;
                    """
        print(url)
        """
        self.db_connector.execute_insert_query(
            insert_query=delete_query, 
            data=self.items_list, 
            type_execute=ExecutionType.MANY, 
            new_conn=True
        )
        """
