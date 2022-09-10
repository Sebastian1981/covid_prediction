import streamlit as st
from eda import run_eda_app
from modeling import run_model_app
from about import run_project_description_app


def main():
    st.title('Let´s Predict the Number of COVID-19 Patients in Intensive Care Units (ICU) per Million People')
    menu = ["About this Project", "Predict ICU Patients"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == 'About this Project':
        st.header('About this Project')
        run_project_description_app()
         
    elif choice == 'Predict ICU Patients':
        st.header('Explore Live Data from "Our World in Data"')
        run_eda_app()
        st.header('Train AI-Model and Run Predictions!')
        run_model_app()
        

if __name__ == "__main__":
    main()