import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Initialize Selenium WebDriver (assuming you have configured it properly)
driver = webdriver.Chrome()
wait = WebDriverWait(driver, 10)  # Adjust the timeout as needed

jobs = []

company_urls = ["https://intel.wd1.myworkdayjobs.com/en-US/External"]

job_ids_dict = {url: [] for url in company_urls}

try:
    for company_url in company_urls:
        driver.get(company_url)
        seturl = company_url

        page = 1
        while True:
            # Wait for job elements to load
            wait.until(
                EC.presence_of_element_located((By.XPATH, '//li[@class="css-1q2dra3"]'))
            )

            job_elements = driver.find_elements(By.XPATH, '//li[@class="css-1q2dra3"]')

            for job_element in job_elements:
                job_title_element = job_element.find_element(By.XPATH, ".//h3/a")
                job_id_element = job_element.find_element(
                    By.XPATH, './/ul[@data-automation-id="subtitle"]/li'
                )
                job_id = job_id_element.text.strip()
                job_href = job_title_element.get_attribute("href")
                job_title = job_title_element.text.strip()
                posted_on_element = job_element.find_element(
                    By.XPATH,
                    './/dd[@class="css-129m7dg"][preceding-sibling::dt[contains(text(),"posted on")]]',
                )
                posted_on = posted_on_element.text

                if job_id not in job_ids_dict[company_url]:
                    job_ids_dict[company_url].append(job_id)
                    jobs.append((seturl, job_title, job_href))
                else:
                    print(f"Job ID {job_id} already in job_ids_dict")

            print(
                f"Page {page} - Total jobs parsed from {company_url}: {len(job_ids_dict[company_url])}"
            )

            # Check if there's a next page button
            next_button = driver.find_element(
                By.XPATH, '//button[@data-uxi-element-id="next"]'
            )
            if "disabled" in next_button.get_attribute("class"):
                break  # exit loop if the "next" button is disabled

            # Click on the next page button
            next_button.click()
            page += 1
            time.sleep(2)  # Adjust this delay as needed for page loading

except Exception as e:
    print(f"An error occurred while processing {company_url}: {str(e)}")

finally:
    driver.quit()

# Print all parsed jobs (for demonstration)
for job in jobs:
    print(job)
