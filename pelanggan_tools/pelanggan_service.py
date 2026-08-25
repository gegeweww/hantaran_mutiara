"""Penyimpanan data pelanggan."""

from common_tools.database import insert_data
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
