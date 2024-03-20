from fastapi import FastAPI, Depends, HTTPException, status, Query, Response
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import json
import os
import pandas as pd
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from typing import List, Optional

DATABASE = os.environ['DATABASE']
DOCKER_POSTGRES_HOST = os.environ['DOCKER_POSTGRES_HOST']
POSTGRES_USER = os.environ['POSTGRES_USER']
POSTGRES_PASSWORD = os.environ['POSTGRES_PASSWORD']
PORT = os.environ['PORT']

api = FastAPI()

users = {
    POSTGRES_USER: POSTGRES_PASSWORD,
}

db_params = {
	"database": DATABASE,
	"user": POSTGRES_USER,
	"password": POSTGRES_PASSWORD,
	"host": DOCKER_POSTGRES_HOST,
	"port": PORT
}

def get_db_connection():
    conn = psycopg2.connect(**db_params)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    return conn

security = HTTPBasic()


def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
	"""
		Fonction d'authentification
	"""
	if credentials.username in users and users[credentials.username] == credentials.password:
		return credentials.username
	else:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Nom d'utilisateur ou mot de passe incorrect",
			headers={"Authorization": "Basic"},
		)

@api.get("/")
def get_index():
    """
    Message Bienvenue
    """
    return {
            "status": status.HTTP_200_OK,
            "message": "Bienvenue sur l'API Job Market"
        }

@api.get("/companies")
async def get_companies():
	conn = get_db_connection()
	companies = pd.read_sql("SELECT * FROM companies", conn)
	conn.close()
	return companies.to_dict(orient="records")

@api.get("/skills")
async def get_skills():
	conn = get_db_connection()
	skills = pd.read_sql("SELECT * FROM skills", conn)
	conn.close()
	return skills.to_dict(orient="records")

@api.get("/sources")
async def get_sources():
	conn = get_db_connection()
	sources = pd.read_sql("SELECT * FROM sources", conn)
	conn.close()
	return sources.to_dict(orient="records")

@api.get("/joboffer_skills")
async def get_joboffer_skills():
	conn = get_db_connection()
	joboffer_skills = pd.read_sql("SELECT * FROM joboffer_skills", conn)
	conn.close()
	return joboffer_skills.to_dict(orient="records")

@api.get("/joboffer_skills/most-demand-skills")
async def get_most_demanded_skills():
	conn = get_db_connection()
	cur = conn.cursor()
	joboffer_skills = cur.execute(
		"""
		SELECT skillname, count(*) AS nb_count 
		FROM joboffer_skills AS jos
		JOIN skills AS s
		ON jos.skillid = s.skillid
		GROUP BY skillname ORDER BY nb_count DESC;
		"""
	)
	joboffer_skills = cur.fetchall()

	conn.commit()
	cur.close()
	conn.close()

	return joboffer_skills

@api.get("/joboffers")
async def get_joboffers():
	conn = get_db_connection()
	joboffers = pd.read_sql("SELECT * FROM joboffers", conn)
	conn.close()
	return joboffers.to_dict(orient="records")

@api.get("/joboffers_contracts")
async def get_joboffers_contracts():
	conn = get_db_connection()
	joboffers_contracts = pd.read_sql("SELECT contracttype, COUNT(*) AS number_offer FROM joboffers GROUP BY contracttype ORDER BY contracttype DESC;", conn)
	conn.close()
	return joboffers_contracts.to_dict(orient="records")

@api.get("/coordinates")
async def get_location_coordinates():
	conn = get_db_connection()
	locations = pd.read_sql("SELECT * FROM locations", conn)
	locations = locations.dropna()
	conn.close()
	return locations.to_dict(orient="records")
	