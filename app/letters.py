# -*- coding: utf-8 -*-
"""Cover letters via DeepSeek PRO - tailored to company and vacancy."""
from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CANDIDATE = """
Владислав. UX/UI -> PM -> руководитель направления delivery (Smart Space Lab).
10+ лет digital, enterprise B2B: ERP, автоматизация, presale, внедрения, PMO.
Руковожу delivery: 3-4 PM, команды до 10-12 человек, presale -> сдача -> сопровождение.
Стартовал как UX/UI - стык дизайна, продукта и разработки.
Удалёнка, Ярославль. ЗП: от 180k на руки, комфортно 250k.
Английский язык не использую в работе - не упоминать.
""".strip()

BAD_PATTERNS = (
    "По описанию вижу пересечение с моим опытом",
    "UX/UI -> PM -> delivery: discovery, бэклог",
    "Задачи внедрения и интеграций близки: presale -> требования",
    "Вёл масштабные enterprise-проекты: проработка процессов",
    "английским владею",
    "владею английским",
    "английский свободно",
    "уровень англиского",
    "английский язык",
    "Upper-Intermediate",
    "upper-intermediate",
    "Pre-Intermediate",
    "Intermediate English",
    "Fluent English",
    "English - Upper",
    "English language",
    "bilingual",
    "английский на уровне",
)

_ENGLISH_SKILL_RE = re.compile(
    r"(англиск\w*|english|upper[\s-]?intermediate|pre[\s-]?intermediate|"
    r"fluent|bilingual|b1|b2|c1|уровень\s+языка)",
    re.IGNORECASE,
)


def _load_project_env() -> None:
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    with open(env_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            if line.startswith("export "):
                line = line[7:].strip()
            key, _, val = line.partition("=")
            os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))


_load_project_env()


def is_bad_letter(text: str) -> bool:
    lower = (text or "").lower()
    if any(p.lower() in lower for p in BAD_PATTERNS):
        return True
    if _ENGLISH_SKILL_RE.search(lower):
        return True
    if re.search(r"англиск\w*", lower) and re.search(
        r"(владе|свобод|upper|fluent|b2|c1|intermediate|bilingual)", lower
    ):
        return True
    return False

def is_complete_letter(text: str) -> bool:
    """Reject letters cut off by token limit or missing the standard footer."""
    t = (text or "").strip()
    if len(t) < 400:
        return False
    if is_bad_letter(t):
        return False
    if "Владислав" not in t:
        return False
    lower = t.lower()
    if "180" not in t and "на руки" not in lower:
        return False
    return True


def _clean_description(description: str, company: str) -> str:
    text = re.sub(r"\s+", " ", (description or "").strip())
    if not text:
        return ""
    text = re.sub(
        r"^(Мы\s*[—\-]\s*|We are\s*|О компании\s*|About us\s*)[^.]{0,200}\.\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )
    if company and company != "—":
        text = re.sub(
            rf"^{re.escape(company)}\s*[—\-]?\s*",
            "",
            text,
            flags=re.IGNORECASE,
        )
    return text[:2800].strip()


def _finalize_letter(content: str) -> str:
    """Trim cut-off tails and ensure standard HH footer."""
    t = content.strip()
    t = re.sub(r"^```(?:markdown|text)?\s*", "", t)
    t = re.sub(r"\s*```$", "", t).strip()
    sig = "Владислав"
    footer = "\n\nУдалёнка, Ярославль. ЗП: от 180k на руки.\n\nВладислав"
    if sig in t[-140:] and "180" in t[-220:]:
        return t
    if t and t[-1].isalpha():
        t = re.sub(r"[^.!?\n]*$", "", t).strip()
    if not t.endswith(sig):
        t = t.rstrip(".,;:- ") + footer
    return t

def generate_cover_letter(
    *,
    title: str,
    company: str,
    salary: str,
    description: str,
    profile: dict | None = None,
) -> str:
    desc = _clean_description(description, company)
    last_err: Exception | None = None
    for attempt in range(3):
        try:
            letter = _deepseek_letter(title, company, salary, desc, profile)
            if letter and is_complete_letter(letter):
                return letter
            print(
                f"Incomplete letter attempt {attempt + 1} [{title[:40]}]: len={len(letter or '')}",
                flush=True,
            )
        except Exception as e:
            last_err = e
            print(f"DeepSeek PRO attempt {attempt + 1} [{title[:40]}]: {e}")
            time.sleep(2 * (attempt + 1))
    if last_err:
        print(f"DeepSeek PRO failed after retries [{title[:40]}]: {last_err}")
    raise RuntimeError(f"DeepSeek PRO не смог сгенерировать письмо для «{title}»")


def _api_key() -> str:
    for name in ("DEEPSEEK_API_KEY", "DEEPSEEK_API_KEY_MAX"):
        val = os.environ.get(name, "").strip()
        if val:
            return val
    raise RuntimeError("DEEPSEEK_API_KEY не найден в /opt/hh-job-scout/.env")


def _model() -> str:
    return os.environ.get("DEEPSEEK_MODEL_LETTERS") or "deepseek-chat"


def _deepseek_letter(
    title: str,
    company: str,
    salary: str,
    description: str,
    profile: dict | None,
) -> str:
    company_clean = company if company and company != "—" else "компания"
    resume = (profile or {}).get("resume_summary") or CANDIDATE
    sal_note = salary if salary and salary not in ("—", "?") else "не указана"

    prompt = f"""Напиши сопроводительное письмо на русском для отклика на HeadHunter.

Компания-работодатель: {company_clean}
Вакансия: «{title}»
Зарплата: {sal_note}

Текст вакансии (суть и требования):
{description or "опирайся на название вакансии"}

Профиль кандидата (только для твоей ориентации, не копируй):
{resume}

Требования:
- Обращение к компании {company_clean} по имени, не обобщай HR-шаблоном
- Покажи пользу для вакансии «{title}» - минимум 2-3 конкретных задачи/результата из вакансии и связь с опытом кандидата
- Не шаблон и не список общих фраз, конкретика важнее общих слов
- Не повторяй дословно шаблонные фразы типа «По описанию вижу пересечение» или маркетинговые buzzwords без смысла
- НЕ упоминай английский язык, уровень владения и языковые навыки - у кандидата нет навыков английского, язык в работе не используется
- Не выдумывай английский и не подстраивай письмо под языковые требования - в сопроводительном их нет
- Если в вакансии требуется английский - не пиши, что владеешь; лучше не упоминать язык вообще
- 5-7 предложений, живой деловой тон
- Начни: «Добрый день!»
- Закончи: удобная связь, Ярославль, ЗП от 180k на руки. Подпись: Владислав
- Только текст письма, без markdown"""

    base = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/")
    max_tokens = int(os.environ.get("DEEPSEEK_MAX_TOKENS_PRO") or os.environ.get("DEEPSEEK_MAX_TOKENS") or "1200")

    payload = {
        "model": _model(),
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.5,
        "max_tokens": max_tokens,
    }
    req = urllib.request.Request(
        f"{base}/v1/chat/completions",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {_api_key()}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")[:300]
        raise RuntimeError(f"HTTP {e.code}: {body}") from e

    choice = data["choices"][0]
    if choice.get("finish_reason") == "length":
        raise RuntimeError("truncated: max_tokens")

    content = choice["message"]["content"].strip()
    return _finalize_letter(content)
