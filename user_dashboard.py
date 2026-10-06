import os
import streamlit as st
import pandas as pd

from auth import get_connection, initialize_database

st.set_page_config(page_title="User Dashboard", page_icon="🎓", layout="wide")
initialize_database()

if not st.session_state.get("logged_in"):
    st.switch_page("app.py")
if st.session_state.get("user_role") != "user":
    st.error("❌ User access required.")
    st.stop()

CSS_PATH = os.path.join(os.path.dirname(__file__), "style.css")
if os.path.exists(CSS_PATH):
    with open(CSS_PATH, "r", encoding="utf-8") as file:
        st.markdown(f"<style>{file.read()}</style>", unsafe_allow_html=True)

username = st.session_state.get("username", "User")
user_id = st.session_state.get("user_id")

with st.sidebar:
    st.markdown("### 📢 Smart Complaint System")
    st.write(f"**{st.session_state.get('full_name', username)}**")
    if st.button("📝 Submit Complaint", use_container_width=True):
        st.switch_page("submit_complaint.py")
    if st.button("🔍 Track Complaint", use_container_width=True):
        st.switch_page("track_complaint.py")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.clear()
        st.switch_page("app.py")

st.title("🎓 User Dashboard")
st.write(f"Welcome, **{st.session_state.get('full_name', username)}** 👋")

with get_connection() as connection:
    data = pd.read_sql_query(
        """
        SELECT id, complaint, category, priority, department,
               assigned_staff, status, created_at
        FROM complaints
        WHERE user_id = ? OR (user_id IS NULL AND student_username = ?)
        ORDER BY id DESC
        """,
        connection,
        params=(user_id, username),
    )

st.subheader("📊 My Complaint Overview")
counts = data["status"].value_counts() if not data.empty else pd.Series(dtype=int)
cols = st.columns(5)
for col, label in zip(cols, ["Total", "Submitted", "Assigned", "In Progress", "Resolved"]):
    value = len(data) if label == "Total" else int(counts.get(label, 0))
    with col:
        st.metric(label, value)

st.divider()
col1, col2 = st.columns(2)
with col1:
    if st.button("➕ Submit a New Complaint", type="primary", use_container_width=True):
        st.switch_page("submit_complaint.py")
with col2:
    if st.button("🔎 Track My Complaint", use_container_width=True):
        st.switch_page("track_complaint.py")

st.divider()
st.subheader("📋 My Recent Complaints")

if data.empty:
    st.info("You have not submitted any complaints yet.")
else:
    display = data.copy()
    display["Complaint ID"] = display["id"].map(lambda x: f"CMP-{x:04d}")
    display = display[["Complaint ID", "complaint", "category", "priority", "department", "status", "created_at"]]
    display.columns = ["Complaint ID", "Complaint", "Category", "Priority", "Department", "Status", "Created At"]
    st.dataframe(display.head(20), use_container_width=True, hide_index=True)

st.divider()
st.subheader("ℹ️ How the System Works")
cols = st.columns(4)
steps = [
    ("📝", "Submit", "Describe your complaint."),
    ("🤖", "Analyze", "AI predicts category and rules detect priority."),
    ("🏢", "Route", "The complaint is routed to the right department."),
    ("🔍", "Track", "Monitor progress until resolution."),
]
for col, (icon, title, text) in zip(cols, steps):
    with col:
        st.info(f"{icon} **{title}**\n\n{text}")
