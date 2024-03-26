#!/usr/bin/env python3
"""
This script uses streamlit to provide an app-like interface
enabling some interaction with the vizualisations
"""
#ces imports seront in fine dans streamlit_dashboard/requirements.txt
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import requests
import os
import json
import time 
import plotly.express as px
import folium

API_BASE_URL = os.environ['API_BASE_URL']

titre = "Projet Jobmarket : les offres d'emplois pour Data Engineers en France"
st.title(titre)


def clean_column_df(df, column):
    """
    to clean all rows where location is Null
    to know how many f"{all.isnull().value_counts()}"
    reset_index to make sure indexes pair with number of rows
    """
    cleaned_column_df = df.dropna(subset=column).reset_index(drop=True)
    return cleaned_column_df


def sort_contracttypes(contract_type):
    """
    To categorize all contracts type in 5 main types :
    - CDI
    - CDD
    - Alternance
    - Stage
    - Freelance
    If the contract is not mentionned or the categories keywords
    are not present, the row is taken out of the dataframe
    """
    contract_type = str(contract_type).lower().split()
    if "cdi" in contract_type:
        return "CDI"
    elif "cdd" in contract_type:
        return "CDD"
    elif "alternance" in contract_type:
        return "Alternance"
    elif "stage" in contract_type:
        return "Stage"
    elif "freelance" in contract_type:
        return "Freelance"
    else:
        return None


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

#conn = psycopg2.connect(**st.secrets.db_params)
#conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

# Perform query
# table_choisie = st.selectbox(
#      'De quelle table souhaitez-vous voir un extrait ?',
#      ('JobOffers', 'Companies', 'Sources', 'Skills', 'JobOffer_Skills'))
# 
# df = fetch_data("joboffer_skills/most-demand-skills")
# query = f"SELECT * FROM {table_choisie};"
# 
# table_to_display = pd.read_sql(query, conn)
# f"### Voici la table {table_choisie}"
# st.dataframe(table_to_display)
# "### une brève description avec la méthode describe() de pandas"
# st.dataframe(table_to_display.describe(include="all"))

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

def fetch_full_data(endpoint):
    print(f"{API_BASE_URL}/{endpoint}")
    response = requests.get(f"{API_BASE_URL}/{endpoint}")
    return pd.DataFrame(response.json(), columns=['contracttype', 'number_offer'])

all_contracts = fetch_full_data("joboffers_contracts")
# Worth mentionning, the nunique() method does NOT include the None values
f"""Initialement, les {all_contracts.number_offer.sum()} annonces récupérées sont réparties en {all_contracts['contracttype'].nunique()} types de contrat possibles.\n"""
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
*sans compter donc les {int(unspecified_contracts)} annonces où le contrat n'est pas mentionné et qui ont donc été retirées du jeu de données."""


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

# from branca.colormap import viridis
# import branca.colormap as cm
# import matplotlib.cm as cm
# from matplotlib.colors import rgb2hex
# from branca.colormap import linear
# from streamlit_folium import st_folium
# "# streamlit-folium"

import altair as alt
import matplotlib.pyplot as plt


def fetch_full_data(endpoint):
    #print(f"{API_BASE_URL}/{endpoint}")
    response = requests.get(f"{API_BASE_URL}/{endpoint}")
    return pd.DataFrame(response.json())


def fetch_location_coordinates(endpoint):
    #print(f"{API_BASE_URL}/{endpoint}")
    response = requests.get(f"{API_BASE_URL}/{endpoint}")
    print(response)
    return pd.DataFrame(response.json(), columns=['location', 'latitude', 'longitude'])

all_offers = fetch_full_data("joboffers")
all_offers
location_coordinates = fetch_location_coordinates("coordinates")

unknown_locations = all_offers.location.isnull().sum()
not_all_offers = all_offers.dropna(subset = ['location'])
location_coordinates
st.map(location_coordinates)

all_offers_located = pd.merge(not_all_offers, location_coordinates, on='location', how='left')
all_offers_located = all_offers_located.dropna(subset=['latitude', 'longitude'])
# Display merged dataframe
all_offers_located
st.map(all_offers_located)

# ajout nombre d'offres
# ajout proportionalité taille
# ajout lien annonce
# ajout lien url cliquable



# FOLIUM FIRST TEST
# STREAMLIT_FOLIUM
"""
# Group data by location and count number of job offers at each location
location_counts = all_offers_located.groupby(['latitude', 'longitude']).size().reset_index(name='job_offer_count')

# Calculate marker size proportional to the number of job offers
max_job_offers = location_counts['job_offer_count'].max()
scaling_factor = 50  # Adjust as needed
location_counts['marker_size'] = location_counts['job_offer_count'] / max_job_offers * scaling_factor

# Create Folium map centered on the mean of the coordinates
m = folium.Map(location=[all_offers_located['latitude'].mean(), all_offers_located['longitude'].mean()], zoom_start=5)

# Add markers to the map
for index, row in location_counts.iterrows():
    folium.CircleMarker(
        location=[row['latitude'], row['longitude']],
        radius=row['marker_size'],
        color='blue',
        fill=True,
        fill_color='blue'
    ).add_to(m)

# Display the map in Streamlit
#st.write(m)
# call to render Folium map in Streamlit
st_folium(m)
"""

# FOLIUM SECOND TEST FOR COLOR
"""

# Group data by location and count number of job offers at each location
location_counts = all_offers_located.groupby(['latitude', 'longitude']).size().reset_index(name='job_offer_count')

# Normalize job offer counts to range [0, 1] for the color scale
min_count = location_counts['job_offer_count'].min()
max_count = location_counts['job_offer_count'].max()
location_counts['normalized_count'] = (location_counts['job_offer_count'] - min_count) / (max_count - min_count)

# Create a colormap using Viridis from Matplotlib
colormap = cm.viridis

# Convert colormap to list of HTML hex colors
num_colors = 100  # Choose the number of colors to generate
colors = [rgb2hex(colormap(i / num_colors)[:3]) for i in range(num_colors)]


# Create Folium map centered on the mean of the coordinates
m = folium.Map(location=[all_offers_located['latitude'].mean(), all_offers_located['longitude'].mean()], zoom_start=5)

# Add markers to the map with colors from the colormap
for index, row in location_counts.iterrows():
    color_index = int(row['normalized_count'] * (num_colors - 1))
    color = colors[color_index]
    folium.CircleMarker(
        location=[row['latitude'], row['longitude']],
        radius=5,
        color=None,
        fill=True,
        fill_color=color,
    ).add_to(m)

# Add legend for the color scale
colormap.caption = 'Number of Job Offers'
#m.add_child(colormap)

# Display the map in Streamlit
st.write(m)
"""