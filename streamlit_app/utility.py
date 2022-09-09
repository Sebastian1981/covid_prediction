
import streamlit as st
import os
from pathlib import Path
import pandas as pd
from pycaret.regression import *
import joblib

# set directories
rootdir = os.getcwd()
DATAPATH = Path(rootdir) / 'data'
MODELPATH = Path(rootdir) / 'models'

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


def add_new_deaths_pct_change(df_country:pd.DataFrame)->pd.DataFrame:
    """calculate percent change between the median number of deaths 14 days earlier and the median number of deaths today"""
    df = df_country.copy()
    df['new_deaths_per_million_pct_change'] = df['new_deaths_per_million'].pct_change(periods=14, fill_method='pad', freq='D')
    df['new_deaths_per_million_pct_change'].fillna(value=None, method='bfill', axis=0, inplace=True, limit=30, downcast=None)
    df.dropna(axis=0, inplace=True)
    return df

def add_case_fatality_rate(df_country:pd.DataFrame)->pd.DataFrame:
    """calculate case fatality rate CFR for single country df; CFR is the ratio between the 14-day median number of deaths and the 14-day median number of cases 14 days earlier """
    df = df_country.copy()
    df['case_fatality_rate'] = df['new_deaths_per_million'] / df['new_cases_per_million'].shift(14)
    # set inf values to zero i.e. the assumption is when there are no cases then there are no deaths
    df['case_fatality_rate'][df['new_cases_per_million']==0] = 0
    # set na values to zero i.e. the assumption is when there are no deaths and at the same time zero cases, then CFR is still zero
    df['case_fatality_rate'][df['new_deaths_per_million']==0] = 0
    # cfr above 100% makes no sense
    df['case_fatality_rate'][df['case_fatality_rate']>1] = 1
    # do a little smoothing i.e. average over 7 days
    df['case_fatality_rate'] = df['case_fatality_rate'].rolling(7).median()
    # fill in new nas
    df['case_fatality_rate'].fillna(value=None, method='bfill', axis=0, inplace=True, limit=30, downcast=None)
    df.dropna(axis=0, inplace=True)
    return df

def filter_date(dataframe:pd.DataFrame, start_date:str, end_date:str)->pd.DataFrame:
    """Filter dataframe by date range including start_date and end_date. """
    return dataframe.loc[(dataframe.index >= start_date) & (dataframe.index <= end_date)]

def get_start_end_date(df_country:pd.DataFrame)->str:
    """Get start and end dates in dataframe of single country """
    start_date = str(df_country.index[0])[:-9]
    end_date = str(df_country.index[-1])[:-9]
    return start_date, end_date

def train_test_split(df_country:pd.DataFrame, split_date:str)->pd.DataFrame:
    """Split into train and test given a split date"""
    start_date, end_date = get_start_end_date(df_country)
    day_after_split_date = str(pd.to_datetime(split_date) + pd.DateOffset(days=1))[:-9]
    df_train = filter_date(df_country, start_date=start_date, end_date=split_date)
    df_test = filter_date(df_country, start_date=day_after_split_date, end_date=end_date) 
    return df_train, df_test





##########################################################################
# Modeling
##########################################################################
@st.cache
def init_model_pipe(df_train, target_name):
    """Initialize a pycaret modeling preprocessing pipeline; Pass the training data and the target name 
    """
    setup(df_train, 
        target = target_name,
        #ignore_features = ['location', 'new_cases_per_million', 'new_deaths_per_million_pct_change'],
        ignore_features = ['location'],
        train_size = .99999,
        data_split_shuffle = False, 
        fold_strategy = 'timeseries', fold=2,
        imputation_type = 'simple',
        numeric_imputation = 'median',
        remove_multicollinearity = True,
        multicollinearity_threshold = 0.3,
        feature_interaction=False,
        polynomial_features=False,
        remove_outliers = False,
        transform_target=False,
        transformation = False,
        normalize = False,
        feature_selection = False,
        feature_selection_method='boruta',
        feature_selection_threshold = 0.3,
        silent = True, 
        verbose = True, 
        session_id = 123)

    # train light gradient boosting machine because its very fast and works good on few data points
    best_model = create_model('lightgbm') 
    # save model
    joblib.dump(best_model, MODELPATH / 'best_model.pkl') 