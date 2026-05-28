import streamlit as st
from menu import show_menu

# ================= LOGIN =================
def login():

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    # kalau sudah login
    if st.session_state.logged_in:
        return True

    # form login
    st.title("Login")

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Masuk"):
        if password == st.secrets["PASSWORD"]:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Password salah")

    return False


# ================= CEK LOGIN =================
if not login():
    st.stop()


# ================= APP UTAMA =================
show_menu()