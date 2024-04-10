#!/usr/bin/env python3
"""
This script contains the functions that feed the tab4
and tab5 questions of our streamlit app
"""

import pandas as pd
import streamlit as st
import requests
import os
import plotly.express as px
from datetime import datetime
from streamlit_plotly_events import plotly_events

API_BASE_URL = os.environ['API_BASE_URL']

if 'access_token' not in st.session_state:
    st.session_state['access_token'] = None
headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}

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
    
def fetch_data_contract(endpoint):
    print(f"{API_BASE_URL}/{endpoint}")
    response = requests.get(f"{API_BASE_URL}/{endpoint}", headers=headers)
    return pd.DataFrame(response.json(), columns=['contracttype', 'number_offer'])

def fetch_company_name_id(endpoint):
    response = requests.get(f"{API_BASE_URL}/{endpoint}", headers=headers)
    return pd.DataFrame(response.json(), columns=['companyname', 'companyid'])

def display_offer_verbose(df, city_to_display,number_of_offer):
    to_display = df[df['city'] == city_to_display]
    to_display_extract = df[df['city'] == city_to_display].head(number_of_offer)
    reste_des_annonces = len(to_display) - len(to_display_extract)
    if len(to_display) == 1:
        st.write(f"Voici la seule annonce disponible à **{city_to_display}** :")
    elif len(to_display) <= len(to_display_extract):
        st.write(f"Voici les {len(to_display_extract)} annonces disponibles à **{city_to_display}** :")
    else:
        st.write(f"Voici {len(to_display_extract)} des annonces disponibles à **{city_to_display}** :")
    
    company_name_id = fetch_company_name_id("company_name_id")
    for index, row in to_display_extract.reset_index().iterrows():
        company_name = company_name_id[company_name_id['companyid'] == row['companyid']].iloc[0, 0]
        if index+1 >= 2:
            st.divider()
        now = datetime.now()
        days = (now - datetime.strptime(row['publicationdate'], '%Y-%m-%d')).days
        source = "l'API d'Adzuna" if {row['sourceid']} == 1 else "Welcome to the Jungle"
        details_start = f'''
        - L'annonce n°{index+1} est **{row['title']}** chez **{company_name}**.  \n Publiée il y a {days} jours sur {source},'''
        details_salary = f''' la grille salariale n'est pas mentionnée.''' if (row["salary"] is '0' or "Non spécifié.") else f''' le salaire indiqué est {row["salary"]}.'''
        details_description = f''' La description fournie commence par ''' if row["descriptions"] is not None else ''' Désolée, nous n'avons pas pu obtenir plus d'informations pour cette annonce.'''
        st.write(details_start + details_salary + details_description)    
        if row["descriptions"]:
            col1, col2 = st.columns([0.03, 0.97])
            with col2: 
                container = st.container(height=100,border=True)
                container.write(f'''{row["descriptions"]}''')    
                container.empty() 
        details_end = f'''  Pour postuler, rendez-vous directement sur [ce lien]({row['joblink']}).'''
        st.write(details_end)   

    if reste_des_annonces:
        if st.button(f"Pour voir l'ensemble des offres offres localisées à {city_to_display} dont les **{reste_des_annonces} autres**", help="Le dataframe complet va s'afficher si vous cliquez", type="primary", use_container_width=True):
            st.dataframe(to_display)

def fetch_full_table(endpoint):
    response = requests.get(f"{API_BASE_URL}/{endpoint}", headers=headers)
    return pd.DataFrame(response.json())

