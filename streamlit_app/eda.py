import streamlit as st
import os
from pathlib import Path
from datetime import datetime
import pandas as pd
import plotly.express as px
from utility import download_data, drop_countries, filter_country, ts_filling, add_new_deaths_pct_change, add_case_fatality_rate, get_start_end_date

# set directories
rootdir = os.getcwd()
DATAPATH = Path(rootdir) / 'data'
Path(DATAPATH).mkdir(parents=True, exist_ok=True)

# download url of the data
url_data = (r'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv')

# columns of interest
features = ['date',
            'location', 
            'new_cases_per_million',            
            'new_deaths_per_million',
            'icu_patients_per_million']


def run_eda_app():

    st.header('Get the Data!')
    if st.button('Download or Update COVID-Data'):
        data_load_state = st.text('Loading data from our-world-in-data.org ...')
        df = download_data(url_data, features)
        data_load_state.text('Loading data from our-world-in-data.org ...done! (using st.cache)')

    st.subheader('Inspect Raw Data of All Countries')
    df = download_data(url_data, features)
    st.write('The shape of the data is: ', df.shape)
    st.write('The raw dataset contains {} different countries.'.format(df['location'].nunique()))
    st.write('Each country contains {} data rows on average.'.format(int(df.shape[0] / df['location'].nunique())))
    st.write( pd.DataFrame(df.isna().sum(), columns=['Missing Rows']))    


    st.header('Set Missing Rows Percentage-Threshold!')
    max_pct_missing = st.slider('Set Max Percent Missing Data Rows: ', 1, 20, 5)
    df_reduced = drop_countries(df, max_missing_pct=max_pct_missing/100)
    st.subheader('Inspect Filtered Data of {} Countries Left'.format(df_reduced['location'].nunique()))
    st.write('Each country contains {} data rows on average.'.format(int(df_reduced.shape[0] / df_reduced['location'].nunique())))
    st.write( pd.DataFrame(df_reduced.isna().sum(), columns=['Missing Rows']))

    # select country
    st.header('Select Country!')
    countries = [country for country in df_reduced['location'].unique()]
    country_selected = st.selectbox('Select Country from Dropdown', options=countries)
    df_country = filter_country(df_reduced, country_selected)
    st.write('Country selected: ', country_selected)
    st.subheader('Inspect Data of Selected Country') 
    st.write('{} contains {} rows and {} columns'.format(country_selected, df_country.shape[0], df_country.shape[1]))
    st.write( pd.DataFrame(df_country.isna().sum(), columns=['Missing Rows']))
    st.write(df_country)

    st.header('Prepare {}´s Data!'.format(country_selected))
    st.write('na-filling, smoothing, feature engineering...') 
    st.write('{} contains {} rows and {} columns'.format(country_selected, df_country.shape[0], df_country.shape[1]))
    df_country = ts_filling(df_country)
    df_country = add_new_deaths_pct_change(df_country)
    df_country = add_case_fatality_rate(df_country)
    st.write( pd.DataFrame(df_country.isna().sum(), columns=['Missing Rows']))
    st.write(df_country)
    # save dataset to local folder
    df_country.to_csv(DATAPATH / 'df_country.csv')
    

    # visualize
    st.header('Visualize {}´s Data!'.format(country_selected))
    start_date, end_date = get_start_end_date(df_country)
    split_date = st.slider("Select Training Period", 
                           datetime(pd.to_datetime(start_date).year, pd.to_datetime(start_date).month, pd.to_datetime(start_date).day),
                           datetime(pd.to_datetime(end_date).year, pd.to_datetime(end_date).month, pd.to_datetime(end_date).day),
                           datetime(pd.to_datetime(start_date).year, pd.to_datetime(start_date).month+6, pd.to_datetime(start_date).day), 
                           format="YY/MM/DD")
    split_date = str(split_date)[:-9]
    
    fig = px.line(df_country, 
                    x=df_country.index, 
                    y=['icu_patients_per_million'], 
                    title = '{}: COVID-19 Patients in ICU per Million'.format(country_selected), 
                    width=1200,
                    height=600,
                    template = 'plotly_dark')
    fig.add_vline(x=split_date, line_width=3, line_dash="dash", line_color="red")
    fig.add_vrect(x0=start_date, x1=split_date, row="all", col=1,
                annotation_text="training period", annotation_position="top left",
                fillcolor="green", opacity=0.15, line_width=0)
    fig.add_vrect(x0=split_date, x1=end_date, row="all", col=1,
                annotation_text="testing period", annotation_position="top left",
                fillcolor="red", opacity=0.15, line_width=0)
    st.write(fig)




    

    