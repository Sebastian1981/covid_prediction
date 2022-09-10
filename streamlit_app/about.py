import streamlit as st
from pathlib import Path
import os
from PIL import Image


# set paths
rootdir = os.getcwd()
IMAGEPATH = Path(rootdir) / 'images'
MARKDOWNPATH = Path(rootdir) / 'markdowns'


def run_project_description_app():
    image = Image.open(IMAGEPATH / 'frontpage.png')
    st.image(image, caption='COVID-19 deaths worldwide in March 2020')    
    st.markdown((MARKDOWNPATH / 'about.md').read_text())
    image = Image.open(IMAGEPATH / 'icu_forecast.png')
    st.image(image, caption='COVID-19 patients per million in Italy.')
    st.markdown((MARKDOWNPATH / 'image_description.md').read_text())
    st.markdown((MARKDOWNPATH / 'app_usage.md').read_text())