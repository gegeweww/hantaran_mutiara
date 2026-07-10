import streamlit as st
import pandas as pd

from utils.hantaran_service import (
    load_master_with_price,
    load_detail_paket,
    update_status_paket,
    load_produk_tambahan,
    load_produk_bunga
)


# ==================================================
# DIALOG KONFIRMASI
# ==================================================

@st.dialog("Konfirmasi Penyewaan")
def dialog_konfirmasi(kode_paket, nama_paket):

    st.write(f"**Kode Paket:** {kode_paket}")
    st.write(f"**Nama Paket:** {nama_paket}")

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "Ya, Sewakan",
            type="primary",
            use_container_width=True
        ):

            update_status_paket(
                kode_paket,
                False
            )

            st.session_state.pop(
                "keranjang_hantaran",
                None
            )
            st.session_state.pop(
                "kode_paket",
                None
            )
            st.session_state.pop(
                "kategori_hantaran",
                None
            )
            st.session_state.pop(
                "nama_paket",
                None
            )

            st.success(
                "Paket berhasil disewakan."
            )

            st.rerun()

    with col2:
        if st.button(
            "Batal",
            use_container_width=True
        ):
            st.rerun()


# ==================================================
# PAGE
# ==================================================

def transaksi_hantaran_page():

    st.title("Transaksi Hantaran")
    st.write("Penyewaan Hantaran Pernikahan dan Lamaran")

    # ==================================================
    # INIT SESSION
    # ==================================================
    DEFAULT_SESSION = {
        "nama_pelanggan": "",
        "no_hp": "",
        "selected_paket": None,
        "selected_kategori": "Wedding",
        "selected_bunga": None,
        "jumlah_bunga": 1,
        "keranjang_hantaran": None,
        "kode_paket": None,
        "nama_paket": None,
        "opsi_tambahan": "Tidak Ada Tambahan",
        "produk_tambahan": None,
        "qty_tambahan": 1,
    }

    for key, value in DEFAULT_SESSION.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # ==================================================
    # LOAD DATA (CACHE)
    # ==================================================
    master_df = load_master_with_price()
    produk_bunga = load_produk_bunga()
    produk_tambahan = load_produk_tambahan()

    paket_aktif = (
        master_df.loc[
            master_df["status_aktif"]
        ]
        .sort_values("kode_paket")
        .reset_index(drop=True)
    )

    if paket_aktif.empty:
        st.warning("Tidak ada paket yang tersedia.")
        return

    # ==================================================
    # DATA PELANGGAN
    # ==================================================
    st.subheader("Data Pelanggan")

    st.text_input(
        "Nama",
        key="nama_pelanggan"
    )

    st.text_input(
        "No Hp",
        key="no_hp"
    )

    # ==================================================
    # PESANAN
    # ==================================================
    st.subheader("Pesanan")

    paket_options = (
        paket_aktif["kode_paket"]
        + " - "
        + paket_aktif["nama_paket"]
    ).tolist()

    if (
        st.session_state["selected_paket"] is None
        and paket_options
    ):
        st.session_state["selected_paket"] = paket_options[0]

    selected_label = st.selectbox(
        "Pilih Paket",
        paket_options,
        key="selected_paket"
    )

    kode_paket = selected_label.split(" - ")[0]

    selected_row = (
        paket_aktif.loc[
            paket_aktif["kode_paket"] == kode_paket
        ]
        .iloc[0]
    )

    if (
        st.session_state["selected_bunga"] is None
        and not produk_bunga.empty
    ):
        st.session_state["selected_bunga"] = (
            produk_bunga.iloc[0]["nama_produk"]
        )

    st.selectbox(
        "Pilih Bunga",
        produk_bunga["nama_produk"].tolist(),
        key="selected_bunga"
    )

    st.number_input(
        "Jumlah Bunga",
        min_value=1,
        max_value=4,
        step=1,
        key="jumlah_bunga"
    )

    st.selectbox(
        "Kategori Hantaran",
        ["Wedding", "Engagement"],
        key="selected_kategori"
    )

    # ==================================================
    # HARGA
    # ==================================================
    harga = (
        selected_row["harga_wedding"]
        if st.session_state["selected_kategori"] == "Wedding"
        else selected_row["harga_engagement"]
    )

    st.metric(
        "Harga Sewa",
        f"Rp {harga:,.0f}"
    )

    # ==================================================
    # LOAD DETAIL
    # ==================================================
    if st.button(
        "Lihat Detail Paket",
        type="primary"
    ):

        detail_df = load_detail_paket(
            kode_paket,
            st.session_state["selected_kategori"]
        )

        detail_df = detail_df.drop(
            columns=["id"],
            errors="ignore"
        )

        st.session_state["kode_paket"] = kode_paket
        st.session_state["nama_paket"] = selected_row["nama_paket"]
        st.session_state["kategori_hantaran"] = (
            st.session_state["selected_kategori"]
        )

        st.session_state["keranjang_hantaran"] = detail_df

        st.rerun()

    # ==================================================
    # KERANJANG
    # ==================================================
    if st.session_state["keranjang_hantaran"] is not None:

        st.subheader("Isi Paket")

        st.dataframe(
            st.session_state["keranjang_hantaran"],
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.radio(
            "Apakah ada produk tambahan?",
            [
                "Tidak Ada Tambahan",
                "Tambah Produk"
            ],
            key="opsi_tambahan"
        )

        if (
            st.session_state["opsi_tambahan"]
            == "Tambah Produk"
        ):

            if (
                st.session_state["produk_tambahan"] is None
                and not produk_tambahan.empty
            ):
                st.session_state["produk_tambahan"] = (
                    produk_tambahan.iloc[0]["nama_produk"]
                )

            st.selectbox(
                "Pilih Produk Tambahan",
                produk_tambahan["nama_produk"].tolist(),
                key="produk_tambahan"
            )

            produk_row = (
                produk_tambahan.loc[
                    produk_tambahan["nama_produk"]
                    == st.session_state["produk_tambahan"]
                ]
                .iloc[0]
            )

            st.write(
                f"Harga: Rp {produk_row['harga_sewa']:,.0f}"
            )

            st.number_input(
                "Jumlah",
                min_value=1,
                step=1,
                key="qty_tambahan"
            )

            if st.button("Tambahkan ke Keranjang"):

                tambahan_df = produk_row.to_frame().T.copy()

                tambahan_df["jumlah"] = (
                    st.session_state["qty_tambahan"]
                )

                st.session_state[
                    "keranjang_hantaran"
                ] = pd.concat(
                    [
                        st.session_state[
                            "keranjang_hantaran"
                        ],
                        tambahan_df
                    ],
                    ignore_index=True
                )

                st.success(
                    "Produk tambahan berhasil ditambahkan."
                )

                st.rerun()

    # ==================================================
    # KONFIRMASI
    # ==================================================
    if st.session_state["kode_paket"]:

        if st.button(
            "Konfirmasi Penyewaan",
            type="secondary"
        ):

            dialog_konfirmasi(
                st.session_state["kode_paket"],
                st.session_state["nama_paket"]
            )