import streamlit as st
import inspect
from utils.hantaran_service import (
    load_master_with_price,
    load_detail_paket,
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

def transaksi_hantaran_page():

    st.title("Transaksi Hantaran")
    st.write("Penyewaan Hantaran Pernikahan dan Lamaran")

    # =====================
    # LOAD DATA SEKALI
    # =====================

    master_df = load_master_with_price()

    paket_aktif = (
        master_df.loc[master_df["status_aktif"]]
        .sort_values("kode_paket")
        .reset_index(drop=True)
    )

    if paket_aktif.empty:
        st.warning("Tidak ada paket yang tersedia.")
        return

    # =====================
    # PILIH PAKET
    # =====================

    paket_options = (
        paket_aktif["kode_paket"]
        + " - "
        + paket_aktif["nama_paket"]
    )

    selected_label = st.selectbox(
        "Pilih Paket",
        paket_options.tolist()
    )

    kode_paket = selected_label.split(" - ")[0]

    # Ambil 1 row paket
    selected_row = (
        paket_aktif.loc[
            paket_aktif["kode_paket"] == kode_paket
        ]
        .iloc[0]
    )

    # =====================
    # PILIH KATEGORI
    # =====================

    kategori_list = [
        "Wedding",
        "Engagement"
    ]

    selected_kategori = st.selectbox(
        "Kategori Hantaran",
        kategori_list
    )

    # =====================
    # TAMPILKAN HARGA
    # =====================

    if selected_kategori == "Wedding":
        harga = selected_row["harga_wedding"]
    else:
        harga = selected_row["harga_engagement"]

    if harga is not None:

        st.metric(
            "Harga Sewa",
            f"Rp {harga:,.0f}"
        )

    # =====================
    # LOAD DETAIL
    # =====================
    if st.button("Lihat Detail Paket"):

        st.session_state["kode_paket"] = kode_paket
        st.session_state["kategori_hantaran"] = selected_kategori

        st.session_state["detail_paket"] = (
            load_detail_paket(
                kode_paket,
                selected_kategori
            )
        )

    # =====================
    # DETAIL PAKET
    # =====================

    if "detail_paket" in st.session_state:

        st.subheader("Detail Isi Paket")

        st.dataframe(
            st.session_state["detail_paket"],
            use_container_width=True,
            hide_index=True
        )

    if st.button("Konfirmasi Penyewaan"):

        dialog_konfirmasi(
            st.session_state["kode_paket"],
            selected_row["nama_paket"]
        )