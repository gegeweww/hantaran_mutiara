import streamlit as st

from utils.database import (get_table, update_data)


@st.cache_data(ttl=300)
def load_master_with_price():

    df_master = get_table("master_paket_hantaran")
    df_harga = get_table("harga_hantaran")

    df_harga = (
        df_harga
        .pivot(
            index="kode_paket",
            columns="kategori_hantaran",
            values="harga_sewa"
        )
        .reset_index()
        .rename(
            columns={
                "Wedding": "harga_wedding",
                "Engagement": "harga_engagement"
            }
        )
    )

    return df_master.merge(
        df_harga,
        on="kode_paket",
        how="left"
    )


@st.cache_data(ttl=300)
def load_all_detail_paket():

    return get_table("detail_isi_paket")

@st.cache_data(ttl=300)
def load_produk_satuan():
    return get_table("produk_hantaran_satuan")

def update_status_paket(kode_paket):

    update_data(
        "master_paket_hantaran",
        {"status_aktif": False},
        "kode_paket",
        kode_paket
    )

def load_detail_paket(
    kode_paket,
    kategori_hantaran):

    df = load_all_detail_paket()

    return (
        df.loc[
            (df["kode_paket"] == kode_paket)
            &
            (df["kategori_hantaran"] == kategori_hantaran)
        ]
        .copy()
        .sort_values("nama_item")
        .reset_index(drop=True)
    )