"""Rule-based complaint priority detection."""

import re


def _contains_phrase(text: str, phrase: str) -> bool:
    # Match phrases as words where possible, avoiding accidental substring matches.
    pattern = r"(?<!\w)" + re.escape(phrase.lower()) + r"(?!\w)"
    return bool(re.search(pattern, text))


def detect_priority(complaint: str) -> str:
    text = " ".join(complaint.lower().split())

    critical_words = [
        "emergency", "fire", "attack", "attacked", "threat", "danger",
        "dangerous", "life threatening", "life-threatening",
        "entered without permission", "unauthorized entry",
        "unauthorized person", "someone entered", "suspicious activity",
        "physical danger", "violent", "violence", "accident", "injured",
        "injury", "serious safety issue", "serious security issue",
        "security emergency", "safety emergency",
    ]
    if any(_contains_phrase(text, word) for word in critical_words):
        return "Critical"

    high_words = [
        "urgent", "urgently", "immediately", "immediate", "not received",
        "double charged", "charged twice", "payment failed", "security issue",
        "safety issue", "cannot register", "cannot login", "unable to login",
        "not working at all", "major problem", "serious problem",
        "important issue", "security concern", "safety concern", "no water",
        "bus did not arrive", "lost my id card", "lost my college id",
    ]
    if any(_contains_phrase(text, word) for word in high_words):
        return "High"

    low_words = [
        "information", "information about", "query", "suggestion", "timetable",
        "general question", "clarification", "need information",
        "want information",
    ]
    if any(_contains_phrase(text, word) for word in low_words):
        return "Low"

    return "Medium"
