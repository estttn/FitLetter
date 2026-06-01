# -*- coding: utf-8 -*-
from __future__ import annotations

import re

_ENGLISH_PHRASES = (
    "english",
    "\u0430\u043d\u0433\u043b\u0438\u0439\u0441\u043a",
    "\u0430\u043d\u0433\u043b \u044f\u0437\u044b\u043a",
    "\u0430\u043d\u0433\u043b. \u044f\u0437\u044b\u043a",
    "in english",
    "fluent english",
    "business english",
    "english speaking",
    "native english",
    "\u043d\u0430 \u0430\u043d\u0433\u043b\u0438\u0439\u0441\u043a\u043e\u043c",
    "\u0440\u0430\u0437\u0433\u043e\u0432\u043e\u0440\u043d\u044b\u0439 \u0430\u043d\u0433\u043b",
    "\u0437\u043d\u0430\u043d\u0438\u0435 \u0430\u043d\u0433\u043b",
    "english c1",
    "english c2",
    "english b1",
    "english b2",
    "\u0430\u043d\u0433\u043b\u0438\u0439\u0441\u043a\u0438\u0439 c1",
    "\u0430\u043d\u0433\u043b\u0438\u0439\u0441\u043a\u0438\u0439 b2",
    "\u0430\u043d\u0433\u043b\u0438\u0439\u0441\u043a\u0438\u0439 b1",
    "upper-intermediate",
    "upper intermediate",
    "\u0443\u0440\u043e\u0432\u0435\u043d\u044c c1",
    "\u0443\u0440\u043e\u0432\u0435\u043d\u044c c2",
    "\u0443\u0440\u043e\u0432\u0435\u043d\u044c b1",
    "\u0443\u0440\u043e\u0432\u0435\u043d\u044c b2",
    "b2/c1",
    "b1/c1",
    "bilingual",
    "\u0431\u0438\u043b\u0438\u043d\u0433\u0432",
)

_ENGLISH_LEVEL_RE = re.compile(
    r"(?:"
    r"(?:english|\u0430\u043d\u0433\u043b\u0438\u0439\u0441\u043a\w*)\s*[-:(]?\s*"
    r"(?:upper[\s-]?intermediate|advanced|fluent|b1|b2|c1|c2|native)"
    r"|(?:upper[\s-]?intermediate|advanced|fluent)\s+"
    r"(?:english|\u0430\u043d\u0433\u043b\u0438\u0439\u0441\u043a\w*)"
    r"|(?:\u0443\u0440\u043e\u0432\u0435\u043d\u044c|level)\s*[-:]?\s*"
    r"(?:b1|b2|c1|c2|upper|advanced|fluent)"
    r")",
    re.IGNORECASE,
)

