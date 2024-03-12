from fastapi import FastAPI, Depends, HTTPException, status, Query, Response
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import List, Optional
import pandas as pd
import json
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

api = FastAPI()

users = {
    "admin": "root",
}


db_params = {
    "database": "job_market",
    "user": "admin",
    "password": "root",
    "host": "postgres", # postgres docker image name 
    "port": "5432"
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

@api.get("/joboffers")
async def get_joboffers():
	conn = get_db_connection()
	joboffers = pd.read_sql("SELECT * FROM joboffers", conn)
	conn.close()
	return joboffers.to_dict(orient="records")