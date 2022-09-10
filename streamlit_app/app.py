import streamlit as st
import pandas as pd
from pathlib import Path
import os
from eda import run_eda_app
from modeling import run_model_app
from PIL import Image

# set paths
rootdir = os.getcwd()
IMAGEPATH = Path(rootdir) / 'images'


def main():
    st.title('Let´s Predict the Number of COVID-19 Patients in Intensive Care Units (ICU) per Million People')
    menu = ["About this Project", "Predict ICU Patients"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == 'About this Project':
        st.header('About this Project')
        image = Image.open(IMAGEPATH / 'frontpage.png')
        st.image(image, caption='COVID-19 deaths worldwide in March 2020')
        st.markdown((Path(rootdir) / 'about.md').read_text())
        image = Image.open(IMAGEPATH / 'icu_forecast.png')
        st.image(image, caption='COVID-19 patients per million in Italy.')
        st.markdown((Path(rootdir) / 'image_description.md').read_text())
        st.markdown((Path(rootdir) / 'app_usage.md').read_text()) 
    elif choice == 'Predict ICU Patients':
        st.header('Explore Live Data from "Our World in Data"')
        run_eda_app()
        st.header('Train AI-Model and Run Predictions!')
        run_model_app()
        

if __name__ == "__main__":
    main()