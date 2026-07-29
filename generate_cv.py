#!/usr/bin/env python3
"""
CV Generator
------------
Generates a CV as HTML and PDF from a JSON data file and a CSS file.

Usage:
    python generate_cv.py
    python generate_cv.py --json cv_data.json --css cv.css --output my_cv.pdf
    python generate_cv.py --lang pt
    python generate_cv.py --html-only

Requires a contact_private.json file (not checked into git) providing
email, mobile, and whatsapp_link — see README.md for the expected shape.

See README.md for installation instructions.
"""

import argparse
import json
import sys
from pathlib import Path


# ── Translation helper ────────────────────────────────────────────────────────

def t(field, lang: str, fallback: str = "en") -> str:
    """
    Extract a translated string from a field.
    - Plain string  → returned as-is (no translation needed)
    - Dict          → looks up lang, then fallback, then first available value
    """
    if isinstance(field, str):
        return field
    if isinstance(field, dict):
        return field.get(lang) or field.get(fallback) or next(iter(field.values()))
    return str(field)


# ── HTML helpers ──────────────────────────────────────────────────────────────

def esc(text: str) -> str:
    """Minimal HTML escaping for plain text values from JSON."""
    return (
        text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


CONTACT_LABELS = {
    "en": {
        "email":    "Email",
        "mobile":   "Mobile / WhatsApp",
        "linkedin": "LinkedIn",
        "github":   "GitHub"
    },
    "pt": {
        "email":    "E-mail",
        "mobile":   "Celular / WhatsApp",
        "linkedin": "LinkedIn",
        "github":   "GitHub"
    }
}


def get_contact_label(key: str, lang: str) -> str:
    return CONTACT_LABELS.get(lang, {}).get(key) or CONTACT_LABELS["en"][key]


def build_header(contact: dict, lang: str) -> str:
    name           = esc(t(contact['name'], lang))
    location       = esc(t(contact['location'], lang))
    email          = esc(t(contact['email'], lang))
    mobile         = esc(t(contact['mobile'], lang))
    whatsapp_link  = esc(t(contact['whatsapp_link'], lang))
    linkedin_url   = esc(t(contact['linkedin_url'], lang))
    linkedin_label = esc(t(contact['linkedin_label'], lang))
    github_url     = esc(t(contact['github_url'], lang))
    github_label   = esc(t(contact['github_label'], lang))

    email_label    = esc(get_contact_label("email", lang))
    mobile_label   = esc(get_contact_label("mobile", lang))
    linkedin_lbl   = esc(get_contact_label("linkedin", lang))
    github_lbl     = esc(get_contact_label("github", lang))

    return f"""  <header>
    <div class="name-block">
      <h1>{name}</h1>
      <p>{location}</p>
    </div>
    <div class="contact-block">
      <div><span class="contact-label">{email_label}</span> <a href="mailto:{email}">{email}</a></div>
      <div><span class="contact-label">{mobile_label}</span> <a href="{whatsapp_link}">{mobile}</a></div>
      <div><span class="contact-label">{linkedin_lbl}</span> <a href="{linkedin_url}">{linkedin_label}</a></div>
      <div><span class="contact-label">{github_lbl}</span> <a href="{github_url}">{github_label}</a></div>
    </div>
  </header>"""


def build_summary(items: list, lang: str, label: str) -> str:
    bullets = "\n".join(
        f"        <li>{esc(t(item, lang))}</li>" for item in items
    )
    return f"""    <div class="section-title">{esc(label)}</div>
    <div class="summary">
      <ul>
{bullets}
      </ul>
    </div>"""


def build_skills(groups: list, lang: str, label: str) -> str:
    html = f'    <div class="section-title">{esc(label)}</div>\n'
    for group in groups:
        items = "\n".join(
            f'        <li>{esc(t(item, lang))}</li>' for item in group["items"]
        )
        html += f"""    <div class="skill-group">
      <h4>{esc(t(group['group'], lang))}</h4>
      <ul>
{items}
      </ul>
    </div>\n"""
    return html


def build_languages(languages: list, lang: str, label: str) -> str:
    html = f'    <div class="section-title">{esc(label)}</div>\n'
    for item in languages:
        html += f"""    <div class="lang-item">
      <span class="lang-name">{esc(t(item['name'], lang))}</span>
      <span class="lang-level">{esc(t(item['level'], lang))}</span>
    </div>\n"""
    return html


def build_education(education: list, lang: str, label: str) -> str:
    html = f'    <div class="section-title">{esc(label)}</div>\n'
    for edu in education:
        html += f"""    <div class="edu-item">
      <div class="degree">{esc(t(edu['degree'], lang))}</div>
      <div class="institution">
        {esc(t(edu['institution'], lang))}<br/>
        {esc(t(edu['location'], lang))}
      </div>
      <div class="year">{esc(edu['year'])}</div>
    </div>\n"""
    return html


def build_experience(companies: list, lang: str, label: str) -> str:
    html = f'    <div class="section-title">{esc(label)}</div>\n'
    for company in companies:
        note = t(company.get("note", ""), lang)
        note_html = (
            f'        <span class="company-note">({esc(note)})</span>'
            if note
            else ""
        )
        roles_html = ""
        for role in company["roles"]:
            bullets = "\n".join(
                f'            <li>{esc(t(b, lang))}</li>' for b in role["bullets"]
            )
            roles_html += f"""      <div class="role">
        <div class="role-header">
          <span class="role-title">{esc(t(role['title'], lang))}</span>
          <span class="role-meta">{esc(t(role['period'], lang))}</span>
        </div>
        <div class="role-location">{esc(t(role['location'], lang))}</div>
        <ul>
{bullets}
        </ul>
      </div>\n"""

        html += f"""    <div class="company">
      <div class="company-header">
        <span class="company-name">{esc(t(company['company'], lang))}</span>
{note_html}
      </div>
{roles_html}    </div>\n"""
    return html


# ── Section labels ────────────────────────────────────────────────────────────

DEFAULT_LABELS = {
    "en": {
        "summary":    "Professional Summary",
        "skills":     "Core Skills",
        "languages":  "Languages",
        "education":  "Education",
        "experience": "Professional Experience"
    },
    "pt": {
        "summary":    "Resumo Profissional",
        "skills":     "Competências Principais",
        "languages":  "Idiomas",
        "education":  "Formação Acadêmica",
        "experience": "Experiência Profissional"
    }
}

def get_label(data: dict, section: str, lang: str) -> str:
    """
    Looks up a section label. Priority:
    1. Explicit override in JSON under meta.section_labels.<lang>.<section>
    2. Built-in DEFAULT_LABELS for the requested language
    3. Built-in DEFAULT_LABELS for English
    4. The section key itself as a last resort
    """
    overrides = data.get("meta", {}).get("section_labels", {})
    lang_overrides = overrides.get(lang, {})
    if section in lang_overrides:
        return lang_overrides[section]
    return (
        DEFAULT_LABELS.get(lang, {}).get(section)
        or DEFAULT_LABELS.get("en", {}).get(section)
        or section
    )


# ── HTML assembly ─────────────────────────────────────────────────────────────

def build_html(data: dict, css_path: Path, lang: str) -> str:
    title      = t(data["meta"]["title"], lang)
    header     = build_header(data["contact"], lang)
    skills     = build_skills(data["skills"],         lang, get_label(data, "skills",     lang))
    languages  = build_languages(data["languages"],   lang, get_label(data, "languages",  lang))
    education  = build_education(data["education"],   lang, get_label(data, "education",  lang))
    summary    = build_summary(data["summary"],       lang, get_label(data, "summary",    lang))
    experience = build_experience(data["experience"], lang, get_label(data, "experience", lang))

    return f"""<!DOCTYPE html>
<html lang="{esc(lang)}">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{esc(title)}</title>
  <link rel="stylesheet" href="{css_path.name}"/>
</head>
<body>
<div class="page">

{header}

  <aside class="sidebar">
{skills}
{languages}
{education}
  </aside>

  <main class="main">
{summary}
{experience}
  </main>

</div>
</body>
</html>"""


# ── PDF conversion ────────────────────────────────────────────────────────────

def html_to_pdf(html_path: Path, pdf_path: Path) -> None:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print(
            "\n  ERROR: Playwright is not installed.\n"
            "  Run the following and try again:\n"
            "    pip install playwright\n"
            "    playwright install chromium\n"
        )
        sys.exit(1)

    file_uri = html_path.resolve().as_uri()

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(file_uri, wait_until="networkidle")
        page.pdf(
            path=str(pdf_path),
            format="A4",
            print_background=True,
            margin={
                "top":    "10mm",
                "bottom": "10mm",
                "left":   "0mm",
                "right":  "0mm"
            }
        )
        browser.close()


# ── CLI ───────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a CV as HTML and PDF "
            "from a JSON data file and a CSS file."
        )
    )
    parser.add_argument(
        "--json",
        default="cv_data.json",
        metavar="FILE",
        help="Path to the JSON data file  (default: cv_data.json)"
    )
    parser.add_argument(
        "--css",
        default="cv.css",
        metavar="FILE",
        help="Path to the CSS file         (default: cv.css)"
    )
    parser.add_argument(
        "--contact",
        default="contact_private.json",
        metavar="FILE",
        help="Path to the private contact JSON (email, mobile, whatsapp_link) — "
             "not checked into git (default: contact_private.json)"
    )
    parser.add_argument(
        "--lang",
        default=None,
        metavar="LANG",
        help="Language code to generate    (default: taken from JSON meta.default_language, or 'en')"
    )
    parser.add_argument(
        "--all-languages",
        action="store_true",
        help="Generate a PDF for every language listed in meta.languages_available"
    )
    parser.add_argument(
        "--output",
        default=None,
        metavar="FILE",
        help="Output PDF filename           (default: taken from JSON meta.output_pdf, with language code appended)"
    )
    parser.add_argument(
        "--html-only",
        action="store_true",
        help="Generate HTML only, skip PDF conversion"
    )
    return parser.parse_args()


