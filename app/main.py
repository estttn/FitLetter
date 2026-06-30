from __future__ import annotations

import os
import re
import subprocess
import time
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.auth import user_session_payload, verify_password
from app.collect_jobs import get_progress
from app.collector import collect, fetch_vacancy_description
from app.candidate import merge_profile_for_letters
from app.db import (
    RESUMES_DIR,
    create_resume,
    create_user,
    delete_resume,
    get_resume,
    get_vacancy_for_user,
    get_user_by_username,
    init_db,
    load_resume_profile,
    list_all_users,
    list_pending_users,
    list_resumes,
    list_vacancies,
    mark_applied,
    mark_rejected,
    clear_all_vacancies,
    vacancy_data_stats,
    set_vacancy_response,
    set_user_status,
    stats,
    update_resume_file,
    update_vacancy_letter,
)
from app.deps import get_session_user, require_admin, require_login
from app.letters import generate_cover_letter
from app.resume_parser import SUPPORTED_SUFFIXES, extract_text

app = FastAPI(title="Бюро Скаут")
STATIC_DIR = Path(__file__).parent / "static"
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

from app.auth import session_secret  # noqa: E402

app.add_middleware(SessionMiddleware, secret_key=session_secret(), max_age=60 * 60 * 24 * 14)


def _fmt_date(iso: str) -> str:
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.strftime("%d.%m.%Y")
    except ValueError:
        return (iso or "")[:10]


templates.env.globals["fmt_date"] = _fmt_date

USERNAME_RE = re.compile(r"^[a-zA-Z0-9_]{3,32}$")


def _redirect_if_needed(user_or_redirect):
    if isinstance(user_or_redirect, RedirectResponse):
        return user_or_redirect
    return None


def _selected_resume_id(request: Request, user_id: int, resume_id: int | None) -> int | None:
    resumes = list_resumes(user_id)
    if not resumes:
        return None
    if resume_id is not None:
        if any(r["id"] == resume_id for r in resumes):
            request.session["resume_id"] = resume_id
            return resume_id
    saved = request.session.get("resume_id")
    if saved and any(r["id"] == saved for r in resumes):
        return int(saved)
    rid = resumes[0]["id"]
    request.session["resume_id"] = rid
    return rid


def _ensure_resume_text(user: dict, resume_id: int) -> tuple[bool, str]:
    """Backfill old resumes that have file_path but empty text_content."""
    resume = get_resume(resume_id, user["id"])
    if not resume:
        return False, "Резюме не найдено"
    if (resume.get("text_content") or "").strip():
        return True, ""
    file_path = (resume.get("file_path") or "").strip()
    if not file_path:
        return False, "В резюме нет текста — загрузите файл резюме, чтобы письма были персональными"
    path = Path(file_path)
    if not path.exists():
        return False, "Файл резюме не найден — загрузите резюме повторно"
    try:
        text = extract_text(path)
    except Exception:
        return False, "Не удалось прочитать файл резюме — загрузите его повторно"
    if not text.strip():
        return False, "В файле резюме нет читаемого текста"
    update_resume_file(
        resume_id,
        user["id"],
        file_path=str(path),
        text_content=text,
        display_name=user.get("display_name") or "",
        email=user.get("email") or "",
    )
    return True, ""


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: str = ""):
    if get_session_user(request):
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": error},
    )


@app.post("/login")
async def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    user = get_user_by_username(username)
    if not user or not verify_password(password, user["password_hash"]):
        return RedirectResponse("/login?error=invalid", status_code=303)
    if user["status"] == "blocked":
        return RedirectResponse("/login?error=blocked", status_code=303)
    if user["role"] != "admin" and user["status"] != "active":
        return RedirectResponse("/login?error=pending", status_code=303)
    request.session["user"] = user_session_payload(user)
    return RedirectResponse("/", status_code=303)


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request, error: str = ""):
    if get_session_user(request):
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse(
        "register.html",
        {"request": request, "error": error},
    )


@app.post("/register")
async def register_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    password2: str = Form(...),
    display_name: str = Form(""),
    email: str = Form(""),
):
    username = username.strip()
    if not USERNAME_RE.match(username):
        return RedirectResponse("/register?error=username", status_code=303)
    if len(password) < 6:
        return RedirectResponse("/register?error=password", status_code=303)
    if password != password2:
        return RedirectResponse("/register?error=mismatch", status_code=303)
    if get_user_by_username(username):
        return RedirectResponse("/register?error=taken", status_code=303)
    create_user(
        username=username,
        password=password,
        display_name=display_name.strip() or username,
        email=email.strip() or None,
        status="pending",
    )
    return RedirectResponse("/login?registered=1", status_code=303)