# Non-IT roles that often match generic keywords like "\u0440\u0443\u043a\u043e\u0432\u043e\u0434\u0438\u0442\u0435\u043b\u044c"
_NON_IT_PHRASES = (
    "\u0431\u0435\u0437\u043e\u043f\u0430\u0441\u043d",
    "\u043e\u0445\u0440\u0430\u043d",
    "\u0441\u043b\u0443\u0436\u0431 \u0431\u0435\u0437\u043e\u043f\u0430\u0441",
    "\u0441\u0431 \u0431\u0430\u043d\u043a",
    "\u043a\u0430\u0434\u0440",
    "recruit",
    "\u0440\u0435\u043a\u0440\u0443\u0442",
    "\u0431\u0443\u0445\u0433\u0430\u043b",
    "\u044e\u0440\u0438\u0434",
    "\u044e\u0440\u0438\u0441\u0442",
    "\u0430\u0434\u0432\u043e\u043a\u0430\u0442",
    "\u0430\u043c\u0431\u0430\u0441\u0441\u0430\u0434",
    "pr lead",
    "pr-",
    "\u043f\u0440-\u043d\u0430\u043f\u0440\u0430\u0432",
    "\u043f\u0438\u0430\u0440",
    "\u0441\u0438\u0441\u0442\u0435\u043c\u043d\u044b\u0445 \u0430\u043d\u0430\u043b\u0438\u0442",
    "\u0441\u0438\u0441\u0442\u0435\u043c\u043d\u044b\u0439 \u0430\u043d\u0430\u043b\u0438\u0442",
    "\u0433\u0440\u0443\u043f\u043f\u044b \u0430\u043d\u0430\u043b\u0438\u0442",
    "\u0440\u0443\u043a\u043e\u0432\u043e\u0434\u0438\u0442\u0435\u043b\u044c \u0433\u0440\u0443\u043f\u043f\u044b \u0430\u043d\u0430\u043b\u0438\u0442",
    "\u0443\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u0435 \u0434\u0430\u043d\u043d",
    "\u0443\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u044f \u0434\u0430\u043d\u043d",
    "\u043e\u0442\u0434\u0435\u043b\u0430 \u0443\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u044f \u0434\u0430\u043d\u043d",
    "\u043f\u0440\u043e\u0434\u0430\u0436",
    "sales",
    "\u043a\u043e\u043c\u043c\u0435\u0440\u0447",
    "\u0442\u043e\u0440\u0433\u043e\u0432",
    "\u043c\u0430\u0440\u043a\u0435\u0442\u043e\u043b\u043e\u0433",
    "smm",
    "\u043a\u043e\u043f\u0438\u0440\u0430\u0439\u0442",
    "\u043a\u043b\u0430\u0434\u043e\u0432\u0449",
    "\u043c\u0435\u0434\u0438\u0446",
    "\u0432\u0440\u0430\u0447",
    "\u043c\u0435\u0434\u0441\u0435\u0441\u0442\u0440",
    "\u043f\u043e\u0432\u0430\u0440",
    "\u0443\u0431\u043e\u0440\u0449",
    "\u043a\u043b\u0438\u043d\u0438\u043d\u0433",
    "\u043e\u043f\u0435\u0440\u0430\u0442\u043e\u0440 \u0441\u0442\u0430\u043d",
    "\u043c\u0430\u0441\u0442\u0435\u0440 \u0441\u0442\u0430\u043d",
    "\u0441\u0435\u043a\u0440\u0435\u0442\u0430\u0440",
    "\u0434\u0438\u0440\u0435\u043a\u0442\u043e\u0440 \u043c\u0430\u0433\u0430\u0437",
    "\u0437\u0430\u0432\u0435\u0434\u0443\u044e\u0449",
    "\u0433\u043b\u0430\u0432\u043d\u044b\u0439 \u0431\u0443\u0445\u0433\u0430\u043b\u0442\u0435\u0440",
    "\u0444\u0438\u043d\u0430\u043d\u0441\u043e\u0432\u044b\u0439 \u0434\u0438\u0440\u0435\u043a\u0442\u043e\u0440",
    "\u0433\u0435\u043d\u0435\u0440\u0430\u043b\u044c\u043d",
    "\u043b\u043e\u0433\u0438\u0441\u0442",
    "\u0441\u043a\u043b\u0430\u0434",
    "\u043f\u0440\u043e\u0438\u0437\u0432\u043e\u0434",
    "\u0442\u0435\u0445\u043d\u043e\u043b\u043e\u0433 \u0441\u0442\u0430\u043d",
    "\u0441\u043d\u0430\u0431\u0436\u0435\u043d",
    "\u043a\u0430\u0441\u0441\u0438\u0440",
    "\u043e\u0444\u0438\u0446\u0438\u0430\u043d\u0442",
    "\u0430\u0434\u043c\u0438\u043d\u0438\u0441\u0442\u0440\u0430\u0442\u043e\u0440 \u043e\u0444\u0438\u0441",
    "\u0430\u0434\u043c\u0438\u043d\u0438\u0441\u0442\u0440\u0430\u0442\u043e\u0440 \u043f\u0440\u0438\u0435\u043c",
    "\u0434\u0438\u0440\u0435\u043a\u0442\u043e\u0440 \u043f\u043e \u043f\u0435\u0440\u0441\u043e\u043d\u0430\u043b\u0443",
    "\u043c\u0435\u043d\u0435\u0434\u0436\u0435\u0440 \u043f\u043e \u043f\u0435\u0440\u0441\u043e\u043d\u0430\u043b\u0443",
)

_NON_IT_WORDS = (
    "hr",
    "\u0432\u043e\u0434\u0438\u0442\u0435\u043b\u044c",
    "\u043a\u0443\u0440\u044c\u0435\u0440",
)

_DEV_LEAD = (
    "node.js",
    "nodejs",
    " golang",
    "golang ",
    "backend",
    "frontend",
    "front-end",
    "fullstack",
    "full-stack",
    "tech lead",
    "team lead \u0440\u0430\u0437\u0440\u0430\u0431",
    "\u0433\u0440\u0443\u043f\u043f\u044b \u0440\u0430\u0437\u0440\u0430\u0431",
    "\u0440\u0443\u043a\u043e\u0432\u043e\u0434\u0438\u0442\u0435\u043b\u044c \u0440\u0430\u0437\u0440\u0430\u0431",
    "python dev",
    "java dev",
    "c++",
    "devops",
    "sre ",
    " qa lead",
)

_IT_CONTEXT = (
    " it ",
    " it-",
    "-it ",
    "\u0438\u0442 ",
    "\u0438\u0442-",
    "digital",
    "\u0434\u0438\u0434\u0436\u0438\u0442",
    "software",
    "\u0441\u043e\u0444\u0442",
    "\u0440\u0430\u0437\u0440\u0430\u0431",
    "dev",
    "delivery",
    "\u0432\u043d\u0435\u0434\u0440",
    "\u0430\u0432\u0442\u043e\u043c\u0430\u0442\u0438\u0437",
    "erp",
    "crm",
    "pmo",
    "enterprise",
    "\u043f\u0440\u043e\u0435\u043a\u0442",
    "project",
    "\u043f\u0440\u043e\u0434\u0436\u0435\u043a\u0442",
    "\u043f\u0440\u043e\u0434\u0443\u043a\u0442",
    "product",
    "presale",
    "\u043f\u0440\u0435\u0441\u0435\u0439\u043b",
    "\u043f\u0440\u043e\u0433\u0440\u0430\u043c\u043c",
    "\u0441\u0438\u0441\u0442\u0435\u043c",
    "\u0442\u0435\u0445\u043d",
    "\u0438\u043d\u0442\u0435\u0433\u0440",
    "data",
    "\u0431\u0438\u0442\u0440\u0438\u043a\u0441",
    "1c",
    "1\u0441",
    "web",
    "saas",
    "scrum",
    "agile",
    "jira",
    "pm ",
    " pm",
    "pmo",
)

