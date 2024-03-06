import itertools
import pandas as pd
import streamlit as st

"""
# Welcome to Job Market Dashboard!

"""

df = pd.read_csv('job_offers_wttj.csv')
df = df.dropna(subset=['company']).reset_index(drop=True)
df['sector'] = df.company.apply(lambda x : eval(x)['sector'].split(','))


sector_list = list(itertools.chain.from_iterable(df['sector']))
df_sector = pd.DataFrame(sector_list, columns=["sector"])
df_sector_count = df_sector.value_counts("sector")

st.bar_chart(df_sector_count)