@app.post("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)


@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request, tab: str = "pending"):
    user = require_admin(request)
    if redir := _redirect_if_needed(user):
        return redir
    return templates.TemplateResponse(
        "admin.html",
        {
            "request": request,
            "user": user,
            "tab": tab,
            "pending": list_pending_users(),
            "users": list_all_users(),
            "vacancy_stats": vacancy_data_stats(),
        },
    )


@app.get("/api/admin/vacancy-stats")
async def api_admin_vacancy_stats(request: Request):
    user = require_admin(request)
    if redir := _redirect_if_needed(user):
        return JSONResponse({"ok": False, "error": "forbidden"}, status_code=403)
    stats = vacancy_data_stats()
    stats["ok"] = True
    return JSONResponse(stats)


@app.post("/api/admin/clear-vacancies")
async def api_admin_clear_vacancies(request: Request):
    user = require_admin(request)
    if redir := _redirect_if_needed(user):
        return JSONResponse({"ok": False, "error": "forbidden"}, status_code=403)
    t0 = time.perf_counter()
    deleted = clear_all_vacancies()
    return JSONResponse(
        {
            "ok": True,
            "deleted": deleted,
            "elapsed_sec": round(time.perf_counter() - t0, 2),
            "stats": vacancy_data_stats(),
        }
    )


@app.post("/admin/approve/{user_id}")
async def admin_approve(request: Request, user_id: int):
    user = require_admin(request)
    if redir := _redirect_if_needed(user):
        return redir
    set_user_status(user_id, "active")
    return RedirectResponse("/admin?tab=pending", status_code=303)


@app.post("/admin/reject/{user_id}")
async def admin_reject(request: Request, user_id: int):
    user = require_admin(request)
    if redir := _redirect_if_needed(user):
        return redir
    set_user_status(user_id, "rejected")
    return RedirectResponse("/admin?tab=pending", status_code=303)


@app.post("/admin/block/{user_id}")
async def admin_block(request: Request, user_id: int):
    user = require_admin(request)
    if redir := _redirect_if_needed(user):
        return redir
    set_user_status(user_id, "blocked")
    return RedirectResponse("/admin?tab=users", status_code=303)


@app.post("/admin/unblock/{user_id}")
async def admin_unblock(request: Request, user_id: int):
    user = require_admin(request)
    if redir := _redirect_if_needed(user):
        return redir
    set_user_status(user_id, "active")
    return RedirectResponse("/admin?tab=users", status_code=303)


@app.get("/resumes", response_class=HTMLResponse)
async def resumes_page(request: Request, msg: str = ""):
    user = require_login(request)
    if redir := _redirect_if_needed(user):
        return redir
    return templates.TemplateResponse(
        "resumes.html",
        {
            "request": request,
            "user": user,
            "resumes": list_resumes(user["id"]),
            "msg": msg,
            "supported": ", ".join(sorted(SUPPORTED_SUFFIXES)),
        },
    )


@app.post("/resumes/upload")
async def resume_upload(
    request: Request,
    name: str = Form(...),
    file: UploadFile = File(...),
):
    user = require_login(request)
    if redir := _redirect_if_needed(user):
        return redir
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in SUPPORTED_SUFFIXES:
        return RedirectResponse("/resumes?msg=badtype", status_code=303)
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        return RedirectResponse("/resumes?msg=big", status_code=303)
    uid = user["id"]
    resume_name = name.strip() or Path(file.filename or "Резюме").stem
    rid = create_resume(
        user_id=uid,
        name=resume_name,
        text_content="",
        display_name=user.get("display_name") or "",
        email=user.get("email") or "",
    )
    dest_dir = RESUMES_DIR / str(uid)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / f"{rid}{suffix}"
    dest.write_bytes(content)
    try:
        text = extract_text(dest)
    except Exception:
        delete_resume(rid, uid)
        return RedirectResponse("/resumes?msg=parse", status_code=303)
    update_resume_file(
        rid,
        uid,
        file_path=str(dest),
        text_content=text,
        display_name=user.get("display_name") or "",
        email=user.get("email") or "",
    )
    request.session["resume_id"] = rid
    return RedirectResponse("/resumes?msg=ok", status_code=303)


@app.post("/resumes/delete/{resume_id}")
async def resume_delete(request: Request, resume_id: int):
    user = require_login(request)
    if redir := _redirect_if_needed(user):
        return redir
    delete_resume(resume_id, user["id"])
    if request.session.get("resume_id") == resume_id:
        request.session.pop("resume_id", None)
    return RedirectResponse("/resumes?msg=deleted", status_code=303)


