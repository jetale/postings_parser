import time
import hashlib
import logging
from datetime import date, datetime, timedelta

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class PageScraper:
    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait
        self.logger = logging.getLogger("logger")

    def scrape(self, url):
        # Add conditions based on url and which scraper to use. Eg. workday, lever etc.
        postings_list = self.scrape_workday(url)
        return postings_list

    def get_date_time(self):
        current_date = date.today()
        current_time = datetime.now().time()
        formatted_date = current_date.strftime("%Y-%m-%d")
        formatted_time = current_time.strftime("%H:%M:%S.%f")
        return (formatted_date, formatted_time)

    def get_posting_date(self, posted_on):
        current_date = date.today()
        ret_val = None
        if "+" in posted_on:
            ret_val = None
        elif "Today" in posted_on:
            ret_val = current_date.strftime("%Y-%m-%d")
        elif "Yesterday" in posted_on:
            one_day_ago = current_date - timedelta(days=1)
            ret_val = one_day_ago.strftime("%Y-%m-%d")
        else:
            try:
                n_days_ago = int(posted_on.split(" ")[1].strip())
                n_days_ago_date = current_date - timedelta(days=n_days_ago)
                ret_val = n_days_ago_date.strftime("%Y-%m-%d")
            except:
                ret_val = None
        return ret_val

    def scrape_workday(self, url):
        self.logger.info(url)
        postings_list = []
        company_name = url.split(".")[0].split(":")[1].replace("/", "")
        parsed_date, parsed_time = self.get_date_time()
        self.driver.get(url)
        page = 1
        try:
            while page < 50: # I don't think any website will have more than 50 pages. Keeping it to avoid infinite loop just in case
                # Wait for job elements to load
                self.wait.until(
                    EC.presence_of_element_located(
                        (By.XPATH, '//li[@class="css-1q2dra3"]')
                    )
                )
                job_elements = self.driver.find_elements(
                    By.XPATH, '//li[@class="css-1q2dra3"]'
                )
                for job_element in job_elements:
                    job_title_element = job_element.find_element(By.XPATH, ".//h3/a")
                    job_href = job_title_element.get_attribute("href")
                    job_title = job_title_element.text.strip()
                    location = self.get_location(job_element, job_title)
                    job_id, posted_on = self.get_jobid_and_posted_on(job_element, job_title) 
                    job_id = self.generate_unique_id(job_id, company_name, job_href)
                    posted_on_date = self.get_posting_date(posted_on)
                    temp_tuple = (
                        job_id,
                        job_title,
                        company_name,
                        location,
                        posted_on_date,
                        job_href,
                        parsed_date,
                        parsed_time
                    )
                    postings_list.append(temp_tuple)
                try:
                    next_button = self.driver.find_element(
                        By.XPATH, '//button[@data-uxi-element-id="next"]'
                    )  # Check if there's a next page button
                    if "disabled" in next_button.get_attribute("class"):
                        break  # exit loop if the "next" button is disabled
                    next_button.click()
                except Exception as e:
                    print("Reached at the end of all listings")
                    break
                page += 1
                time.sleep(1)  # delay for page loading
        except Exception as e:
            print(f"An error occurred while processing {company_name}: {str(e)}")

        return postings_list


    def get_jobid_and_posted_on(self, job_element, job_title):
        job_id = "dummy" #setting this to dummy because it is used in calculating hash
        posted_on = None

        try:
            job_id_element = job_element.find_element(
                            By.XPATH, './/ul[@data-automation-id="subtitle"]/li'
                        )
            job_id = job_id_element.text.strip()
        except Exception as e:
            self.logger.warning(e)
            self.logger.warning(f"\n Did not find job_id for {job_title}")
            self.logger.warning(job_element.get_attribute("outerHTML"))
            self.logger.warning(job_element.text)
        try:
            posted_on_element = job_element.find_element(
                By.XPATH,
                './/dd[@class="css-129m7dg"][preceding-sibling::dt[contains(text(),"posted on")]]',
            )
            posted_on = posted_on_element.text
        except Exception as e:
            self.logger.warning(e)
            self.logger.warning(f"\n did not find posted on date for {job_title}")
            self.logger.warning(job_element.get_attribute("outerHTML"))
            self.logger.warning(job_element.text)

        return (job_id, posted_on)
    


    def get_location(self, job_element, job_title):
        location = None
        try:
            location_element = job_element.find_element(
                            By.XPATH,
                            './/dd[@class="css-129m7dg"][preceding-sibling::dt[contains(text(),"locations")]]',
                        )
            location = location_element.text.strip()
        except:
            try:
                location_elements = job_element.find_elements(By.CSS_SELECTOR, 'dt.css-y8qsrx')
                location_string_list = []
                for dt in location_elements:
                    if dt.text.lower() == 'remote type':
                        dd_element = dt.find_element(By.XPATH, 'following-sibling::dd[@class="css-129m7dg"]')
                        location_string_list.append(dd_element.text)
                    elif dt.text.lower() == 'locations':
                        dd_element = dt.find_element(By.XPATH, 'following-sibling::dd[@class="css-129m7dg"]')
                        location_string_list.append(dd_element.text)
                location = "\n".join(location_string_list)
            except Exception as e:
                self.logger.warning(e)
                self.logger.warning(f"\n Did not find any location element for {job_title} ")
                self.logger.warning(job_element.get_attribute("outerHTML"))
                self.logger.warning(job_element.text)
        return location


    def generate_unique_id(self, job_title, company_name, job_href):
        composite_key = f"{job_title}-{company_name}-{job_href}"
        return hashlib.md5(composite_key.encode()).hexdigest()
