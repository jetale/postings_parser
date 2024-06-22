from postings_parser.backend.lever_scraper.main_lever_scraper import \
    StartSpiders
from postings_parser.backend.workday_scraper.main_scraper import ParsePostings


class Runner:
    def __init__(self):
        self.run_workday()

    def run_workday(self):
        workday_parser_obj = ParsePostings()
        workday_parser_obj.parse()

    def run_lever(self):
        lever_parser_obj = StartSpiders()
        lever_parser_obj.start_multiprocess()


if __name__ == "__main__":
    Runner()
