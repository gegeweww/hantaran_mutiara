"""Halaman Streamlit untuk mencatat pengembalian hantaran."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from hantaran_tools.hantaran_service import (
    build_return_payload,
    load_item_disewakan,
    load_transaksi_disewakan,
    proses_pengembalian_hantaran,
)


def _format_transaksi(row: pd.Series) -> str:
    tanggal = pd.to_datetime(row["tanggal_acara"]).strftime("%d-%m-%Y")
    return f"{row['id_transaksi']} | {row['nama_pelanggan']} | {tanggal}"


def _clear_form() -> None:
    for key in list(st.session_state):
        if key.startswith("return_rusak_") or key.startswith("return_catatan_"):
            st.session_state.pop(key, None)


@st.dialog("Konfirmasi Pengembalian")
def dialog_konfirmasi_pengembalian(
    id_transaksi: str,
    data_pengembalian: list[dict],
    total_denda: int,
    metode_denda: str | None,
) -> None:
    payload = build_return_payload(data_pengembalian)
    total_aman = sum(item["qty_aman"] for item in payload)
    total_rusak = sum(item["qty_rusak"] for item in payload)

    st.write(f"Transaksi: **{id_transaksi}**")
    aman, rusak, denda = st.columns(3)
    aman.metric("Item Aman", total_aman)
    rusak.metric("Item Rusak", total_rusak)
    denda.metric("Total Denda", f"Rp {total_denda:,.0f}")

    if total_rusak:
        st.warning("Item rusak tidak dikembalikan ke stok.")
    else:
        st.success("Semua item akan dikembalikan ke stok.")

    if st.button("Ya, Proses Pengembalian", type="primary", use_container_width=True):
        try:
            proses_pengembalian_hantaran(
                id_transaksi,
                data_pengembalian,
                total_denda,
                metode_denda,
            )
        except Exception as error:
            st.error(f"Pengembalian gagal diproses: {error}")
            return
        _clear_form()
        st.success("Pengembalian berhasil diproses.")
        st.rerun()


def pengembalian_hantaran_page() -> None:
    st.title("Pengembalian Hantaran")
    st.write("Catat kondisi setiap item sebelum stok dikembalikan.")

    transaksi = load_transaksi_disewakan()
    if transaksi.empty:
        st.info("Tidak ada transaksi hantaran yang menunggu pengembalian.")
        return

    labels = {
        _format_transaksi(row): row["id_transaksi"]
        for _, row in transaksi.iterrows()
    }
    selected_label = st.selectbox(
        "Cari transaksi",
        options=list(labels),
        index=None,
        placeholder="ID transaksi | nama pelanggan | tanggal acara",
    )
    if not selected_label:
        return

    id_transaksi = labels[selected_label]
    items = load_item_disewakan(id_transaksi)
    if items.empty:
        st.warning("Transaksi ini tidak memiliki item fisik untuk dikembalikan.")
        return

    st.subheader("Item Pengembalian")
    data_pengembalian: list[dict] = []
    for _, item in items.iterrows():
        kode_produk = item["kode_produk"]
        jumlah = int(item["jumlah"])
        key_suffix = f"{id_transaksi}_{kode_produk}"
        with st.container(border=True):
            info, input_rusak = st.columns([3, 1])
            info.write(f"**{item['nama_produk']}**")
            info.caption(f"{kode_produk} · Disewa: {jumlah}")
            jumlah_rusak = input_rusak.number_input(
                "Rusak", min_value=0, max_value=jumlah, step=1,
                key=f"return_rusak_{key_suffix}",
            )
            jumlah_aman = jumlah - int(jumlah_rusak)
            st.caption(f"Aman / kembali ke stok: {jumlah_aman}")
            catatan = st.text_input(
                "Catatan kerusakan" if jumlah_rusak else "Catatan (opsional)",
                key=f"return_catatan_{key_suffix}",
                disabled=not bool(jumlah_rusak),
            )
            data_pengembalian.append({
                "kode_produk": kode_produk,
                "jumlah": jumlah,
                "jumlah_rusak": int(jumlah_rusak),
                "harga_denda": int(item["harga_denda"]),
                "catatan": catatan,
            })

    try:
        preview = build_return_payload(data_pengembalian)
    except ValueError as error:
        st.error(str(error))
        return

    total_rusak = sum(item["qty_rusak"] for item in preview)
    total_denda = sum(item["nominal_denda"] for item in preview)
    metode_denda = None

    if total_rusak:
        st.subheader("Pembayaran Denda")
        st.write(f"**Total Denda: Rp {total_denda:,.0f}**")
        metode_denda = st.selectbox(
            "Metode Pembayaran Denda",
            [
                "Cash",
                "Qris EDC Mandiri",
                "Qris EDC BCA",
                "Qris Statis Mandiri",
                "TF BCA",
                "TF Mandiri",
            ],
        )

    if st.button("Proses Pengembalian", type="primary", use_container_width=True):
        dialog_konfirmasi_pengembalian(
            id_transaksi,
            data_pengembalian,
            int(total_denda),
            metode_denda,
        )