_LEADER_WORD = "\u0440\u0443\u043a\u043e\u0432\u043e\u0434\u0438\u0442\u0435\u043b\u044c"


def _norm(s: str) -> str:
    return (s or "").lower().replace("\u0451", "e")


def _padded(s: str) -> str:
    return f" {s} "


def _has_it_context(title: str) -> bool:
    t = _padded(_norm(title))
    return any(k in t for k in _IT_CONTEXT)


def _non_it_reason(title: str) -> str | None:
    t = _norm(title)
    t_pad = _padded(t)
    for kw in _NON_IT_PHRASES:
        if kw in t:
            return f"non-it: {kw.strip()}"
    for kw in _NON_IT_WORDS:
        if f" {kw.strip()} " in t_pad:
            return f"non-it: {kw.strip()}"
    return None


def english_requirement_reason(*texts: str) -> str | None:
    combined = _norm(" ".join(t for t in texts if t))
    if not combined:
        return None
    for phrase in _ENGLISH_PHRASES:
        if phrase in combined:
            return f"english: {phrase}"
    if _ENGLISH_LEVEL_RE.search(combined):
        return "english: level"
    return None


def score_vacancy(
    *,
    title: str,
    company: str,
    salary: str,
    description: str = "",
    profile: dict,
) -> tuple[str, str]:
    t = _norm(title)
    t_pad = _padded(t)
    sal = _norm(salary)

    for kw in profile.get("exclude_title_keywords", []):
        if _norm(kw) in t:
            return "no", f"exclude: {kw}"

    non_it = _non_it_reason(title)
    if non_it:
        return "no", non_it

    for kw in _DEV_LEAD:
        if kw in t_pad or kw.strip() in t:
            return "no", f"dev-lead: {kw.strip()}"

    eng = english_requirement_reason(title, description)
    if eng:
        return "no", eng

    for kw in profile.get("exclude_english_keywords", []):
        if _norm(kw) in _norm(f"{title} {description}"):
            return "no", f"english: {kw}"

    if not any(_norm(kw) in t for kw in profile.get("include_title_keywords", [])):
        return "no", "no PM/delivery keywords in title"

    if _LEADER_WORD in t and not _has_it_context(title):
        return "no", "leader without IT/project context"

    m = re.search(r"(\d[\d\s]*)\s*-?\s*(\d[\d\s]*)?\s*rur\s*\(gross\)", sal)
    if m:
        low = int(m.group(1).replace(" ", ""))
        if low < 200000:
            return "no", "salary gross below threshold"

    strong = [
        "delivery",
        "\u0432\u043d\u0435\u0434\u0440\u0435\u043d",
        "presale",
        "\u043f\u0440\u0435\u0441\u0435\u0439\u043b",
        "pmo",
        "enterprise",
        "\u0440\u0443\u043a\u043e\u0432\u043e\u0434\u0438\u0442\u0435\u043b\u044c \u043f\u0440\u043e\u0435\u043a\u0442",
        "\u0440\u0443\u043a\u043e\u0432\u043e\u0434\u0438\u0442\u0435\u043b\u044c \u043f\u0440\u043e\u0433\u0440\u0430\u043c\u043c",
        "\u0440\u0443\u043a\u043e\u0432\u043e\u0434\u0438\u0442\u0435\u043b\u044c it",
        "\u0440\u0443\u043a\u043e\u0432\u043e\u0434\u0438\u0442\u0435\u043b\u044c \u043d\u0430\u043f\u0440\u0430\u0432\u043b\u0435\u043d",
        "\u0440\u0443\u043a\u043e\u0432\u043e\u0434\u0438\u0442\u0435\u043b\u044c delivery",
    ]
    partial = [
        "project",
        "\u043f\u0440\u043e\u0434\u0436\u0435\u043a\u0442",
        "\u043f\u0440\u043e\u0435\u043a\u0442",
        "product",
        "\u043f\u0440\u043e\u0434\u0443\u043a\u0442",
        "pm",
    ]

    if any(k in t for k in strong):
        return "yes", "strong role match"
    if _LEADER_WORD in t and _has_it_context(title):
        return "yes", "IT leader match"
    if any(k in t for k in partial):
        return "partial", "partial role match"
    return "partial", "passed base filter"
