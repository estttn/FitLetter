from __future__ import annotations

import os
import secrets
from typing import Any

import bcrypt

ADMIN_USERNAME = os.environ.get("FITLETTER_ADMIN_USER", "Fitletter")
ADMIN_PASSWORD = os.environ.get("FITLETTER_ADMIN_PASSWORD", "23112311")


def session_secret() -> str:
    key = os.environ.get("FITLETTER_SESSION_SECRET", "").strip()
    if key:
        return key
    return secrets.token_hex(32)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            password_hash.encode("utf-8"),
        )
    except ValueError:
        return False


def user_session_payload(user: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": user["id"],
        "username": user["username"],
        "role": user["role"],
        "status": user["status"],
        "display_name": user.get("display_name") or user["username"],
    }
