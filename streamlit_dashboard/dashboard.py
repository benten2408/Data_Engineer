#!/usr/bin/env python3
"""
This script uses streamlit to provide an app-like interface
enabling some interaction with the vizualisations
"""
import pandas as pd
import streamlit as st
import requests
import os
import sys
import plotly.express as px
from datetime import datetime
import company_cleaning
import sector_cleaning
import tab3_4

API_BASE_URL = os.environ['API_BASE_URL']

if 'access_token' not in st.session_state:
    st.session_state['access_token'] = None

headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}


def run():
    with st.sidebar:

        def fetch_full_table(endpoint):
            response = requests.get(f"{API_BASE_URL}/{endpoint}", headers=headers)
            return pd.DataFrame(response.json())

        st.sidebar.header("Les données derrières ces visualisations")
        side_bar = f'''
        Comme vous pourrez le lire dans notre [rapport](https://drive.google.com/file/d/1-CGRgKLvHO1lEAQwkvEdz_OBPvjpsJOy/view?usp=sharing), nous avons créé 7 tables : 
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
        st.link_button("rendez-vous sur PGAdmin","http://localhost:8888/",type='primary')
        end = ''' avec les identifiants fournis dans le fichier _.env_.  \n'''
        st.write(end)


    titre = "Projet Jobmarket : les offres d'emplois pour Data Engineers en France"
    st.title(titre)

    introduction = '''
    Dans le cadre de la [formation de Data Engineer par DataScientest](https://datascientest.com/formation-data-engineer) au format bootcamp de janvier à avril 2024, nous avons eu l'occasion de réaliser un projet en groupe.  
    Voici le résultat de nos recherches sur les **offres d\'emplois de Data Engineer publiées en France au cours des 30 derniers jours** *.  
    Au total nous avons récolté **1 342 annonces** soit sur [Welcome to The Jungle](https://www.welcometothejungle.com/en) soit via l'[API d'Adzuna](https://www.adzuna.fr), deux aggrégateurs.  
    Notre objectif est de répondre à ces **5 questions** :   
    - quels **secteurs** recrutent le plus ?   
    - combien d\'**entreprises** par secteur ont publié des annonces ?   
    - quelles sont les **compétences** les plus demandées ?  
    - quel est le **contrat** majoritairement proposé dans les annonces ?  
    - quelle est la **répartition géographique** de ces offres ?  
      \n _(*) à la date du 24 février 2024_'''
    st.markdown(introduction)


    tab0, tab1, tab2, tab3, tab4, tab5 = st.tabs(["Les secteurs qui recrutent",
                                            "Les entreprises par secteurs",
                                            "Les compétences recherchées",
                                            "Les contrats proposés",
                                            "Les villes concernées", "… et les dataframe bruts"])

    with tab0:
        #st.header("Quels secteurs recrutent le plus ?")

        company_cleaning.total_offres_par_secteur
        top_sectors = company_cleaning.total_offres_par_secteur.head(10)
        fig1 = px.pie(
            names=top_sectors.index,  # Noms des secteurs
            values=top_sectors.values,  # Nombre d'offres par secteur
            title=f'Top 10 des secteurs qui recrutent',
            color_discrete_sequence=px.colors.sequential.Viridis
        )
        st.plotly_chart(fig1)

    with tab1:
        #st.header("Combien d'entreprises par secteur ont publié des annonces ?")
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
        #st.header("Quelles sont les compétences les plus demandées ?")
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
        #st.header("Quel est le contrat majoritairement proposé dans les annonces ?")
        col0, col1 = st.columns(2)
        all_contracts = tab3_4.fetch_data_contract("joboffers_contracts")
        
        with col0:
            # Worth mentionning, the nunique() method does NOT include the None values
            st.write(f"  \n Initialement, les {all_contracts.number_offer.sum():,} annonces* récupérées sont réparties en {all_contracts['contracttype'].nunique()} types de contrats possibles.\n".replace(',', ' '))
            unspecified_contracts = all_contracts.loc[all_contracts.contracttype.isnull(), ['number_offer']].values[0]

            all_contracts['contracttype'] = all_contracts['contracttype'].apply(lambda x : tab3_4.sort_contracttypes(x))
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
            ##### La figure à droite représente donc la répartition des {int(result['number_offer'].sum())} annonces restantes.'''
            st.markdown(details)

        with col1:
            fig2 = px.pie(result, values="number_offer", names="contracttype", 
                        color=result.number_offer, hole=0.3,
                        labels={'contracttype': 'Type de contrat ', 
                                'number_offer': 'Nombre d\'annonces '},
                        color_discrete_sequence=px.colors.sequential.Viridis_r)
            fig2.update_layout(title={'text': "Les 5 contrats possibles",
                                      'y':0.95,'x':0.5, 'xanchor': 'center',
                                      'yanchor': 'top'}, height=600)
            fig2.update_traces(marker = dict(line = dict(color = 'white', width = 1)))
            fig2.update_traces(textinfo='label+percent',hoverinfo='label', showlegend = False, rotation=180)
            st.plotly_chart(fig2, use_container_height=True, use_container_width=True)

    with tab4:
        #st.header("Quelle est la répartition géographique des offres ?")

        type_presentation = st.radio(horizontal=True,
            label="Comment préférez-vous voir les annonces ?",
            options=["1. Une carte suivie d'un sélecteur de villes", "2. Une carte cliquable avec les annonces visibles à côté"],
            captions = ["La version plus moderne mais à scroller", "Une version de plotly plus ancienne, mais un seul écran"])

        fig, offers_df = tab3_4.presentation()

        if type_presentation == "1. Une carte suivie d'un sélecteur de villes":
            tab3_4.tall_presentation(fig, offers_df)
        else:
            tab3_4.short_presentation(fig, offers_df)

    with tab5:
        table_to_display = st.selectbox("Quelle table souhaiteriez-vous voir ?",
                                        options=['Companies', 'Job Offers', 'JobOffer_Skills', 'Locations', 'Skills', 'Sources', 'Users'],
                                        placeholder="Job Offers")
        match table_to_display:
            case "Companies":
                st.dataframe(fetch_full_table("companies"))
            case "Job Offers":
                st.dataframe(fetch_full_table("joboffers"))
            case "JobOffer_Skills":
                st.dataframe(fetch_full_table("joboffer_skills"))
            case "Locations":
                st.dataframe(fetch_full_table("coordinates_full"))
            case "Skills":
                st.dataframe(fetch_full_table("skills"))
            case "Sources":
                st.dataframe(fetch_full_table("sources"))
            case "Users":
                #st.dataframe(fetch_full_table("users"))
                st.write("C'est un secret.")
                #st.dataframe(get_user_from_postgresql())
