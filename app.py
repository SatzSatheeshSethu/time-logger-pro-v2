import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from database import (
    init_db, insert_log, get_logs,
    add_user, get_users,
    update_password
)
from auth import login, logout

st.set_page_config(page_title="Time Management System", layout="wide")

init_db()
login()
logout()

st.sidebar.title(f"{st.session_state.username} ({st.session_state.role})")

menu = st.sidebar.selectbox(
    "Menu",
    ["Dashboard","Time Tracker","Reports","User Management","Change Password"]
)

teams = {
    "Ownership": ["OWNGEN","OWNNFSC","OWNCR"],
    "Sanctions": ["SAN"]
}

sub_activities = {
    "Production": ["Production Web","Production QC"],
    "Non Production": ["Break","Meeting","Training"]
}

logs = get_logs()
df = pd.DataFrame(
    logs,
    columns=["id","username","date","team","project","sub","category","start","end","duration","comments"]
)

if st.session_state.role == "Agent":
    df = df[df["username"] == st.session_state.username]

# ================= DASHBOARD =================

if menu == "Dashboard":

    st.title("📊 Productivity Dashboard")

    if df.empty:
        st.info("No data yet")
    else:
        total = df["duration"].sum()
        prod = df[df["category"]=="Production"]["duration"].sum()
        util = (prod/total)*100 if total else 0

        c1,c2,c3 = st.columns(3)
        c1.metric("Total Hours", round(total,2))
        c2.metric("Production Hours", round(prod,2))
        c3.metric("Utilization %", round(util,2))

        if st.session_state.role != "Agent":
            st.subheader("Hours by Agent")
            st.bar_chart(df.groupby("username")["duration"].sum())

# ================= TIME TRACKER =================

if menu == "Time Tracker":

    st.title("⏱️ Start / Stop Timer")

    team = st.selectbox("Team", list(teams.keys()))
    project = st.selectbox("Task", teams[team])
    category = st.selectbox("Category", list(sub_activities.keys()))
    sub = st.selectbox("Sub Activity", sub_activities[category])
    comments = st.text_area("Comments")

    if "running" not in st.session_state:
        st.session_state.running = False
        st.session_state.start_time = None

    if st.button("▶️ Start Timer"):
        st.session_state.running = True
        st.session_state.start_time = datetime.now()
        st.success("Timer started")

    if st.button("⏹ Stop Timer") and st.session_state.running:

        end = datetime.now()
        duration = (end - st.session_state.start_time).total_seconds()/60  # minutes

        data = (
            st.session_state.username,
            datetime.today().strftime("%Y-%m-%d"),
            team,
            project,
            sub,
            category,
            st.session_state.start_time.strftime("%H:%M:%S"),
            end.strftime("%H:%M:%S"),
            duration,
            comments
        )

        insert_log(data)
        st.session_state.running = False
        st.success(f"Saved {round(duration,2)} minutes")

    if st.session_state.running:
        st.warning("Timer running ⏱️")

# ================= REPORTS =================

if menu == "Reports":

    st.title("📋 Detailed Report")

    if not df.empty:

        report_df = df[["username","date","start","end","duration"]]
        report_df.columns = [
            "Agent Name",
            "Date",
            "Start Time",
            "End Time",
            "Total Duration (Minutes)"
        ]

        st.dataframe(report_df)

        csv = report_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download Report CSV",
            csv,
            "detailed_report.csv",
            "text/csv"
        )

# ================= USER MANAGEMENT =================

if menu == "User Management":

    if st.session_state.role != "Admin":
        st.warning("Access Denied")
        st.stop()

    st.title("👤 User Management")

    st.subheader("Add User")
    u = st.text_input("Username")
    p = st.text_input("Password")
    r = st.selectbox("Role", ["Admin","Manager","Agent"])

    if st.button("Add User"):
        add_user(u,p,r)
        st.success("User added")

    st.subheader("Reset User Password")
    users = [x[0] for x in get_users()]
    selected_user = st.selectbox("Select User", users)
    new_pass = st.text_input("New Password")

    if st.button("Reset Password"):
        update_password(selected_user,new_pass)
        st.success("Password Updated")

    st.subheader("Existing Users")
    st.table(get_users())

# ================= CHANGE OWN PASSWORD =================

if menu == "Change Password":

    st.title("🔑 Change Password")

    new_pass = st.text_input("New Password", type="password")

    if st.button("Update Password"):
        update_password(st.session_state.username,new_pass)
        st.success("Password Updated Successfully")
