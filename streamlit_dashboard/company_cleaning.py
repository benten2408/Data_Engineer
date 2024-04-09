#!/usr/bin/env python3


import itertools
import os
import pandas as pd
import requests




API_BASE_URL = os.environ['API_BASE_URL']

def fetch_data(endpoint):  
    print(f"{API_BASE_URL}/{endpoint}")
    response = requests.get(f"{API_BASE_URL}/{endpoint}")
    return pd.DataFrame(response.json(), columns=['secteur', 'nombre_offres'])

df_company_sector = fetch_data("companies/company_sector")
df_company_sector['secteur'] = df_company_sector['secteur'].astype(str)



keyword_groups ={
    'aerospatiale': ['aeronautique', 'spatiale'],
    'automobile': ['automobile'],
    'commerce': ['e-commerce', 'grande distribution', 'économie collaborative', 'sales-jobs'],
    'consulting': ['audit', 'consultancy-jobs', 'other-general-jobs', 'graduate-jobs',
                   "incubateur / accelerateur", "accompagnement d'entreprises", 'organisation / management', 
                   'collectivites publiques et territoriales', 'admin-jobs'],
    'droit': ['legal-jobs', 'service juridique'],
    'education': ['education', 'edtech', 'formation', 'teaching-jobs'],
    'energie': ['energie', 'energy-oil-gas-jobs'],
    'environnement': ['environnement', 'developpement durable', 'collectivites publiques et territoriales',
                      'travaux publics', 'batiment'],
    'finance': ['accounting-finance-jobs', 'fintech / insurtech', 'banque', 'assurance',
                'blockchain', 'big data', 'transformation'],
    'hr': ['recrutement'],
    'immobilier': ['property-jobs', 'immobilier particulier', 'immobilier commercial'],
    'ingenieurie': ['engineering-jobs', 'scientific-qa-jobs', 'Ingénieries Spécialisées'],
    'it': ['it-jobs', 'it/digital', 'intelligence artificielle / machine learning', 'logiciels',
           'saas', 'cloud services', 'application mobile', 'transformation', 'it'],
    'logistique': ['logistique', 'robotique', 'Objets connectés', 'logistics-warehouse-jobs', 
                   'trade-construction-jobs', 'manufacturing-jobs', 'electronique'],
    'luxe': ['luxe', 'cosmetique', 'mode'],
    'marketing': ['digital marketing', 'data marketing', 'big data', 'marketing', 'communication',
                  'pr-advertising-marketing-jobs', 'publicite', 'media', 'television', 
                  'adtech', 'production audiovisuelle', 'strategie'],
    'sante': ['pharmaceutique', 'sante', 'biotechnologique', 'healthcare-nursing-jobs', 'nutrition animale'],
    'social': ['social-work-jobs'],
    'tourisme': ['travel-jobs', 'tourisme', 'hotellerie', 'greentech', 'socialtech'],
    'restauration': ['restauration', 'boissons', 'foodtech'],
    'culture': ['musique', 'jeux video', 'creative-design-jobs', 'martech'],
    #'non repertorié': ['unknown']
 }


def assign_group_(secteur_):
    
    if secteur_ is not None:   
        for group, keywords in keyword_groups.items():    
            for keyword in keywords:
                if keyword.lower() in secteur_.lower():
                    return group 


    #Application de la fonction assign_group pour créer une nouvelle colonne group_company
df_company_sector['secteur_'] = df_company_sector['secteur'].apply(assign_group_)

total_offres_par_secteur = df_company_sector.groupby('secteur_')['nombre_offres'].sum()
total_offres_par_secteur = total_offres_par_secteur.sort_values(ascending=False)
