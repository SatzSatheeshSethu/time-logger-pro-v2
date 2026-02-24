import streamlit as st
import pandas as pd
from datetime import datetime
from auth import login
from supabase_client import supabase

st.set_page_config(page_title="Time Management System", layout="wide")

login()

st.sidebar.title(f"{st.session_state.username} ({st.session_state.role})")

menu = st.sidebar.selectbox("Menu", ["Dashboard","Time Tracker"])

teams = {
    "Ownership": ["OWNGEN","OWNNFSC","OWNCR"],
    "Sanctions": ["SAN"]
}

subs = {
    "Production": ["Production Web","Production QC"],
    "Non Production": ["Break","Meeting","Training"]
}

# ================= TIMER =================

if menu == "Time Tracker":

    st.title("⏱️ Time Tracker")

    team = st.selectbox("Team", list(teams.keys()))
    project = st.selectbox("Task", teams[team])
    category = st.selectbox("Category", list(subs.keys()))
    sub = st.selectbox("Sub Activity", subs[category])
    comments = st.text_area("Comments")

    running = supabase.table("logs").select("*").eq("username", st.session_state.username).eq("status","Running").execute()

    if st.button("▶️ Start Timer"):

        if running.data:
            st.warning("Timer already running")
        else:
            supabase.table("logs").insert({
                "username": st.session_state.username,
                "team": team,
                "project": project,
                "sub_activity": sub,
                "category": category,
                "start_time": datetime.utcnow().isoformat(),
                "status": "Running",
                "comments": comments
            }).execute()

            st.success("Timer started")

    if st.button("⏹ Stop Timer"):

        if running.data:

            start = pd.to_datetime(running.data[0]["start_time"])
            end = datetime.utcnow()

            duration = (end - start).total_seconds()/3600

            supabase.table("logs").update({
                "end_time": end.isoformat(),
                "duration": duration,
                "status": "Completed"
            }).eq("id", running.data[0]["id"]).execute()

            st.success("Timer stopped")

        else:
            st.warning("No active timer")

# ================= DASHBOARD =================

if menu == "Dashboard":

    st.title("📊 Dashboard")

    logs = supabase.table("logs").select("*").execute().data

    df = pd.DataFrame(logs)

    if not df.empty:

        total = df["duration"].sum()
        prod = df[df["category"]=="Production"]["duration"].sum()

        util = (prod/total)*100 if total else 0

        c1,c2,c3 = st.columns(3)

        c1.metric("Total Hours", round(total,2))
        c2.metric("Production", round(prod,2))
        c3.metric("Utilization %", round(util,2))

        df["duration_minutes"] = (df["duration"] * 60).round(2)

        st.dataframe(df[[
            "username",
            "start_time",
            "end_time",
            "duration_minutes",
            "project",
            "sub_activity",
            "category"
        ]])
