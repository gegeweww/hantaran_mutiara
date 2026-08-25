import streamlit as st
import pandas as pd
from datetime import date

from hantaran_tools.hantaran_service import (
    load_master_with_price,
    load_detail_paket,
    simpan_transaksi_hantaran,
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


def reset_transaksi_hantaran():
    for key in [
        "selected_paket",
        "selected_bunga",
        "keranjang_hantaran",
        "kode_paket",
        "nama_paket",
        "produk_tambahan",
        "nominal_pembayaran",
    ]:
        st.session_state.pop(key, None)


@st.dialog("Ringkasan Pembayaran")
def dialog_ringkasan_pembayaran(data):
    st.markdown(f"""
**Tanggal Booking:** {data['tanggal_booking']}  
**Tanggal Acara:** {data['tanggal_acara']}  
**Nama:** {data['nama']}  
**Status:** {data['status']}  
**Metode Pembayaran:** {data['metode_pembayaran']}  
**Sisa:** Rp {data['sisa']:,.0f}
""")

    if st.button("OK", type="primary"):
        try:
            hasil = simpan_transaksi_hantaran(**data["transaksi"])
        except Exception as error:
            st.error(f"Transaksi gagal disimpan: {error}")
            return

        reset_transaksi_hantaran()
        st.success(
            f"Transaksi {hasil['id_transaksi']} berhasil disimpan."
        )
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
        "keranjang_hantaran": None,
        "keranjang_versi": 3,
        "kode_paket": None,
        "nama_paket": None,
        "opsi_tambahan": "Tidak Ada Tambahan",
        "produk_tambahan": None,
        "qty_tambahan": 1,
        "ongkir": 0,
        "diskon_mode": "Diskon Persen",
        "diskon_persen": 0,
        "diskon_harga": 0,
        "via_pembayaran": "Cash",
        "nominal_pembayaran": 0,
    }

    for key, value in DEFAULT_SESSION.items():
        if key not in st.session_state:
            st.session_state[key] = value

    if st.session_state.get("keranjang_versi") != 3:
        st.session_state["keranjang_hantaran"] = None
        st.session_state["keranjang_versi"] = 3

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
    # TANGGAL PESANAN
    # ==================================================
    st.subheader("Tanggal Pesanan")

    tanggal_booking = st.date_input(
        "Tanggal Booking",
        value=date.today(),
        format="DD/MM/YYYY"
    )

    tanggal_acara = st.date_input(
        "Tanggal Acara",
        value=date.today(),
        format="DD/MM/YYYY"
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

    selected_label = st.selectbox(
        "Pilih Paket",
        paket_options,
        index=None,
        placeholder="Pilih Paket",
        key="selected_paket"
    )

    if selected_label is None:
        st.info("Silakan pilih paket terlebih dahulu.")
        return

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

    kategori_options = ["Wedding", "Engagement"]
    if "harga_custom_event" in master_df.columns:
        kategori_options.append("Custom Event")

    st.selectbox(
        "Kategori Hantaran",
        kategori_options,
        key="selected_kategori"
    )

    # ==================================================
    # HARGA
    # ==================================================
    kolom_harga = {
        "Wedding": "harga_wedding",
        "Engagement": "harga_engagement",
        "Custom Event": "harga_custom_event",
    }[st.session_state["selected_kategori"]]
    harga = selected_row[kolom_harga]
    produk_tambahan = load_produk_tambahan(
        kode_paket,
        st.session_state["selected_kategori"]
    )

    st.metric(
        "Harga Sewa",
        f"Rp {harga:,.0f}"
    )

    # ==================================================
    # KERANJANG TRANSAKSI
    # ==================================================
    st.session_state["kode_paket"] = kode_paket
    st.session_state["nama_paket"] = selected_row["nama_paket"]
    st.session_state["kategori_hantaran"] = st.session_state["selected_kategori"]

    bunga_row = (
        produk_bunga.loc[
            produk_bunga["nama_produk"]
            == st.session_state["selected_bunga"]
        ]
        .iloc[0]
    )

    item_utama = pd.DataFrame([
        {
            "kode_produk": kode_paket,
            "nama_item": selected_row["nama_paket"],
            "tipe_item": "Paket",
            "jumlah": 1,
            "harga": harga,
        },
        {
            "kode_produk": bunga_row["kode_produk"],
            "nama_item": bunga_row["nama_produk"],
            "tipe_item": "Include",
            "jumlah": 1,
            "harga": 0,
        }
    ])

    keranjang_lama = st.session_state["keranjang_hantaran"]
    if (
        keranjang_lama is not None
        and "tipe_item" in keranjang_lama.columns
    ):
        item_tambahan = keranjang_lama.loc[
            keranjang_lama["tipe_item"].eq("Tambahan")
        ].copy()
    else:
        item_tambahan = pd.DataFrame()

    st.session_state["keranjang_hantaran"] = pd.concat(
        [item_utama, item_tambahan],
        ignore_index=True
    )

    st.subheader("Keranjang")
    header = st.columns([0.5, 3.5, 1.4, 0.8, 1.4, 1])
    for kolom, label in zip(
        header,
        ["No", "Nama Item", "Tipe Item", "Qty", "Harga", "Aksi"]
    ):
        kolom.markdown(f"**{label}**")

    for index, item in st.session_state["keranjang_hantaran"].iterrows():
        kolom = st.columns([0.5, 3.5, 1.4, 0.8, 1.4, 1])
        kolom[0].write(index + 1)
        kolom[1].write(item["nama_item"])
        kolom[2].write(item["tipe_item"])
        kolom[3].write(item["jumlah"])
        kolom[4].write(f"Rp {item['harga']:,.0f}")

        with kolom[5].popover("⋮"):
            if item["tipe_item"] == "Tambahan":
                qty_baru = st.number_input(
                    "Qty",
                    min_value=1,
                    value=int(item["jumlah"]),
                    key=f"edit_qty_{index}"
                )
                if st.button("Simpan", key=f"simpan_item_{index}"):
                    st.session_state["keranjang_hantaran"].loc[
                        index,
                        "jumlah"
                    ] = qty_baru
                    st.rerun()

                if st.button("Hapus", key=f"hapus_item_{index}"):
                    st.session_state["keranjang_hantaran"] = (
                        st.session_state["keranjang_hantaran"]
                        .drop(index=index)
                        .reset_index(drop=True)
                    )
                    st.rerun()
            else:
                st.caption("Ubah paket atau bunga dari pilihan di atas.")

    st.radio(
        "Apakah ada produk tambahan?",
        ["Tidak Ada Tambahan", "Tambah Produk"],
        key="opsi_tambahan"
    )

    if st.session_state["opsi_tambahan"] == "Tambah Produk":
        if produk_tambahan.empty:
            st.warning("Tidak ada produk tambahan yang tersedia.")
        else:
            if st.session_state["produk_tambahan"] is None:
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
            harga_produk = produk_row[kolom_harga]

            if pd.isna(harga_produk):
                st.warning(
                    "Harga sewa produk tambahan untuk kategori ini belum tersedia."
                )
            else:
                st.write(f"Harga satuan: Rp {harga_produk:,.0f}")
                st.number_input(
                    "Jumlah",
                    min_value=1,
                    step=1,
                    key="qty_tambahan"
                )

                if st.button("Tambahkan ke Keranjang"):
                    tambahan_baru = pd.DataFrame([{
                        "kode_produk": produk_row["kode_produk"],
                        "nama_item": produk_row["nama_produk"],
                        "tipe_item": "Tambahan",
                        "jumlah": st.session_state["qty_tambahan"],
                        "harga": harga_produk,
                    }])
                    st.session_state["keranjang_hantaran"] = pd.concat(
                        [
                            st.session_state["keranjang_hantaran"],
                            tambahan_baru
                        ],
                        ignore_index=True
                    )
                    st.rerun()

    # ==================================================
    # RINGKASAN & PEMBAYARAN
    # ==================================================
    total_pesanan = (
        st.session_state["keranjang_hantaran"]["harga"]
        .mul(st.session_state["keranjang_hantaran"]["jumlah"])
        .sum()
    )

    st.divider()
    st.subheader("Ringkasan Pembayaran")
    st.number_input(
        "Ongkir (Rp)",
        min_value=0,
        step=500,
        key="ongkir"
    )

    st.markdown("**Pilih Diskon**")
    st.radio(
        "Jenis Diskon",
        ["Diskon Persen", "Diskon Harga"],
        key="diskon_mode"
    )

    if st.session_state["diskon_mode"] == "Diskon Persen":
        st.selectbox(
            "Diskon (%)",
            [0, 5, 10, 15, 20],
            key="diskon_persen"
        )
        diskon = (
            total_pesanan
            * st.session_state["diskon_persen"]
            / 100
        )
    else:
        st.number_input(
            "Diskon Harga (Rp)",
            min_value=0,
            step=500,
            key="diskon_harga"
        )
        diskon = st.session_state["diskon_harga"]

    harga_final = max(
        0,
        total_pesanan
        - diskon
        + st.session_state["ongkir"]
    )
    st.write(f"Subtotal: Rp {total_pesanan:,.0f}")
    st.write(f"Diskon: -Rp {diskon:,.0f}")
    st.write(f"Ongkir: Rp {st.session_state['ongkir']:,.0f}")
    st.write(f"**Harga Final: Rp {harga_final:,.0f}**")

    st.subheader("Pembayaran")
    st.selectbox(
        "Metode Pembayaran",
        [
            "Cash",
            "Qris EDC Mandiri",
            "Qris EDC BCA",
            "Qris Statis Mandiri",
            "TF BCA",
            "TF Mandiri"
        ],
        key="via_pembayaran"
    )
    st.number_input(
        "Masukkan Nominal",
        min_value=0,
        step=1000,
        key="nominal_pembayaran"
    )

    sisa = harga_final - st.session_state["nominal_pembayaran"]
    if sisa <= 0:
        status = "Lunas"
        sisa = 0
    else:
        status = "Belum Lunas"

    if st.button(
        "Konfirmasi Penyewaan",
        type="secondary"
    ):
        if not st.session_state["nama_pelanggan"].strip():
            st.warning("Nama pelanggan wajib diisi.")
            return

        detail_paket = load_detail_paket(
            kode_paket,
            st.session_state["selected_kategori"]
        )
        dialog_ringkasan_pembayaran({
            "tanggal_booking": tanggal_booking.strftime("%d/%m/%Y"),
            "tanggal_acara": tanggal_acara.strftime("%d/%m/%Y"),
            "nama": st.session_state["nama_pelanggan"],
            "status": status,
            "metode_pembayaran": st.session_state["via_pembayaran"],
            "sisa": sisa,
            "kode_paket": kode_paket,
            "transaksi": {
                "nama_pelanggan": st.session_state["nama_pelanggan"].strip(),
                "no_hp": st.session_state["no_hp"].strip(),
                "tanggal_booking": tanggal_booking,
                "tanggal_acara": tanggal_acara,
                "kategori_hantaran": st.session_state["selected_kategori"],
                "ongkir": st.session_state["ongkir"],
                "diskon": diskon,
                "total_harga": harga_final,
                "nominal_pembayaran": st.session_state["nominal_pembayaran"],
                "metode_pembayaran": st.session_state["via_pembayaran"],
                "sisa_pembayaran": sisa,
                "keranjang": st.session_state["keranjang_hantaran"].copy(),
                "detail_paket": detail_paket,
            },
        })

    return

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

            if produk_tambahan.empty:
                st.warning("Tidak ada produk tambahan yang tersedia.")
                return

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

            harga_produk = (
                produk_row["harga_wedding"]
                if st.session_state["selected_kategori"] == "Wedding"
                else produk_row["harga_engagement"]
            )

            if pd.isna(harga_produk):
                st.warning(
                    "Harga sewa produk tambahan untuk kategori ini belum tersedia."
                )
                return

            st.write(
                f"Harga: Rp {harga_produk:,.0f}"
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
                tambahan_df["harga_sewa"] = harga_produk

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

        # ==============================================
        # RINGKASAN PEMBAYARAN
        # ==============================================
        harga_tambahan = 0

        if "harga_sewa" in st.session_state["keranjang_hantaran"].columns:
            harga_tambahan = (
                pd.to_numeric(
                    st.session_state["keranjang_hantaran"]["harga_sewa"],
                    errors="coerce"
                )
                .fillna(0)
                .mul(
                    pd.to_numeric(
                        st.session_state["keranjang_hantaran"]["jumlah"],
                        errors="coerce"
                    ).fillna(0)
                )
                .sum()
            )

        total_pesanan = harga + harga_tambahan

        st.divider()
        st.subheader("Ringkasan Pembayaran")

        st.number_input(
            "Ongkir (Rp)",
            min_value=0,
            step=500,
            key="ongkir"
        )

        st.markdown("**Pilih Diskon**")
        st.radio(
            "Jenis Diskon",
            ["Diskon Persen", "Diskon Harga"],
            key="diskon_mode"
        )

        if st.session_state["diskon_mode"] == "Diskon Persen":
            st.selectbox(
                "Diskon (%)",
                [0, 5, 10, 15, 20],
                key="diskon_persen"
            )
            diskon = (
                total_pesanan
                * st.session_state["diskon_persen"]
                / 100
            )
        else:
            st.number_input(
                "Diskon Harga (Rp)",
                min_value=0,
                step=500,
                key="diskon_harga"
            )
            diskon = st.session_state["diskon_harga"]

        harga_final = max(
            0,
            total_pesanan
            - diskon
            + st.session_state["ongkir"]
        )

        col1, col2, col3 = st.columns(3)
        col1.metric("Subtotal", f"Rp {total_pesanan:,.0f}")
        col2.metric("Diskon", f"Rp {diskon:,.0f}")
        col3.metric("Harga Final", f"Rp {harga_final:,.0f}")

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
