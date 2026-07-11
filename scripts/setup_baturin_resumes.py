#!/usr/bin/env python3
"""Install or refresh three role-based resumes (PM, Copywriter, BA) on FitLetter."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.candidate import profile_from_resume_text, profile_to_json
from app.db import (
    RESUMES_DIR,
    connect,
    create_resume,
    delete_resume,
    get_user_by_username,
    init_db,
    list_resumes,
    update_resume_file,
)
from app.resume_parser import extract_text
from app.resume_roles import ROLE_BA, ROLE_COPYWRITER, ROLE_PM, apply_role_template

RESUME_PACK = (
    (ROLE_PM, "PM", ROOT / "resumes" / "pdf" / "HH-PM-Baturin.pdf"),
    (ROLE_COPYWRITER, "Копирайтер", ROOT / "resumes" / "pdf" / "HH-Kopirajter-Baturin.pdf"),
    (ROLE_BA, "BA", ROOT / "resumes" / "pdf" / "HH-BA-Baturin.pdf"),
)


def _first_active_user_id() -> int | None:
    with connect() as conn:
        row = conn.execute(
            """
            SELECT id FROM users
            WHERE role = 'user' AND status = 'active'
            ORDER BY id ASC LIMIT 1
            """
        ).fetchone()
        if row:
            return int(row["id"])
        row = conn.execute(
            "SELECT id FROM users WHERE role = 'admin' AND status = 'active' ORDER BY id ASC LIMIT 1"
        ).fetchone()
        return int(row["id"]) if row else None


def _resolve_user_id(username: str | None) -> int:
    if username:
        user = get_user_by_username(username)
        if not user:
            raise SystemExit(f"User not found: {username}")
        return int(user["id"])
    uid = _first_active_user_id()
    if uid is None:
        raise SystemExit("No active user found; pass --username")
    return uid


def _clear_resumes(user_id: int) -> None:
    for resume in list_resumes(user_id):
        delete_resume(int(resume["id"]), user_id)
        print(f"deleted resume id={resume['id']} name={resume['name']!r}")


def _install_one(user_id: int, role: str, name: str, pdf_path: Path, *, display_name: str, email: str) -> int:
    if not pdf_path.exists():
        raise SystemExit(f"Missing PDF: {pdf_path}")
    text = extract_text(pdf_path)
    rid = create_resume(
        user_id=user_id,
        name=name,
        text_content=text,
        display_name=display_name,
        email=email,
        role=role,
    )
    dest_dir = RESUMES_DIR / str(user_id)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / f"{rid}.pdf"
    dest.write_bytes(pdf_path.read_bytes())
    profile = apply_role_template(
        profile_from_resume_text(
            text,
            display_name=display_name,
            email=email,
            role=role,
            resume_name=name,
        ),
        role,
    )
    update_resume_file(
        rid,
        user_id,
        file_path=str(dest),
        text_content=text,
        display_name=display_name,
        email=email,
        resume_name=name,
    )
    with connect() as conn:
        conn.execute(
            "UPDATE resumes SET profile_json = ? WHERE id = ? AND user_id = ?",
            (profile_to_json(profile), rid, user_id),
        )
        conn.commit()
    print(f"installed resume id={rid} role={role} name={name!r} file={dest.name}")
    return rid


def main() -> None:
    parser = argparse.ArgumentParser(description="Setup PM / Copywriter / BA resumes")
    parser.add_argument("--username", help="FitLetter username (default: first active user)")
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Delete existing resumes for user before install",
    )
    args = parser.parse_args()

    init_db()
    user_id = _resolve_user_id(args.username)
    with connect() as conn:
        row = conn.execute("SELECT username, display_name, email FROM users WHERE id = ?", (user_id,)).fetchone()
    if not row:
        raise SystemExit(f"User id={user_id} missing")
    display_name = row["display_name"] or row["username"]
    email = row["email"] or ""

    print(f"user={row['username']!r} id={user_id}")
    if args.replace:
        _clear_resumes(user_id)

    for role, name, pdf in RESUME_PACK:
        _install_one(user_id, role, name, pdf, display_name=display_name, email=email)

    print("Done.")


if __name__ == "__main__":
    main()
