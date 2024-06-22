import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


# right now i want to parse all postings. After that we can modify to check for previous posting and then notify only about new ones
class ParsePostings:
    def __init__(self):
        self.input_path = "input/urls.txt"

    def load_url(self):
        with open(self.input_path, "r") as input_f:
            for line in input_f:
                line = line.strip()
                yield line

    def parse(self):

        loader = self.load_url()
        for url in loader:
            print(url)


if __name__ == "__main__":
    main = ParsePostings()
    main.parse()
