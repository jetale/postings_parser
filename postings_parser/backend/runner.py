

from postings_parser.backend.workday_scraper.main_scraper import ParsePostings



class Runner:
    def __init__(self):
        pass

    def run_workday(self):
        workday_parser_obj = ParsePostings()
        workday_parser_obj.parse()



if __name__ == "__main__":
    Runner()