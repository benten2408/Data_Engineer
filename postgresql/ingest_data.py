import os
import pandas as pd

import locale
locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
import requests

from env_config import DATA_TO_INGEST_FOLDER


def get_skills_list():
	df_skills = pd.read_csv(os.path.join(DATA_TO_INGEST_FOLDER, 'skills.csv'), header=None)
	skills_list = df_skills.iloc[:, 0].tolist()
    
	return skills_list


def ingest_skills_query(cur):
	skills_list = get_skills_list()
      
	for skill in skills_list:
		cur.execute("SELECT skillName FROM Skills WHERE skillName = %s;", (skill,))
		result = cur.fetchone()
		if result is None:
			cur.execute("INSERT INTO Skills (skillName) VALUES (%s);", [skill])
    

def link_job_skill(cur, row, jobOfferId, skills_list):
    """
	for the JobOffer_Skills table
	2 possiblités : 
		soit une ligne par skillId (et donc plusieurs lignes pour le même jobId) 
		soit une ligne par jobId  ligne (et donc plusieurs pour le même skillId)

	pour rappel
	CREATE TABLE JobOffer_Skills (
			jobOfferId INTEGER REFERENCES JobOffers,
			skillId INTEGER REFERENCES Skills(skillId),
			PRIMARY KEY (jobOfferId, skillId)
		);

	Direction des flèches: il y a deux relations impliquées ici
	JobOffer vers JobOffer_Skills
	Skill vers JobOffer_Skills
	Signification : Chaque flèche pointe vers JobOffer_Skills, indiquant qu’elle sert de table de jonction. 
	Il n’y a pas de flèche directe entre JobOffer et Skills parce que leur relation est médiée à travers JobOffer_Skills. 
	Un offre d’emploi peut être associée à plusieurs compétences et vice versa.

	"""
    description = row['description']
    if description:
        for skill in skills_list:
            if skill in description:
                cur.execute("SELECT skillId FROM Skills WHERE skillName = %s;", [skill])
                skill_id  = cur.fetchone()
                if skill_id:
                    cur.execute("INSERT INTO JobOffer_Skills (jobofferid,skillid) VALUES (%s, %s);", (jobOfferId, skill_id,))

def get_or_create_company(cur, company_data):
    company = eval(company_data)
    cur.execute("SELECT companyId FROM Companies WHERE companyName = %s;", (company['name'],))
    result = cur.fetchone()
    if result:
        return result[0]
    else:
        cur.execute("INSERT INTO Companies (companyName, location, sector, information) VALUES (%s, %s, %s, %s) RETURNING companyId;",
                    (company['name'], company.get('location'), company.get('sector'), ''))
        return cur.fetchone()[0]

def get_or_create_source(cur, source_name):
    #print(source_name, type(source_name))
    cur.execute("SELECT sourceId FROM Sources WHERE sourceName = %s;", (source_name,))
    result = cur.fetchone()
    if result:
        return result[0]
    else:
        cur.execute("INSERT INTO Sources (sourceName) VALUES (%s) RETURNING sourceId;", (source_name,))
        return cur.fetchone()[0]


def concat_format_data():
	"""
    Création du dataframe complet
    """
	job_offer_adzuna = pd.read_csv(os.path.join(DATA_TO_INGEST_FOLDER, 'job_offers_adzuna.csv'))
	job_offer_wttj = pd.read_csv(os.path.join(DATA_TO_INGEST_FOLDER, 'job_offers_wttj.csv'))
    
	df = pd.concat([job_offer_adzuna, job_offer_wttj], ignore_index=True)

	df = df[~df.company.isna()].reset_index(drop=True)

	df = df.assign(
		starting_date=pd.to_datetime(df['starting_date'], format='%d %B %Y')
	)
	df['starting_date'] = df['starting_date'].dt.date

	df['publication_date'] = pd.to_datetime(df['publication_date'], errors='coerce', format='%Y-%m-%d')

	df = df.where(pd.notnull(df), None)
    
	return df


def ingest_joboffers_query(cur):
	"""Itération sur chaque ligne du dataframe pour intégrer chaque annonce à JobOffers
	"""
	df = concat_format_data()
	skills_list = get_skills_list()
      
	for _, row in df.iterrows():
		company_id = get_or_create_company(cur, row['company'])
		source_id = get_or_create_source(cur, row['source'])

		job_offer_data = (
			row['title'],
			company_id,
			row['salary'],
			row['remote_type'],
			row['contract_type'],
			row['starting_date'] if not pd.isnull(row['starting_date']) else None,
			row['location'],
			row['require_experience'],
			row['education'],
			row['description'],
			row['profil_experience'],
			row['publication_date'].date() if not pd.isnull(row['publication_date']) else None,
			row['url_direct_offer'],
			source_id,
		)
		cur.execute(
			"INSERT INTO JobOffers (title, companyId, salary, remoteType, contractType, startingDate, location, requiredExp, education, descriptions, profilExp, publicationDate, jobLink, sourceId) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING jobOfferId;", 
			job_offer_data
		)
		jobOfferId = cur.fetchone()
		link_job_skill(cur, row, jobOfferId, skills_list)


def get_location_coordinates(address):
    url = "https://api-adresse.data.gouv.fr/search/?q=" + str(address)
    try:
        response = requests.get(url).json()
        if response["features"][0]:
            #f"response {response}"
            longitude = response["features"][0]["geometry"]["coordinates"][0]
            latitude = response["features"][0]["geometry"]["coordinates"][1]
            city = response["features"][0]["properties"]["city"]
            postal_code = response["features"][0]["properties"]["postcode"]
            #f"location {address}  latitude {latitude}  longitude {longitude}"
            return (latitude, longitude, city, postal_code)
    except:
        f"Pour information, les coordonnées de l'adresse « {address} » n'ont pas pu être récupérées"
        return (None, None, None, None)


def create_csv_coordinates():
	df = concat_format_data()
	location = pd.DataFrame(df["location"].unique(), columns=["location"])
	location = location.dropna()
	location["latitude"], location["longitude"], location["city"], location["postal_code"] = zip(*location["location"].apply(lambda x : get_location_coordinates(x))) #axis = 0
	#location["latitude"], location["longitude"], location["city"], location["postal_code"] = zip(*location["location"].apply(lambda x: (48.60, 7.74, 67302, "Schiltigheim") if x == "Schiltigheim, Strasbourg-Campagne" else (None, None, None, None)))
	location.to_csv(os.path.join(DATA_TO_INGEST_FOLDER, 'locations.csv'), index=False)


def get_or_create_location(cur, location_data):
    #print(location_data)
    #print(type(location_data))
    cur.execute("SELECT location FROM Locations WHERE location = %s;", (str(location_data["location"]),))
    result = cur.fetchone()
    if result is None:
        cur.execute("INSERT INTO Locations (location, latitude, longitude, city, postal_code) VALUES (%s, %s, %s, %s, %s);", location_data)


def ingest_location(cur):
    df = pd.read_csv(os.path.join(DATA_TO_INGEST_FOLDER, 'locations.csv'))
    for _, row in df.iterrows():
        get_or_create_location(cur, row)


def location_process(cur):
	create_csv_coordinates()
	ingest_location(cur)


def get_or_create_user(cur, user, password):
    pass
	"""
     response = requests.get(url).json()
		if response:
          
    cur.execute("SELECT * FROM Users WHERE username = %s;", (username,))
    result = cur.fetchone()
    if result:
        return result[0]
    else:
        cur.execute("INSERT INTO Users (username, password) VALUES (%s, %s);",
                    (user, password))
        return cur.fetchone()[0] 
        """