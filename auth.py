"""Authentication and database helpers for Smart Complaint Resolution System."""

from __future__ import annotations

import hashlib
import hmac
import os
import secrets
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.getenv("COMPLAINT_DB_PATH", str(BASE_DIR / "complaints.db")))


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH, timeout=30)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA busy_timeout = 30000")
    return connection


def _column_names(connection: sqlite3.Connection, table: str) -> set[str]:
    return {row["name"] for row in connection.execute(f"PRAGMA table_info({table})")}


def initialize_database() -> None:
    """Create the current schema and safely migrate the original project schema."""
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                sector TEXT NOT NULL,
                user_type TEXT NOT NULL,
                organization TEXT NOT NULL,
                id_proof_type TEXT NOT NULL,
                id_number TEXT NOT NULL UNIQUE,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS complaints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                complaint TEXT NOT NULL,
                category TEXT NOT NULL,
                priority TEXT NOT NULL,
                department TEXT NOT NULL,
                assigned_staff TEXT,
                status TEXT NOT NULL DEFAULT 'Submitted',
                created_at TEXT NOT NULL,
                student_username TEXT,
                user_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
            )
        """)

        columns = _column_names(connection, "complaints")
        if "student_username" not in columns:
            connection.execute("ALTER TABLE complaints ADD COLUMN student_username TEXT")
        if "user_id" not in columns:
            connection.execute("ALTER TABLE complaints ADD COLUMN user_id INTEGER")

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_complaints_user_id
            ON complaints(user_id)
        """)
        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_complaints_username
            ON complaints(student_username)
        """)
        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_complaints_status
            ON complaints(status)
        """)


def hash_password(password: str) -> str:
    """Hash a password using PBKDF2-HMAC-SHA256 with a random salt."""
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, 210_000
    )
    return f"pbkdf2_sha256$210000${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored_password: str) -> bool:
    """Verify current PBKDF2 hashes and legacy SHA-256 hashes."""
    if not stored_password:
        return False

    if stored_password.startswith("pbkdf2_sha256$"):
        try:
            _, iterations, salt_hex, digest_hex = stored_password.split("$", 3)
            digest = hashlib.pbkdf2_hmac(
                "sha256",
                password.encode("utf-8"),
                bytes.fromhex(salt_hex),
                int(iterations),
            )
            return hmac.compare_digest(digest.hex(), digest_hex)
        except (ValueError, TypeError):
            return False

    # Compatibility with the original project's SHA-256 storage.
    legacy_digest = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return hmac.compare_digest(legacy_digest, stored_password)


def register_user(
    full_name: str,
    sector: str,
    user_type: str,
    organization: str,
    id_proof_type: str,
    id_number: str,
    username: str,
    password: str,
) -> tuple[bool, str]:
    initialize_database()

    values = {
        "full_name": full_name.strip(),
        "sector": sector.strip(),
        "user_type": user_type.strip(),
        "organization": organization.strip(),
        "id_proof_type": id_proof_type.strip(),
        "id_number": id_number.strip(),
        "username": username.strip(),
    }

    if not all(values.values()):
        return False, "All required fields must be completed."
    if len(values["username"]) < 3:
        return False, "Username must contain at least 3 characters."
    if len(password) < 8:
        return False, "Password must contain at least 8 characters."

    created_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    try:
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO users
                (full_name, sector, user_type, organization, id_proof_type,
                 id_number, username, password_hash, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    values["full_name"], values["sector"], values["user_type"],
                    values["organization"], values["id_proof_type"],
                    values["id_number"], values["username"],
                    hash_password(password), created_at,
                ),
            )
        return True, "Registration successful."
    except sqlite3.IntegrityError as exc:
        message = str(exc).lower()
        if "username" in message:
            return False, "Username already exists."
        if "id_number" in message:
            return False, "This ID number is already registered."
        return False, "This account already exists."


def authenticate_user(username: str, password: str) -> Optional[sqlite3.Row]:
    initialize_database()
    with get_connection() as connection:
        user = connection.execute(
            "SELECT * FROM users WHERE username = ?",
            (username.strip(),),
        ).fetchone()

    if not user or not verify_password(password, user["password_hash"]):
        return None

    # Transparently upgrade legacy SHA-256 passwords after successful login.
    if not user["password_hash"].startswith("pbkdf2_sha256$"):
        with get_connection() as connection:
            connection.execute(
                "UPDATE users SET password_hash = ? WHERE id = ?",
                (hash_password(password), user["id"]),
            )

    return user


def get_admin_credentials() -> tuple[str, str]:
    """Read admin credentials from Streamlit secrets first, then environment."""
    try:
        import streamlit as st
        username = st.secrets.get("ADMIN_USERNAME", "")
        password = st.secrets.get("ADMIN_PASSWORD", "")
        if username and password:
            return str(username), str(password)
    except Exception:
        pass

    return (
        os.getenv("ADMIN_USERNAME", ""),
        os.getenv("ADMIN_PASSWORD", ""),
    )


def authenticate_admin(username: str, password: str) -> bool:
    configured_username, configured_password = get_admin_credentials()
    return bool(configured_username and configured_password) and hmac.compare_digest(
        username.strip(), configured_username
    ) and hmac.compare_digest(password, configured_password)
