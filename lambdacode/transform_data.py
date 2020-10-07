# -*- coding: utf-8 -*-
"""
Created on Sat Oct  3 23:32:54 2020

@author: rahul.wadekar
"""

import pandas as pd

def transform_dataframe(df_nytimes, df_johns_hopkins, initial_data, date_max):
    
    # Convert data to proper format
    df_nytimes['date'] = pd.to_datetime(df_nytimes['date'],format='%Y-%m-%d')
    df_nytimes['cases'] = df_nytimes['cases'].astype('int64')
    df_nytimes['deaths'] = df_nytimes['deaths'].astype('int64')

    # Filter only US data and correct date format
    df_johns_hopkins=df_johns_hopkins[df_johns_hopkins['Country/Region']=='US'][['Date','Recovered']]
    df_johns_hopkins['Date'] = pd.to_datetime(df_johns_hopkins['Date'],format='%Y-%m-%d')
    df_johns_hopkins.rename(columns={'Date':'date'},inplace=True)
    df_johns_hopkins['Recovered'] = df_johns_hopkins['Recovered'].astype('int64')
    
    # if not intial load of data only add data for new dates
    if initial_data==False:
        df_nytimes=df_nytimes[df_nytimes['date'] > date_max]
        df_johns_hopkins=df_johns_hopkins[df_johns_hopkins['date'] > date_max]

    df_merged=pd.merge(df_nytimes,df_johns_hopkins,on='date',how='inner')
    
    df_merged['date'] = pd.to_datetime(df_merged['date'],format='%Y-%m-%d')

    return df_merged
    