def presentation():
    all_offers_full = fetch_full_table("joboffers")      
    # getting latitude, longitude, city every unique location
    location_coordinates = fetch_full_table("coordinates_full")
    # nombre de "location" nulles
    unknown_locations = all_offers_full.location.isnull().sum()
    #on ne garde que les lignes où la 'location' est connue
    not_all_offers = all_offers_full.dropna(subset = ['location'])
    # attention voir si 'Schiltigheim, Strasbourg-Campagne' pose problème (alors 19 lignes à retirer) ou pas 
    # on crée un nouveau dataframe par merge en ajoutant les 4 colonnes au dataframe complet de toutes les joboffers localisées
    all_offers_located = not_all_offers.merge(location_coordinates[['location', 'latitude', 'longitude', 'city', 'postal_code']], on='location', how='left')
    # on intégre une colonne comme simple décompte qui serra additionner pour obtenir le nombre d'offre par localisation
    all_offers_located.insert(18, "job_offer_count", [1 for _ in range(all_offers_located.shape[0])])
    # remplacer les offres localisées en France par Paris
    all_offers_located.loc[all_offers_located['location'] == 'France', 'latitude'] = 48.859
    all_offers_located.loc[all_offers_located['location'] == 'France', 'longitude'] = 2.347
    all_offers_located.loc[all_offers_located['location'] == 'France', 'city'] = 'Paris'
    all_offers_located.loc[all_offers_located['location'] == 'France', 'postal_code'] = 75001
    # compléter pour le cas de Schiltigheim étrangemment pas trouvé par l'api adresses gouv
    # et Saint-Denis qui s'est retrouvé en Libye à cause de la moyenne > ou à corriger autrement en les excluant avant l'opération mean
    all_offers_located.loc[all_offers_located['location'] == 'Saint-Denis', 'latitude'] = 48.9366028
    all_offers_located.loc[all_offers_located['location'] == 'Saint-Denis', 'longitude'] = 2.3583204
    all_offers_located.loc[all_offers_located['location'] == 'Saint-Denis', 'postal_code'] = 93200
    all_offers_located.loc[all_offers_located['location'] == 'Schiltigheim, Strasbourg-Campagne', 'latitude'] = 48.60533263495311
    all_offers_located.loc[all_offers_located['location'] == 'Schiltigheim, Strasbourg-Campagne', 'longitude'] = 7.746870067373243
    all_offers_located.loc[all_offers_located['location'] == 'Schiltigheim, Strasbourg-Campagne', 'postal_code'] = 67302
    all_offers_located.loc[all_offers_located['location'] == 'Schiltigheim, Strasbourg-Campagne', 'city'] = 'Schiltigheim'
    len1 = len(all_offers_located)
    all_offers_located = all_offers_located.dropna(subset=['latitude', 'longitude'])
    len2 = len(all_offers_located)
    # vérification que tout est bien complété
    #len1==len2
    # nettoyer pour n'avoir qu'un point par ville
    all_offers_located.loc[all_offers_located['location'].str.contains('Paris'), 'city'] = 'Paris'
    city_mean_coordinates = all_offers_located.groupby('city').agg({'latitude': 'mean', 'longitude': 'mean'}).reset_index()
    all_offers_located = all_offers_located.merge(city_mean_coordinates, on='city', suffixes=('', '_mean'))
    all_offers_located['latitude'] = all_offers_located['latitude_mean']
    all_offers_located['longitude'] = all_offers_located['longitude_mean']
    all_offers_located.drop(['latitude_mean', 'longitude_mean'], axis=1, inplace=True)
    distinct_city = all_offers_located.groupby(by="city")["city"].unique().value_counts().sum()
    st.write(f"Pour information - sur les {len(all_offers_full):,} annonces récupérées - seules {unknown_locations} ont été retirées faute de lieu précisé. \
                Voici la répartition des **{len(not_all_offers):,} offres restantes dans {distinct_city} villes**.".replace(',', ' '))
    job_offer_count_sum = all_offers_located.groupby(by="city")["job_offer_count"].sum()
    job_offer_count_sum_dict = job_offer_count_sum.to_dict()
    all_offers_located['sum_of_job_offers'] = all_offers_located['city'].map(job_offer_count_sum_dict)
    fig = create_px_scatter_mapbox(all_offers_located)
    return fig, all_offers_located

def tall_presentation(fig, offers_df):
    st.plotly_chart(fig, use_container_width=True)
    city_to_display = st.selectbox(label="Visualisez les annonces disponibles dans la ville de …",
                                    options=offers_df.city.sort_values().unique(),
                                    disabled=False, label_visibility="visible")
    display_offer_verbose(offers_df, city_to_display, 10)
    
    
def create_px_scatter_mapbox(all_offers_located):
    px.set_mapbox_access_token(open(".mapbox_token").read())
    fig = px.scatter_mapbox(all_offers_located, lat="latitude", lon="longitude",
                            color="sum_of_job_offers", size="sum_of_job_offers",
                            labels={"sum_of_job_offers" : "Nombre d'offres d'emploi"},
                            custom_data=[all_offers_located['city'], all_offers_located['sum_of_job_offers'], (all_offers_located['sum_of_job_offers']*100)/all_offers_located.shape[0]],
                            center={'lat':46.49388889,'lon':2.60277778},
                            color_continuous_scale=px.colors.sequential.Viridis, 
                            size_max=50, zoom=5, mapbox_style='light')
    fig.update_traces(hovertemplate="<br>".join(["<b>%{customdata[0]}</b>",
        "Nombre d'annonces : %{customdata[1]}",
        "Pourcentage : %{customdata[2]:.1f} %"])) 
    fig.update_layout(height=800, width=1000)
    return fig


def short_presentation(fig, offers_df):
    col_map, col_df = st.columns(2)
    with col_map:
        selected_points = plotly_events(fig, click_event=True,override_height=1000) #dommage échelle un peu moins jolie
    with col_df:
        if not selected_points:
            st.write("  \nSi vous cliquez sur l'une des villes, les annonces liées s'afficheront ci-dessous.")
        if selected_points:
            index_city = selected_points[0]['pointNumber']
            city_hovered = offers_df.loc[index_city]['city']
            display_offer_verbose(offers_df, city_hovered, 3)
            st.cache_data.clear()
