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
from datetime import datetime
import company_cleaning
import sector_cleaning
from mapbox import create_map
import mapboxgl
# import locale

# loc = locale.getlocale(locale.LC_ALL)
# st.write(loc)
# locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8') ## Error: unsupported locale setting  apt-get install apt-get install packages.txt
#from api_backend/app.main import get_user_from_postgresql
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
    with st.sidebar:

        def fetch_full_table(endpoint):
            response = requests.get(f"{API_BASE_URL}/{endpoint}", headers=headers)
            st.write(response)
            return pd.DataFrame(response.json())

        st.sidebar.header("Les données derrières ces visualisations")
        side_bar = f'''
        Comme vous pourrez le lire dans notre [rapport🚨 version pdf à mettre avant soutenance⚠️](https://docs.google.com/document/d/1RdEme_BMk8fh_ZRzwjCSCIh9AFD4mGTBaRY09J685dA/edit?usp=sharing), nous avons créé 7 tables : 
        - Companies
        - Job Offers
        - JobOffer_Skills
        - Locations
        - Skills
        - Sources
        - Users
        \n
        Pour les voir directement dans notre base de données'''
        st.write(side_bar)
        st.link_button("rendez-vous sur PGAdmin","http://localhost:8888/")
        end = ''' avec les identifiants fournis dans le fichier .env.  \n Sinon pour voir une de ces tables au format brut ici, faites votre choix :'''
        st.write(end)
        table_to_display = st.selectbox("Quelle table souhaiteriez-vous voir ?",
                                        options=['Companies', 'Job Offers', 'JobOffer_Skills', 'Locations', 'Skills', 'Sources', 'Users'],
                                        placeholder="Job Offers", label_visibility="collapsed")
        st.write("""🚨⚠️🚧VOIR AVEC NAM car erreur 401 Undocumented	Error: Unauthorized Response body{"detail": "Not authenticated"}""")
        """
        match table_to_display:
            case "Companies":
                companies = fetch_full_table("/companies")
                st.dataframe(companies)
            case "Job Offers":
                st.dataframe(fetch_full_table("/joboffers"))
            case "JobOffer_Skills":
                st.dataframe(fetch_full_table("/joboffer_skills"))
            case "Locations":
                st.dataframe(fetch_full_table("/coordinates_full"))
            case "Skills":
                st.dataframe(fetch_full_table("/skills"))
            case "Sources":
                st.dataframe(fetch_full_table("/sources"))
            case "Users":
                st.write("That is our secret")
                #st.dataframe(get_user_from_postgresql())
            """


    titre = "Projet Jobmarket : les offres d'emplois pour Data Engineers en France"
    st.title(titre)
    introduction = '''
    Dans le cadre de la [formation de Data Engineer par DataScientest](https://datascientest.com/formation-data-engineer) au format bootcamp de janvier à avril 2024, nous avons eu l'occasion de réaliser un projet en groupe.  
    Voici le résultat de nos recherches sur les **offres d\'emplois de Data Engineer publiées en France au cours des 30 derniers jours** *.  
    Au total nous avons récolté **1 342 annonces** soit sur [Welcome to The Jungle](https://www.welcometothejungle.com/en) soit via l'[API d'Adzuna](https://www.adzuna.fr), deux aggrégateurs.  
    Notre objectif est de répondre à ces **5 questions** :   
    - quels secteurs recrutent le plus ?   
    - combien d\'entreprises par secteur ont publié des annonces ?   
    - quelles sont les compétences les plus demandées ?  
    - quel est le contrat majoritairement proposé dans les annonces ?  
    - quelle est la zone géographique avec le plus d\'offres ?  
      \n _(*) à la date du 24 février 2024_'''
    st.markdown(introduction)


    tab0, tab1, tab2, tab3, tab4 = st.tabs(["Les secteurs qui recrutent",
                                            "Les entreprises par secteurs",
                                            "Les compétences recherchées",
                                            "Les contrats proposés",
                                            "Les villes concernées"])

    with tab0:
        st.header("Quels secteurs recrutent le plus ?")

        fig1 = px.bar(
            x=company_cleaning.df_company_sector.group_company, 
            y=company_cleaning.df_company_sector.nombre_offres,
            title='Nombre d\'offres par secteur',
            labels={'x': 'Secteur', 'y': 'Total offres'},
            color =company_cleaning.df_company_sector.nombre_offres, 
            color_continuous_scale=px.colors.sequential.Viridis    
        )
        st.plotly_chart(fig1)

    with tab1:
        st.header("Combien d'entreprises par secteur ont publié des annonces ?")
        sector_cleaning.sectors_counts
        fig2 = px.bar(
            x=sector_cleaning.sectors_counts.index, 
            y=sector_cleaning.sectors_counts.values,
            title='Nombre d\'entreprises par secteur', 
            labels={'x': 'SECTEUR', 'y': 'Nombre d\'entreprises'},
            color=sector_cleaning.sectors_counts.values,
            color_continuous_scale=px.colors.sequential.Viridis
            )
        st.plotly_chart(fig2)


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
            st.write(f"  \n Initialement, les {all_contracts.number_offer.sum():,} annonces* récupérées sont réparties en {all_contracts['contracttype'].nunique()} types de contrats possibles.\n".replace(',', ' '))
            unspecified_contracts = all_contracts.loc[all_contracts.contracttype.isnull(), ['number_offer']].values[0]

            all_contracts['contracttype'] = all_contracts['contracttype'].apply(lambda x : sort_contracttypes(x))
            unspecified_contracts += all_contracts.contracttype.isnull().sum()
            known_contracts = all_contracts.dropna(subset = ['contracttype'])
            result = known_contracts.groupby('contracttype')['number_offer'].sum().reset_index()
            result.sort_values('number_offer', inplace=True, ascending=False)
            details = f'''
            Pour une meilleure lisibilité, nous les avons rassemblées en **5 catégories** :  
            - CDI  
            - CDD  
            - Freelance  
            - Alternance  
            - Stage  \n
             (*) sans compter donc _les {int(unspecified_contracts)} annonces_ où le contrat n'est pas mentionné et qui ont donc été retirées du jeu de données.  \
            \n
            La figure à droite représente donc la répartition des **{int(result['number_offer'].sum())} annonces restantes**.'''
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

        #on ne garde que les lignes où la 'location' est connue
        not_all_offers = all_offers.dropna(subset = ['location'])
        # attention voir si 'Schiltigheim, Strasbourg-Campagne' pose problème (alors 19 lignes à retirer) ou pas 
        st.write(f"Pour information - sur les {len(all_offers):,} annonces récupérées - seules {unknown_locations} ont été retirées faute de lieu précisé. \
                 \n Voici la répartition des **{len(not_all_offers):,} offres restantes**.".replace(',', ' '))

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
                    "Nombre d'annonces " : all_offers_located['sum_of_job_offers'], #à améliorer
                    'latitude':False, # remove latitude from hover data
                    'longitude':False, # remove longitude from hover data
                    'location':False} # remove location from hover data
                    #"Lien d'annonce " : 'to figure out', #à améliorer
        
        fig = px.scatter_mapbox(all_offers_located, lat="latitude", lon="longitude",
                                hover_name="city", hover_data=hover_data,
                                color="sum_of_job_offers", size="sum_of_job_offers",
                                center={'lat':46.49388889,'lon':2.60277778},
                                color_continuous_scale=px.colors.sequential.Viridis, 
                                size_max=50, zoom=5, mapbox_style='light')# à améliorer pour mieux gérer la taille de départ qui ne doit pas être minuscule


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

        #fig.update_layout(autosize=True)

        #fig.update_layout(mapbox_style='open-street-map')
        #fig.update_layout(mapbox_style='outdoors')
        #fig.update_layout(mapbox_style='streets')
        #fig.update_layout(mapbox_style='light')
        
        #st.plotly_chart(fig, use_container_width=True)
        #st.plotly_chart(fig, height=1800,use_container_width=True)
        
        #width = st.sidebar.slider("plot width", 100, 1000, 10)
        #height = st.sidebar.slider("plot height", 100, 1000, 10)
        #fig.update_layout(width=width, height=height)
        fig.update_layout(height=800)
        st.plotly_chart(fig, use_container_width=True)


        def fetch_company_name_id(endpoint):
            """
            to complete
            """
            response = requests.get(f"{API_BASE_URL}/{endpoint}", headers=headers)
            #st.write(response)
            return pd.DataFrame(response.json(), columns=['companyname', 'companyid'])


        city_to_display = st.selectbox("Visualisez les annonces disponibles dans la ville de …", 
                                        options=all_offers_located.city.sort_values().unique(),
                                        placeholder="Paris", disabled=False, label_visibility="visible")
        #st.write(city_to_display)
        #st.dataframe(all_offers_located.loc[all_offers_located['city' == city_to_display]])
        #all_offers_located.loc[all_offers_located['city' == city_to_display], "joblink"]
        to_display = all_offers_located[all_offers_located['city'] == city_to_display]
        to_display_extract = all_offers_located[all_offers_located['city'] == city_to_display].head(10)
        if len(to_display) == 1:
            st.write(f"Voici la seule annonce disponible à **{city_to_display}** :")
        else:
            st.write(f"Voici {len(to_display_extract)} des annonces disponibles à **{city_to_display}** :")
        
        company_name_id = fetch_company_name_id("company_name_id")
        for index, row in to_display_extract.reset_index().iterrows():
            company_name = company_name_id[company_name_id['companyid'] == row['companyid']].iloc[0, 0]
            if index+1 >= 2:
                st.divider()
            #date = datetime.strptime(row['publicationdate'], '%Y-%m-%d').strftime('le %d %B %Y')
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
    
        if len(to_display) > len(to_display_extract):
            reste_des_annonces = len(to_display) - len(to_display_extract)
            if st.button(f"Pour voir l'ensemble des offres offres localisées à {city_to_display} dont les {reste_des_annonces} suivantes", help="Le dataframe va s'afficher ci-après", type="primary", use_container_width=True):
                st.dataframe(to_display)
        # testing to display dom tom
        #map =  create_map()

        # Render the map
        #mapboxgl.show(map)
        #st.map(map)

        #st.components.v1.html('<iframe src="v1.html" width=800 height=600></iframe>')



    

    # catégorie d'améliorations : 
        # MAP ajout bouton pour centrer France métropolitaine 
        # MAP trouver solution pour découper avec dom tom en bas à gauche et idf en haut à gauche agrandie
    # réfléchir au lien map <> selectbox 
    # si souris hover map > selectbox active 
    # si selectbox active > point sur map affiche
    
    # amélioration quand descriptif sur plusieurs lignes
    # réfléchir à potentielle proposition pour aller plus loin et voir l'intégralité des offres

