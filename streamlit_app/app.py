import streamlit as st
import pandas as pd


from eda import run_eda_app
from modeling import run_model_app

def main():
    st.title('Let´s Predict the Number of COVID-19 Patients in Intensive Care Units (ICU) per Million People')
    menu = ["About this Project", "Import Data", "Predict ICU Patients"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == 'Import Data':
        run_eda_app()
    elif choice == 'Predict ICU Patients':
        run_model_app()
        

if __name__ == "__main__":
    main()