@app.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
    filter: str = "pending",
    resume_id: int | None = None,
    fit_min: str = "",
    date_filter: str = "",
    sort: str = "date_desc",
):
    user = require_login(request)
    if redir := _redirect_if_needed(user):
        return redir
    resumes = list_resumes(user["id"])
    rid = _selected_resume_id(request, user["id"], resume_id)
    vacancies: list = []
    st = {"total": 0, "applied": 0, "new_today": 0}
    collect_result = None
    if request.query_params.get("collected") is not None:
        collect_result = {"new": int(request.query_params.get("collected") or 0)}

    if rid is not None:
        fit_val = int(fit_min) if fit_min.isdigit() else None
        only_applied = filter == "applied"
        only_rejected = filter == "rejected"
        if not only_applied and not only_rejected:
            sort = "fit_desc"
        vacancies = list_vacancies(
            user["id"],
            rid,
            hide_applied=not only_applied and not only_rejected,
            hide_rejected=not only_rejected,
            only_rejected=only_rejected,
            only_applied=only_applied,
            fit_min=fit_val,
            date_filter=date_filter or None,
            sort=sort,
        )
        st = stats(user["id"], rid)
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "user": user,
            "resumes": resumes,
            "resume_id": rid,
            "vacancies": vacancies,
            "stats": st,
            "filter": filter,
            "fit_min": fit_min,
            "date_filter": date_filter,
            "sort": sort,
            "collect_result": collect_result,
        },
    )


def _resume_query(request: Request, resume_id: int | None) -> str:
    rid = resume_id or request.session.get("resume_id")
    return f"&resume_id={rid}" if rid else ""


def _view_query(
    *,
    filter_name: str,
    resume_id: int | None,
    date_filter: str = "",
) -> str:
    parts = [f"filter={filter_name}"]
    if resume_id:
        parts.append(f"resume_id={resume_id}")
    if date_filter:
        parts.append(f"date_filter={date_filter}")
    return "&".join(parts)


@app.post("/reject/{vacancy_id}")
async def reject_vacancy(
    request: Request,
    vacancy_id: int,
    resume_id: int | None = Form(None),
    reject_reason: str = Form(""),
):
    user = require_login(request)
    if redir := _redirect_if_needed(user):
        return redir
    mark_rejected(vacancy_id, user["id"], reason=reject_reason)
    q = _resume_query(request, resume_id)
    return RedirectResponse(f"/?filter=pending{q}", status_code=303)


@app.post("/apply/{vacancy_id}")
async def apply(
    request: Request,
    vacancy_id: int,
    resume_id: int | None = Form(None),
):
    user = require_login(request)
    if redir := _redirect_if_needed(user):
        return redir
    mark_applied(vacancy_id, user["id"])
    q = _resume_query(request, resume_id)
    return RedirectResponse(f"/?filter=pending{q}", status_code=303)


@app.get("/regen/{vacancy_id}")
async def regenerate_letter_get(vacancy_id: int):
    return RedirectResponse("/?regen_error=bad_method", status_code=303)


@app.post("/regen/{vacancy_id}")
async def regenerate_letter(
    request: Request,
    vacancy_id: int,
    resume_id: int | None = Form(None),
    filter_name: str = Form("pending"),
    date_filter: str = Form(""),
):
    user = require_login(request)
    if redir := _redirect_if_needed(user):
        return redir

    q = _view_query(filter_name=filter_name, resume_id=resume_id, date_filter=date_filter)

    try:
        v = get_vacancy_for_user(vacancy_id, user["id"])
        if not v:
            return RedirectResponse(f"/?{q}&regen_error=not_found", status_code=303)

        resume = get_resume(v["resume_id"], user["id"])
        if not resume:
            return RedirectResponse(f"/?{q}&regen_error=no_resume", status_code=303)

        ok, err = _ensure_resume_text(user, resume["id"])
        if not ok:
            update_vacancy_letter(
                vacancy_id,
                user["id"],
                cover_letter="",
                letter_status="failed",
                letter_error=err[:500],
            )
            return RedirectResponse(f"/?{q}&regen_error=1", status_code=303)

        profile = merge_profile_for_letters(
            load_resume_profile(resume),
            display_name=user.get("display_name") or "",
            email=user.get("email") or "",
            resume_text=resume.get("text_content") or "",
        )
        desc = (v.get("description") or "").strip()
        if not desc:
            desc = fetch_vacancy_description(v["url"])

        letter = generate_cover_letter(
            title=v["title"],
            company=v["company"] or "—",
            salary=v["salary"] or "—",
            description=desc,
            profile=profile,
        )
        update_vacancy_letter(
            vacancy_id,
            user["id"],
            cover_letter=letter,
            letter_status="ok",
            letter_error=None,
        )
        return RedirectResponse(f"/?{q}&regen_ok=1", status_code=303)
    except Exception as e:
        try:
            update_vacancy_letter(
                vacancy_id,
                user["id"],
                cover_letter="",
                letter_status="failed",
                letter_error=str(e)[:500],
            )
        except Exception:
            pass
        return RedirectResponse(f"/?{q}&regen_error=1", status_code=303)


