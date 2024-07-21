import logging

import boto3
from botocore.config import Config



class BotoConnector:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(BotoConnector, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, ) -> None:
        if self._initialized:
            return 
        self.logger = logging.getLogger("logger")
        client_config = Config(region_name="us-east-2")
        self.s3_connection = boto3.client('s3', config=client_config)

        self._initialized = True



    def upload_to_s3(self, local_file_path: str, s3_bucket_name: str, s3_dest_path: str)-> None:
        try:
            self.s3_connection.upload_file(local_file_path, s3_bucket_name, s3_dest_path)
        except Exception as e:
            self.logger.info(f"An Error occured while uploading file to s3 bucket in upload_to_s3 {e}")


    def upload_json_to_s3(self, json_data: str, bucket_name:str, s3_dest_path: str )-> None:
        self.s3_connection.put_object(Bucket=bucket_name, Key=s3_dest_path, Body=json_data, ContentType='application/json')
