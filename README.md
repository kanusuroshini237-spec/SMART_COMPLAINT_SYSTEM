# Smart Complaint Resolution System

A Streamlit-based complaint management platform with:

- User registration and secure PBKDF2 password hashing
- User login and account-specific complaint access
- ML-based complaint category classification
- Rule-based priority detection
- Automatic department routing
- Complaint tracking
- Admin analytics, staff assignment, and status management
- SQLite persistence for simple deployments

## 1. Local setup

Use Python 3.11.9 for deployment and local testing.

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
python model/train_model.py
streamlit run app.py
```

Open the URL printed by Streamlit.

## 2. Admin credentials

Admin credentials are intentionally **not hard-coded**.

For local development, set:

**Windows PowerShell**
```powershell
$env:ADMIN_USERNAME="admin"
$env:ADMIN_PASSWORD="change-this-password"
streamlit run app.py
```

**macOS/Linux**
```bash
export ADMIN_USERNAME="admin"
export ADMIN_PASSWORD="change-this-password"
streamlit run app.py
```

For Streamlit Community Cloud, add `ADMIN_USERNAME` and `ADMIN_PASSWORD` under the app's Secrets settings.

## 3. Deployment

This repository is configured for Python 3.11.9 and Streamlit Community Cloud hosting.

- Main file: `app.py`
- Dependency file: `requirements.txt` (uses only the deployment dependency set specified for this project)
- Python runtime: `python-3.11.9` (see `runtime.txt`)
- Do **not** upload the local `.venv/`/`venv/` directory.
- The included `complaints.db` is kept as starter data. SQLite storage on ephemeral hosting is not durable across replacement/redeployment; use an external database for production persistence.
- If the trained model needs to be rebuilt, run `python model/train_model.py`.

## 4. Security notes

- Passwords use salted PBKDF2-HMAC-SHA256.
- Existing legacy SHA-256 user passwords are upgraded automatically after a successful login.
- Users can only view their own complaints.
- Admin credentials come from deployment secrets/environment variables.
- Database queries use parameters rather than string interpolation.

## 5. Project structure

```text
Smart_Complaint_Routing/
├── app.py
├── auth.py
├── complaints.py
├── requirements.txt
├── complaints.db
├── assets/
│   └── style.css
├── dataset/
│   └── complaints.csv
├── model/
│   ├── complaint_model.pkl
│   ├── priority.py
│   ├── routing.py
│   └── train_model.py
└── pages/
    ├── user_dashboard.py
    ├── submit_complaint.py
    ├── track_complaint.py
    └── admin_dashboard.py
```

## GitHub-ready flattened layout

All application files are intentionally kept in the repository root so the project can be uploaded directly to GitHub without preserving application subfolders.

The Streamlit entrypoint is `app.py`. Model, dataset, CSS, and page files are also in the root directory.

For Streamlit Community Cloud, use Python 3.11.9 and configure `ADMIN_USERNAME` and `ADMIN_PASSWORD` in Secrets.
