import os
import streamlit as st

from auth import (
    authenticate_admin,
    authenticate_user,
    get_admin_credentials,
    initialize_database,
    register_user,
)

st.set_page_config(
    page_title="Smart Complaint Resolution System",
    page_icon="📢",
    layout="wide",
    initial_sidebar_state="collapsed",
)

initialize_database()

CSS_PATH = os.path.join(os.path.dirname(__file__), "style.css")
if os.path.exists(CSS_PATH):
    with open(CSS_PATH, "r", encoding="utf-8") as file:
        st.markdown(f"<style>{file.read()}</style>", unsafe_allow_html=True)

DEFAULTS = {
    "logged_in": False, "user_role": None, "user_id": None, "username": None,
    "full_name": None, "sector": None, "user_type": None, "organization": None,
    "id_proof_type": None, "id_number": None,
}
for key, value in DEFAULTS.items():
    st.session_state.setdefault(key, value)

if st.session_state.logged_in:
    if st.session_state.user_role == "admin":
        navigation = st.navigation([
            st.Page("admin_dashboard.py", title="Admin Dashboard", icon="🛠️"),
        ])
    else:
        navigation = st.navigation([
            st.Page("user_dashboard.py", title="User Dashboard", icon="🎓"),
            st.Page("submit_complaint.py", title="Submit Complaint", icon="📝"),
            st.Page("track_complaint.py", title="Track Complaint", icon="🔍"),
        ])
    navigation.run()
    st.stop()

st.markdown("""
<div class="hero">
    <h1>📢 Smart Complaint Resolution System</h1>
    <p>Resolve Faster • Route Smarter • Serve Better</p>
</div>
""", unsafe_allow_html=True)

mode = st.radio(
    "Select Option",
    ["🔐 Login", "📝 New User Registration"],
    horizontal=True,
    key="main_auth_mode",
)
st.divider()

if mode == "🔐 Login":
    st.markdown('<div class="section-title">🔐 Secure Login</div>', unsafe_allow_html=True)
    login_type = st.radio(
        "Login as",
        ["👤 User", "🛠️ Administrator"],
        horizontal=True,
        key="login_type",
    )

    if login_type == "👤 User":
        username = st.text_input("👤 Username", placeholder="Enter your username")
        password = st.text_input("🔑 Password", type="password", placeholder="Enter your password")

        if st.button("🔐 Login", type="primary", use_container_width=True):
            if not username.strip() or not password:
                st.error("Please enter username and password.")
            else:
                user = authenticate_user(username, password)
                if user:
                    st.session_state.update({
                        "logged_in": True,
                        "user_role": "user",
                        "user_id": user["id"],
                        "username": user["username"],
                        "full_name": user["full_name"],
                        "sector": user["sector"],
                        "user_type": user["user_type"],
                        "organization": user["organization"],
                        "id_proof_type": user["id_proof_type"],
                        "id_number": user["id_number"],
                    })
                    st.switch_page("user_dashboard.py")
                else:
                    st.error("❌ Invalid username or password.")
    else:
        admin_username = st.text_input("🛠️ Admin Username")
        admin_password = st.text_input("🔑 Admin Password", type="password")

        configured_username, _ = get_admin_credentials()
        if not configured_username:
            st.warning(
                "Admin login is not configured. Set ADMIN_USERNAME and "
                "ADMIN_PASSWORD in Streamlit secrets or environment variables."
            )

        if st.button("🛠️ Login to Admin Portal", type="primary", use_container_width=True):
            if authenticate_admin(admin_username, admin_password):
                st.session_state.update({
                    "logged_in": True,
                    "user_role": "admin",
                    "user_id": None,
                    "username": admin_username.strip(),
                    "full_name": "System Administrator",
                })
                st.switch_page("admin_dashboard.py")
            else:
                st.error("❌ Invalid admin credentials.")

