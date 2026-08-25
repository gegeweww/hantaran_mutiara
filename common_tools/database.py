"""Akses database bersama.

Modul ini menjadi satu pintu untuk utility umum. Implementasi koneksi saat
ini tetap berada di ``hantaran_tools.database`` agar import lama tidak putus.
"""

from hantaran_tools.database import get_table_raw, insert_data, update_data

__all__ = ["get_table_raw", "insert_data", "update_data"]
