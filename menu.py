import streamlit as st

from pages_custom.data_hantaran import data_hantaran_page
from pages_custom.transaksi_hantaran import transaksi_hantaran_page

def show_menu():

    menu = st.sidebar.radio(
        "Menu",
        [
            "Data Hantaran",
            "Transaksi Hantaran"
        ]
    )

    if st.sidebar.button("Logout"):
        st.session_state.login = False
        st.rerun()

    if menu == "Data Hantaran":
        data_hantaran_page()
    elif menu == "Transaksi Hantaran":
        transaksi_hantaran_page()
