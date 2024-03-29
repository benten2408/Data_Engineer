from fastapi import FastAPI, Depends, HTTPException, status, Query, Response, Security
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import json
import os
import pandas as pd
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from typing import List, Optional

from app.auth_utils import create_access_token, verify_password

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

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_db_connection():
    conn = psycopg2.connect(**db_params)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    return conn


def get_user_from_postgresql():
	conn = get_db_connection()
	result = pd.read_sql("SELECT * FROM users", conn)
	users_db = dict()
	for index, row in result.iterrows():
		users_db[row['username']] = {
			'username': row['username'],
			'hashed_password': row['password']
		}
	conn.close()
	return users_db


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return user_dict


def authenticate_user(username: str, password: str):
    users_db = get_user_from_postgresql()
    user = get_user(users_db, username)
    if not user:
        return False
    if not verify_password(password, user['hashed_password']):
        return False
    return user


@api.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user['username']})
    return {"access_token": access_token, "token_type": "bearer"}


def token_present(token: str = Security(oauth2_scheme)):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No access token provided"
        )
    return True


@api.get("/secure")
def secure(token_checked: bool = Depends(token_present)):
    return {"message": f"Access is {token_checked}"}


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
async def get_companies(token_checked: bool = Depends(token_present)):
	conn = get_db_connection()
	companies = pd.read_sql("SELECT * FROM companies", conn)
	conn.close()
	return companies.to_dict(orient="records")


@api.get("/skills")
async def get_skills(token_checked: bool = Depends(token_present)):
	conn = get_db_connection()
	skills = pd.read_sql("SELECT * FROM skills", conn)
	conn.close()
	return skills.to_dict(orient="records")


@api.get("/sources")
async def get_sources(token_checked: bool = Depends(token_present)):
	conn = get_db_connection()
	sources = pd.read_sql("SELECT * FROM sources", conn)
	conn.close()
	return sources.to_dict(orient="records")


@api.get("/joboffer_skills")
async def get_joboffer_skills(token_checked: bool = Depends(token_present)):
	conn = get_db_connection()
	joboffer_skills = pd.read_sql("SELECT * FROM joboffer_skills", conn)
	conn.close()
	return joboffer_skills.to_dict(orient="records")


@api.get("/joboffer_skills/most-demanded-skills")
async def get_most_demanded_skills(token_checked: bool = Depends(token_present)):
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
async def get_joboffers(token_checked: bool = Depends(token_present)):
	conn = get_db_connection()
	joboffers = pd.read_sql("SELECT * FROM joboffers", conn)
	conn.close()
	return joboffers.to_dict(orient="records")


@api.get("/joboffers_contracts")
async def get_joboffers_contracts(token_checked: bool = Depends(token_present)):
	conn = get_db_connection()
	joboffers_contracts = pd.read_sql("SELECT contracttype, COUNT(*) AS number_offer FROM joboffers GROUP BY contracttype ORDER BY contracttype DESC;", conn)
	conn.close()
	return joboffers_contracts.to_dict(orient="records")


@api.get("/coordinates")
async def get_location_coordinates():
	conn = get_db_connection()
	locations = pd.read_sql("SELECT location, latitude, longitude FROM locations", conn)
	locations = locations.dropna()
	conn.close()
	return locations.to_dict(orient="records")


@api.get("/coordinates_full")
async def get_full_location_coordinates():
	conn = get_db_connection()
	locations = pd.read_sql("SELECT * FROM locations", conn)
	locations = locations.dropna()
	conn.close()
	return locations.to_dict(orient="records")


