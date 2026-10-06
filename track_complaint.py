import os
import re
import streamlit as st

from auth import get_connection, initialize_database

st.set_page_config(page_title="Track Complaint", page_icon="🔍", layout="centered")
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

with st.sidebar:
    if st.button("🎓 Dashboard", use_container_width=True):
        st.switch_page("user_dashboard.py")
    if st.button("📝 Submit Complaint", use_container_width=True):
        st.switch_page("submit_complaint.py")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.clear()
        st.switch_page("app.py")

st.title("🔍 Track My Complaint")
st.write("You can view only complaints belonging to your account.")

complaint_id = st.text_input("Complaint ID", placeholder="Example: CMP-0009")

if st.button("🔎 Track Complaint", type="primary", use_container_width=True):
    match = re.fullmatch(r"(?:CMP[-\s]*)?(\d+)", complaint_id.strip(), re.IGNORECASE)
    if not match:
        st.error("❌ Invalid Complaint ID. Use a format such as CMP-0009.")
    else:
        numeric_id = int(match.group(1))
        username = st.session_state["username"]
        user_id = st.session_state["user_id"]

        with get_connection() as connection:
            result = connection.execute(
                """
                SELECT id, complaint, category, priority, department,
                       assigned_staff, status, created_at
                FROM complaints
                WHERE id = ?
                  AND (user_id = ? OR (user_id IS NULL AND student_username = ?))
                """,
                (numeric_id, user_id, username),
            ).fetchone()

        if not result:
            st.error("❌ Complaint not found in your account.")
        else:
            st.success("✅ Complaint found!")
            st.subheader(f"🎫 CMP-{result['id']:04d}")
            st.write(f"**Complaint:** {result['complaint']}")
            st.write(f"**Submitted At:** {result['created_at']}")

            cols = st.columns(2)
            with cols[0]:
                st.write(f"**Category:** {result['category']}")
                st.write(f"**Priority:** {result['priority']}")
                st.write(f"**Department:** {result['department']}")
            with cols[1]:
                st.write(f"**Status:** {result['status']}")
                st.write(f"**Assigned Staff:** {result['assigned_staff'] or 'Not Assigned Yet'}")

            st.subheader("📈 Complaint Progress")
            statuses = ["Submitted", "Assigned", "In Progress", "Resolved", "Closed"]
            current_index = statuses.index(result["status"]) if result["status"] in statuses else 0
            for index, status in enumerate(statuses):
                if index < current_index:
                    st.write(f"✅ {status}")
                elif index == current_index:
                    st.write(f"🟢 **{status}**")
                else:
                    st.write(f"⚪ {status}")
