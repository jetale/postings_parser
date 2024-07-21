from typing import Optional
from dataclasses import dataclass, field

import pyarrow as pa


@dataclass
class DataSource:
    name: str
    table_name: str
    parquet_file_name: str
    s3_bucket_name: str

    # ---------- Value assigned later in execution
    is_backup_req: bool = field(default=False)
    dates_to_backup: list = field(default_factory=list)
    parquet_table: Optional[pa.Table] = field(default=None)




sources: list[DataSource] = [
    DataSource(
        name="selenium",
        table_name="postings",
        parquet_file_name="selenium.parquet",
        s3_bucket_name="selenium-job-postings"
    ),
    DataSource(
        name="scrapy",
        table_name="postings_new",
        parquet_file_name="scrapy.parquet",
        s3_bucket_name="scrapy-job-postings"
    )
]