else:
    st.markdown('<div class="section-title">📝 Create Your Account</div>', unsafe_allow_html=True)
    st.info("Create an account using your organization or institution ID.")

    col1, col2 = st.columns(2)
    with col1:
        full_name = st.text_input("Full Name *")
    with col2:
        organization = st.text_input("Organization / Institution *")

    sector = st.selectbox(
        "🏢 Sector *",
        ["Education", "Healthcare", "Corporate", "Government", "Residential",
         "Hospitality", "Industrial", "Public Services", "Other"],
    )

    user_types = {
        "Education": ["Student", "Teacher", "Staff", "Maintenance Worker", "Security Staff", "Other"],
        "Healthcare": ["Patient", "Doctor", "Nurse", "Hospital Staff", "Security Staff", "Visitor", "Other"],
        "Corporate": ["Employee", "Manager", "HR Staff", "IT Staff", "Maintenance Staff", "Security Staff", "Other"],
        "Government": ["Citizen", "Government Employee", "Officer", "Contract Worker", "Other"],
        "Residential": ["Resident", "Tenant", "Owner", "Maintenance Staff", "Security Staff", "Other"],
        "Hospitality": ["Guest", "Hotel Staff", "Manager", "Housekeeping Staff", "Maintenance Staff", "Security Staff", "Other"],
        "Industrial": ["Worker", "Engineer", "Manager", "Maintenance Staff", "Security Staff", "Other"],
        "Public Services": ["Citizen", "Passenger", "Visitor", "Staff", "Other"],
        "Other": ["Student", "Teacher", "Employee", "Patient", "Staff", "Visitor", "Other"],
    }
    user_type = st.selectbox("👤 User Type *", user_types[sector])

    id_types = {
        "Education": ["College ID", "Student ID", "Employee ID", "Teacher ID", "Organization ID"],
        "Healthcare": ["Patient ID", "Doctor ID", "Hospital Staff ID", "Hospital ID"],
        "Corporate": ["Employee ID", "Company ID", "Staff ID"],
        "Government": ["Citizen ID", "Employee ID", "Government ID"],
        "Residential": ["Resident ID", "Tenant ID", "Apartment ID"],
        "Hospitality": ["Guest ID", "Booking ID", "Employee ID"],
        "Industrial": ["Employee ID", "Worker ID", "Company ID"],
        "Public Services": ["Service ID", "Passenger ID", "Employee ID"],
        "Other": ["Organization ID", "Employee ID", "Other ID"],
    }
    id_proof_type = st.selectbox("🪪 ID Proof Type *", id_types[sector])
    id_number = st.text_input("🔢 ID Number *")

    col1, col2 = st.columns(2)
    with col1:
        new_username = st.text_input("Username *", placeholder="At least 3 characters")
    with col2:
        new_password = st.text_input("Password *", type="password", placeholder="Minimum 8 characters")
    confirm_password = st.text_input("Confirm Password *", type="password")

    if st.button("🚀 Create Account", type="primary", use_container_width=True):
        if new_password != confirm_password:
            st.error("Passwords do not match.")
        else:
            success, message = register_user(
                full_name, sector, user_type, organization,
                id_proof_type, id_number, new_username, new_password,
            )
            if success:
                st.success("🎉 Account created successfully. Select Login above to continue.")
            else:
                st.error(f"❌ {message}")

st.divider()
st.markdown('<div class="section-title">✨ One Platform. Every Sector.</div>', unsafe_allow_html=True)
cols = st.columns(4)
features = [
    ("🤖", "AI-Powered Routing", "Automatically classify complaints and route them to the appropriate department."),
    ("⚡", "Priority Detection", "Identify urgent and critical complaints for faster attention."),
    ("🔍", "Easy Tracking", "Users can securely track their own complaints from submission to closure."),
    ("🛠️", "Admin Management", "Administrators can assign staff, update status, and monitor analytics."),
]
for col, (icon, title, text) in zip(cols, features):
    with col:
        st.markdown(
            f'<div class="feature-card"><div class="feature-icon">{icon}</div>'
            f'<h3>{title}</h3><p>{text}</p></div>',
            unsafe_allow_html=True,
        )

st.markdown("""
<div class="footer">
<strong>Smart Complaint Resolution System</strong><br>
Resolve Faster • Route Smarter • Serve Better
</div>
""", unsafe_allow_html=True)
