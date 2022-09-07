import streamlit as st
import pandas as pd


from eda import run_eda_app


def main():
    st.title('Let´s Predict the Number of COVID-19 Patients in Intensive Care per Million People')
    menu = ["About this Project", "Exploratory Data Analysis", "Modeling"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == 'Exploratory Data Analysis':
        run_eda_app()
        

if __name__ == "__main__":
    main()