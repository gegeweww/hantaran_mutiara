import streamlit as st
import pandas as pd
from datetime import date, timedelta

from common_tools.database import insert_data
from common_tools.id_generator import generate_transaksi_hantaran_id
from pelanggan_tools.pelanggan_service import get_or_create_pelanggan
from hantaran_tools.pembayaran_hantaran_service import (
    create_pembayaran_hantaran,
)

from hantaran_tools.database import (get_table, get_table_raw, update_data)


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


def _perbarui_stock(detail_item, perubahan):
    """Tambah atau kurangi stok berdasarkan daftar barang fisik."""
    kebutuhan = pd.DataFrame(detail_item).groupby(
        "kode_produk",
        as_index=False
    )["jumlah"].sum()
    produk = get_table_raw("produk_hantaran_satuan")

    stock_baru = []
    for _, item in kebutuhan.iterrows():
        cocok = produk.loc[
            produk["kode_produk"].eq(item["kode_produk"])
        ]
        if cocok.empty:
            raise ValueError(f"Produk {item['kode_produk']} tidak ditemukan.")

        stok = int(cocok.iloc[0]["total_stock"])
        jumlah_baru = stok + (perubahan * int(item["jumlah"]))
        if jumlah_baru < 0:
            raise ValueError(
                f"Stok {item['kode_produk']} tidak cukup untuk disewakan."
            )

        stock_baru.append((item["kode_produk"], jumlah_baru))

    for kode_produk, jumlah_baru in stock_baru:
        update_data(
            "produk_hantaran_satuan",
            {"total_stock": jumlah_baru},
            "kode_produk",
            kode_produk,
        )


def _validasi_stock(detail_item):
    """Pastikan semua kebutuhan barang tersedia sebelum transaksi disimpan."""
    kebutuhan = pd.DataFrame(detail_item).groupby(
        "kode_produk",
        as_index=False,
    )["jumlah"].sum()
    produk = get_table_raw("produk_hantaran_satuan")

    for _, item in kebutuhan.iterrows():
        cocok = produk.loc[
            produk["kode_produk"].eq(item["kode_produk"])
        ]
        if cocok.empty or int(cocok.iloc[0]["total_stock"]) < int(item["jumlah"]):
            raise ValueError(
                f"Stok {item['kode_produk']} tidak cukup untuk disewakan."
            )


def refresh_status_paket():
    """Aktifkan paket hanya bila seluruh produk fisiknya masih mencukupi."""
    detail = load_all_detail_paket()
    produk = get_table_raw("produk_hantaran_satuan")
    stok = produk.set_index("kode_produk")["total_stock"].to_dict()

    kebutuhan_paket = (
        detail.groupby(["kode_paket", "kode_produk"], as_index=False)["jumlah"]
        .max()
    )

    for kode_paket, kebutuhan in kebutuhan_paket.groupby("kode_paket"):
        tersedia = all(
            int(stok.get(item["kode_produk"], 0)) >= int(item["jumlah"])
            for _, item in kebutuhan.iterrows()
        )
        update_data(
            "master_paket_hantaran",
            {"status_aktif": tersedia},
            "kode_paket",
            kode_paket,
        )

    load_master_with_price.clear()
    load_produk_satuan.clear()
    get_table.clear()


def load_transaksi_disewakan():
    """Ambil transaksi yang belum diproses pengembaliannya."""
    transaksi = get_table_raw("transaksi_hantaran")
    if transaksi.empty:
        return transaksi

    return transaksi.loc[
        transaksi["status_pengembalian"].fillna("").astype(str)
        .str.casefold().eq("disewakan")
    ].copy()


def load_item_disewakan(id_transaksi):
    """Ambil barang fisik yang perlu dikembalikan dalam satu transaksi."""
    detail = get_table_raw("detail_item_hantaran")
    return detail.loc[detail["id_transaksi"].eq(id_transaksi)].copy()


def proses_pengembalian_hantaran(id_transaksi):
    """Kembalikan seluruh stok transaksi dan perbarui ketersediaan paket."""
    transaksi = get_table_raw("transaksi_hantaran")
    status = transaksi.loc[
        transaksi["id_transaksi"].eq(id_transaksi),
        "status_pengembalian",
    ]
    if status.empty or str(status.iloc[0]).casefold() != "disewakan":
        raise ValueError("Transaksi ini sudah dikembalikan atau tidak ditemukan.")

    detail_item = load_item_disewakan(id_transaksi)
    if detail_item.empty:
        raise ValueError("Detail barang transaksi tidak ditemukan.")

    _perbarui_stock(detail_item.to_dict("records"), perubahan=1)
    update_data(
        "transaksi_hantaran",
        {"status_pengembalian": "Dikembalikan"},
        "id_transaksi",
        id_transaksi,
    )
    insert_data(
        "log_hantaran",
        [
            {
                "kode_produk": item["kode_produk"],
                "status": "Dikembalikan",
                "jumlah": item["jumlah"],
                "keterangan": f"Dikembalikan dari transaksi: {id_transaksi}",
            }
            for item in detail_item.to_dict("records")
        ]
    )
    refresh_status_paket()
    return date.today()


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
    id_pelanggan = get_or_create_pelanggan(nama_pelanggan, no_hp)
    id_transaksi = generate_transaksi_hantaran_id()
    tanggal_hantaran = hitung_tanggal_hantaran(tanggal_acara)
    status_pembayaran = "Lunas" if sisa_pembayaran == 0 else "Belum Lunas"
    detail_item = _build_detail_item_hantaran(
        id_transaksi,
        detail_paket,
        keranjang,
    )
    _validasi_stock(detail_item)

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

    _perbarui_stock(detail_item, perubahan=-1)
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

    refresh_status_paket()

    return {
        "id_pelanggan": id_pelanggan,
        "id_transaksi": id_transaksi,
        "id_pembayaran": id_pembayaran,
    }
