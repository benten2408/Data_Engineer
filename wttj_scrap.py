import time
import pandas as pd
from joblib import Parallel, delayed
from tqdm import tqdm

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.webdriver import WebDriver

from datastruct import Company, JobOffer


def get_page_links(driver: WebDriver, wttj_url: str, links: list):
    """
    This function will scrape the wttj_url to retrieve the URLs of all jobs,
    then add them to the list of links

    Args:
        driver (WebDriver): selenium driver
        wttj_url (str): url of Welcome to the jungle "data engineer" jobs
        links (list): list that contains all job links
    """

    driver.get(wttj_url)
    time.sleep(5)
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, ".ais-Hits-list-item")
            )
        )
        job_offers = driver.find_elements(By.CSS_SELECTOR, ".ais-Hits-list-item")

        for job in job_offers:
            try:
                link = job.find_element(By.TAG_NAME, "a").get_attribute("href")
                links.append(link)
            except NoSuchElementException:
                print("Failed to find link for one of the job offers.")

        WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, ".ais-Hits-list-item")
            )
        )

    except TimeoutException:
        print(f"Timed out waiting for job offers to load on {wttj_url}")


def get_all_page_links(url: str, nb_pages: int):
    driver = webdriver.Chrome()

    links = []
    for i in range(1, nb_pages + 1):
        wttj_url = f"{url}&page={i}"

        get_page_links(driver, wttj_url, links)

    return links


class JobScraper:
    def __init__(self, url):
        self.driver = webdriver.Chrome()
        self.url = url
        self.company = Company()
        self.job_offer = JobOffer()
        self.job_offer.url_direct_offer = url

    def scrap_company_info(self):
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "div.sc-dQEtJz.kiMwlt")
            )
        )

        company_elements = self.driver.find_elements(
            By.CSS_SELECTOR, "div.sc-dQEtJz.kiMwlt"
        )

        if company_elements:
            self.company.sector = company_elements[0].text
            self.company.employees = company_elements[1].text
            self.company.creation_year = company_elements[2].text.replace(
                "Créée en ", ""
            )

            for element in company_elements[3:]:
                information = element.text
                if "Chiffre d'affaires" in information:
                    self.company.turnover = information.replace(
                        "Chiffre d'affaires : ", ""
                    ).strip()
                elif "Âge moyen" in information:
                    self.company.mean_age = information.replace(
                        "Âge moyen :", ""
                    ).strip()
        else:
            print("Company informations not found.")

        return self.company

    def get_description(self, section_id):
        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, f"[data-testid={section_id}]")
                )
            )

            view_more_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "[data-testid='view-more-btn']")
                )
            )

            self.driver.execute_script("arguments[0].click();", view_more_btn)

            description = self.driver.find_element(
                By.CSS_SELECTOR, f"[data-testid='{section_id}']"
            ).text

            return description
        except Exception as e:
            return None

    def get_publication_date(self):
        try:

            WebDriverWait(self.driver, 5).until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, "p.sc-ERObt.cvpaYF")
                )
            )

            datetime_value = self.driver.find_element(
                By.TAG_NAME, "time"
            ).get_attribute("datetime")
            return datetime_value[:10]
        except:
            return None

    def scrap_job_offer_info(self):
        self.job_offer.publication_date = self.get_publication_date()

        self.job_offer.title = self.driver.find_element(
            By.CSS_SELECTOR, "h2.sc-ERObt.fMYXdq.wui-text"
        ).text

        self.company.name = self.driver.find_element(
            By.CSS_SELECTOR, "span.sc-ERObt.kkLHbJ.wui-text"
        ).text

        self.job_offer.company = vars(self.company)

        WebDriverWait(self.driver, 5).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "div.sc-dQEtJz.iIerXh")
            )
        )

        job_elements = self.driver.find_elements(
            By.CSS_SELECTOR, "div.sc-dQEtJz.iIerXh"
        )

        if job_elements:

            self.job_offer.contract_type = job_elements[0].text
            self.job_offer.location = (
                job_elements[1].text if "Salaire" not in job_elements[1].text else None
            )
            self.job_offer.description = self.get_description("job-section-description")
            self.job_offer.profil_experience = self.get_description(
                "job-section-experience"
            )

            for element in job_elements[1:]:
                information = element.text
                if "Salaire" in information:
                    self.job_offer.salary = information.replace("Salaire :\n", "")
                elif "Télétravail" in information:
                    self.job_offer.remote_type = information
                elif "Début" in information:
                    self.job_offer.starting_date = information.replace(
                        "Début :", ""
                    ).strip()
                elif "Expérience" in information:
                    self.job_offer.require_experience = information.replace(
                        "Expérience :", ""
                    ).strip()
                elif "Éducation" in information:
                    self.job_offer.education = information.replace(
                        "Éducation :", ""
                    ).strip()

        else:
            print("Job informations not found.")

        return self.job_offer

    def driver_get(self):
        self.driver.get(self.url)

    def scrape_job_details(self):
        self.driver.get(self.url)

        try:
            self.scrap_company_info()
            self.scrap_job_offer_info()

        except Exception as e:
            print(f"Error occurred: {e}")
        finally:
            self.driver.close()

        return self.job_offer


def scrape_job(link):
    scraper = JobScraper(link)
    job_details = scraper.scrape_job_details()
    return vars(job_details)


if __name__ == "__main__":
    # wttj_url = "https://www.welcometothejungle.com/fr/jobs?refinementList%5Boffices.country_code%5D%5B%5D=FR&query=%22data%20engineer%22"

    # links = get_all_page_links(url=wttj_url, nb_pages=11)

    links = pd.read_csv("output/jobs_links_wttj.csv")["link"].to_list()

    job_offers = Parallel(n_jobs=4)(
        delayed(scrape_job)(link)
        for link in tqdm(links[:1], desc="Scraping job offers")
    )

    df_jobs = pd.DataFrame(job_offers)
    df_jobs["source"] = "wttj"

    df_jobs.to_csv("output/job_offers_wttj.csv", index=False, encoding="utf-8-sig")
