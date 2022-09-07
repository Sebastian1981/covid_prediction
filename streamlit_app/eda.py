import streamlit as st
import pandas as pd

from utility import download_data, drop_countries


# download url of the data
url_data = (r'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv')

# columns of interest
features = ['date',
            'location', 
            'new_cases_per_million',            
            'new_deaths_per_million',
            'icu_patients_per_million']


def run_eda_app():

    if st.button('Download or Update COVID-Data'):
        data_load_state = st.text('Loading data from our-world-in-data.org ...')
        df = download_data(url_data, features)
        data_load_state.text('Loading data from our-world-in-data.org ...done! (using st.cache)')

    if st.button('Inspect Raw Data'):
        df = download_data(url_data, features)
        st.write('The shape of the data is: ', df.shape)
        st.write('The raw dataset contains {} different countries.'.format(df['location'].nunique()))
        st.write('Each country contains {} data rows on average.'.format(int(df.shape[0] / df['location'].nunique())))
        st.write( pd.DataFrame(df.isna().sum(), columns=['Missing Rows']))
    
    if st.button('Drop Countries with Too Much Missing Data'):
        df = download_data(url_data, features)
        df_reduced = drop_countries(df, max_missing_pct=.05)
        st.write('The shape of the reduced data is: ', df_reduced.shape)
        st.write('The reduced dataset contains {} different countries.'.format(df_reduced['location'].nunique()))
        st.write('Each country contains {} data rows on average.'.format(int(df_reduced.shape[0] / df_reduced['location'].nunique())))
        st.write( pd.DataFrame(df_reduced.isna().sum(), columns=['Missing Rows']))