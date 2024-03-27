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
st.set_page_config(layout="wide")
titre = "Projet Jobmarket : les offres d'emplois pour Data Engineers en France"
st.title(titre)


# pour rendre l'ensemble en onglet 
# https://docs.streamlit.io/library/api-reference/layout/st.tabs

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


url_wttj = "https://www.welcometothejungle.com/en" #to edit to link to the proper page
url_adzuna = "https://www.adzuna.fr" #to edit to link to the proper page
#st.write("check out this [link](%s)" % url)
#st.markdown("check out this [link](%s)" % url)

introduction = f"""Dans le cadre de la formation de Data Engineer par DataScientest au format bootcamp de janvier à avril 2024, nous avons eu l'occasion de réaliser un projet en groupe.\n
Voici le résultat de nos recherches sur les offres d'emplois de Data Engineer publiées en France au cours des 30 derniers jours.\n
Nous avons récolté les annonces publiées sur [Welcome to The Jungle](https://www.welcometothejungle.com/en) et via l'[API d'Adzuna](https://www.adzuna.fr), deux aggrégateurs.
Notre objectif est de répondre à ces 5 questions : 
- quels secteurs recrutent le plus ?
- combien d'entreprises par secteur ont publié des annonces ?
- quelles sont les \"skills\"  _(remplacer par compétences ?)_ les plus demandées ?
- quel est le contrat majoritairement proposé dans les annonces ? 
- quelle est la zone géographique avec le plus d'offres ?  _(remplacer par Quelle est la répartition géographique des offres ?)_"""
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
    st.header("Quelles sont les \"skills\"  _(à remplacer par compétences ?)_ les plus demandées ?")


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


with tab4:
    st.header("Quelle est la zone géographique avec le plus d'offres ?  _(à remplacer par Quelle est la répartition géographique des offres ?)_")


    def fetch_full_data(endpoint):
        """
        returns 
        """
        response = requests.get(f"{API_BASE_URL}/{endpoint}")
        return pd.DataFrame(response.json())


    def fetch_location_coordinates(endpoint):
        """
        returns 
        """
        response = requests.get(f"{API_BASE_URL}/{endpoint}")
        return pd.DataFrame(response.json(), columns=['location', 'latitude', 'longitude'])

    all_offers = fetch_full_data("joboffers")
    #all_offers
    location_coordinates = fetch_location_coordinates("coordinates")
    #location_coordinates
    st.map(location_coordinates)

    unknown_locations = all_offers.location.isnull().sum()
    not_all_offers = all_offers.dropna(subset = ['location'])

    all_offers_located = pd.merge(not_all_offers, location_coordinates, on='location', how='left')
    all_offers_located = all_offers_located.dropna(subset=['latitude', 'longitude'])
    # Display merged dataframe
    #all_offers_located
    #st.map(all_offers_located)

    # ajout nombre d'offres
    # ajout proportionalité taille via couleur
    # ajout lien annonce
    # ajout lien url cliquable
    # ajout bouton pour centrer France métropolitaine



    # ALTAIR FIRST TEST

    import altair as alt
    import matplotlib.pyplot as plt

    print(alt.topo_feature('france_topo.json', 'feature').to_dict())

    #a_com_topo = d3.json("https://static.data.gouv.fr/resources/contours-des-communes-de-france-simplifie-avec-regions-et-departement-doutre-mer-rapproches/20210523-101900/a-com2021-2154-topo.json")

    # France GeoJSON data source
    france_geojson_url = 'https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/regions.geojson'

    # Create Altair's topo feature for France
    france = alt.topo_feature(france_geojson_url, 'regions')


    # France GeoJSON data source
    france_geojson_url = 'https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/regions.geojson'

    # Create a base map layer
    base_map = alt.Chart(alt.Data(url=france_geojson_url)).mark_geoshape(
        fill='lightgray',
        stroke='white'
    ).encode(
        tooltip=['properties.nom:N']
    ).properties(
        width=600,
        height=400
    )

    # Display the base map
    #base_map


    # TOPO FIRST TEST 
    # 
    # import topojson # install from https://github.com/sgillies
    # import json
    # 
    # with open("france_topo.json") as json_file:
    #     "bloud"
    #     jdata = json_file.read()
    #     topoJSON = json.loads(jdata)
    # 
    # topoJSON
    # 
    # with open("france_topo.json", 'r') as f:
    #     data = json.load(f)
    # # parse topojson file using `object_name`
    # topo = topojson.Topology(data, object_name="data")
    # topo.toposimplify(4).to_svg()



    # PYDECK TEST 


    import pydeck as pdk


    # Defining the Latitude and Longite as 0 to centre the map
    # setting it at the center of France
    lat0=47.0
    lon0=2.0
    #zoom 4.3 to show Corsica completely
    # other choice could be 
    # location=[all_offers_located['latitude'].mean(), all_offers_located['longitude'].mean()]
    # but because some offers are way over the map not fun 

    legend="test"

    st.pydeck_chart(pdk.Deck(
        map_style=None,
        initial_view_state=pdk.ViewState(
            latitude=lat0,
            longitude=lon0,
            zoom=4.3,
            pitch=20,
            description=legend,
        ),
        
        layers=[(pdk.Layer(
        "ColumnLayer",
        data=all_offers_located,
        get_position='[longitude, latitude]',
        elevation_scale=50,
        pickable=True,
        elevation_range=[50, 500],
        get_fill_color=[180, 0, 200, 140],
        extruded=True,
        radius=25,
        coverage=50,
        auto_highlight=True,)
    ),
            pdk.Layer(
                "GeoJsonLayer",
                data=all_offers_located,
                get_position='[longitude, latitude]',
                get_color='[200, 30, 0, 160]',
                #get_radius=20,
            ),
        ],
    ))


    # PLOTLY TEST 

    # Group data by location and count number of job offers at each location
    locations = all_offers_located.groupby(['location', 'latitude', 'longitude']).size().reset_index(name='job_offer_count')
    #locations
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


    locations
    import plotly.express as px
    import plotly.graph_objects as go



    #px.set_mapbox_access_token(open(".mapbox_token").read())

    hover_data={'longitude':False, # remove longitude from hover data
                'latitude':False, # remove latitude from hover data
                'location':False,} # remove location from hover data
                #"Lien vers l'annonce":True, # add other column, RESTE A FAIRE LIEN})
    #locations
    fig = px.scatter_mapbox(locations, lat="latitude", lon="longitude", 
                            hover_name= "location", hover_data=hover_data,
                            color='job_offer_count', size='job_offer_count',
                            color_continuous_scale=px.colors.sequential.Viridis, size_max=50, zoom=3)

    fig.add_trace(go.Scatter(hovertemplate=
                            "<b>%{hover_name}</b>" +
                            "Nombres d'annonces %{job_offer_count}<br>",))

    fig.update_traces(marker_colorbar_showticklabels=False)
    #fig = go.Figure(go.Scattermapbox(hovertemplate=
    #                        "<b>%{hover_name}</b>" +
    #                        "Nombres d'annonces : %{job_offer_count}<br>",))
    #fig.update_layout(mapbox_style='open-street-map')
    fig.update_layout(mapbox_style='outdoors')
    st.plotly_chart(fig, use_cotainer_width=True)
