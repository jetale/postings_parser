import time
from typing import Any
from datetime import date, timedelta

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException


from postings_parser.backend.dynamic_scraper.base.base_scraper import \
    BaseScraper


class WorkdayScraper(BaseScraper):
    def __init__(self, driver, wait):
        super().__init__(driver, wait)
        self.pages_to_scrape = 50

    def only_get_pages(self, url)-> tuple[Any | str, dict]:
        postings_urls_list: list = []
        html_pages_dict: dict = dict()
        return_dict: dict = dict()

        company_name: str = url.split(".")[0].split(":")[1].replace("/", "")
        
        ## ----------- get links to individual job postings ------------------
        self.driver.get(url)
        page: int = 1
        
        while (page < self.pages_to_scrape):
            
            try:
                job_elements = self.wait.until(
                    EC.presence_of_element_located(
                        (By.XPATH, '//li[@class="css-1q2dra3"]')
                    )
                )
            except Exception as e:
                print(f"An error occurred while getting job elements for {company_name} on page->{page}: {str(e)}")
                break

            for job_element in job_elements:
                try:
                    job_title_element = self.wait.until(
                        EC.presence_of_element_located(
                            (By.XPATH, ".//h3/a")
                        )
                    )
                    job_href = job_title_element.get_attribute("href")
                    posted_on_element = job_element.find_element(
                                            By.XPATH,
                                            './/dd[@class="css-129m7dg"][preceding-sibling::dt[contains(text(),"posted on")]]',
                                            )
                    posted_on = posted_on_element.text
                except (StaleElementReferenceException, TimeoutException) as e:
                    self.logger.warning(f"An error occurred while finding job_title or job_href on page->{page}: {e}")
                    continue
                except Exception as e:
                    self.logger.error(f"An unexpected error occurred on page->{page}: {e}")
                    continue
                if "Today" not in posted_on:
                    # ---------- Old postings EXIT ------- #
                    break
                postings_urls_list.append(job_href)
            
            next_btn_prsd: bool = self.click_next_button()
            if not next_btn_prsd:
                self.logger.info("Reached at the end of all listings")
                break
            page += 1
        
        # ---------- get html for individual postings -----------
        for p_url in postings_urls_list:
            self.driver.get(p_url)
            html = self.driver.page_source
            html_pages_dict[p_url] = html
        
        return_dict[company_name] = html_pages_dict

        return company_name, return_dict




    def scrape(self, url):
        """
        This is the main scraper. 
        It loads the page and finds job_elemements
        Then gets all info for a job_element in a tuple
        Appends it and clicks next_page if exists
        """
        self.logger.info(url)
        postings_list = []
        company_name = url.split(".")[0].split(":")[1].replace("/", "")
        parsed_date, parsed_time = BaseScraper.get_date_time()
        self.driver.get(url)
        page = 1
        try:
            while (
                page < self.pages_to_scrape
            ):  # I don't think any website will have more than 50 pages
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
                    is_today, info_tuple = self.extract_info_from_posting(
                        job_element=job_element,
                        company_name=company_name,
                        parsed_date=parsed_date,
                        parsed_time=parsed_time,
                    )
                    postings_list.append(info_tuple)
                    if not is_today:
                        self.logger.info("Finished scraping new postings")
                        break
                next_btn_prsd = self.click_next_button()
                if not next_btn_prsd:
                    self.logger.info("Reached at the end of all listings")
                    break
                page += 1
                time.sleep(1)  # delay for page loading
        except Exception as e:
            print(f"An error occurred while processing {company_name}: {str(e)}")
        return postings_list

    def get_posting_date(self, posted_on):
        current_date = date.today()
        is_today = False
        ret_val = None
        if "+" in posted_on:
            ret_val = None
        elif "Today" in posted_on:
            ret_val = current_date.strftime("%Y-%m-%d")
            is_today = True
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
        return (is_today, ret_val)

    def extract_info_from_posting(
        self, job_element, company_name, parsed_date, parsed_time
    ):
        job_title_element = job_element.find_element(By.XPATH, ".//h3/a")
        job_href = job_title_element.get_attribute("href")
        job_title = job_title_element.text.strip()
        location = self.get_location(job_element, job_title)
        job_id, posted_on = self.get_jobid_and_posted_on(job_element, job_title)
        job_id = BaseScraper.generate_unique_id(job_id, company_name, job_href)
        is_today, posted_on_date = self.get_posting_date(posted_on)
        temp_tuple = (
            job_id,
            job_title,
            company_name,
            location,
            posted_on_date,
            job_href,
            parsed_date,
            parsed_time,
        )
        return (is_today, temp_tuple)

    def get_jobid_and_posted_on(self, job_element, job_title):
        job_id = (
            "dummy"  # not setting it to None because it is used in calculating hash
        )
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
                location_elements = job_element.find_elements(
                    By.CSS_SELECTOR, "dt.css-y8qsrx"
                )
                location_string_list = []
                for dt in location_elements:
                    if dt.text.lower() == "remote type":
                        dd_element = dt.find_element(
                            By.XPATH, 'following-sibling::dd[@class="css-129m7dg"]'
                        )
                        location_string_list.append(dd_element.text)
                    elif dt.text.lower() == "locations":
                        dd_element = dt.find_element(
                            By.XPATH, 'following-sibling::dd[@class="css-129m7dg"]'
                        )
                        location_string_list.append(dd_element.text)
                location = "\n".join(location_string_list)
            except Exception as e:
                self.logger.warning(e)
                self.logger.warning(
                    f"\n Did not find any location element for {job_title} "
                )
                self.logger.warning(job_element.get_attribute("outerHTML"))
                self.logger.warning(job_element.text)
        return location

    def click_next_button(self):
        button_pressed = False
        try:
            next_button = self.driver.find_element(
                By.XPATH, '//button[@data-uxi-element-id="next"]'
            )  # Check if there's a next page button
            if not "disabled" in next_button.get_attribute("class"):
                button_pressed = True  # Do not exit loop if the "next" button is disabled
                next_button.click()
        except Exception as e:
            print("Reached at the end of all listings")

        return button_pressed