@app.post("/response/{vacancy_id}")
async def set_response_status(
    request: Request,
    vacancy_id: int,
    response_status: str = Form(...),
    resume_id: int | None = Form(None),
    date_filter: str = Form(""),
):
    user = require_login(request)
    if redir := _redirect_if_needed(user):
        return redir
    ok = set_vacancy_response(vacancy_id, user["id"], response_status)
    q = _view_query(filter_name="applied", resume_id=resume_id, date_filter=date_filter)
    if ok:
        return RedirectResponse(f"/?{q}&resp_ok=1", status_code=303)
    return RedirectResponse(f"/?{q}&resp_error=1", status_code=303)


@app.post("/api/collect")
async def api_collect(request: Request):
    user = require_login(request)
    if redir := _redirect_if_needed(user):
        return JSONResponse({"ok": False, "error": "unauthorized"}, status_code=401)
    rid = request.session.get("resume_id")
    if not rid:
        return JSONResponse({"ok": False, "error": "Сначала выберите или загрузите резюме"}, status_code=400)
    ok, err = _ensure_resume_text(user, int(rid))
    if not ok:
        return JSONResponse({"ok": False, "error": err}, status_code=400)
    t0 = time.perf_counter()
    try:
        result = await collect(user["id"], int(rid), background_letters=True)
    except Exception as e:
        return JSONResponse(
            {"ok": False, "error": str(e), "elapsed_sec": round(time.perf_counter() - t0, 1)},
            status_code=500,
        )
    if not isinstance(result, dict):
        result = {"ok": True, "new": 0, "scanned": 0, "unique": 0}
    result["elapsed_sec"] = round(time.perf_counter() - t0, 1)
    result.setdefault("ok", True)
    result.setdefault("phase", "listed")
    return JSONResponse(result)


@app.get("/api/collect/progress")
async def api_collect_progress(request: Request):
    user = require_login(request)
    if redir := _redirect_if_needed(user):
        return JSONResponse({"ok": False, "error": "unauthorized"}, status_code=401)
    rid = request.session.get("resume_id")
    if not rid:
        return JSONResponse({"ok": False, "error": "no resume"}, status_code=400)
    progress = get_progress(user["id"], int(rid))
    progress["ok"] = True
    return JSONResponse(progress)


@app.post("/api/hooks/deploy")
async def deploy_hook(request: Request):
    """Production deploy: GitHub Actions calls this with Bearer token (no SSH)."""
    token = os.environ.get("FITLETTER_DEPLOY_HOOK_TOKEN", "").strip()
    if not token:
        return JSONResponse({"ok": False, "error": "hook disabled"}, status_code=503)
    auth = request.headers.get("Authorization", "")
    if auth != f"Bearer {token}":
        return JSONResponse({"ok": False, "error": "forbidden"}, status_code=403)

    root = Path(__file__).resolve().parent.parent
    script = root / "scripts" / "pull_and_deploy.sh"
    if not script.is_file():
        return JSONResponse({"ok": False, "error": "deploy script missing"}, status_code=500)

    log_path = root / "data" / "deploy.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "ab") as log:
        log.write(b"\n--- deploy hook ---\n")
        subprocess.Popen(
            ["/bin/bash", str(script)],
            cwd=str(root),
            stdout=log,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    return JSONResponse({"ok": True, "message": "deploy started"})


def _deploy_revision() -> str:
    root = Path(__file__).resolve().parent.parent
    env_rev = os.environ.get("FITLETTER_DEPLOY_REV", "").strip()
    if env_rev:
        return env_rev
    rev_file = root / "data" / "deploy_rev.txt"
    if rev_file.is_file():
        return rev_file.read_text(encoding="utf-8").strip()
    if not (root / ".git").is_dir():
        return ""
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(root),
            stderr=subprocess.DEVNULL,
            timeout=5,
        )
        return out.decode().strip()
    except (OSError, subprocess.SubprocessError):
        return ""


@app.get("/health")
async def health():
    rev = _deploy_revision()
    payload: dict[str, str | bool] = {"ok": True}
    if rev:
        payload["rev"] = rev
    return payload
