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
MARKDOWNPATH = Path(rootdir) / 'markdowns'

def main():
    st.title('Let´s Predict the Number of COVID-19 Patients in Intensive Care Units (ICU) per Million People')
    menu = ["About this Project", "Predict ICU Patients"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == 'About this Project':
        st.header('About this Project')
        
        try: # this should work on a local computer
            image = Image.open(IMAGEPATH / 'frontpage.png')
            st.image(image, caption='COVID-19 deaths worldwide in March 2020')    
            st.markdown((MARKDOWNPATH / 'about.md').read_text())
            image = Image.open(IMAGEPATH / 'icu_forecast.png')
            st.image(image, caption='COVID-19 patients per million in Italy.')
            #st.markdown(Path('./streamlit_app/markdowns/image_description.md').read_text())
            st.markdown((MARKDOWNPATH / 'image_description.md').read_text())
            #st.markdown(Path('./streamlit_app/markdowns/app_usage.md').read_text())
            st.markdown((MARKDOWNPATH / 'app_usage.md').read_text())
        except: # this should work for whatever reason when deployed in streamlit cloud (...there is a path problem....)
            image = Image.open(IMAGEPATH / 'frontpage.png')
            st.image(image, caption='COVID-19 deaths worldwide in March 2020')    
            st.markdown(Path('./streamlit_app/markdowns/about.md').read_text())
            #st.markdown((MARKDOWNPATH / 'about.md').read_text())
            image = Image.open(IMAGEPATH / 'icu_forecast.png')
            st.image(image, caption='COVID-19 patients per million in Italy.')
            st.markdown(Path('./streamlit_app/markdowns/image_description.md').read_text())
            #st.markdown((MARKDOWNPATH / 'image_description.md').read_text())
            st.markdown(Path('./streamlit_app/markdowns/app_usage.md').read_text())
            #st.markdown((MARKDOWNPATH / 'app_usage.md').read_text())

        
         
    elif choice == 'Predict ICU Patients':
        st.header('Explore Live Data from "Our World in Data"')
        run_eda_app()
        st.header('Train AI-Model and Run Predictions!')
        run_model_app()
        

if __name__ == "__main__":
    main()