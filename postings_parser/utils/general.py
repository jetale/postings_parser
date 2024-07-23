import hashlib
from datetime import date, datetime

def generate_unique_id(job_title, company_name, job_href) -> str:
        job_title: str = job_title.strip()
        company_name: str = company_name.strip()
        job_href: str = job_href.strip()
        
        composite_key = f"{job_title}-{company_name}-{job_href}"
        return hashlib.md5(composite_key.encode()).hexdigest()


def get_date_time():
        current_date = date.today()
        current_time = datetime.now().time()
        formatted_date = current_date.strftime("%Y-%m-%d")
        formatted_time = current_time.strftime("%H:%M:%S.%f")
        return (formatted_date, formatted_time)