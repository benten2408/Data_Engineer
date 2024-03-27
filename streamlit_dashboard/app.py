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
import data_cleaning

API_BASE_URL = os.environ['API_BASE_URL']
st.set_page_config(layout="wide")
titre = "Projet Jobmarket : les offres d'emplois pour Data Engineers en France"
st.title(titre)

# a ejecter dans un autre fichier
def clean_location_column(df):
    """
    to clean all rows where location is Null
    to know how many f"{all.isnull().value_counts()}"
    reset_index to make sure indexes pair with number of rows
    """
    #cleaned_column_df = df.dropna(subset=column).reset_index(drop=True)
    location = df['location']
    location_list_unique = set(str(location).lower().split())
    #for name in location_list_unique:
    #    print(name)
    #df['location_cleaned'] = cleaned_location_column_df['location']
    return location_list_unique

# aejecter dans un autre fichier
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


introduction = f"""Dans le cadre de la [formation de Data Engineer par DataScientest](https://datascientest.com/formation-data-engineer) au format bootcamp de janvier à avril 2024, nous avons eu l'occasion de réaliser un projet en groupe.\n
Voici le résultat de nos recherches sur les offres d'emplois de Data Engineer publiées en France au cours des 30 derniers jours.\n
Nous avons récolté les annonces publiées sur [Welcome to The Jungle](https://www.welcometothejungle.com/en) et via l'[API d'Adzuna](https://www.adzuna.fr), deux aggrégateurs.
Notre objectif est de répondre à ces 5 questions : 
- quels secteurs recrutent le plus ?
- combien d'entreprises par secteur ont publié des annonces ?
- quelles sont les compétences les plus demandées ?
- quel est le contrat majoritairement proposé dans les annonces ? 
- quelle est la zone géographique avec le plus d'offres ?_"""
st.write(introduction)
tab0, tab1, tab2, tab3, tab4 = st.tabs(["Les secteurs qui recrutent le plus",
                                        "Les entreprises par secteurs",
                                        "Les compétences recherchées",
                                        "Les contrats proposés",
                                        "Les villes concernées"])

with tab0:
    st.header("Quels secteurs recrutent le plus ?")
    # géré par Jean 


with tab1:
    st.header("Combien d'entreprises par secteur ont publié des annonces ?")
    # géré par Jean

with tab2:
    st.header("Quelles sont les compétences les plus demandées ?")


    def fetch_data_skills(endpoint):
        response = requests.get(f"{API_BASE_URL}/{endpoint}")
        return pd.DataFrame(response.json(), columns=['skillname', 'nb_count'])

    df = fetch_data_skills("joboffer_skills/most-demand-skills").head(15)
    fig = px.bar(df, x='skillname', y='nb_count', 
                 title='Top 15 des compétences les plus demandées',
                 labels={'skillname': 'Compétence', 'nb_count': 'Nombre de demandes'},
                 color='nb_count', color_continuous_scale=px.colors.sequential.Viridis)
    st.plotly_chart(fig)


with tab3:
    st.header("Quel est le contrat majoritairement proposé dans les annonces ? ")

    def fetch_data_contract(endpoint):
        print(f"{API_BASE_URL}/{endpoint}")
        response = requests.get(f"{API_BASE_URL}/{endpoint}")
        return pd.DataFrame(response.json(), columns=['contracttype', 'number_offer'])

    all_contracts = fetch_data_contract("joboffers_contracts")
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


