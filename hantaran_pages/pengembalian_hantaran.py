import streamlit as st

from hantaran_tools.hantaran_service import (
    load_item_disewakan,
    load_transaksi_disewakan,
    proses_pengembalian_hantaran,
)


@st.dialog("Konfirmasi Pengembalian")
def dialog_konfirmasi_pengembalian(id_transaksi):
    st.write(f"Transaksi: **{id_transaksi}**")
    st.write("Semua barang transaksi ini akan dikembalikan ke stok.")

    if st.button("Ya, Proses Pengembalian", type="primary"):
        try:
            proses_pengembalian_hantaran(id_transaksi)
        except Exception as error:
            st.error(f"Pengembalian gagal diproses: {error}")
            return

        st.success("Stok berhasil dikembalikan dan status paket diperbarui.")
        st.rerun()


def pengembalian_hantaran_page():
    st.title("Pengembalian Hantaran")
    st.write("Proses pengembalian seluruh barang dari transaksi yang disewakan.")

    transaksi = load_transaksi_disewakan()
    if transaksi.empty:
        st.info("Tidak ada transaksi hantaran yang menunggu pengembalian.")
        return

    pilihan = (
        transaksi["id_transaksi"]
        + " - "
        + transaksi["tanggal_acara"].astype(str)
    ).tolist()
    selected_label = st.selectbox("Pilih Transaksi", pilihan)
    id_transaksi = selected_label.split(" - ")[0]

    item = load_item_disewakan(id_transaksi)
    st.subheader("Barang yang Dikembalikan")
    st.dataframe(
        item[["kode_produk", "jumlah"]].rename(
            columns={"kode_produk": "Kode Produk", "jumlah": "Qty"}
        ),
        use_container_width=True,
        hide_index=True,
    )

    if st.button("Proses Pengembalian", type="primary"):
        dialog_konfirmasi_pengembalian(id_transaksi)
