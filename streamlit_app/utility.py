
import streamlit as st
import pandas as pd

@st.cache
def download_data(url_data, features)->pd.DataFrame:
    """download latest covid data from https://ourworldindata.org and return . Provide the url and the features you want."""
    df = pd.read_csv(url_data, usecols = features)
    # reorder columns
    df = df[features]
    # set date as index
    df.set_index('date', inplace=True)
    # Converting date to index
    df.index = pd.to_datetime(df.index)
    return df

def filter_country(dataframe:pd.DataFrame, LOCATION:str):
  """Filter dataframe by country. """
  return dataframe[dataframe.location == LOCATION]

def ts_filling(df_country:pd.DataFrame)->pd.DataFrame:
    """Fill missing data and smooth ts in dataframe of single country"""
    # backfill missing data by 2 months
    df = df_country.copy()
    df.fillna(value=None, method='bfill', axis=0, inplace=True, limit=80, downcast=None)
    # forwardfill missing data by 2 months
    df.fillna(value=None, method='ffill', axis=0, inplace=True, limit=80, downcast=None)
    # smooth time series
    for col in df.columns[1:]:
        df[col] = df[col].rolling(21).median()
    # fill in new nas
    df.fillna(value=None, method='bfill', axis=0, inplace=True, limit=30, downcast=None)
    return df

@st.cache
def drop_countries(df:pd.DataFrame, max_missing_pct=0.1)->pd.DataFrame:
    """Drop countries in df containing all countries with at least onnce column having more than max_missing_pct rows with missing data """
    # generate list of countries to keep
    country_list = [] # list of countries to keep
    for country in df['location'].unique():
        # select country
        df_country = filter_country(df, country)
        # fill nas in ts
        df_country = ts_filling(df_country)
        # if there is still missing data, then drop the country from the dataset
        if df_country.isna().sum().max() < len(df_country) * max_missing_pct:
            country_list.append(country)
    # keep only countries in the list i.e. drop the remaining ones
    return df[df['location'].isin(country_list)]