#!/usr/bin/env python3
"""Convert the html HTML documentation files in html/ to Markdown in markdown/."""

import re
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString, Tag

DOCS_DIR = Path(__file__).parent.parent / "docs"
SPLIT_DIR = DOCS_DIR / "html"
OUTPUT_DIR = DOCS_DIR / "markdown"

DOCS_DIR.mkdir(exist_ok=True)
SPLIT_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)


def _convert_inline(element):
    """Convert an element's children to inline markdown (handles nested formatting).

    When a tag like ``<a>`` is stripped, surrounding whitespace may be lost.
    Callers that need compact output (e.g. list items, table cells) should
    normalize the result with ``" ".join(text.html())``.
    """
    parts = []
    for child in element.children:
        if isinstance(child, NavigableString):
            parts.append(str(child))
        elif isinstance(child, Tag):
            if child.name == "strong":
                parts.append(f"**{_convert_inline(child)}**")
            elif child.name == "em":
                parts.append(f"*{_convert_inline(child)}*")
            elif child.name == "code":
                parts.append(f"`{_convert_inline(child)}`")
            elif child.name == "a":
                parts.append(_convert_inline(child))
            elif child.name == "br":
                parts.append("\n")
            else:
                parts.append(_convert_inline(child))
    return "".join(parts)


def _heading_to_md(element):
    level = int(element.name[1])
    anchor = element.find("a", class_="anchor")
    if anchor:
        anchor.decompose()
    return f"{'#' * level} {element.get_text(strip=True)}\n\n"


def _table_to_md(element):
    headers = []
    thead = element.find("thead")
    if thead:
        for th in thead.find_all("th"):
            headers.append(th.get_text(strip=True))

    rows = []
    tbody = element.find("tbody")
    if tbody:
        for tr in tbody.find_all("tr"):
            cells = [" ".join(td.get_text().split()) for td in tr.find_all("td")]
            rows.append(cells)

    lines = []
    if headers:
        lines.append("| " + " | ".join(headers) + " |")
        lines.append("| " + " | ".join("---" for _ in headers) + " |")
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines) + "\n\n"


def _list_to_md(element):
    lines = []
    for li in element.find_all("li", recursive=False):
        parts = []
        for child in li.children:
            if isinstance(child, NavigableString):
                parts.append(str(child))
            elif isinstance(child, Tag):
                inner = _convert_inline(child)
                if child.name == "strong":
                    parts.append(f" **{inner}** ")
                elif child.name == "em":
                    parts.append(f" *{inner}* ")
                elif child.name == "code":
                    parts.append(f" `{inner}` ")
                elif child.name == "a":
                    parts.append(f" {inner} ")
                elif child.name == "br":
                    parts.append("\n")
                else:
                    parts.append(inner)
        text = " ".join("".join(parts).split())
        lines.append(f"- {text}")
    return "\n".join(lines) + "\n\n"


def _blockquote_to_md(element):
    lines = []
    for child in element.children:
        if isinstance(child, Tag):
            text = " ".join(_convert_inline(child).split())
            for line in text.split("\n"):
                lines.append(f"> {line}")
    return "\n".join(lines) + "\n\n"


def _element_to_md(element):
    if not isinstance(element, Tag):
        return ""
    if element.name in ("h3", "h4", "h5", "h6"):
        return _heading_to_md(element)
    if element.name == "p":
        return " ".join(_convert_inline(element).split()) + "\n\n"
    if element.name == "table":
        return _table_to_md(element)
    if element.name in ("ul", "ol"):
        return _list_to_md(element)
    if element.name == "pre":
        code = element.find("code")
        text = code.get_text() if code else element.get_text()
        if not text.endswith("\n"):
            text += "\n"
        max_backticks = max((len(m.group(0)) for m in re.finditer(r'`+', text)), default=0)
        fence = '`' * max(max_backticks + 1, 3)
        return f"{fence}\n{text}{fence}\n\n"
    if element.name == "blockquote":
        return _blockquote_to_md(element)
    return ""


def convert_file(html_path):
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
    content = soup.find("div", id="dev_page_content")
    if not content:
        return None

    md_parts = []
    for element in content.children:
        if isinstance(element, Tag):
            md_parts.append(_element_to_md(element))

    return "".join(md_parts).strip() + "\n"


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    html_files = sorted(p for p in SPLIT_DIR.glob("*.html") if p.name != "index.html")
    print(f"Converting {len(html_files)} HTML files to Markdown...")

    for html_path in html_files:
        md_content = convert_file(html_path)
        if md_content is None:
            print(f"  Skipping {html_path.name} (no content div)")
            continue
        out_path = OUTPUT_DIR / html_path.with_suffix(".md").name
        out_path.write_text(md_content, encoding="utf-8")
        print(f"  {html_path.name} -> {out_path.name}")

    print(f"Done! Output in {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
