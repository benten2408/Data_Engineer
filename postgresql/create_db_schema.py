
import psycopg2
from env_config import DATABASE

def create_database_query(cur):

    cur.execute(f"DROP DATABASE IF EXISTS {DATABASE} WITH (force);")
    cur.execute(f"CREATE DATABASE {DATABASE};")


def create_schema_query(cur):

    commands = (
        """
        CREATE TABLE Companies (
            companyID SERIAL PRIMARY KEY,
            companyName VARCHAR(255),
            location VARCHAR(255),
            sector VARCHAR(255),
            information TEXT
        );
        """,
        """
        CREATE TABLE Sources (
            sourceId SERIAL PRIMARY KEY,
            sourceName VARCHAR(255)
        );
        """,
        """
        CREATE TABLE Skills (
            skillId SERIAL PRIMARY KEY,
            skillName VARCHAR(255)
        );
        """,
        """
        CREATE TABLE JobOffers (
            jobOfferId SERIAL PRIMARY KEY,
            title VARCHAR(255),
            companyId INTEGER REFERENCES Companies(CompanyID),
            salary VARCHAR(255),
            remoteType VARCHAR(255),
            contractType VARCHAR(255),
            startingDate DATE,
            location VARCHAR(255),
            requiredExp VARCHAR(255),
            education VARCHAR(255),
            descriptions TEXT,
            profilExp TEXT,
            publicationDate DATE,
            jobLink VARCHAR(255),
            sourceId INTEGER REFERENCES Sources(SourceId)
        );
        """,
        """
        CREATE TABLE JobOffer_Skills (
            jobOfferId INTEGER REFERENCES JobOffers,
            skillId INTEGER REFERENCES Skills(skillId),
            PRIMARY KEY (jobOfferId, skillId)
        );
        """,
        """
        CREATE TABLE Locations (
            location VARCHAR(255),
            latitude DOUBLE PRECISION,
            longitude DOUBLE PRECISION,
            PRIMARY KEY (location)
        );
        """
    )

    for command in commands:
        table_name = ''.join(command.split("CREATE TABLE")[1].split("(")[0])
        try:
            cur.execute(command)
            print(f"Table {table_name} created successfully.")
        except psycopg2.Error as e:
            print(f"An error occurred: {e}")
