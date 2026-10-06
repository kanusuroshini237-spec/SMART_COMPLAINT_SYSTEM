"""Complaint operations and ML inference."""

from __future__ import annotations

import pickle
from datetime import datetime, timezone
from pathlib import Path

from auth import get_connection
from priority import detect_priority
from routing import get_department


BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "complaint_model.pkl"


def load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            "The trained complaint model is missing. "
            "Run `python train_model.py` before starting the app."
        )
    with MODEL_PATH.open("rb") as file:
        return pickle.load(file)


def analyze_complaint(text: str, model=None) -> tuple[str, str, str]:
    complaint = " ".join(text.split())
    if not complaint:
        raise ValueError("Complaint description cannot be empty.")

    model = model or load_model()
    category = str(model.predict([complaint])[0])
    priority = detect_priority(complaint)
    department = get_department(category)
    return category, priority, department


def create_complaint(
    user_id: int,
    username: str,
    complaint: str,
    category: str,
    priority: str,
    department: str,
) -> int:
    created_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO complaints
            (complaint, category, priority, department, assigned_staff,
             status, created_at, student_username, user_id)
            VALUES (?, ?, ?, ?, NULL, 'Submitted', ?, ?, ?)
            """,
            (
                complaint.strip(), category, priority, department,
                created_at, username, user_id,
            ),
        )
        return int(cursor.lastrowid)
