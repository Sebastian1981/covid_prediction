import streamlit as st
from pathlib import Path
import os
from PIL import Image


# set paths
rootdir = os.getcwd()
IMAGEPATH = Path(rootdir) / 'images'
MARKDOWNPATH = Path(rootdir) / 'markdowns'


def run_project_description_app():

    try: # this should work on a local computer
        image = Image.open(IMAGEPATH / 'frontpage.png')
        st.image(image, caption='COVID-19 deaths worldwide in March 2020')    
        st.markdown((MARKDOWNPATH / 'about.md').read_text())
        image = Image.open(IMAGEPATH / 'icu_forecast.png')
        st.image(image, caption='COVID-19 patients per million in Italy.')
        st.markdown((MARKDOWNPATH / 'image_description.md').read_text())
        st.markdown((MARKDOWNPATH / 'app_usage.md').read_text())
    except: # this should work for whatever reason when deployed in streamlit cloud (...there is a path problem....)
        image = Image.open(IMAGEPATH / 'frontpage.png')
        st.image(image, caption='COVID-19 deaths worldwide in March 2020')    
        st.markdown(Path('./streamlit_app/markdowns/about.md').read_text())
        image = Image.open(IMAGEPATH / 'icu_forecast.png')
        st.image(image, caption='COVID-19 patients per million in Italy.')
        st.markdown(Path('./streamlit_app/markdowns/image_description.md').read_text())
        st.markdown(Path('./streamlit_app/markdowns/app_usage.md').read_text())