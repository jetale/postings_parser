from postings_parser.backend.dynamic_scraper.main_scraper import RunBatches
from postings_parser.backend.static_scraper.main_lever_scraper import \
    StartSpiders


class Runner:
    def __init__(self):
        pass

    def run_workday(self):
        workday_parser_obj = RunBatches()
        workday_parser_obj.main_executor()

    def run_lever(self):
        lever_parser_obj = StartSpiders()
        lever_parser_obj.start_multiprocess()


if __name__ == "__main__":
    current_runner = Runner()
    current_runner.run_workday()
