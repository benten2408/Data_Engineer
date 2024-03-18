#!/usr/bin/env python3
"""
This script uses streamlit to provide an app-like interface
enabling some interaction with the vizualisations
"""
#ces imports seront in fine dans streamlit_dashboard/requirements.txt
import itertools
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import requests
from cleaning import clean_column_df 
from cleaning import sort_contracttypes
import time 
import folium
import plotly.express as px
from stqdm import stqdm
stqdm.pandas(desc="Récupération des coordonnées géographiques ")

API_BASE_URL = os.environ['API_BASE_URL']

titre = "Projet Jobmarket : les offres d'emplois pour Data Engineers en France"
st.title(titre)

"""
Dans le cadre de la formation de Data Engineer par DataScientest au format bootcamp de janvier à avril 2024, nous avons eu l'occasion de réaliser un projet en groupe.\n
Voici le résultat de nos recherches sur les offres d'emplois de Data Engineer  publiées en France au cours des 30 derniers jours.\n
Nous avons récolté les annonces publiées sur Welcome to The Jungle et via l'API d'Adzuna, deux aggrégateurs. _(ajout lien url ?)_\n
Ces données ont alimenté 5 tables : JobOffer_Skills, JobOffers, Skills, Sources, Companies. _(ajout diagramme UML ?)_\n

Notre objectif est de répondre à ces 5 questions  _(ajout lien cliquable ?)_: 
- quels secteurs recrutent le plus ?
- combien d'entreprises par secteur ont publié des annonces ?
- quelles sont les "skills"  _(à remplacer par compétences ?)_ les plus demandées ?
- quel est le contrat majoritairement proposé dans les annonces ? 
- quelle est la zone géographique avec le plus d'offres ?  _(à remplacer par Quelle est la répartition géographique des offres ?)_
"""

conn = psycopg2.connect(**st.secrets.db_params)
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

# Perform query
table_choisie = st.selectbox(
    'De quelle table souhaitez-vous voir un extrait ?',
    ('JobOffers', 'Companies', 'Sources', 'Skills', 'JobOffer_Skills'))

query = f"SELECT * FROM {table_choisie};"

table_to_display = pd.read_sql(query, conn)
f"### Voici la table {table_choisie}"
st.dataframe(table_to_display)
"### une brève description avec la méthode describe() de pandas"
st.dataframe(table_to_display.describe(include="all"))

"## Quels secteurs recrutent le plus ?"
# géré par Jean

"""
## Combien d'entreprise par secteur ont publié des annonces ?
"""
# géré par Jean

"""
## Quelles sont les "skills" les plus demandées ?
"""

def fetch_data(endpoint):
    print(f"{API_BASE_URL}/{endpoint}")
    response = requests.get(f"{API_BASE_URL}/{endpoint}")
    return pd.DataFrame(response.json(), columns=['skillname', 'nb_count'])

df = fetch_data("joboffer_skills/most-demand-skills").head(15)

fig = px.bar(
    df, x='skillname', y='nb_count', title='Top 15 des compétences les plus demandées',
    labels={'skillname': 'Compétence', 'nb_count': 'Nombre de demandes'},
    color='nb_count', color_continuous_scale=px.colors.sequential.Viridis
)

st.plotly_chart(fig)

"""
## Quel est le contrat majoritaire proposé dans les annonces ? 
"""

#à remplacer evntually par la connexion api
query = "SELECT contracttype, COUNT(*) AS number_offer FROM joboffers GROUP BY contracttype ORDER BY contracttype DESC;"
all_contracts = pd.read_sql(query, conn)

#st.dataframe(all_contracts)

# Worth mentionning, the nunique() method does NOT include the None values
f"""Initialement, les {all_contracts.number_offer.sum()} annonces récupérées sont réparties en {all_contracts['contracttype'].nunique()} types de contrat possibles.\n"""

