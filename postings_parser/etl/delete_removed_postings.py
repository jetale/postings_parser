# get all urls
# visit each url one by one
# see if the job posting exits
# if not mark the row to be deleted
import logging 

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from postings_parser.utils.database_connector import Connector, ExecutionType

logging.basicConfig(level=logging.INFO)

class DeleteRemoved:

    def __init__(self):
        self.logger = logging.getLogger("logger")
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--remote-debugging-pipe")
        chrome_options.experimental_options["prefs"] = {
            "profile.managed_default_content_settings.images": 2
        }
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(driver=self.driver, timeout=20)  # Adjust the timeout as needed
        self.conn = Connector()


    def _delete_marked(self, to_be_deleted: list) -> None:
        delete_query = "DELETE FROM postings WHERE job_id = ANY(%s);"
        self.conn.execute_insert_query(
            insert_query = delete_query, 
            data = to_be_deleted,
            type_execute = ExecutionType.MANY,
            new_conn = True
            )
        self.logger.info(f"Deleted {len(to_be_deleted)} rows successfully")


    def check_if_posting_exists(self, response) -> None:
        to_be_deleted: list = list()
        for index, item in enumerate(response):
            job_id = item[0]
            url = item[1]
            self.driver.get(url)
            try:
                self.wait.until(
                        EC.presence_of_element_located(
                            (By.XPATH, '//div[@class="css-1vosg8"]')
                        )
                    )
            except:
                print(f"timeout for url {url}")
                continue
            element = self.driver.find_element(By.XPATH, '//*[@id="mainContent"]/div/div')
            try:
                data_automation_id = element.get_attribute('data-automation-id')
                if data_automation_id == "errorContainer":
                    to_be_deleted.append(job_id)
            except:
                continue

            if index%1000 == 0:
                self.logger.info(f"{index} out of {len(response)} urls checked")

        if to_be_deleted:
            self.logger.info(f"Deleting {len(to_be_deleted)} rows from postings table" )
            self._delete_marked(to_be_deleted=to_be_deleted)


    def _get_all_urls(self) -> None:
        select_query = """
                    SELECT job_id, posting_url 
                    FROM postings
                    """

        response = self.conn.execute_select_query(query=select_query)
        if response:
            self.check_if_posting_exists(response)


    def run(self) -> None:
        self._get_all_urls()

if __name__ == "__main__":
    DeleteRemoved().run()
