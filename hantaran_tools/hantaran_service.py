import streamlit as st
import pandas as pd
from datetime import timedelta

from common_tools.database import insert_data
from common_tools.id_generator import generate_transaksi_hantaran_id
from pelanggan_tools.pelanggan_service import create_pelanggan
from hantaran_tools.pembayaran_hantaran_service import (
    create_pembayaran_hantaran,
)

from hantaran_tools.database import (get_table, update_data)


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
                "Engagement": "harga_engagement",
                "Custom Event": "harga_custom_event"
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

def load_produk_tambahan(kode_paket=None, kategori_hantaran=None):
    df = load_produk_satuan()
    df_harga = get_table("harga_produk_hantaran_satuan")
    df_harga["kategori_hantaran"] = df_harga[
        "kategori_hantaran"
    ].replace({"Engangement": "Engagement"})

    df_harga = (
        df_harga
        .pivot(
            index="kode_produk",
            columns="kategori_hantaran",
            values="harga_sewa"
        )
        .reset_index()
        .rename(
            columns={
                "Wedding": "harga_wedding",
                "Engagement": "harga_engagement",
                "Custom Event": "harga_custom_event"
            }
        )
    )

    produk_tambahan = (
        df.loc[
            df["kategori_produk"].eq("Tambahan")
        ]
        .copy()
        .merge(
            df_harga,
            on="kode_produk",
            how="left"
        )
    )

    if kode_paket is None or kategori_hantaran is None:
        return produk_tambahan

    detail_paket = load_all_detail_paket()
    kode_box = detail_paket.loc[
        (detail_paket["kode_paket"] == kode_paket)
        & (detail_paket["kategori_hantaran"] == kategori_hantaran)
        & (detail_paket["tipe_item"] == "Box"),
        "kode_produk"
    ].drop_duplicates()

    produk_box = (
        df.loc[
            df["kode_produk"].isin(kode_box)
        ]
        .copy()
        .merge(
            df_harga,
            on="kode_produk",
            how="left"
        )
    )

    return pd.concat(
        [produk_tambahan, produk_box],
        ignore_index=True
    ).drop_duplicates(subset="kode_produk")

def load_produk_bunga():
    df = load_produk_satuan()

    return (
        df.loc[
            df["kategori_produk"].eq("Bunga")
        ]
        .copy()
    )

def update_status_paket(kode_paket, status_aktif):

    update_data(
        "master_paket_hantaran",
        {"status_aktif": status_aktif},
        "kode_paket",
        kode_paket
    )
    load_master_with_price.clear()

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


def _build_detail_item_hantaran(id_transaksi, detail_paket, keranjang):
    """Bentuk daftar barang fisik yang keluar pada transaksi hantaran."""
    detail_item = []

    for _, item in detail_paket.iterrows():
        detail_item.append({
            "id_transaksi": id_transaksi,
            "kode_produk": item["kode_produk"],
            "jumlah": int(item["jumlah"]),
        })

    for _, item in keranjang.iterrows():
        if item["tipe_item"] not in ("Include", "Tambahan"):
            continue

        detail_item.append({
            "id_transaksi": id_transaksi,
            "kode_produk": item["kode_produk"],
            "jumlah": int(item["jumlah"]),
        })

    return detail_item


def hitung_tanggal_hantaran(tanggal_acara):
    """Hitung periode blok H-6 hingga batas pengembalian H+2."""
    return {
        "tanggal_blok_mulai": tanggal_acara - timedelta(days=6),
        "tanggal_max_pengembalian": tanggal_acara + timedelta(days=2),
    }


def simpan_transaksi_hantaran(
    nama_pelanggan,
    no_hp,
    tanggal_booking,
    tanggal_acara,
    kategori_hantaran,
    ongkir,
    diskon,
    total_harga,
    nominal_pembayaran,
    metode_pembayaran,
    sisa_pembayaran,
    keranjang,
    detail_paket,
):
    """Simpan header, detail, log, dan pembayaran transaksi hantaran."""
    id_pelanggan = create_pelanggan(nama_pelanggan, no_hp)
    id_transaksi = generate_transaksi_hantaran_id()
    tanggal_hantaran = hitung_tanggal_hantaran(tanggal_acara)
    status_pembayaran = "Lunas" if sisa_pembayaran == 0 else "Belum Lunas"

    insert_data(
        "transaksi_hantaran",
        {
            "id_transaksi": id_transaksi,
            "id_pelanggan": id_pelanggan,
            "tanggal_booking": tanggal_booking.isoformat(),
            "tanggal_acara": tanggal_acara.isoformat(),
            "tanggal_blok_mulai": (
                tanggal_hantaran["tanggal_blok_mulai"].isoformat()
            ),
            "tanggal_max_pengembalian": (
                tanggal_hantaran["tanggal_max_pengembalian"].isoformat()
            ),
            "kategori_hantaran": kategori_hantaran,
            "ongkir": int(ongkir),
            "diskon": int(diskon),
            "total_harga": int(total_harga),
            "status_pembayaran": status_pembayaran,
            "status_transaksi": "Aktif",
            "status_pengembalian": "Disewakan",
        }
    )

    detail_transaksi = []
    for _, item in keranjang.iterrows():
        harga = int(item["harga"])
        jumlah = int(item["jumlah"])
        detail_transaksi.append({
            "id_transaksi": id_transaksi,
            "tipe_item": item["tipe_item"],
            "kode_produk": item["kode_produk"],
            "kategori_hantaran": kategori_hantaran,
            "jumlah": jumlah,
            "harga": harga,
            "subtotal": harga * jumlah,
        })
    insert_data("detail_transaksi_hantaran", detail_transaksi)

    detail_item = _build_detail_item_hantaran(
        id_transaksi,
        detail_paket,
        keranjang,
    )
    insert_data("detail_item_hantaran", detail_item)

    insert_data(
        "log_hantaran",
        [
            {
                "kode_produk": item["kode_produk"],
                "status": "Disewakan",
                "jumlah": item["jumlah"],
                "keterangan": f"Disewakan pada transaksi: {id_transaksi}",
            }
            for item in detail_item
        ]
    )

    id_pembayaran = create_pembayaran_hantaran(
        id_transaksi=id_transaksi,
        nominal=int(nominal_pembayaran),
        metode_pembayaran=metode_pembayaran,
        sisa=int(sisa_pembayaran),
    )

    kode_paket = keranjang.loc[
        keranjang["tipe_item"].eq("Paket"),
        "kode_produk"
    ].iloc[0]
    update_status_paket(kode_paket, False)

    return {
        "id_pelanggan": id_pelanggan,
        "id_transaksi": id_transaksi,
        "id_pembayaran": id_pembayaran,
    }