#all_contracts = all_contracts.fillna('Non spécifié')
#loc to find the value of (condition all 'Non spécifié' contractype) followed by values[0] transforming the dataframe in a numpy array and extracting its single value
#unspecified_contracts = all_contracts.loc[all_contracts['contracttype'] == "Non spécifié", ['number_offer']].values[0]

unspecified_contracts = all_contracts.loc[all_contracts.contracttype.isnull(), ['number_offer']].values[0]

all_contracts['contracttype'] = all_contracts['contracttype'].apply(lambda x : sort_contracttypes(x))
unspecified_contracts += all_contracts.contracttype.isnull().sum()
known_contracts = all_contracts.dropna(subset = ['contracttype'])
result = known_contracts.groupby('contracttype')['number_offer'].sum().reset_index()
result.sort_values('number_offer', inplace=True, ascending=False)
f"""
Pour une meilleure lisibilité, nous les avons rassemblées en 5 catégores* : \n
- CDI
- CDD
- Freelance 
- Alternance
- Stage\n
*sans compter donc les {int(unspecified_contracts)} annonces où le contrat n'est pas mentionné."""


fig = px.bar(
    result,  x="contracttype", y="number_offer", title='Les 5 contrats possibles',
    labels={'contracttype': 'Contrats', 'number_offer': 'Nombre d\'annonces'},
    text="number_offer",
    color='number_offer', color_continuous_scale=px.colors.sequential.Viridis
)

st.plotly_chart(fig)

"""
## Quelle est la zone avec le plus d'offres ?
"""
# géré par Elsa
# (format probable carte avec cercles proportionnelles au nombre d'offres)

query = "SELECT * FROM joboffers;"
all_offers = pd.read_sql(query, conn)
#st.dataframe(all_offers)
unknown_locations = all_offers.location.isnull().sum()
not_all_offers = all_offers.dropna(subset = ['location'])

import requests

def get_lat_long_city_adresse_gouv(row):
    #row
    #address = row["location"]
    address = row
    url = "https://api-adresse.data.gouv.fr/search/?q=" + str(address)
    #time.sleep(1)
    try:
        response = requests.get(url).json()
        if response["features"][0]:
            #f"response {response}"
            longitude = response["features"][0]["geometry"]["coordinates"][0]
            latitude = response["features"][0]["geometry"]["coordinates"][1]
            #f"location {address}  latitude {latitude}  longitude {longitude}"
            return (latitude, longitude)
    except:
        f"Pour information, les coordonnées de l'adresse « {address} » n'ont pas pu être récupérées"
        return (None,None)


time_start = time.time()
not_all_offers["latitude"], not_all_offers["longitude"] = zip(*not_all_offers["location"].progress_apply(lambda x : get_lat_long_city_adresse_gouv(x)))
time_end = time.time()
time_diff = time_end - time_start
f"La récupération des coordonnées géographiques via get_lat_long_city_adresse_gouv a pris {time_diff} secondes"
cleared_lat = not_all_offers.dropna(subset = ['latitude'])
cleared_lat_lon = cleared_lat.dropna(subset = ['longitude'])
unknown_latitudes = not_all_offers.latitude.isnull().sum()
unknown_longitudes = cleared_lat.longitude.isnull().sum()
unknown_lat_lon = unknown_latitudes + unknown_longitudes

f"""L'adresse n'étant pas précisée sur {unknown_locations} annonces, elles ont par conséquent été retirées.\n
Sur les {not_all_offers.shape[0]} annonces restantes, {unknown_lat_lon} annonce(s)
supplémentaire(s) a(ont) dû être supprimé(es), faute de coordonnées géographiques.
\nVoici la répartition géographique des {cleared_lat_lon.shape[0]} annonces
finales."""
import colormaps as cmaps
plt.register_cmap(name='viridis', cmap=cmaps.viridis)
plt.set_cmap(cmaps.viridis)
result = cleared_lat_lon.reset_index()
#st.dataframe(result)
st.map(result,color=)
import colormaps as cmaps

# ajout nombre d'offres
# ajout proportionalité taille 
# ajout lien annonce
# ajout lien url cliquable



conn.commit()
conn.close()