#!/usr/bin/env python3
"""
This script uses streamlit to provide an app-like interface
"""

import itertools
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

st.title("Welcome to Job Market Dashboard!")
st.title("Les offres d'emplois pour Data Engineers en France")

if st.checkbox('🇬🇧 Show English description'):
    """
    ## This is our app created for the project during our DataScientest Data Engineering bootcamp.
    Our chosen topic is Job Market and we decided to focus our data on Data Engineering offers published in France in the previous 30 days.
    Our 5 main KPI answer these questions:
    - which is the sector that recruits the most?
    - 
    """
if st.checkbox('🇫🇷 Présentez l\'introduction en français'):
    """
    Voici le résultat de nos recherches sur les offres d'emplois de Data Engineer  publiées en France au cours des 30 derniers jours.\n
    Nous avons récolté les annonces publiées sur Welcome to The Jungle et via l'API d'Adzuna, deux aggrégateurs.\n
    5 tables ont alors été créées : JobOffer_Skills, JobOffers, Skills, Sources, Companies.\n
    Notre objectif est de répondre à ces 5 questions : 
    - quel secteur recrute le plus ?
    - combien d'entreprise par secteur ont publié des annonces ?
    - quelles sont les "skills" les plus demandées ? (format probable barplot)
    - quelle est la zone avec le plus d'offres  (format probable carte avec cercles proportionnelles au nombre d'offres)
    - quel est le contrat majoritairement proposé dans les annonces ? 
    """
import os

#cwd = os.getcwd()  # Get the current working directory (cwd)
#files = os.listdir(cwd)  # Get all the files in that directory
#"Files in %r: %s" % (cwd, files)
#new_cwd = os.chdir('/usr/src/app/streamlit_dashboard')  # Get all the files in that directory
#new_cwd = os.chdir('/usr/src/app/streamlit_dashboard/.streamlit')  # Get all the files in that directory
#new_files = os.listdir(new_cwd)  # Get all the files in that directory
#"Files in %r: %s" %(new_cwd,new_files)  # Get all the files in that directory

#import toml
#
#toml_data = toml.load("/usr/src/app/streamlit_dashboard/.streamlit/secrets.toml")
#f"{toml_data}"
#f"type({toml_data})"
#f"type({toml_data.keys})"
#f"{toml_data.keys}"

df = pd.read_csv('/usr/src/app/streamlit_dashboard/job_offers_wttj.csv')
df = df.dropna(subset=['company']).reset_index(drop=True)
df['sector'] = df.company.apply(lambda x : eval(x)['sector'].split(','))

sector_list = list(itertools.chain.from_iterable(df['sector']))
df_sector = pd.DataFrame(sector_list, columns=["sector"])
df_sector_count = df_sector.value_counts("sector")

st.bar_chart(df_sector_count)

#f"len(df_sector_count) {len(df_sector)} , len(sector_list)) {len(sector_list)}"

# comment lier à postgres
# on devra probablement utiliser st.cache_resource

"______________ EN COURS DE CREATION________"
# Initialize connection
#import os

# # Everything is accessible via the st.secrets dict:
# f"os.environ['username'] == st.secrets['username'],"
# f"{st.secrets.connections.postgresql.password}"
# f"{st.secrets.connections.postgresql.username}"
# f"{st.secrets.connections.postgresql.database}"
# #"{**st.secrets.connections.postgresql}"
#st.write("DB username:", st.secrets["username"])
#st.write("DB password:", st.secrets["db_password"])
#st.write("My cool secrets:", st.secrets["my_cool_secrets"]["things_i_like"])

# And the root-level secrets are also accessible as environment variables:
#st.write(
#    "Has environment variables been set:",
#    os.environ["db_username"] == st.secrets["db_username"],
#)
#conn = st.connection("postgresql", type="streamlit.connections.SQLConnection")

