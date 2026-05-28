import streamlit as st
from utils.database import get_table


def data_hantaran_page():
    st.title("Data Hantaran")

    df_master = get_table("master_paket_hantaran")
    df_master = df_master.drop(
        columns=["id", "created_at"],
        errors="ignore"
    )

    st.write(df_master)