def generate_one(data: dict, css_path: Path, lang: str,
                 output: str | None, html_only: bool) -> None:
    """Build HTML and optionally PDF for a single language."""
    pdf_filename = output or data["meta"].get("output_pdf", "cv_output.pdf")
    pdf_path  = Path(pdf_filename).with_stem(f"{Path(pdf_filename).stem}_{lang}")
    html_path = pdf_path.with_suffix(".html")

    print(f"\n  Language : {lang}")
    html_content = build_html(data, css_path, lang)
    html_path.write_text(html_content, encoding="utf-8")
    print(f"  Written  HTML : {html_path}")

    if html_only:
        print("  Skipped  PDF  : (--html-only flag set)")
    else:
        print(f"  Generating PDF: {pdf_path}  ", end="", flush=True)
        html_to_pdf(html_path, pdf_path)
        print("done.")


def main() -> None:
    args = parse_args()

    json_path    = Path(args.json)
    css_path     = Path(args.css)
    contact_path = Path(args.contact)

    for path in (json_path, css_path):
        if not path.exists():
            print(f"\n  ERROR: File not found: {path}\n")
            sys.exit(1)

    if not contact_path.exists():
        print(
            f"\n  ERROR: Private contact file not found: {contact_path}\n"
            f"  This file holds your email, mobile, and WhatsApp link and is "
            f"intentionally not checked into git.\n"
            f"  Create it with the following shape and try again:\n\n"
            f'    {{\n'
            f'      "email": "you@example.com",\n'
            f'      "mobile": "+1 (555) 123-4567",\n'
            f'      "whatsapp_link": "https://wa.me/15551234567"\n'
            f'    }}\n'
        )
        sys.exit(1)

    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"\n  ERROR: Invalid JSON in {json_path}:\n  {e}\n")
        sys.exit(1)

    try:
        contact_data = json.loads(contact_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"\n  ERROR: Invalid JSON in {contact_path}:\n  {e}\n")
        sys.exit(1)

    data["contact"].update(contact_data)

    print(f"\n  Reading  JSON : {json_path}")
    print(f"  Reading  CSS  : {css_path}")
    print(f"  Reading  Contact (private) : {contact_path}")

    if args.all_languages:
        available = data.get("meta", {}).get("languages_available", ["en"])
        for lang in available:
            generate_one(data, css_path, lang, args.output, args.html_only)
    else:
        lang = args.lang or data.get("meta", {}).get("default_language", "en")
        generate_one(data, css_path, lang, args.output, args.html_only)

    print("\n  All done.\n")


if __name__ == "__main__":
    main()
