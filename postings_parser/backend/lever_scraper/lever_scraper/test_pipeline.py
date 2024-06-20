from scrapy.utils.project import get_project_settings
from pipelines import LeverScraperPipeline

if __name__ == "__main__":
    setting = get_project_settings()
    item_pipelines = setting.get('ITEM_PIPELINES')
    print(vars(item_pipelines))
    exit()
    pipeline = LeverScraperPipeline()
    
    test_item = {
        'job_id': '1',
        'job_title': 'Test Job',
        'company_name': 'Test Company',
        'parsed_date': '2024-06-16',
        'parsed_time': '00:50:39.134950',
        'job_href': 'http://example.com/job',
        'posting_date': '2024-06-16'
    }

    pipeline.process_item(test_item, None)
    pipeline.close_spider(None)
