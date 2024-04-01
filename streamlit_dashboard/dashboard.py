#!/usr/bin/env python3
"""
This script uses streamlit to provide an app-like interface
enabling some interaction with the vizualisations
"""
import pandas as pd
import streamlit as st
import requests
import os
import plotly.express as px
from datetime import datetime
import company_cleaning
import sector_cleaning

API_BASE_URL = os.environ['API_BASE_URL']

if 'access_token' not in st.session_state:
    st.session_state['access_token'] = None

headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}

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
        st.link_button("rendez-vous sur PGAdmin","http://localhost:8888/",type='primary')
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
    - quels **secteurs** recrutent le plus ?   
    - combien d\'**entreprises** par secteur ont publié des annonces ?   
    - quelles sont les **compétences** les plus demandées ?  
    - quel est le **contrat** majoritairement proposé dans les annonces ?  
    - quelle est la **zone géographique** avec le plus d\'offres ?  
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
        st.header("Quelle est la répartition géographique des offres ?")

        def fetch_full_table(endpoint):
            response = requests.get(f"{API_BASE_URL}/{endpoint}", headers=headers)
            return pd.DataFrame(response.json())

        # getting all the offers
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
        # associer le bon nombres d'offres disponibles en fonction de la ville via la function function map
        all_offers_located['sum_of_job_offers'] = all_offers_located['city'].map(job_offer_count_sum_dict)
        px.set_mapbox_access_token(open(".mapbox_token").read())
        fig = px.scatter_mapbox(all_offers_located, lat="latitude", lon="longitude",
                                color="sum_of_job_offers", size="sum_of_job_offers",
                                custom_data=[all_offers_located['city'], all_offers_located['sum_of_job_offers'], (all_offers_located['sum_of_job_offers']*100)/all_offers_located.shape[0]],
                                center={'lat':46.49388889,'lon':2.60277778},
                                color_continuous_scale=px.colors.sequential.Viridis, 
                                size_max=50, zoom=5, mapbox_style='light')
        fig.update_traces(hovertemplate="<br>".join(["<b>%{customdata[0]}</b>",
            "Nombre d'annonces : %{customdata[1]}",
            "Pourcentage : %{customdata[2]:.1f} %"]))
        fig.update_layout(height=800)
        
        #st.plotly_chart(fig, use_container_width=True)
        from streamlit_plotly_mapbox_events import plotly_mapbox_events
        # Create an instance of the plotly_mapbox_events component
        mapbox_events = plotly_mapbox_events(
            fig,
            click_event=True,
            override_height=800
        )

        # Display the captured events
        plot_name_holder_clicked = st.empty()
        plot_name_holder_clicked.write(f"Clicked Point: {mapbox_events[0]}")

        def fetch_company_name_id(endpoint):
            response = requests.get(f"{API_BASE_URL}/{endpoint}", headers=headers)
            return pd.DataFrame(response.json(), columns=['companyname', 'companyid'])

        city_to_display = st.selectbox("Visualisez les annonces disponibles dans la ville de …", 
                                        options=all_offers_located.city.sort_values().unique(),
                                        placeholder="Paris", disabled=False, label_visibility="visible")
        to_display = all_offers_located[all_offers_located['city'] == city_to_display]
        to_display_extract = all_offers_located[all_offers_located['city'] == city_to_display].head(10)
        reste_des_annonces = len(to_display) - len(to_display_extract)
        if len(to_display) == 1:
            st.write(f"Voici la seule annonce disponible à **{city_to_display}** :")
        elif len(to_display_extract) <+ 10:
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
     
