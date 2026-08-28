import streamlit as st

# Import fungsi-fungsi halaman dari folder masing-masing
from hantaran_pages.data_hantaran import data_hantaran_page
from hantaran_pages.transaksi_hantaran import transaksi_hantaran_page
from hantaran_pages.pengembalian_hantaran import pengembalian_hantaran_page
from hantaran_pages.h_dashboard import hantaran_dasboard_page
from craft_pages.data_craft import data_craft_page


def logout():
    st.session_state.login = False
    st.rerun()


def show_menu():
    # Deklarasi Menu dan Submenu dengan st.Page
    pages = {
        "🎁 Hantaran": [
            st.Page(
                data_hantaran_page,
                title="Data Hantaran",
                icon="📊",
                default=True,
            ),
            st.Page(
                transaksi_hantaran_page, title="Transaksi Hantaran", icon="🛒"
            ),
            st.Page(
                pengembalian_hantaran_page,
                title="Pengembalian Hantaran",
                icon="🔄",
            ),
            st.Page(
                hantaran_dasboard_page,
                title="Dashboard",
                icon="💹"
            )
        ],
        "🎨 Craft": [
            st.Page(data_craft_page, title="Data Craft", icon="✂️"),
        ],
    }

    # Jalankan Navigasi
    pg = st.navigation(pages)

    # Tambahkan tombol Logout di bagian paling bawah Sidebar
    with st.sidebar:
        st.divider()
        st.button("Logout", on_click=logout, use_container_width=True)

    # Eksekusi halaman yang dipilih
    pg.run()