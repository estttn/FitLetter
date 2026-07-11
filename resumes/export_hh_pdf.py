#!/usr/bin/env python3
"""Export HH-formatted resume HTML files to PDF (Arial, Cyrillic)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

from fpdf import FPDF

ROOT = Path(__file__).resolve().parent
PDF_DIR = ROOT / "pdf"
FONT = Path(r"C:\Windows\Fonts\arial.ttf")
FONT_BOLD = Path(r"C:\Windows\Fonts\arialbd.ttf")

RESUMES = [
    ("hh-it-project-manager.html", "HH-PM-Baturin.pdf"),
    ("hh-kopirajter-b2b-it.html", "HH-Kopirajter-Baturin.pdf"),
    ("hh-biznes-analitik-it.html", "HH-BA-Baturin.pdf"),
]


class ResumePDF(FPDF):
    def __init__(self) -> None:
        super().__init__()
        self.set_margins(14, 12, 14)
        self.set_auto_page_break(auto=True, margin=12)
        self.add_font("Arial", "", str(FONT))
        self.add_font("Arial", "B", str(FONT_BOLD))


def extract_body(html: str) -> str:
    match = re.search(r"<body[^>]*>(.*)</body>", html, re.DOTALL | re.IGNORECASE)
    if not match:
        return html
    body = match.group(1)
    body = re.sub(r"<style[^>]*>.*?</style>", "", body, flags=re.DOTALL | re.IGNORECASE)
    return body.strip()


def export_pdf(html_name: str, pdf_name: str) -> Path:
    html_path = ROOT / html_name
    pdf_path = PDF_DIR / pdf_name
    if not html_path.exists():
        raise FileNotFoundError(html_path)
    if not FONT.exists():
        raise FileNotFoundError(f"Font not found: {FONT}")

    PDF_DIR.mkdir(parents=True, exist_ok=True)
    html = html_path.read_text(encoding="utf-8")
    body = extract_body(html)

    pdf = ResumePDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    pdf.write_html(body)
    pdf.output(str(pdf_path))
    return pdf_path


def main() -> None:
    paths: list[Path] = []
    for html, name in RESUMES:
        path = export_pdf(html, name)
        paths.append(path)
        print(path)
    print(f"\nDone: {len(paths)} PDF(s) -> {PDF_DIR}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
