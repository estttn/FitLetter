# -*- coding: utf-8 -*-
"""Per-role search and letter settings for multi-resume FitLetter."""
from __future__ import annotations

from typing import Any

ROLE_PM = "pm"
ROLE_COPYWRITER = "copywriter"
ROLE_BA = "ba"

PROFILE_PRESERVE_KEYS = (
    "role",
    "target_role",
    "letter_focus",
    "search_queries",
    "include_title_keywords",
    "exclude_title_keywords",
    "exclude_english_keywords",
    "salary_min_net",
    "salary_comfort_net",
    "area",
    "remote",
    "search_period",
    "pages_per_query",
    "request_delay_sec",
    "letter_delay_sec",
    "experience",
)

ROLE_TEMPLATES: dict[str, dict[str, Any]] = {
    ROLE_PM: {
        "role": ROLE_PM,
        "target_role": "IT Project Manager (middle)",
        "letter_focus": (
            "Заказная B2B-разработка, ведение проектов под ключ: сроки, команда, "
            "ТЗ, ERP, автоматизация, работа с заказчиком."
        ),
        "salary_min_net": 80000,
        "salary_comfort_net": 120000,
        "search_queries": [
            "IT project manager заказная разработка",
            "менеджер IT проектов удаленно",
            "project manager внедрение ERP",
        ],
        "include_title_keywords": [
            "project",
            "проджект",
            "проект",
            "pm",
            "менеджер проектов",
            "it project",
            "delivery",
            "руководитель проектов",
        ],
        "exclude_title_keywords": [
            "product owner",
            "scrum master",
            "junior",
            "стажер",
            "стажёр",
            "1c программист",
            "разработчик",
            "developer",
            "анalyst",
            "аналитик",
            "копирайт",
            "редактор",
            "маркетолог",
        ],
    },
    ROLE_COPYWRITER: {
        "role": ROLE_COPYWRITER,
        "target_role": "Копирайтер B2B IT",
        "letter_focus": (
            "Тексты для IT-компаний: кейсы, лендинги, КП, статьи, описания продуктов. "
            "Опыт в заказной разработке и понимание B2B IT изнутри."
        ),
        "salary_min_net": 60000,
        "salary_comfort_net": 80000,
        "search_queries": [
            "копирайтер IT",
            "контент-маркетолог IT",
            "редактор B2B IT",
            "технический писатель IT",
        ],
        "include_title_keywords": [
            "копирайт",
            "редактор",
            "контент",
            "writer",
            "copywriter",
            "текст",
            "маркетолог",
            "писатель",
        ],
        "exclude_title_keywords": [
            "smm",
            "таргет",
            "performance",
            "видеомонтаж",
            "дизайнер",
            "junior",
            "стажер",
            "стажёр",
            "ассистент",
            "project",
            "проджект",
            "pm ",
        ],
    },
    ROLE_BA: {
        "role": ROLE_BA,
        "target_role": "Бизнес-аналитик IT (middle)",
        "letter_focus": (
            "Сбор требований, discovery, описание процессов, подготовка и согласование ТЗ "
            "до старта разработки. Опыт ERP, автоматизации, B2B."
        ),
        "salary_min_net": 80000,
        "salary_comfort_net": 100000,
        "search_queries": [
            "бизнес-аналитик IT",
            "business analyst IT",
            "аналитик discovery IT",
        ],
        "include_title_keywords": [
            "бизнес-аналитик",
            "business analyst",
            "аналитик",
            " ba",
            "ba ",
        ],
        "exclude_title_keywords": [
            "системный аналитик",
            "system analyst",
            "data analyst",
            "data engineer",
            "1c программист",
            "sql developer",
            "junior",
            "стажер",
            "стажёр",
            "копирайт",
            "project manager",
        ],
    },
}

# Global non-IT filter phrases to ignore for specific roles (substring in title).
ROLE_NON_IT_SKIP: dict[str, tuple[str, ...]] = {
    ROLE_COPYWRITER: (
        "копирайт",
        "маркетолог",
    ),
    ROLE_BA: (),
    ROLE_PM: (),
}


def detect_role_from_name(name: str) -> str | None:
    n = (name or "").lower().replace("ё", "e")
    if "копирайт" in n or "copywriter" in n or "контент" in n:
        return ROLE_COPYWRITER
    if n.strip() == "ba" or "аналитик" in n or "business analyst" in n:
        return ROLE_BA
    if n.strip() == "pm" or "project manager" in n or "проджект" in n or "менеджер проектов" in n:
        return ROLE_PM
    return None


def apply_role_template(profile: dict[str, Any], role: str) -> dict[str, Any]:
    template = ROLE_TEMPLATES.get(role)
    if not template:
        return profile
    out = dict(profile)
    out.update(template)
    return out


def merge_preserved_profile(old: dict[str, Any], new: dict[str, Any]) -> dict[str, Any]:
    """Keep search/role settings when re-parsing resume text."""
    out = dict(new)
    for key in PROFILE_PRESERVE_KEYS:
        if key in old and old[key] not in (None, "", [], {}):
            out[key] = old[key]
    return out
