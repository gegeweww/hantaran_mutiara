import streamlit as st

from pages_custom.data_hantaran import data_hantaran_page

def show_menu():

    menu = st.sidebar.selectbox(
        "Menu",
        [
            "Data Hantaran"
        ]
    )

    if st.sidebar.button("Logout"):
        st.session_state.login = False
        st.rerun()

    if menu == "Data Hantaran":
        data_hantaran_page()

