import os
import streamlit as st

from auth import initialize_database
from complaints import analyze_complaint, create_complaint

st.set_page_config(page_title="Submit Complaint", page_icon="📝", layout="wide")
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
    st.markdown("### 📢 Smart Complaint System")
    if st.button("🎓 Dashboard", use_container_width=True):
        st.switch_page("user_dashboard.py")
    if st.button("🔍 Track Complaint", use_container_width=True):
        st.switch_page("track_complaint.py")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.clear()
        st.switch_page("app.py")

st.title("📝 Submit Complaint")
st.write("Describe the issue clearly. The system will classify, prioritize, and route it automatically.")

complaint = st.text_area(
    "Complaint Description *",
    placeholder="Example: Wi-Fi is not working in the computer lab...",
    height=180,
)

if st.button("🚀 Analyze & Submit Complaint", type="primary", use_container_width=True):
    if len(complaint.strip()) < 10:
        st.warning("Please provide at least 10 characters so the system can analyze the complaint.")
    else:
        try:
            category, priority, department = analyze_complaint(complaint)
            complaint_id = create_complaint(
                st.session_state["user_id"],
                st.session_state["username"],
                complaint,
                category,
                priority,
                department,
            )

            st.success("✅ Complaint submitted successfully!")
            st.subheader(f"🎫 Complaint ID: CMP-{complaint_id:04d}")

            cols = st.columns(3)
            with cols[0]:
                st.metric("Category", category)
            with cols[1]:
                st.metric("Priority", priority)
            with cols[2]:
                st.metric("Department", department)

            if priority == "Critical":
                st.error("🚨 Critical priority: immediate attention is recommended.")
            elif priority == "High":
                st.warning("🔴 High priority: urgent attention is recommended.")
            elif priority == "Medium":
                st.info("🟡 Medium priority: normal processing.")
            else:
                st.success("🟢 Low priority: normal processing.")

            st.info(f"🏢 Your complaint has been routed to **{department}**.")
            if st.button("🔍 Track this complaint"):
                st.switch_page("track_complaint.py")
        except Exception as exc:
            st.error(f"Unable to submit the complaint: {exc}")
