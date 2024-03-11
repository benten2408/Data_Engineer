#!/usr/bin/env python3
"""
This script uses streamlit to provide an app-like interface
"""

import itertools
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

st.title("Welcome to Job Market Dashboard!")
st.title("Les offres d'emplois DE en France")

if st.checkbox('Show 🇬🇧'):
    """
    ## This is our app created for the project during our DataScientest Data Engineering bootcamp.
    Our chosen topic is Job Market and we decided to focus our data on Data Engineering offers published in France in the previous 30 days.
    Our 5 main KPI answer these questions:
    - which sector 
    """
if st.checkbox('Show 🇫🇷'):
    """
    Voici le résultat de nos recherches sur les offres d'emplois de Data Engineer  publiées en France au cours des 30 derniers jours.\n
    Nous avons récolté les annonces publiées sur Welcome to The Jungle et via l'API d'Adzuna, deux aggrégateurs.\n
    5 tables ont été ainsi créés : JobOffer_Skills, JobOffers, Skills, Sources, Companies.\n
    Notre objectif est de répondre à ces 5 questions : 
    - quel secteur recrute le plus (format probable piechart (ou différent selon le nombre de secteurs uniques)
    - combien d'entreprise par secteur ont publié des annonces ?
    - quelles sont les "skills" les plus demandées ? (format probable barplot)
    - quelle est la zone avec le plus d'offres  (format probable carte avec cercles proportionnelles au nombre d'offres)
    - quel est le contrat majoritaire proposé dans les annonces ? 

    """


df = pd.read_csv('job_offers_wttj.csv')
df = df.dropna(subset=['company']).reset_index(drop=True)
df['sector'] = df.company.apply(lambda x : eval(x)['sector'].split(','))

sector_list = list(itertools.chain.from_iterable(df['sector']))
df_sector = pd.DataFrame(sector_list, columns=["sector"])
df_sector_count = df_sector.value_counts("sector")

st.bar_chart(df_sector_count)

f"len(df_sector_count) {len(df_sector)} , len(sector_list)) {len(sector_list)}"

# comment lier à postgres
# on devra probablement utiliser st.cache_resource

"______________ EN COURS DE CREATION________"
# Initialize connection
conn = st.connection("postgresql", type="sql")

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