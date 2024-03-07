#!/usr/bin/env python3
"""
This script allows the user to access the Adzuna API to search for jobs offers.
The resulting jobs offers are individually classified into JobOffer class.
The list collecting these objects is transformed into a pandas DataFrame.
The output file is a comma separated value file (.csv) saved in an output
directory accessible in the same directory as this script.

This script requires that httpx, pandas, requests and tqdm modules be installed
within the Python environment you are running this script in.

A few environment variables are instantiated as parameters
for the query on job offers. For security, the API_ID and API_KEY are set in 
a .env file found at the root of the directory.

This file can also be imported as a module and contains the following
functions:

    * create_url - strings together search parameters to create functionnal url
    * scrape_url - get requests from Adzuna API for each url passed
    * combing_each_offer - iterates over each offer found on each page
    * main - the main function of the script
"""

from decouple import config
from httpx import HTTPError
import pandas as pd
import requests
from tqdm import tqdm

from datastruct import Company, JobOffer

COUNTRY = "fr"
API_ID = config("API_ID")
API_KEY = config("API_KEY")
RESULTS_PER_PAGE = str(25)
PAGE_SCRAPED = 100
QUERY_PARAMETERS = "&title_only="
KEYWORDS = "data%20engineer"
MAX_OLD_DAYS = str(30)


def create_url():
    """
    Strings together search parameters to create functionnal url

    Parameters
    ----------
    None

    Returns
    -------
    url_list : list
        a list of the API Adzuna urls ready to be requested
    """
    url_list = []
    for page_number in range(1, PAGE_SCRAPED):
        print(f"page_number: {page_number} and PAGE_SCRAPED {PAGE_SCRAPED}\n")
        number_page = str(page_number)
        full_url = f"http://api.adzuna.com/v1/api/jobs/{COUNTRY}/search/{number_page}?app_id={API_ID}&app_key={API_KEY}&results_per_page={RESULTS_PER_PAGE}{QUERY_PARAMETERS}{KEYWORDS}&max_days_old={MAX_OLD_DAYS}&content-type=application/json"
        print(f"full_url {full_url} \n")
        url_list.append(full_url)
    return url_list


def scrape_url(url):
    """
    Get requests from Adzuna API for each url passed

    Parameters
    ----------
    url : str
        the url needed to get the Adzuna API response

    Returns
    -------
    response.json() : json object
        a dictionary with 4 keys ['results', '__CLASS__', 'count', 'mean']
        the actual job offer details are in results

    Raises
    ------
    HTTPError
        If the status code is not 200 (Standard response for successful
        HTTP requests), the incorrect status code and url are displayed
    """
    response = requests.get(url, timeout=500)
    if response.status_code == 200:
        return response.json()
    raise HTTPError(f"The request for {url} was not successful : \
          status {response.raise_for_status()}")


class GetJobOffer():
    """
    A class used to fill in details of
    the instances of the 2 other classes Job and Company

    Attributes
    ----------
    full_info : dict
        a dictionnary with 15 keys (['location', 'title', 
        'created', 'latitude', 'adref', 'company', 'contract_time',
        'category', 'salary_is_predicted', 'id', 'longitude',
        'redirect_url', 'description', '__CLASS__', 'contract_type']
        corresponding to the core of the job offer
    job_offer : class JobOffer()
    company : class Company()

    Methods
    -------
    get_job_details
        assigning the right piece of information to the correct attribute of
        the JobOffer object
    get_company_details
        assigning the right piece of information to the correct attribute of
        the Company object
    """
    def __init__(self, full_info):
        """
        Parameters
        ----------
        full_info : dict
            The actual job offer information available via the Adzuna API
        """
        self.full_info = full_info
        self.job_offer = JobOffer()
        self.company = Company()

    def get_job_details(self):
        """
        assigning the right piece of information to the correct attribute of
        the JobOffer object

        Parameters
        ----------
        self
        """

        results = self.full_info
        self.job_offer.title = results["title"] if "title" in results else None
        self.job_offer.location = results["location"]["display_name"] if \
            "location" in results else None
        self.job_offer.company = vars(self.company)
        if ("contract_type" in results) or ("contract_time" in results):
            if ("contract_type" in results) and ("contract_time" in results):
                self.job_offer.contract_type = results["contract_type"] \
                    + " and " + results["contract_time"]
            elif ("contract_type" in results) and ("contract_time" not in
                                                   results):
                self.job_offer.contract_type = results["contract_type"]
            else:
                self.job_offer.contract_type = results["contract_time"]
        self.job_offer.salary = results["salary_is_predicted"] \
            if "salary_is_predicted" in results else None
        self.job_offer.description = results["description"] if "description" \
            in results else None
        self.job_offer.publication_date = results["created"][:10] if \
            "created" in results else None
        self.job_offer.url_direct_offer = results["redirect_url"] if \
            "redirect_url" in results else None

    def get_company_details(self):
        """
        assigning the right piece of information to the correct attribute of
        the Company object

        Parameters
        ----------
        self
        """
        results = self.full_info
        if "category" in results:
            self.company.sector = results["category"]["tag"]
        if 'company' in results:
            if "display_name" in results['company']:
                self.company.name = results['company']["display_name"]
            elif "name" in results['company']:
                self.company.name = results['company']["name"]

    def combine_job_company(self):
        """
        to match the structure of the DataFrame created following the wttj
        scrape, the Company object needs to be a directory within the
        JobOffer.company attribute

        Parameters
        ----------
        self

        Returns
        ----------
        vars(self.job_offer) : dict
            a dictionnary representing the JobOffer object
            filled in with every piece of information available 
            from the Adzuna API
            the keys are the attribute of the JobOffer object
        """
        self.get_company_details()
        self.get_job_details()
        return vars(self.job_offer)


def combing_each_offer(jobs_offers):
    """
    Iterates over each offer found on each page

    Parameters
    ----------
    jobs_offers : lst
        a list of all the json objects collected from the individual HTTP
        requests made to the Adzuna API
        As previously mentionned, withing each json object, the only
        interesting key is "results" which is in itself a list
        Depending on the value of RESULTS_PER_PAGE, the lenght of this
        "results" list (when existing) may vary from the maximum size
        (= RESULTS_PER_PAGE) to the smallest (1)

    Returns
    -------
    jobs_ready_for_export : lst
        a list of all JobOffer objects filled in and ready to be exported
    """
    jobs_ready_for_export = []
    for offer in jobs_offers:
        nb_offers_on_page = 0
        while nb_offers_on_page < len(offer["results"]):
            getjoboffer = GetJobOffer(offer["results"][nb_offers_on_page])
            jobs_ready_for_export.append(getjoboffer.combine_job_company())
            nb_offers_on_page += 1
    return jobs_ready_for_export


if __name__ == "__main__":
    """
    initiating the script that eventually saves a csv file in the output
    directory with the full DataFrame of job offers as well as a csv file
    of the entire list of url scraped

    Parameters
    ----------
    None

    Returns
    ----------
    N/A
    """
    url_list = create_url()
    pd.DataFrame(url_list).to_csv('output/job_urls_adzuna.csv', index=False)
    jobs_offers = [scrape_url(url) for url in tqdm(url_list,
                                                   desc="Accessing API")]
    jobs_ready_for_export = combing_each_offer(jobs_offers)
    df_adzuna_jobs = pd.DataFrame(jobs_ready_for_export)
    df_adzuna_jobs["source"] = ["adzuna_api"]*df_adzuna_jobs.shape[0]
    df_adzuna_jobs.to_csv('output/job_offers_adzuna.csv', index=False)