with tab4:
    st.header("Quelle est la répartition géographique des offres ?")


    def fetch_full_table_job_offers(endpoint):
        """
        to complete 
        """
        response = requests.get(f"{API_BASE_URL}/{endpoint}")
        return pd.DataFrame(response.json())


    def fetch_full_table_job_offers_alternative(endpoint):
        """
        to complete 
        """
        response = requests.get(f"{API_BASE_URL}/{endpoint}")
        f'{response}'
        return pd.DataFrame(response.json(), columns=['location', 'latitude', 'longitude'])


    def fetch_location_coordinates(endpoint):
        """
        to complete
        """
        response = requests.get(f"{API_BASE_URL}/{endpoint}")
        return pd.DataFrame(response.json(), columns=['location', 'latitude', 'longitude', 'city', 'postal_code'])

    def fetch_full_location_coordinates(endpoint):
        """
        to complete
        """
        response = requests.get(f"{API_BASE_URL}/{endpoint}")
        return pd.DataFrame(response.json(), columns=['location', 'latitude', 'longitude', 'city', 'postal_code'])


    # getting all the offers
    all_offers = fetch_full_table_job_offers("joboffers")
    "all_offers"
    all_offers, all_offers.shape
    #all_offers_alternative = fetch_full_table_job_offers_alternative("joboffers_alternative")
    #all_offers_alternative
    
    # getting latitude and longitude every unique location
    location_coordinates = fetch_full_location_coordinates("coordinates_full")
    #location_coordinates.shape
    "location_coordinates"
    location_coordinates, location_coordinates.shape
    
    # affiche un planisfère de toute la largeur avec points rouges non proportionnels
    st.map(location_coordinates)

    # nombre de "location" nulles
    unknown_locations = all_offers.location.isnull().sum()
    # attention voir si 'Schiltigheim, Strasbourg-Campagne' pose problème (alors 19 lignes à retirer) ou pas 
    f"Pour information sur les **{len(all_offers)} annonces récupérées**, seules {unknown_locations} ont été retirées faute de lieu précisé."
    #on ne garde que les lignes où la 'location' est connue
    not_all_offers = all_offers.dropna(subset = ['location'])
    'not_all_offers'
    not_all_offers, not_all_offers.shape
    
    #array_to_see = not_all_offers['location'].unique()
    #array_to_see
    #f"{len(array_to_see)} unique locations"


    # on crée un nouveau dataframe par merge en ajoutant les colonnes latitude et longitude aux dataframe complet de toutes les locations connues
    all_offers_located = not_all_offers.merge(location_coordinates[['location', 'latitude', 'longitude', 'city', 'postal_code']], on='location', how='left')
    'all_offers_located'
    all_offers_located, all_offers_located.shape
    all_offers_located.insert(18,"job_offer_count", [1 for _ in range(all_offers_located.shape[0])])
    all_offers_located

    all_offers_located.loc[all_offers_located['location'] == 'Schiltigheim, Strasbourg-Campagne', 'latitude'] = 48.60533263495311
    all_offers_located.loc[all_offers_located['location'] == 'Schiltigheim, Strasbourg-Campagne', 'longitude'] = 7.746870067373243
    all_offers_located.loc[all_offers_located['location'] == 'Schiltigheim, Strasbourg-Campagne', 'postal_code'] = 67302
    all_offers_located.loc[all_offers_located['location'] == 'Schiltigheim, Strasbourg-Campagne', 'city'] = 'Schiltigheim'
    #all_offers_located.loc[all_offers_located['location'] == 'Schiltigheim, Strasbourg-Campagne']
    #location["latitude"], location["longitude"], location["city"], location["postal_code"] = zip(*location["location"].apply(lambda x: (48.60, 7.74, 67302, "Schiltigheim") if x == "Schiltigheim, Strasbourg-Campagne" else (None, None, None, None)))
    # étrange il semblerait qu'il y ait des lignes avec une latitude ou une longitude vide mais je ne les vois pas
    #indeed avant quand je récupérais en direct je savais que Schiltigheim, Strasbourg-Campagne n'était pas trouvé
    len1 = len(all_offers_located)
    all_offers_located = all_offers_located.dropna(subset=['latitude', 'longitude'])
    len2 = len(all_offers_located)
    # vérification que tout est bien complété
    len1==len2

    # ajout lien annonce
    # ajout lien url cliquable
    # ajout bouton pour centrer France métropolitaine


    # PLOTLY TEST 

    # Group data by location and count number of job offers at each location
    #all_offers_located['job_offer_count'] = all_offers_located.groupby(['city']).size().reset_index(name='job_offer_count')['job_offer_count']
    #" all_offers_located[['city','job_offer_count']]"
    #all_offers_located[['city','job_offer_count']]
    #"comment ça se fait qu'il ya des None ________________\n\n"
    #all_offers_located['job_offer_count'].shape
    #type(all_offers_located['job_offer_count'])
    #locations = all_offers_located.groupby(['city']).size().reset_index(name='job_offer_count')
    
    
    job_offer_count_sum = all_offers_located.groupby(by="city")["job_offer_count"].sum()


    # First, convert the Series to a dictionary
    job_offer_count_sum_dict = job_offer_count_sum.to_dict()

    # Then, use the map function to create a new column based on the 'city' column
    all_offers_located['sum_of_job_offers'] = all_offers_located['city'].map(job_offer_count_sum_dict)

    #all_offers_located["job_offer_count"] = all_offers_located.groupby(by="city")["job_offer_count"].sum()
    
    'la table job_offer_count_sum:'
    job_offer_count_sum
    'les dimensions de la table job_offer_count_sum:'
    job_offer_count_sum.shape
    number_of_offers_with_location = job_offer_count_sum.sum()
    ' ce qui représentent '
    number_of_offers_with_location
    'annonces'
    # Adding count number of job offers at each location as the last columns 
    # but strange car some are none 
    #all_offers_located.columns
    #all_offers_located.shape
    #all_offers_located
    #all_offers_located["job_offer_count"] = all_offers_located.groupby(['location', 'latitude', 'longitude']).size().reset_index(name='job_offer_count')["job_offer_count"]
    #test_correct_job_counts = all_offers_located.groupby('location').value_counts()
    #st.write("\ntest_correct_job_counts : ")
    #test_correct_job_counts

    #all_offers_double = all_offers_located
    #all_offers_double['location_cleaned'] = all_offers_double['location'].apply(lambda x : x.lower().replace(',','').split())
    #all_offers_double[['location','location_cleaned']]


    #all_offers_located['location_cleaned'] = all_offers_located.loc[all_offers_located['location']].lower()
    #
    #locations = list(all_offers_located['location'])
    ##locations.shape
    #locations
    #f'{type(locations)}'
    #location_list_unique = sorted(set(str(locations).lower().split()))
    #location_list_unique

    # grouping all_offers_located by the "location" column
    #locations['job_offer_count']
    #all_offers_located["job_offer_count"] = locations['job_offer_count']
    
    
    # autre technique via un dictionnaire
    # grouped_locations = all_offers_located.groupby('city')
    # grouped_locations
    # f'{type(grouped_locations)}'
    # # creating a dictionary using dictionary comprehension to access each offer for each location
    # data_by_location = {location: rest_of_the_offer for location, rest_of_the_offer in grouped_locations}
    # f'{type(data_by_location)}'
    #data_by_location

    #st.write(len(data_by_location))
    #st.write(len(data_by_location.keys()))
   # st.write(data_by_location.keys())
   # st.write(data_by_location.values())
    #st.write(len(data_by_location.values()))

    # data_by_location['Lyon, Rhône']
    # f'{type(data_by_location)}'
    #data_by_location.iloc[0,:]
    #len(data_by_location['Paris']['jobofferid'])

    #all_offers_located
    #incorrect_jo_count = all_offers_located['job_offer_count'].isnull().sum()
    #incorrect_jo_count
    #locations["job_offer_count"]
    #st.write(type(locations))
    #st.write(locations.columns)

    # Calculate marker size proportional to the number of job offers
    #max_job_offers = locations['job_offer_count'].max()
    #max_job_offers
    #scaling_factor = 10  # Adjust as needed
    #locations['marker_size'] = (locations['job_offer_count'] / max_job_offers) * scaling_factor
    #all_offers_located['job_offer_count'] = locations['job_offer_count'].copy()
    #all_offers_located['marker_size'] = locations["marker_size"].copy()
    #location_counts

    #all_offers_located
    #locations = all_offers_located.groupby(['location', 'latitude', 'longitude']).size().reset_index(name='job_offer_count')
    #locations = all_offers_located.groupby(['location', 'latitude', 'longitude']).count().reset_index(name='job_offer_count')
    #all_offers_located['job_offer_count'] = all_offers_located.groupby(['location']).count()
    #all_offers_located['job_offer_count'] = all_offers_located.groupby(['location', 'latitude', 'longitude']).agg({'location': 'nunique'}) #> TypeError: incompatible index of inserted column with frame index
    
    
    #all_offers_located['job_offer_count'] = all_offers_located.groupby(['location', 'latitude', 'longitude']).nunique()
    # test = all_offers_located.groupby(['location']).nunique()
    # test
    
    #test = all_offers_located.groupby('location')['joblink'].apply(list)
    #test

    #all_offers_located
    #locations
    import plotly.express as px
    import plotly.graph_objects as go

    #all_offers_located[all_offers_located["location"]==locations['location']] # > ValueError: Can only compare identically-labeled Series objects
    #the_offer_to_display = all_offers_located["location"].reset_index(drop=True).equals(locations["location"].reset_index(drop=True))
    #the_offer_to_display
    #px.set_mapbox_access_token(open(".mapbox_token").read())

    #for key, values in data_by_location:
    #    fig = px.scatter_mapbox(data_by_location[key], lat="latitude", lon="longitude", 
    #                            hover_name="location", hover_data=hover_data,
    #                            color="job_offer_count", size="job_offer_count",
    #                            color_continuous_scale=px.colors.sequential.Viridis, size_max=50, zoom=3)
    #   
    "all_offers_located"
    all_offers_located
    hover_data={"sum_of_job_offers":"sum_of_job_offers"} # remove longitude from hover data
                #'latitude':False, # remove latitude from hover data
                #'location':False,} # remove location from hover data
                #"Lien annonce":data_by_location["location"]["joblink"]}
    #locations
    fig = px.scatter_mapbox(all_offers_located, lat="latitude", lon="longitude", 
                            hover_name="city", hover_data=hover_data,
                            color="sum_of_job_offers", size="sum_of_job_offers",
                            color_continuous_scale=px.colors.sequential.Viridis)#, size_max=50, zoom=3)


    #fig.update_layout(autosize=True)
    #def _max_width_():
    #    max_width_str = f"max-width: 2000px;"
    #    st.markdown(
    #        f"""
    #    <style>
    #    .reportview-container .main .block-container{{
    #        {max_width_str}
    #    }}
    #    </style>    
    #    """,
    #        unsafe_allow_html=True,
    #    )
    #_max_width_()
    #px.defaults.width = 1000
    #px.defaults.height = 500
    #fig.update_layout(width=1000,height=600)
    # fig.add_trace(px.scatter_mapbox(hovertemplate=
    #                         "<b>%{hover_name}</b>" +
    #                         "Nombres d'annonces %{job_offer_count}<br>",))

    #fig.update_traces(marker_colorbar_showticklabels=False)
    #fig = go.Figure(go.Scattermapbox(hovertemplate=
    #                        "<b>%{hover_name}</b>" +
    #                        "Nombres d'annonces : %{job_offer_count}<br>",))
    #fig.update_layout(mapbox_style='open-street-map')
    #fig.update_layout(mapbox_style='outdoors')
    st.plotly_chart(fig, use_container_width=True)
