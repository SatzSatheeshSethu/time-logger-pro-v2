import streamlit as st
from supabase_client import supabase

def login():

    if "logged" not in st.session_state:
        st.session_state.logged = False

    if not st.session_state.logged:

        st.title("🔐 Login")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):

            res = supabase.table("users").select("*").eq("username", username).eq("password", password).execute()

            if res.data:
                st.session_state.logged = True
                st.session_state.username = username
                st.session_state.role = res.data[0]["role"]
                st.rerun()
            else:
                st.error("Invalid login")

        st.stop()
