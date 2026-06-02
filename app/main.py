from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.collector import collect
from app.db import init_db, list_vacancies, mark_applied, stats

app = FastAPI(title="FitLetter")
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, filter: str = "pending"):
    hide_applied = filter != "all"
    only_new = filter == "new"
    vacancies = list_vacancies(only_new=only_new, hide_applied=hide_applied)
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "vacancies": vacancies,
            "stats": stats(),
            "filter": filter,
        },
    )


@app.post("/apply/{vacancy_id}")
async def apply(vacancy_id: str):
    mark_applied(vacancy_id)
    return RedirectResponse(url="/", status_code=303)


@app.post("/collect")
async def run_collect():
    result = await collect()
    return RedirectResponse(url=f"/?collected={result.get('new', 0)}", status_code=303)


@app.get("/health")
async def health():
    return {"ok": True, **stats()}
