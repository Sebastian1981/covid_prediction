import streamlit as st
import pandas as pd
from pathlib import Path

from eda import run_eda_app
from modeling import run_model_app

def main():
    st.title('Let´s Predict the Number of COVID-19 Patients in Intensive Care Units (ICU) per Million People')
    menu = ["About this Project", "Predict ICU Patients"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == 'About this Project':
        st.header('About this Project')
        st.image('./frontpage.png')
        st.markdown(Path('About.md').read_text())
        st.image('./icu_forecast.png')
        st.markdown(Path('image_description.md').read_text()) 
        st.markdown(Path('app_usage.md').read_text())
    elif choice == 'Predict ICU Patients':
        st.header('Explore Live Data from "Our World in Data"')
        run_eda_app()
        st.header('Train AI-Model and Run Predictions!')
        run_model_app()
        

if __name__ == "__main__":
    main()