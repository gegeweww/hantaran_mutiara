import streamlit as st

# ================= LOGIN =================
def login():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if st.session_state.logged_in:
        return True

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


# ================= STOP JIKA BELUM LOGIN =================
if not login():
    st.stop()


# ================= APP UTAMA =================
st.sidebar.title("Hantaran Mutiara")
st.write("Aplikasi jalan di sini")