import os
#env POSTGRES_DB_NAME=jobmarket
#env POSTGRES_DB_HOST=localhost
#env POSTGRES_DB_PORT=5432
#env POSTGRES_DB_USER=admin
#env POSTGRES_DB_PASS=root
#
#postgres_uri = "postgresql://{}:{}@{}?port={}&dbname={}".format(
#    os.environ['POSTGRES_DB_USER'],
#    os.environ['POSTGRES_DB_PASS'],
#    os.environ['POSTGRES_DB_HOST'],
#    os.environ['POSTGRES_DB_PORT'],
#    os.environ['POSTGRES_DB_NAME'],
#)
POSTGRES_DB_NAME='jobmarket'
POSTGRES_DB_HOST='localhost'
POSTGRES_DB_PORT='5432'
POSTGRES_DB_USER='admin'
POSTGRES_DB_PASS='root'

postgres_uri = "postgresql://{}:{}@{}?port={}&dbname={}".format(
    POSTGRES_DB_USER,
    POSTGRES_DB_PASS,
    POSTGRES_DB_HOST,
    POSTGRES_DB_PORT,
    POSTGRES_DB_NAME,
)
postgres_uri
#postgresql://postgres:postgres@localhost?port=5432&dbname=hfds_demo
from datasets import Dataset

ds = Dataset.from_sql('SELECT * FROM joboffers;', postgres_uri)

ds

#import psycopg2
#
#def init_connection():
#    return psycopg2.connect(**st.secrets["postgres"])
#    #return psycopg2.connect(**st.secrets["postgresql"])
#
#conn = init_connection()

#conn = st.connection('postgresql', type='sql')

#my_db.connect(**st.secrets.db_credentials)

# Perform query
table_choisie = st.selectbox(
    'De quelle table souhaitez-vous voir un extrait ?',
    ('Companies', 'Sources', 'Skills', 'JobOffers', 'JobOffer_Skills'))

# st.write("Voici l'extrait de la table ", table_choisie, ".\n")
# extrait = conn.query(f"select * from {table_choisie} LIMIT 15")
# st.dataframe(extrait)

# By default, query() results are cached without expiring. In this case, we set ttl="10m" to ensure the query result is cached for no longer than 10 minutes. You can also set ttl=0 to disable caching. Learn more in Caching.
# df = conn.query('SELECT * FROM joboffers;', ttl="10m")

# Print results.
"Ici les 10 premières annonces de la table JobOffers : "
for row in df[:10].itertuples():
    st.write(f"Le poste « {row.title} » se situe à {row.location}.")

"# _ EN COURS DE CREATION _"

"## Quels secteurs recrutent le plus ?"


def update_pie():
    """
    Enabling the display of top recruiting sectors
    in piechart format depending on the input_number 
    chosen by the user and accessed via the session_state
    """
    top_number = st.session_state.input_number
    unique_sectors = set(sector_list)
    only_top_sectors = list(unique_sectors)[:top_number]
    # Pie chart, where the slices will be ordered and plotted counter-clockwise:
    fig1, ax1 = plt.subplots()
    #problème à régler car pourcentage relatif au top_number probablement du à autopct='%1.1f%%' mais je ne sais pas comment afficher la valeur autrement
    ax1.pie(df_sector_count[:top_number], labels=only_top_sectors,
            shadow=True, startangle=90, autopct='%1.1f%%')
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    st.pyplot(fig1)


col1,col2,col3 = st.columns(3)

with col1:
    "Vous voulez voir le top"

with col2:
    top_sectors = st.number_input("top", min_value=0, max_value=10, value=3,
                                  step=1, key="input_number", format="%d",
                                  on_change=update_pie,
                                  label_visibility="collapsed")

with col3:
    "des secteurs qui recrutent"

update_pie()

"""
## Combien d'entreprise par secteur ont publié des annonces ?
"""
"""
## Quelles sont les "skills" les plus demandées ? (format probable barplot)
"""
"""
## Quelle est la zone avec le plus d'offres  (format probable carte avec cercles proportionnelles au nombre d'offres)
"""
"""
## Quel est le contrat majoritaire proposé dans les annonces ? 
"""