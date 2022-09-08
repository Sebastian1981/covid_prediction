import os
from pathlib import Path
import joblib
from datetime import datetime
import streamlit as st
import pandas as pd
import plotly.express as px
from pycaret.regression import *
from utility import get_start_end_date, train_test_split


# set directories
rootdir = os.getcwd()
DATAPATH = Path(rootdir) / 'data'
MODELPATH = Path(rootdir) / 'models'
Path(MODELPATH).mkdir(parents=True, exist_ok=True)


def run_model_app():
    
    ########################################
    # import country data
    ########################################
    df_country = pd.read_csv(DATAPATH / 'df_country.csv', index_col='date')
    df_country.index = pd.to_datetime(df_country.index)
    country_selected = df_country['location'][0]
    st.header('Forecast ICU Patients for {}!'.format(country_selected))

    ########################################
    # Define Forecast Horizont
    ########################################
    st.subheader('Define Forecast Horizont')
    forecast_horizont = st.slider("Select Forecasting Horizont", 1, 28, 7)
    target_name = 'icu_patients_per_million' + '_' + str(forecast_horizont) + 'days_ahead'
    df_country[target_name] = df_country['icu_patients_per_million'].shift(-forecast_horizont)
    df_country.dropna(axis=0, inplace=True)
    
    ########################################
    # Train & Test Split
    ########################################
    st.subheader('Seperate Data into Training and Testing Periods!')
    start_date, end_date = get_start_end_date(df_country)
    split_date = st.slider("Select Training Period", 
                           datetime(pd.to_datetime(start_date).year, pd.to_datetime(start_date).month, pd.to_datetime(start_date).day),
                           datetime(pd.to_datetime(end_date).year, pd.to_datetime(end_date).month, pd.to_datetime(end_date).day),
                           datetime(pd.to_datetime(start_date).year, pd.to_datetime(start_date).month+6, pd.to_datetime(start_date).day), 
                           format="YY/MM/DD")
    split_date = str(split_date)[:-9]
    df_train, df_test = train_test_split(df_country, split_date = split_date)
    
    # visualize 
    fig = px.line(df_country, 
                    x=df_country.index, 
                    y=['icu_patients_per_million', target_name], 
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


    ########################################
    # Model Training
    ########################################    
    st.subheader('Train Machine Learning Model!')
    if st.button('Train Model'):
        train_state = st.text('Training Model...(30s-3min!)')
        s = setup(df_train, 
            target = target_name,
            #ignore_features = ['location', 'new_cases_per_million', 'new_deaths_per_million_pct_change'],
            ignore_features = ['location'],
            train_size = .99,
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

        # compare models
        #best_model = compare_models(#include=['xgboost', 'dummy', 'lr', 'lightgbm'],
        #                            include=['lightgbm','dt','gbr'],
        #                            #include=['xgboost', 'lightgbm','lr'],
        #                            #include=['lr','dummy'],
        #                            sort='R2', 
        #                            verbose=True,
        #                            n_select = 1)


        # train light gradient boosting machine
        best_model = create_model('lightgbm') 
        # tune best model
        best_model = tune_model(best_model)
        # finalize model on all training data
        best_model = finalize_model(best_model)
        # save model
        joblib.dump(best_model, MODELPATH / 'best_model.pkl')
        train_state = st.text('Training...Done!')
    
    ########################################
    # Plot Forecast
    ########################################
    st.subheader('Visualize the Forecast!')
    best_model = joblib.load(MODELPATH / 'best_model.pkl')
    # predict on training 
    forecast_name = str(forecast_horizont) + 'days_ahead_forecast'
    df_train = predict_model(best_model, data=df_train, round=1, verbose=False)
    df_train.rename(columns={'Label': forecast_name}, inplace=True) # rename prediction column
    # predict on testing set
    df_test = predict_model(best_model, data=df_test, round=1, verbose=False)
    df_test.rename(columns={'Label': forecast_name}, inplace=True) # rename prediction column
    # predict on whole dataset
    df_country = predict_model(best_model, data=df_country, round=1, verbose=False)
    df_country.rename(columns={'Label': forecast_name}, inplace=True) # rename prediction column
    # smooth forecast
    smooth_ndays = st.slider("Smooth forecast: select number of days to average", 1, 14, 5)
    df_country[forecast_name] = df_country[forecast_name].rolling(smooth_ndays).median()

        
    fig = px.line(df_country, 
                    x=df_country.index, 
                    y=['icu_patients_per_million', forecast_name], 
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

    ########################################
    # Plot Feature Importance
    ########################################        
    st.subheader('Analyze Feature Importance!')
    if st.button('Show Feature Importance'): 
        best_model = joblib.load(MODELPATH / 'best_model.pkl')   
        plot_model(best_model, 'feature', display_format='streamlit')

    
