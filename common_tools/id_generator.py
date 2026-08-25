"""Generator ID bisnis Hantaran Mutiara."""

from common_tools.database import get_table_raw


ID_CONFIG = {
    "pelanggan": ("HMP", "pelanggan", "id_pelanggan"),
    "transaksi_hantaran": ("HMT", "transaksi_hantaran", "id_transaksi"),
    "transaksi_craft": ("HMC", "transaksi_craft", "id_transaksi"),
    "pembayaran_hantaran": (
        "HMBH", "pembayaran_hantaran", "id_pembayaran"
    ),
    "pembayaran_craft": ("HMBC", "pembayaran_craft", "id_pembayaran"),
    "pengeluaran": ("HME", "pengeluaran", "id_pengeluaran"),
}

MARKETPLACE_IDS = {
    "Shopee": "HMM001",
    "TikTok Shop": "HMM002",
}


def generate_next_id(prefix, existing_ids):
    """Buat ID berikutnya dari kumpulan ID yang sudah ada.

    Contoh: ``generate_next_id('HMT', ['HMT001', 'HMT009'])`` menghasilkan
    ``HMT010``. ID dengan prefix lain diabaikan.
    """

    nomor_terakhir = 0

    for value in existing_ids:
        if not isinstance(value, str) or not value.startswith(prefix):
            continue

        suffix = value[len(prefix):]
        if suffix.isdigit():
            nomor_terakhir = max(nomor_terakhir, int(suffix))

    return f"{prefix}{nomor_terakhir + 1:03d}"


def generate_id(jenis):
    """Buat ID berikutnya untuk jenis data yang terdaftar di ``ID_CONFIG``."""

    if jenis not in ID_CONFIG:
        raise ValueError(f"Jenis ID tidak dikenal: {jenis}")

    prefix, table_name, column_name = ID_CONFIG[jenis]
    data = get_table_raw(table_name)
    existing_ids = data[column_name].dropna().tolist() if column_name in data else []

    return generate_next_id(prefix, existing_ids)


def generate_marketplace_id(nama_marketplace):
    """Kembalikan ID marketplace yang memang ditetapkan secara tetap."""

    try:
        return MARKETPLACE_IDS[nama_marketplace]
    except KeyError as error:
        pilihan = ", ".join(MARKETPLACE_IDS)
        raise ValueError(
            f"Marketplace tidak dikenal: {nama_marketplace}. Pilihan: {pilihan}"
        ) from error


def generate_pelanggan_id():
    return generate_id("pelanggan")


def generate_transaksi_hantaran_id():
    return generate_id("transaksi_hantaran")


def generate_transaksi_craft_id():
    return generate_id("transaksi_craft")


def generate_pembayaran_hantaran_id():
    return generate_id("pembayaran_hantaran")


def generate_pembayaran_craft_id():
    return generate_id("pembayaran_craft")


def generate_pengeluaran_id():
    return generate_id("pengeluaran")
