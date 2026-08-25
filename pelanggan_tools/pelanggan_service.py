"""Penyimpanan data pelanggan."""

from common_tools.database import get_table_raw, insert_data
from common_tools.id_generator import generate_pelanggan_id


def create_pelanggan(nama, no_hp):
    """Buat pelanggan baru dan kembalikan ID pelanggan."""

    id_pelanggan = generate_pelanggan_id()
    insert_data(
        "pelanggan",
        {
            "id_pelanggan": id_pelanggan,
            "nama": nama,
            "no_hp": no_hp,
        }
    )
    return id_pelanggan


def get_or_create_pelanggan(nama, no_hp):
    """Ambil pelanggan dengan kombinasi nama dan nomor HP yang sama.

    Pelanggan baru hanya dibuat bila kombinasi tersebut belum tercatat.
    """

    pelanggan = get_table_raw("pelanggan")
    nama_normal = nama.strip().casefold()
    no_hp_normal = no_hp.strip()

    if not pelanggan.empty:
        cocok = pelanggan.loc[
            pelanggan["nama"].fillna("").astype(str).str.strip().str.casefold()
            .eq(nama_normal)
            & pelanggan["no_hp"].fillna("").astype(str).str.strip()
            .eq(no_hp_normal)
        ]

        if not cocok.empty:
            return cocok.iloc[0]["id_pelanggan"]

    return create_pelanggan(nama, no_hp)
