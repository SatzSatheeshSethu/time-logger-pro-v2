import streamlit as st
from database import validate_user

def login():

    if "logged" not in st.session_state:
        st.session_state.logged = False

    if not st.session_state.logged:

        st.title("🔐 Login")

        u = st.text_input("Username")
        p = st.text_input("Password", type="password")

        if st.button("Login"):
            user = validate_user(u,p)
            if user:
                st.session_state.logged = True
                st.session_state.username = u
                st.session_state.role = user[0]
                st.rerun()
            else:
                st.error("Invalid login")

        st.stop()

def logout():
    if st.sidebar.button("Logout"):
        st.session_state.logged = False
        st.rerun()
