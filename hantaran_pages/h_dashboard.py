import streamlit as st
from streamlit_echarts import st_echarts
from hantaran_tools.hantaran_service import (
    load_master_with_price, load_all_detail_paket, load_produk_satuan, load_pemasukan)
def format_rupiah(value):
    if not value:
        return "-"

    return f"Rp{value:,.0f}".replace(",", ".")


def hantaran_dasboard_page():
    pemasukan = load_pemasukan()
    pemasukan["tanggal_bayar"] = pemasukan["tanggal_bayar"].astype(str)

    total_pemasukan = pemasukan.groupby("tanggal_bayar")['nominal'].sum().reset_index()

    list_tanggal = total_pemasukan["tanggal_bayar"].tolist()
    list_nominal = total_pemasukan["nominal"].tolist()

    options = {
    "title": {"text": "Simple Chart"},
    "tooltip": {"trigger": "axis"}, # Tambahan: agar grafik menampilkan info saat di-hover
    "xAxis": {
        "type": "category", 
        "data": list_tanggal # Menggunakan list tanggal hasil groupby yang sudah unik
    },
    "yAxis": {"type": "value"},
    "series": [{
        "data": list_nominal, # Menggunakan list nominal hasil sum
        "type": "line", 
        "areaStyle": {"opacity": 0.1}
    }],
    }

    st_echarts(options=options, height="400px", theme="streamlit")
