import os
import streamlit as st
import pandas as pd

from auth import get_connection, initialize_database

st.set_page_config(page_title="Admin Dashboard", page_icon="🛠️", layout="wide")
initialize_database()

if not st.session_state.get("logged_in"):
    st.switch_page("app.py")
if st.session_state.get("user_role") != "admin":
    st.error("❌ Admin access required.")
    st.stop()

CSS_PATH = os.path.join(os.path.dirname(__file__), "style.css")
if os.path.exists(CSS_PATH):
    with open(CSS_PATH, "r", encoding="utf-8") as file:
        st.markdown(f"<style>{file.read()}</style>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🛠️ Administrator")
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.clear()
        st.switch_page("app.py")

st.title("🛠️ Admin Dashboard")
st.write("Monitor complaints, assign staff, and update resolution status.")

with get_connection() as connection:
    data = pd.read_sql_query(
        """
        SELECT id, student_username, complaint, category, priority,
               department, assigned_staff, status, created_at
        FROM complaints
        ORDER BY id DESC
        """,
        connection,
    )

st.subheader("📊 Complaint Overview")
counts = data["status"].value_counts() if not data.empty else pd.Series(dtype=int)
cols = st.columns(6)
for col, label in zip(cols, ["Total", "Submitted", "Assigned", "In Progress", "Resolved", "Closed"]):
    value = len(data) if label == "Total" else int(counts.get(label, 0))
    with col:
        st.metric(label, value)

if not data.empty:
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.write("### 📂 Complaints by Category")
        st.bar_chart(data["category"].value_counts())
    with col2:
        st.write("### 🚨 Complaints by Priority")
        st.bar_chart(data["priority"].value_counts())
    st.write("### 🏢 Complaints by Department")
    st.bar_chart(data["department"].value_counts())

st.divider()
st.subheader("📋 All Complaints")

if data.empty:
    st.info("No complaints have been submitted yet.")
else:
    display = data.copy()
    display["Complaint ID"] = display["id"].map(lambda x: f"CMP-{x:04d}")
    display["student_username"] = display["student_username"].fillna("Legacy complaint")
    display["assigned_staff"] = display["assigned_staff"].fillna("Not Assigned")
    display = display[
        ["Complaint ID", "student_username", "complaint", "category", "priority",
         "department", "assigned_staff", "status", "created_at"]
    ]
    display.columns = [
        "Complaint ID", "User", "Complaint", "Category", "Priority",
        "Department", "Assigned Staff", "Status", "Created At"
    ]
    st.dataframe(display, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("👤 Manage Complaint")

    ids = data["id"].tolist()
    selected_id = st.selectbox(
        "Select Complaint",
        ids,
        format_func=lambda x: f"CMP-{x:04d}",
        key="admin_complaint_id",
    )
    selected = data.loc[data["id"] == selected_id].iloc[0]

    st.info(
        f"**Category:** {selected['category']}  \n"
        f"**Priority:** {selected['priority']}  \n"
        f"**Department:** {selected['department']}  \n"
        f"**Complaint:** {selected['complaint']}"
    )

    staff_members = {
        "IT Department": ["IT Staff 1", "IT Staff 2", "IT Staff 3"],
        "Accounts Department": ["Accounts Staff 1", "Accounts Staff 2", "Accounts Staff 3"],
        "Maintenance Department": ["Maintenance Staff 1", "Maintenance Staff 2", "Maintenance Staff 3"],
        "Academic Department": ["Academic Staff 1", "Academic Staff 2", "Academic Staff 3"],
        "Hostel Department": ["Hostel Staff 1", "Hostel Staff 2", "Hostel Staff 3"],
        "Security Department": ["Security Officer 1", "Security Officer 2", "Security Officer 3"],
        "Transport Department": ["Transport Staff 1", "Transport Staff 2", "Transport Staff 3"],
        "General Department": ["General Staff 1", "General Staff 2"],
    }
    available_staff = staff_members.get(selected["department"], ["General Staff 1", "General Staff 2"])
    current_staff = selected["assigned_staff"]
    default_index = available_staff.index(current_staff) if current_staff in available_staff else 0

    col1, col2 = st.columns(2)
    with col1:
        selected_staff = st.selectbox("Assign Staff", available_staff, index=default_index)
    with col2:
        statuses = ["Submitted", "Assigned", "In Progress", "Resolved", "Closed"]
        current_status = selected["status"] if selected["status"] in statuses else "Submitted"
        selected_status = st.selectbox("Status", statuses, index=statuses.index(current_status))

    if st.button("💾 Save Complaint Update", type="primary", use_container_width=True):
        with get_connection() as connection:
            connection.execute(
                """
                UPDATE complaints
                SET assigned_staff = ?, status = ?
                WHERE id = ?
                """,
                (selected_staff, selected_status, selected_id),
            )
        st.success(f"✅ CMP-{selected_id:04d} updated successfully.")
        st.rerun()
