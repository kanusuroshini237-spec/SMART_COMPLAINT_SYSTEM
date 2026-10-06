"""Complaint category to department routing rules."""

DEPARTMENT_MAP = {
    "Technical": "IT Department",
    "Finance": "Accounts Department",
    "Maintenance": "Maintenance Department",
    "Academic": "Academic Department",
    "Hostel": "Hostel Department",
    "Security": "Security Department",
    "Transport": "Transport Department",
}


def get_department(category: str) -> str:
    return DEPARTMENT_MAP.get(category, "General Department")
