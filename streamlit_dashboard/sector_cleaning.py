#!/usr/bin/env python3

import itertools
import os
import pandas as pd
import requests


API_BASE_URL = os.environ['API_BASE_URL']


def fetch_data(endpoint):
    print(f"{API_BASE_URL}/{endpoint}")
    response = requests.get(f"{API_BASE_URL}/{endpoint}")   
    return pd.DataFrame(response.json(), columns=['sector'])

df_sector = fetch_data("companies/sector")
df_sector['sector'] = df_sector['sector'].astype(str)


sector_groups ={
    
    'aerospatiale': ['aeronautique', 'spatiale'],
    'automobile': ['automobile'],
    'commerce': ['e-commerce', 'grande distribution', 'économie collaborative'],
    'consulting': ['audit', 'consultancy-jobs', 'other-general-jobs', 'graduate-jobs',
                   "incubateur / accelerateur", "accompagnement d'entreprises", 'organisation / management', 
                   'collectivites publiques et territoriales'],
    'droit': ['legal-jobs', 'service juridique'],
    'education': ['education', 'edtech', 'formation', 'teaching-jobs'],
    'energie': ['energie', 'energy-oil-gas-jobs'],
    'environnement': ['environnement', 'developpement durable', 'collectivites publiques et territoriales',
                      'travaux publics', 'batiment'],
    'finance': ['accounting-finance-jobs', 'fintech / insurtech', 'banque', 'assurance',
                'blockchain', 'big data', 'transformation'],
    'hr': ['recrutement'],
    'immobilier': ['property-jobs', 'immobilier particulier', 'immobilier commercial'],
    'ingenieurie': ['engineering-jobs', 'scientific-qa-jobs', 'ingenieries specialisees'],
    'it': ['it-jobs', 'it/digital', 'intelligence artificielle / machine learning', 'logiciels',
           'saas', 'cloud services', 'application mobile', 'transformation', 'it'],
    'logistique': ['logistique', 'robotique', 'objets connectes', 'logistics-warehouse-jobs', 
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
}

def assign_group(secteur):
    
    if secteur is not None:   
        for group, keywords in sector_groups.items():    
            for keyword in keywords:
                if keyword.lower() in secteur.lower():
                    return group 

df_sector['secteur'] = df_sector['sector'].apply(assign_group)
sectors_counts = df_sector['secteur'].value_counts()
sectors_counts = sectors_counts.rename('Nombre d\'entreprises')
