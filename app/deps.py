from __future__ import annotations

from fastapi import Request
from fastapi.responses import RedirectResponse

from app.db import get_user_by_id


def get_session_user(request: Request) -> dict | None:
    raw = request.session.get("user")
    if not raw:
        return None
    user = get_user_by_id(int(raw["id"]))
    if not user:
        request.session.clear()
        return None
    return user


def require_login(request: Request) -> dict | RedirectResponse:
    user = get_session_user(request)
    if not user:
        return RedirectResponse("/login", status_code=303)
    if user["status"] == "blocked":
        request.session.clear()
        return RedirectResponse("/login?error=blocked", status_code=303)
    if user["role"] != "admin" and user["status"] != "active":
        request.session.clear()
        return RedirectResponse("/login?error=pending", status_code=303)
    return user


def require_admin(request: Request) -> dict | RedirectResponse:
    user = require_login(request)
    if isinstance(user, RedirectResponse):
        return user
    if user["role"] != "admin":
        return RedirectResponse("/", status_code=303)
    return user
