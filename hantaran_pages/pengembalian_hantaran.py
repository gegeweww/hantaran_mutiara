import streamlit as st
from hantaran_tools.hantaran_service import (
    load_master_with_price, 
    update_status_paket
)

@st.dialog("Konfirmasi Penyewaan")
def dialog_konfirmasi(kode_paket, nama_paket):

    st.write(f"**Kode Paket:** {kode_paket}")
    st.write(f"**Nama Paket:** {nama_paket}")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Ya, Sewakan"):

            update_status_paket(kode_paket)

            del st.session_state["detail_paket"]
            del st.session_state["kode_paket"]
            del st.session_state["kategori_hantaran"]

            st.rerun()

    with col2:
        if st.button("Batal"):
            st.rerun()

def pengembalian_hantaran_page():
    master_df = load_master_with_price()
    st.dataframe(master_df[master_df['status_aktif'] == False])