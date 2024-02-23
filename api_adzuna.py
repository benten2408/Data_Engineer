import pandas as pd
import requests
from tqdm import tqdm

# STEP 0 - setting Environment Variables

country = "fr"
api_id = "37fe08af"
api_key = "17c1369ea8fb68bc48f834aebc0bec53"
results_per_page = 25
page_scraped = 100
what_and = "data%20engineer"
max_days_old = str(30)

# ETAPE 1 connexion à l'API + récupération offres


def create_url(start_url="http://api.adzuna.com/v1/api/jobs/"):
    """
    concactène l'adresse url à partir des paramètres choisis
    comment améliorer pour que les paramètres soient correctement passés ?
    """
    url_list = []
    for page_number in range(1, page_scraped):
        part0_url = "/search/"
        number_page = str(page_number) 
        part1_url = "?app_id="
        part2_url = "&app_key="
        part3_url = "&results_per_page="
        offers_per_page = str(results_per_page)
        part4_url = "&what_and="
        part5_url = "&max_days_old="
        end_url = "&content-type=application/json"
        full_url = f"{start_url}{country}{part0_url}{number_page}{part1_url}{api_id}{part2_url}{api_key}{part3_url}{offers_per_page}{part4_url}{what_and}{part5_url}{max_days_old}{end_url}"
        url_list.append(full_url)
    return url_list


def scrape_urls(url):
    """
    lance la requête sur l'api Adzuna pour chacunes des url crééés
    si le status_code est incorrect, il s'affiche et l'url liée s'affiche
    """
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("The request for {} was not successful : status {}".format(url, response.status_code))
        return None


class Company:
    def __init__(self):
        self.name = None
        self.sector = None
        self.employees = None
        self.creation_year = None
        self.turnover = None
        self.mean_age = None


class JobOffer:
    def __init__(self):
        self.title = None
        self.company = None
        self.contract_type = None
        self.location = None
        self.salary = None
        self.remote_type = None
        self.starting_date = None
        self.required_experience = None
        self.education = None
        self.description = None
        self.profil_experience = None
        self.publication_date = None
        self.url_direct_offer = None
      

class GetJobOffer():
    def __init__(self, full_info):
        self.full_info = full_info
        self.job_offer = JobOffer()
        self.company = Company()

    def get_job_details(self):
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
        results = self.full_info
        if "category" in results:
            self.company.sector = results["category"]["tag"]
        if 'company' in results:
            if "display_name" in results['company']:
                self.company.name = results['company']["display_name"]
            elif "name" in results['company']:
                self.company.name = results['company']["name"]

    def combine_job_company(self):
        self.get_company_details()
        self.get_job_details()
        return vars(self.job_offer)


def final_step(jobs_offers):
    jobs_ready_for_export = []
    for offer in jobs_offers:
        nb_offers_on_page = 0
        while nb_offers_on_page < results_per_page:
            getjoboffer = GetJobOffer(offer["results"][nb_offers_on_page])
            jobs_ready_for_export.append(getjoboffer.combine_job_company())
            nb_offers_on_page += 1
    return jobs_ready_for_export    


url_list = create_url()
jobs_offers = [scrape_urls(url) for url in tqdm(url_list, desc="Accessing API")]
jobs_ready_for_export = final_step(jobs_offers)
df_adzuna_jobs = pd.DataFrame(jobs_ready_for_export)
df_adzuna_jobs.to_csv('output/job_offers_adzuna.csv')
df_adzuna_jobs.describe()