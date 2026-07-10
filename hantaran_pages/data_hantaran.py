import streamlit as st
from utils.hantaran_service import (load_master_with_price, load_all_detail_paket, load_produk_satuan)

DISPLAY_COLUMNS = {
    "master_paket": [
        "kode_paket",
        "nama_paket",
        "harga_wedding",
        "harga_engagement",
        "status_aktif",
    ],
    "detail_paket": [
        "kode_paket",
        "kode_produk",
        "nama_item",
        "tipe_item",
        "jumlah",
    ],
    "produk_satuan": [
        "kode_produk",
        "nama_produk",
        "kategori_hantaran",
        "total_stock",
    ]
}


def prepare_dataframe(df, display_columns):
    # Ambil hanya kolom yang diizinkan
    available_columns = [
        col for col in display_columns
        if col in df.columns
    ]

    df = df[available_columns].copy()

    # Rapikan header
    df.columns = [
        col.replace("_", " ").title()
        for col in df.columns
    ]

    # Nomor urut mulai dari 1
    df = df.reset_index(drop=True)
    df.index += 1
    df.index.name = "No"

    return df

def format_rupiah(value):
    if not value:
        return "-"

    return f"Rp{value:,.0f}".replace(",", ".")


def data_hantaran_page():

    st.title("Data Hantaran")
    if st.button("🔄 Refresh Data", use_container_width=False):
        st.cache_data.clear()
        st.rerun()

    # ==================================================
    # DAFTAR PAKET
    # ==================================================
    st.header("Daftar Paket")

    df_master_raw = load_master_with_price()

    df_master_raw = (
        df_master_raw
        .sort_values(
            by=["status_aktif", "kode_paket"],
            ascending=[False, True]
        )
        .reset_index(drop=True)
    )

    df_master = prepare_dataframe(
        df_master_raw,
        DISPLAY_COLUMNS["master_paket"]
    )

    for col in ["Harga Wedding", "Harga Engagement"]:
        df_master[col] = df_master[col].apply(format_rupiah)

    df_master["Status"] = df_master["Status Aktif"].apply(
        lambda x: "🟢 Tersedia" if x else "🔴 Disewa"
    )

    df_master = df_master.drop(
        columns=["Status Aktif"]
    )

    st.dataframe(
        df_master,
        use_container_width=True
    )

    # ==================================================
    # DAFTAR ISI PAKET
    # ==================================================
    st.divider()
    st.header("Daftar Isi Paket")

    df_detail_raw = load_all_detail_paket()

    kategori_list = [
        "Wedding",
        "Engagement"
    ]

    tabs = st.tabs(kategori_list)
    for tab, kategori in zip(tabs, kategori_list):
        with tab:
            df = df_detail_raw[
                df_detail_raw["kategori_hantaran"] == kategori
            ].sort_values(by=["kode_paket", "nama_item", "tipe_item"]).copy()

            df = prepare_dataframe(
                df,
                DISPLAY_COLUMNS["detail_paket"]
            )

            st.dataframe(
                df,
                use_container_width=True
            )

    # ==================================================
    # DAFTAR STOCK
    # ==================================================
    st.divider()
    st.header("Daftar Stock")

    df_stock = prepare_dataframe(
        load_produk_satuan(),
        DISPLAY_COLUMNS["produk_satuan"]
    )

    st.dataframe(
        df_stock,
        use_container_width=True
    )