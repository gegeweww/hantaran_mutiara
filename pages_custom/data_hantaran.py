import streamlit as st
from utils.database import get_table

@st.cache_data(ttl=300)
def load_master_paket():
    return get_table("master_paket_hantaran")

@st.cache_data(ttl=300)
def load_harga_hantaran():
    return get_table("harga_hantaran")

@st.cache_data(ttl=300)
def load_master_with_price():
    df_master = load_master_paket()
    df_harga = load_harga_hantaran()

    df_harga = (
        df_harga
        .pivot(
            index="kode_paket",
            columns="kategori_hantaran",
            values="harga_sewa"
        )
        .reset_index()
    )

    df_harga = df_harga.rename(
        columns={
            "Wedding": "harga_wedding",
            "Engagement": "harga_engagement"
        }
    )

    return df_master.merge(
        df_harga,
        on="kode_paket",
        how="left"
    )

@st.cache_data(ttl=300)
def load_detail_paket():
    return get_table("detail_isi_paket")


@st.cache_data(ttl=300)
def load_produk_satuan():
    return get_table("produk_hantaran_satuan")


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


def data_hantaran_page():

    st.title("Data Hantaran")
    if st.button("🔄 Refresh Data", use_container_width=False):
        st.cache_data.clear()
        st.rerun()

    # ==================================================
    # DAFTAR PAKET
    # ==================================================
    st.header("Daftar Paket")

    df_master = prepare_dataframe(
        load_master_with_price(),
        DISPLAY_COLUMNS["master_paket"]
    )
    df_master["Harga Wedding"] = df_master["Harga Wedding"].apply(
        lambda x: f"Rp{x:,.0f}".replace(",", ".")
        if x else "-"
    )

    df_master["Harga Engagement"] = df_master["Harga Engagement"].apply(
        lambda x: f"Rp{x:,.0f}".replace(",", ".")
        if x else "-"
    )

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

    df_detail_raw = load_detail_paket()

    tab_wedding, tab_engagement = st.tabs(
        ["Wedding", "Engagement"]
    )

    with tab_wedding:
        df_wedding = df_detail_raw[
            df_detail_raw["kategori_hantaran"] == "Wedding"
        ].copy()

        df_wedding = prepare_dataframe(
            df_wedding,
            DISPLAY_COLUMNS["detail_paket"]
        )

        st.dataframe(
            df_wedding,
            use_container_width=True
        )

    with tab_engagement:
        df_engagement = df_detail_raw[
            df_detail_raw["kategori_hantaran"] == "Engagement"
        ].copy()

        df_engagement = prepare_dataframe(
            df_engagement,
            DISPLAY_COLUMNS["detail_paket"]
        )

        st.dataframe(
            df_engagement,
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

    df_stock = df_stock.reset_index(drop=True)
    df_stock.index += 1
    df_stock.index.name = "No"

    st.dataframe(
        df_stock,
        use_container_width=True
    )