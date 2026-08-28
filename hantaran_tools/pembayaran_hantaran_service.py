"""Penyimpanan pembayaran transaksi hantaran."""

from datetime import date

from common_tools.database import insert_data
from common_tools.id_generator import generate_pembayaran_hantaran_id


def create_pembayaran_hantaran(
    id_transaksi,
    nominal,
    metode_pembayaran,
    sisa,
    jenis_pembayaran="Sewa",
):
    """Simpan pembayaran sewa atau denda bila transaksi menerima pembayaran."""

    if nominal <= 0:
        return None

    id_pembayaran = generate_pembayaran_hantaran_id()
    insert_data(
        "pembayaran_hantaran",
        {
            "id_pembayaran": id_pembayaran,
            "id_transaksi": id_transaksi,
            "kategori_transaksi": "Hantaran",
            "jenis_pembayaran": jenis_pembayaran,
            "tanggal_bayar": date.today().isoformat(),
            "nominal": nominal,
            "metode": metode_pembayaran,
            "pembayaran_ke": 1,
            "sisa": sisa,
        }
    )
    return id_pembayaran
