'''
crime.py
--------

This file collects raw crime data, and summarizes the information
for each census tract. It is called by make_zone_facts.py

The resulting dataset from this file looks like:

zone_type |   zone  | crime  | violent_crime  | non_violent_crime
----------|---------|--------|----------------|------------------
tract     | 000100  |   392  |             5  |               387
tract     | 000201  |    21  |             0  |                21
tract     | 000202  |   390  |             6  |               384
tract     | 000300  |   108  |             4  |               104
tract     | 000400  |    25  |             0  |                25
'''
from . import utils
from sqlalchemy import create_engine
import pandas as pd

def mark_violent(row):
    '''Returns 1 if a violent crime else 0. Use apply with axis=1'''
    if row.offense in {'ASSAULT W/DANGEROUS WEAPON', 'SEX ABUSE', 'HOMICIDE'}:
        return 1
    if row.method in {'GUN', 'KNIFE'}:
        return 1
    return 0

def get_crime_for_year(path):
    df = pd.read_csv(path)
    df.columns = df.columns.str.lower()

    # Todo, filter by start_date
    df = df[['report_dat', 'census_tract', 'ward', 'neighborhood_cluster', 'offense', 'method']]
    df['neighborhood_cluster'] = utils.just_digits(df['neighborhood_cluster'])
    df = filter_date(df)

    df['tract'] = df.census_tract.apply(utils.fix_tract)
    df = df.drop('census_tract', axis=1)
    df['violent_crime'] = df.apply(mark_violent, axis=1)

    df['non_violent_crime'] = df.violent_crime.apply(lambda x: 1 if x == 0 else 0)
    df['crime'] = 1

    return df

def filter_date(df):
    '''Returns observations within the past year.'''
    df.report_dat = pd.to_datetime(df.report_dat.str.slice(0,10))
    return df[df.report_dat > utils.year_ago()]

def get_crime_data():
    paths = utils.get_paths_for_data('crime', years=utils.get_years())
    df = pd.concat([get_crime_for_year(path) for path in paths])
    data = []
    for geo in ['tract', 'neighborhood_cluster', 'ward']:
        temp = df.groupby(geo)[['crime', 'violent_crime', 'non_violent_crime']].sum()
        temp['zone_type'] = geo
        temp['zone'] = temp.index
        data.append(temp)
    return pd.concat(data).reset_index(drop=True)

def load_crime_data():
    '''Actually loads the data into the db.'''
    try:
        get_crime_data().to_sql(
            'new_crime',
            create_engine(utils.get_credentials('docker_database_connect_str')),
            if_exists='replace',
            index=False)
        return True
    except:
        return False
if __name__ == '__main__':
    print(get_crime_data())