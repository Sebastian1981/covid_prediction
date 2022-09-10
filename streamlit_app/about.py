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

    try: # this should work on a local computer
        st.markdown((MARKDOWNPATH / 'about.md').read_text())
    except: # this should work for whatever reason when deployed in streamlit cloud (...there is a path problem....)
        st.markdown(Path('./streamlit_app/markdowns/about.md').read_text())

    image = Image.open(IMAGEPATH / 'icu_forecast.png')
    st.image(image, caption='ICU patients for Italy: actual curve(blue) and running 14-day ahead forecast (red)')

    try: # this should work on a local computer
        st.markdown((MARKDOWNPATH / 'image_description.md').read_text())
        st.markdown((MARKDOWNPATH / 'app_usage.md').read_text())
    except: # this should work for whatever reason when deployed in streamlit cloud (...there is a path problem....)
        st.markdown(Path('./streamlit_app/markdowns/image_description.md').read_text())
        st.markdown(Path('./streamlit_app/markdowns/app_usage.md').read_text())
