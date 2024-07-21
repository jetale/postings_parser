import os
import gzip
import logging
from datetime import datetime

import boto3
from botocore.config import Config
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from postings_parser.analytics.backup_sources import sources
from postings_parser.utils.database_connector import Connector

PROJ_ROOT = os.getenv("PROJ_POSTINGS_PARSER_PATH")
OUT_FILE_PATH = PROJ_ROOT + "/postings_parser/input/"



class DataBackup:
    def __init__(self) -> None:
        client_config = Config(region_name="us-east-2")
        self.s3_connection = boto3.client('s3', config=client_config)
        self.db_connector = Connector()
        self.logger: logging.Logger = logging.getLogger("logger")


    def get_data_from_db(self) -> None:
        """
        -> Gets data for dates which have not been backed up yet
        -> If upbackuped data exists then converts it to df and 
            creates parquet files
        """
        is_backup_req: bool = False
        connection, cursor = self.db_connector.get_single_conn()
        for source in sources:
            query: str = self.get_query(table_name=source.table_name, data_source=source.name)
            cursor.execute(query)
            results = cursor.fetchall()
            if results:
                is_backup_req = True
                column_names: list = [desc[0] for desc in cursor.description]
                results_df: pd.DataFrame = pd.DataFrame(results, columns=column_names)
                source.parquet_table = pa.Table.from_pandas(results_df)
        cursor.close()
        connection.close()

        if is_backup_req:
            self.upload_to_s3()


    def upload_to_s3(self) -> None:
        """
        -> If parquet table was created then assumes we created pq files
        -> Uploads parquet files to s3 in gz format
        """
        date_str: str = datetime.now().strftime('%Y-%m-%d')
        dir_name: str = date_str + "/"
        for source in sources:
            if source.parquet_table:
                self.logger.info(f"-----Uploading {source.parquet_file_name} to s3")
                pq_file_path =  OUT_FILE_PATH + source.parquet_file_name
                s3_dest_path: str = dir_name + source.parquet_file_name + ".gz"
                
                pq.write_table(source.parquet_table, pq_file_path)

                with open(pq_file_path, 'rb') as f_in:
                    with gzip.open(pq_file_path+".gz", 'wb') as f_out:
                        f_out.writelines(f_in)

                self.s3_connection.upload_file(pq_file_path, source.s3_bucket_name, s3_dest_path)
        
        self.delete_pq_files()

    def delete_pq_files(self) -> None:
        """
        -> Deletes files from local after uploading to s3
        """
        for source in sources:
            pq_file_path = OUT_FILE_PATH + source.parquet_file_name
            self.logger.info(f"Deleting {pg_file_path}")
            os.remove(pq_file_path)
            os.remove(pq_file_path+".gz")


    def get_query(self, table_name: str, data_source: str) -> str:
        """
        -> Creates query to fetch new unbackuped data
        -> dynamically adds table_name and data_source
        """
        check_new_date_query: str = \
                            f"""
                            SELECT *
                            FROM {table_name}
                            WHERE parsed_date IN (
                                SELECT DISTINCT parsed_date
                                FROM {table_name}
                                WHERE parsed_date NOT IN (
                                    SELECT DISTINCT date_column
                                    FROM backed_up_dates
                                    WHERE data_source = '{data_source}'
                                )
                            );
                            """
        return check_new_date_query
            

    def process(self) -> None:
        self.get_data_from_db()



if __name__ == "__main__":
    DataBackup().process()