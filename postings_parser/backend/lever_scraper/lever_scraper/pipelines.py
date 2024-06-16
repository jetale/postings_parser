# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

from postings_parser.utils.database_connector import Connector


class LeverScraperPipeline:

    def __init__(self):
        db_connector = Connector()
        self.connection, self.cursor = db_connector.connect()

    def process_item(self, item, spider):
        item_list = self.convert_to_list(item)
        self.insert_data(item_list)
        return item

    
    def convert_to_list(self, item):
        keys_order = ['job_id', 'job_title', 'company_name',  'parsed_date', 'parsed_time', 'job_href', 'posting_date' ]
        list_ordered = [item[key] for key in keys_order]
        return list_ordered
    

    def insert_data(self, postings_list):
        insert_query = \
                    """
                    INSERT INTO postings(job_id,  
                                        job_title,       
                                        company,         
                                        parsed_date,     
                                        parsed_time,     
                                        posting_url,
                                        posting_date )
                    VALUES (%s, %s, %s, %s, %s, %s, %s);
                    """
        try:
            self.cursor.execute(insert_query, postings_list)
            self.connection.commit()
        except Exception as e:
            print(f"An error occurred: {e}")
            self.connection.rollback()
        
    def close_spider(self, spider):
        self.cursor.close()
        self.connection.close()
