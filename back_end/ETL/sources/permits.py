'''
permits.py
----------

This file collects raw building permit data, and summarizes the information
for each census tract. It is called by make_zone_facts.py

The resulting dataset from this file looks like:

    tract  | construction_permits | total_permits
    -------|----------------------|--------------
    000100 |                 231  |          575
    000201 |                   2  |            6
    000202 |                 145  |          363
    000300 |                 102  |          351
    000400 |                  77  |          204
'''
from . import utils
import pandas as pd
URL = 'https://opendata.arcgis.com/datasets/52e671890cb445eba9023313b1a85804_8.csv'
def get_permit_data():
    df = pd.read_csv(URL)
    df.columns = df.columns.str.lower()
    df['construction_permits'] = df['permit_type_name'].apply(
            lambda x: 1 if x == 'CONSTRUCTION' else 0)
    df['total_permits'] = 1

    # Get census tract
    df = utils.get_census_tract_for_data(df, 'longitude', 'latitude')
    df = df[['tract', 'ward', 'neighborhoodcluster', 'construction_permits', 'total_permits']]

    df = df.rename(columns={'neighborhoodcluster': 'neighborhood_cluster'})
    df['neighborhood_cluster'] = utils.just_digits(df['neighborhood_cluster'])

    return [df.groupby(geo)[['construction_permits', 'total_permits']].sum() \
            for geo in ['tract', 'neighborhood_cluster', 'ward']]