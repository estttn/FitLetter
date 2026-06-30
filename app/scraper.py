"""Parse vacancies from hh.ru HTML (SSR JSON, no api.hh.ru)."""
from __future__ import annotations

import html as html_lib
import json
import re
from dataclasses import dataclass
from typing import Any

STATE_RE = re.compile(r'id="HH-Lux-InitialState"[^>]*>(\{.*\})</template>', re.S)
TAG_RE = re.compile(r"<[^>]+>")


@dataclass
class VacancyItem:
    id: str
    title: str
    company: str
    salary: str
    url: str


def parse_initial_state(html: str) -> dict[str, Any] | None:
    m = STATE_RE.search(html)
    if not m:
        return None
    return json.loads(m.group(1))


def strip_html(text: str) -> str:
    text = html_lib.unescape(text or "")
    text = TAG_RE.sub(" ", text)
    return re.sub(r"\s+", " ", text).strip()


def parse_vacancy_description(html: str) -> str:
    data = parse_initial_state(html)
    if not data:
        return ""
    vv = data.get("vacancyView") or {}
    raw = vv.get("description") or ""
    if isinstance(raw, dict):
        raw = raw.get("text") or raw.get("$") or ""
    return strip_html(str(raw))[:4000]


def parse_search_html(html: str) -> list[VacancyItem]:
    data = parse_initial_state(html)
    if not data:
        return _parse_fallback_links(html)
    raw: list[dict[str, Any]] = []

    def walk(obj: Any) -> None:
        if isinstance(obj, dict):
            if "vacancyId" in obj and "name" in obj:
                raw.append(obj)
            for v in obj.values():
                walk(v)
        elif isinstance(obj, list):
            for v in obj:
                walk(v)

    walk(data)
    seen: set[str] = set()
    out: list[VacancyItem] = []
    for v in raw:
        vid = str(v["vacancyId"])
        if vid in seen:
            continue
        seen.add(vid)
        company = (v.get("company") or {}).get("name") or "—"
        host = v.get("displayHost") or "hh.ru"
        url = _vacancy_url(v, host, vid)
        out.append(
            VacancyItem(
                id=vid,
                title=html_lib.unescape(v.get("name") or ""),
                company=html_lib.unescape(company),
                salary=format_compensation(v.get("compensation") or {}),
                url=url,
            )
        )
    return out


def _vacancy_url(v: dict[str, Any], host: str, vid: str) -> str:
    links = v.get("links") or {}
    for key in ("desktop", "mobile"):
        href = links.get(key)
        if isinstance(href, str) and href.startswith("http"):
            return href
        if isinstance(href, str) and href.startswith("/"):
            return f"https://{host}{href}"
    click = v.get("clickUrl")
    if isinstance(click, str) and click.startswith("http"):
        return click
    return f"https://{host}/vacancy/{vid}"


def _money_int(val: Any) -> int | None:
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return int(val)
    s = re.sub(r"[^\d]", "", str(val))
    return int(s) if s else None


def _format_money_block(block: dict[str, Any]) -> str:
    fr = _money_int(block.get("from") or block.get("@from"))
    to = _money_int(block.get("to") or block.get("@to"))
    cur = block.get("currencyCode") or block.get("currency") or "RUR"
    gross = block.get("gross") if "gross" in block else block.get("@gross")
    net_label = "gross" if gross else "net"
    if fr and to:
        return f"{fr}–{to} {cur} ({net_label})"
    if fr:
        return f"от {fr} {cur} ({net_label})"
    if to:
        return f"до {to} {cur} ({net_label})"
    return ""


def format_compensation(comp: dict[str, Any]) -> str:
    if not comp or comp.get("noCompensation"):
        return "—"
    for key in (
        "fromTo",
        "onlyFrom",
        "onlyTo",
        "perModeFromTo",
        "range",
        "monthly",
        "month",
    ):
        block = comp.get(key)
        if isinstance(block, dict):
            text = _format_money_block(block)
            if text:
                return text
    # HH sometimes nests compensation under mode / value
    for block in comp.values():
        if isinstance(block, dict):
            text = _format_money_block(block)
            if text:
                return text
    return "—"


_SALARY_TO_RE = re.compile(
    r"до\s+(\d[\d\s\u00a0\u202f]*)\s*(?:₽|руб\.?|rur|rub)",
    re.I,
)
_SALARY_RANGE_RE = re.compile(
    r"(\d[\d\s\u00a0\u202f]*)\s*[–\-—]\s*(\d[\d\s\u00a0\u202f]*)\s*(?:₽|руб\.?|rur|rub)",
    re.I,
)
_SALARY_FROM_RE = re.compile(
    r"от\s+(\d[\d\s\u00a0\u202f]*)\s*(?:₽|руб\.?|rur|rub)",
    re.I,
)


def salary_from_html_text(html: str) -> str:
    text = strip_html(html)
    m = _SALARY_TO_RE.search(text)
    if m:
        val = _money_int(m.group(1))
        if val:
            return f"до {val} RUR (gross)"
    m = _SALARY_RANGE_RE.search(text)
    if m:
        lo, hi = _money_int(m.group(1)), _money_int(m.group(2))
        if lo and hi:
            return f"{lo}–{hi} RUR (gross)"
    m = _SALARY_FROM_RE.search(text)
    if m:
        val = _money_int(m.group(1))
        if val:
            return f"от {val} RUR (gross)"
    return "—"


def parse_vacancy_page(html: str) -> tuple[str, str]:
    """Return (description, salary) from a vacancy page."""
    data = parse_initial_state(html)
    description = parse_vacancy_description(html)
    salary = "—"
    if data:
        vv = data.get("vacancyView") or {}
        comp = vv.get("compensation") or vv.get("salary")
        if isinstance(comp, dict):
            salary = format_compensation(comp)
    if salary == "—":
        salary = salary_from_html_text(html)
    return description, salary


def _parse_fallback_links(html: str) -> list[VacancyItem]:
    out: list[VacancyItem] = []
    seen: set[str] = set()
    for m in re.finditer(
        r'data-qa="vacancy-serp__vacancy-title"[^>]*href="([^"]+/vacancy/(\d+))"[^>]*>([^<]+)',
        html,
    ):
        vid = m.group(2)
        if vid in seen:
            continue
        seen.add(vid)
        out.append(
            VacancyItem(
                id=vid,
                title=re.sub(r"\s+", " ", m.group(3)).strip(),
                company="—",
                salary="—",
                url=m.group(1),
            )
        )
    return out
