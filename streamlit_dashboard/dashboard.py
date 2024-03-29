#!/usr/bin/env python3
"""
This script uses streamlit to provide an app-like interface
enabling some interaction with the vizualisations
"""
#ces imports seront in fine dans streamlit_dashboard/requirements.txt
import pandas as pd
import streamlit as st
#import matplotlib.pyplot as plt
import requests
import os
#import json
#import time 
import plotly.express as px
#import plotly.graph_objects as go

API_BASE_URL = os.environ['API_BASE_URL']

#st.write(st.session_state)
#st.write(st.session_state=={})


if 'access_token' not in st.session_state:
    st.session_state['access_token'] = None
#st.write(st.session_state)
headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}

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

# a ranger dans un autre fichier
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
    considered_cdi = ["cdi", "contract", "full_time", "part_time", "permanent", "partiel"]
    for type_contract in considered_cdi:
        if type_contract in contract_type:
            return "CDI"
    if "cdd" in contract_type:
        return "CDD"
    elif "alternance" in contract_type:
        return "Alternance"
    elif "stage" in contract_type:
        return "Stage"
    elif "freelance" in contract_type:
        return "Freelance"
    else:
        return None

def run():
    titre = "Projet Jobmarket : les offres d'emplois pour Data Engineers en France"
    st.title(titre)
    introduction = '''Dans le cadre de la [formation de Data Engineer par DataScientest](https://datascientest.com/formation-data-engineer) au format bootcamp de janvier à avril 2024, nous avons eu l'occasion de réaliser un projet en groupe.  
    Voici le résultat de nos recherches sur les **offres d\'emplois de Data Engineer publiées en France au cours des 30 derniers jours**.  
    Nous avons récolté les annonces publiées sur [Welcome to The Jungle](https://www.welcometothejungle.com/en) et via l'[API d'Adzuna](https://www.adzuna.fr), deux aggrégateurs.  
    Notre objectif est de répondre à ces 5 questions :   
      - quels secteurs recrutent le plus ?   
      - combien d\'entreprises par secteur ont publié des annonces ?   
      - quelles sont les compétences les plus demandées ?  
      - quel est le contrat majoritairement proposé dans les annonces ?  
      - quelle est la zone géographique avec le plus d\'offres ?  '''
    st.markdown(introduction)
    tab0, tab1, tab2, tab3, tab4 = st.tabs(["Les secteurs qui recrutent",
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
            response = requests.get(
                f"{API_BASE_URL}/{endpoint}",
                headers=headers
            )
            return pd.DataFrame(response.json(), columns=['skillname', 'nb_count'])

        df = fetch_data_skills("joboffer_skills/most-demanded-skills").head(15)
        fig = px.bar(df, x='skillname', y='nb_count', 
                    title='Top 15 des compétences les plus demandées',
                    labels={'skillname': 'Compétence', 'nb_count': 'Nombre de demandes'},
                    color='nb_count', color_continuous_scale=px.colors.sequential.Viridis)
        st.plotly_chart(fig)

    with tab3:
        st.header("Quel est le contrat majoritairement proposé dans les annonces ?")

        col0, col1 = st.columns(2)

        def fetch_data_contract(endpoint):
            print(f"{API_BASE_URL}/{endpoint}")
            response = requests.get(f"{API_BASE_URL}/{endpoint}", headers=headers)
            return pd.DataFrame(response.json(), columns=['contracttype', 'number_offer'])

        all_contracts = fetch_data_contract("joboffers_contracts")
        
        with col0:
            # Worth mentionning, the nunique() method does NOT include the None values
            st.write(f"  \n Initialement, les **{all_contracts.number_offer.sum()} annonces** * récupérées sont réparties en {all_contracts['contracttype'].nunique()} types de contrat possibles.\n")
            unspecified_contracts = all_contracts.loc[all_contracts.contracttype.isnull(), ['number_offer']].values[0]

            all_contracts['contracttype'] = all_contracts['contracttype'].apply(lambda x : sort_contracttypes(x))
            unspecified_contracts += all_contracts.contracttype.isnull().sum()
            known_contracts = all_contracts.dropna(subset = ['contracttype'])
            result = known_contracts.groupby('contracttype')['number_offer'].sum().reset_index()
            result.sort_values('number_offer', inplace=True, ascending=False)
            details = f'''Pour une meilleure lisibilité, nous les avons rassemblées en **5 catégories** :  
            - CDI  
            - CDD  
            - Freelance  
            - Alternance  
            - Stage  
             * _sans compter donc les {int(unspecified_contracts)} annonces_ où le contrat n'est pas mentionné et qui ont donc été retirées du jeu de données.  \n \
             La figure représente donc la répartition des {int(result['number_offer'].sum())} annonces restantes'''
            st.markdown(details)

        with col1:
            fig = px.bar(
                result,  x="contracttype", y="number_offer", 
                labels={'contracttype': 'Contrats ', 'number_offer': 'Nombre d\'annonces '},
                text="number_offer",
                color='number_offer', color_continuous_scale=px.colors.sequential.Viridis
            )
            fig.update_yaxes(showgrid=True, gridwidth=1, title_text='')
            fig.update_xaxes(showgrid=False, title_text='')
            fig.update_layout(autosize=True)
            fig.update_layout(title={'text': "Les 5 contrats possibles",
                'y':0.9,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'})
            st.plotly_chart(fig)

    with tab4:
        st.header("Quelle est la répartition géographique des offres ?")

        def fetch_full_table_job_offers(endpoint):
            """
            to complete 
            """
            response = requests.get(f"{API_BASE_URL}/{endpoint}", headers=headers)
            return pd.DataFrame(response.json())

        def fetch_full_table_job_offers_alternative(endpoint):
            """
            to complete 
            """
            response = requests.get(f"{API_BASE_URL}/{endpoint}", headers=headers)
            f'{response}'
            return pd.DataFrame(response.json(), columns=['location', 'latitude', 'longitude'])

        def fetch_location_coordinates(endpoint):
            """
            to complete
            """
            response = requests.get(f"{API_BASE_URL}/{endpoint}", headers=headers)
            return pd.DataFrame(response.json(), columns=['location', 'latitude', 'longitude'])

        def fetch_full_location_coordinates(endpoint):
            """
            to complete
            """
            response = requests.get(f"{API_BASE_URL}/{endpoint}", headers=headers)
            return pd.DataFrame(response.json(), columns=['location', 'latitude', 'longitude', 'city', 'postal_code'])


        # getting all the offers
        all_offers = fetch_full_table_job_offers("joboffers")
        
        # getting latitude, longitude, city every unique location
        location_coordinates = fetch_full_location_coordinates("coordinates_full")

        # affiche un planisfère de toute la largeur avec points rouges non proportionnels
        #st.map(location_coordinates)

        # nombre de "location" nulles
        unknown_locations = all_offers.location.isnull().sum()

        # attention voir si 'Schiltigheim, Strasbourg-Campagne' pose problème (alors 19 lignes à retirer) ou pas 
        f"Pour information sur les **{len(all_offers)} annonces récupérées**, seules {unknown_locations} ont été retirées faute de lieu précisé."
        #on ne garde que les lignes où la 'location' est connue
        not_all_offers = all_offers.dropna(subset = ['location'])

        # on crée un nouveau dataframe par merge en ajoutant les 4 colonnes au dataframe complet de toutes les joboffers localisées
        all_offers_located = not_all_offers.merge(location_coordinates[['location', 'latitude', 'longitude', 'city', 'postal_code']], on='location', how='left')

        # on intégre une colonne comme simple décompte qui serra additionner pour obtenir le nombre d'offre par localisation
        all_offers_located.insert(18, "job_offer_count", [1 for _ in range(all_offers_located.shape[0])])
        
        # remplacer les offres localisées en France par Paris
        all_offers_located.loc[all_offers_located['location'] == 'France', 'latitude'] = 48.859
        all_offers_located.loc[all_offers_located['location'] == 'France', 'longitude'] = 2.347
        all_offers_located.loc[all_offers_located['location'] == 'France', 'city'] = 'Paris'
        all_offers_located.loc[all_offers_located['location'] == 'France', 'postal_code'] = 75001
        
        # compléter pour le cas de Schiltigheim étrangemment pas trouvé par l'api
        all_offers_located.loc[all_offers_located['location'] == 'Schiltigheim, Strasbourg-Campagne', 'latitude'] = 48.60533263495311
        all_offers_located.loc[all_offers_located['location'] == 'Schiltigheim, Strasbourg-Campagne', 'longitude'] = 7.746870067373243
        all_offers_located.loc[all_offers_located['location'] == 'Schiltigheim, Strasbourg-Campagne', 'postal_code'] = 67302
        all_offers_located.loc[all_offers_located['location'] == 'Schiltigheim, Strasbourg-Campagne', 'city'] = 'Schiltigheim'
        len1 = len(all_offers_located)
        all_offers_located = all_offers_located.dropna(subset=['latitude', 'longitude'])
        len2 = len(all_offers_located)
        # vérification que tout est bien complété
        #len1==len2

        all_offers_located.loc[all_offers_located['location'].str.contains('Paris'), 'city'] = 'Paris'

        city_mean_coordinates = all_offers_located.groupby('city').agg({'latitude': 'mean', 'longitude': 'mean'}).reset_index()

        # Merge mean coordinates with original DataFrame on 'city'
        all_offers_located = all_offers_located.merge(city_mean_coordinates, on='city', suffixes=('', '_mean'))

        # Update latitude and longitude columns with mean values
        all_offers_located['latitude'] = all_offers_located['latitude_mean']
        all_offers_located['longitude'] = all_offers_located['longitude_mean']
        # Drop redundant columns
        all_offers_located.drop(['latitude_mean', 'longitude_mean'], axis=1, inplace=True)


        job_offer_count_sum = all_offers_located.groupby(by="city")["job_offer_count"].sum()
        job_offer_count_sum_dict = job_offer_count_sum.to_dict()

        #st.dataframe(all_offers_located)
        # map function to create a new column based on the 'city' column
        all_offers_located['sum_of_job_offers'] = all_offers_located['city'].map(job_offer_count_sum_dict)

        #job_offer_link_dict = {city: {'number_joblinks':len(list(group['joblink'])), 'job_links':list(group['joblink'])} for city, group in all_offers_located.groupby("city")}
        #all_offers_located['list_of_joblinks'] = all_offers_located['city'].map(job_offer_link_dict)

        # Calculate marker size proportional to the number of job offers
        max_job_offers = all_offers_located['sum_of_job_offers'].max()
        #max_job_offers
        scaling_factor = 10  # Adjust as needed
        all_offers_located['marker_size'] = (all_offers_located['sum_of_job_offers'] / max_job_offers) * scaling_factor
        #all_offers_located['job_offer_count'] = locations['job_offer_count'].copy()
        #all_offers_located['marker_size'] = locations["marker_size"].copy()
        #location_counts

        #for key, values in data_by_location:
        #    fig = px.scatter_mapbox(data_by_location[key], lat="latitude", lon="longitude", 
        #                            hover_name="location", hover_data=hover_data,
        #                            color="job_offer_count", size="job_offer_count",
        #                            color_continuous_scale=px.colors.sequential.Viridis, size_max=50, zoom=3)
        #   
        #st.dataframe(all_offers_located)
        px.set_mapbox_access_token(open(".mapbox_token").read())
        #"all_offers_located"

        hover_data = {"sum_of_job_offers":False,
                    "Nombre d'annonce " : all_offers_located['sum_of_job_offers'], #à améliorer
                    'latitude':False, # remove latitude from hover data
                    'longitude':False, # remove longitude from hover data
                    'location':False} # remove location from hover data
                    #"Lien d'annonce " : 'to figure out', #à améliorer
        
        fig = px.scatter_mapbox(all_offers_located, lat="latitude", lon="longitude",
                                hover_name="city", hover_data=hover_data,
                                color="sum_of_job_offers", size="sum_of_job_offers",
                                color_continuous_scale=px.colors.sequential.Viridis, 
                                size_max=50, zoom=4.5)# à améliorer pour mieux gérer la taille de départ qui ne doit pas être minuscule


        # my_customdata = []  # something you want to hover
        # plot_data = [
        #     go.Scattermapbox(
        #     lon=all_offers_located["longitude"], 
        #     lat=all_offers_located["latitude"], 
        #     mode="markers", 
        #     text=all_offers_located['city'], 
        #     customdata=my_customdata,
        #     hovertemplate="<b>%{text}</b><br><br>" + "longitude: %{lon:.2f}<br>" + "latitude: %{lat:.2f}<br>" + "altitude: %{customdata[0]:.0f}<br>"+ "ppm: %{marker.color:.2f}<extra></extra>",
        # )]

        fig.update_layout(autosize=True)

        #fig.update_layout(mapbox_style='open-street-map')
        #fig.update_layout(mapbox_style='outdoors')
        #fig.update_layout(mapbox_style='streets')
        fig.update_layout(mapbox_style='light')
        
        #st.plotly_chart(fig, use_container_width=True)
        #st.plotly_chart(fig, height=1800,use_container_width=True)
        
        #width = st.sidebar.slider("plot width", 100, 1000, 10)
        #height = st.sidebar.slider("plot height", 100, 1000, 10)
        #fig.update_layout(width=width, height=height)

        fig.update_layout(width=1000, height=800)
        st.plotly_chart(fig)

    # ajout lien annonce
    # ajout lien url cliquable
    
    # ajout bouton pour centrer France métropolitaine 
    # trouver solution pour découper avec dom tom en bas à gauche et idf en haut à gauche agrandie

    # corriger les coordonées différentes pour des mêmes noms de villes 
