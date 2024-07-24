import json
import logging
from datetime import datetime
from dataclasses import dataclass, fields, field
from typing import Tuple, List, Optional

import boto3
from tqdm import tqdm
from botocore.config import Config
from bs4 import BeautifulSoup as bs

from postings_parser.utils.general import generate_unique_id
from postings_parser.utils.database_connector import Connector, ExecutionType


@dataclass
class PostingData:
    job_id: str = field(default=str())
    job_title: str = field(default=str())
    company: str = field(default=str())
    work_location: str = field(default=str())
    posting_url: str = field(default=str())
    posting_date: str = field(default=str())
    parsed_date: str = field(default=str())
    parsed_time: str = field(default='12:00:00')
    job_description: str = field(default=str())
    country: str = field(default=str())
    is_remote: str = field(default=str())

    def to_tuple(self) -> Tuple[str, ...]:
        return tuple(getattr(self, field.name) for field in fields(self))

    def get_column_names(self) -> Tuple[str, ...]:
        return tuple(field.name for field in fields(self))
    

class MainDataLoader:
    def __init__(self) -> None:
        self.logger: logging.Logger = logging.getLogger("logger")
        
        self.bucket_name: str = "selenium-job-postings"
        self.base_path: str = "postings/"
        self.date_dir: str = str()
        self.parsed_date: str = str()
        self.posting_data_list: list = list()

        client_config = Config(region_name="us-east-2")
        self.s3_connector = boto3.client('s3', config=client_config)
        self.db_connector = Connector()


    def _insert_into_db(self) -> None:
        insert_query = """
                    INSERT INTO postings (
                        job_id, job_title, company, work_location, posting_url, 
                        posting_date, parsed_date, parsed_time, job_description, country, is_remote
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (job_id) DO UPDATE SET
                        posting_date = EXCLUDED.posting_date,
                        job_description = EXCLUDED.job_description,
                        country = EXCLUDED.country,
                        is_remote = EXCLUDED.is_remote,
                        posting_url = EXCLUDED.posting_url;
                """
        self.db_connector.execute_insert_query(
            insert_query=insert_query,
            data=self.posting_data_list, 
            type_execute=ExecutionType.MANY,
            new_conn=True)

    def _extract_script_elements(
            self, 
            url,
            company_name,
            job_title_tag,
            job_description_tag,
            script_element
            ) -> None:
        
        posting = PostingData()
        json_content = script_element.string
        data: dict = json.loads(json_content)

        posting.job_title = job_title_tag.get('content')
        posting.company = company_name
        posting.job_description = job_description_tag.get('content')
        posting.country = data.get('jobLocation', {}).get('address', {}).get('addressCountry', 'All')
        posting.work_location = data.get('jobLocation', {}).get('address', {}).get('addressLocality', 'All')
        posting.is_remote = data.get('jobLocationType', None)
        posting.posting_date = data.get('datePosted', None)
        posting.parsed_date = self.parsed_date
        posting.posting_url = url
        #employment_type = data.get('employmentType', None)
        #req_id = data.get('identifier', {}).get('value', None)
        posting.job_id = generate_unique_id(
            job_title=posting.job_title, 
            company_name=company_name,
            job_href=url)
        
        self.posting_data_list.append(posting.to_tuple())


    def _extract_posting_info(self, company_name: str, url: str, posting_html: str):
        soup = bs(posting_html, 'html.parser')
        job_title_tag = soup.find('meta', {'name': 'title', 'property': 'og:title'})
        job_description_tag = soup.find('meta', {'name':'description', 'property':'og:description'})
        script_tag = soup.find('script', type='application/ld+json')

        if script_tag and job_title_tag and job_description_tag:
            self._extract_script_elements(
                url=url,
                company_name=company_name,
                job_title_tag=job_title_tag,
                job_description_tag=job_description_tag,
                script_element=script_tag
                ) 
           

    def _parse_object(self, file_obj: dict) -> None:
        file_content = file_obj['Body'].read()
        file_content_dict = json.loads(file_content.decode('utf-8'))
        company_name =  list(file_content_dict.keys())[0]
        for key, val in file_content_dict[company_name].items():
            self._extract_posting_info(
                company_name=company_name, 
                url=key, 
                posting_html=val)
  

    def _get_objects(self, objects: list) -> None:
        for obj in tqdm(objects, "Parsing Objects"):
            file_obj = self.s3_connector.get_object(Bucket=self.bucket_name, Key=obj)
            self._parse_object(file_obj) 
        self._insert_into_db()

    def _get_objects_list(self, date_dir: str) -> None:
        prefix: str = self.base_path + date_dir + "/" 
        paginator = self.s3_connector.get_paginator('list_objects_v2')
        page_iterator = paginator.paginate(Bucket=self.bucket_name, Prefix=prefix)
        
        objects: list = []
        for page in page_iterator:
            if 'Contents' in page:
                for obj in page['Contents']:
                    objects.append(obj['Key'])
        
        if objects:
            self._get_objects(objects)
        else:
            self.logger.error(f"Latest date directory does not contain any objects. {date_dir}  Exiting ---")


    def _list_date_directories(self) -> list:
        paginator = self.s3_connector.get_paginator('list_objects_v2')
        page_iterator = paginator.paginate(Bucket=self.bucket_name, Prefix=self.base_path, Delimiter='/')
        
        date_directories: list = []
        for page in page_iterator:
            if 'CommonPrefixes' in page:
                for cp in page['CommonPrefixes']:
                    date_directories.append(cp['Prefix'].split('/')[-2])
        
        return date_directories
    
    def _get_latest_date_directory(self)-> None:
        date_directories: list = self._list_date_directories()
        date_directories.sort(reverse=True, key=lambda date: datetime.strptime(date, '%Y-%m-%d'))

        if date_directories:
            self.parsed_date = date_directories[0]
            self._get_objects_list(date_directories[0])
        else:
            self.logger.error("Could not get any date directories-- Exiting")

    
    def main(self):
        self._get_latest_date_directory()

if __name__ == "__main__":
    MainDataLoader().main()
