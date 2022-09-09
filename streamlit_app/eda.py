import streamlit as st
import os
from pathlib import Path
import pandas as pd
import plotly.express as px
from utility import download_data, drop_countries, filter_country, ts_filling, add_new_deaths_pct_change, add_case_fatality_rate


# set directories
rootdir = os.getcwd()
DATAPATH = Path(rootdir) / 'data'
MODELPATH = Path(rootdir) / 'models'
Path(DATAPATH).mkdir(parents=True, exist_ok=True)
Path(MODELPATH).mkdir(parents=True, exist_ok=True)

# download url of the data
url_data = (r'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv')

# columns of interest
features = ['date',
            'location', 
            'new_cases_per_million',            
            'new_deaths_per_million',
            'icu_patients_per_million']


def run_eda_app():
                    
    ########################################
    # Download Data
    ########################################
    if st.button('Update COVID-Data'):
        data_load_state = st.text('Loading data from our-world-in-data.org ...')
        df = download_data(url_data, features)
        data_load_state.text('Loading data from our-world-in-data.org ...done!')
        df.to_csv(DATAPATH / 'df_raw.csv') # save dataset to local folder    

    ########################################
    # Filter Data Due Missing Values
    ########################################
    st.markdown('**Assure Data Quality:**')
    max_pct_missing = st.slider('Set Maximal Percent Missing Rows in each Country: ', 1, 20, 5)
    df = pd.read_csv(DATAPATH / 'df_raw.csv', index_col='date')
    df.index = pd.to_datetime(df.index)
    df_reduced = drop_countries(df, max_missing_pct=max_pct_missing/100)
    st.write('{} countries left after filtering.'.format(df_reduced['location'].nunique()))

    
    ########################################
    # Select Country
    ########################################
    st.markdown('**Select Country:**')    
    countries = [country for country in df_reduced['location'].unique()]
    country_selected = st.selectbox('Select Country from Dropdown', options=countries)
    df_country = filter_country(df_reduced, country_selected)
    df_country = ts_filling(df_country)
    df_country = add_new_deaths_pct_change(df_country)
    df_country = add_case_fatality_rate(df_country)
    df_country.to_csv(DATAPATH / 'df_country.csv') # save dataset to local folder
    

    ########################################
    # Visualize Data
    ########################################
    st.markdown('**Select Feature for Data Visualization:**')
    st.markdown('- inspect the time series of all features for data quality')
    st.markdown('- if data quality is bad, the model performance is likely to be poor')
    cols = [feat for feat in df_country.columns][1:]
    feature_selected = st.selectbox('Select Feature', options=cols)
    # visualize 
    fig = px.line(df_country, x=df_country.index, 
                    y=[feature_selected], 
                    title = feature_selected, 
                    width=800,
                    height=400,
                    template = 'plotly_dark')
    fig.update_layout({'legend_orientation':'h'})
    st.write(fig)




    

    