#!/usr/bin/env python3
"""Split main.html into per-section HTML files."""

import os
import re
from collections import OrderedDict
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString, Tag

TELEGRAM_BASE = "https://core.telegram.org"
DOCS_DIR = Path(__file__).parent.parent / "docs"
INPUT_FILE = DOCS_DIR / "main.html"
OUTPUT_DIR = DOCS_DIR / "html"

DOCS_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

H3_ANCHOR_RE = re.compile(
    r'<h3><a class="anchor" name="([^"]+)"[^>]*>.*?</a>(.*?)</h3>'
)


def extract_head(original_html: str) -> str:
    """Extract the <head>...</head> block and rewrite local paths."""
    match = re.search(r"<head>(.*?)</head>", original_html, re.DOTALL)
    if not match:
        return ""
    head = match.group(1)
    head = rewrite_local_paths(head)
    return f"<head>{head}</head>"


def rewrite_local_paths(html: str) -> str:
    """Rewrite /css/, /js/, /img/ paths to https://core.telegram.org/..."""
    html = re.sub(r'(href|src)=(["\'])/(css/)', r'\1=\2' + TELEGRAM_BASE + r"/\3", html)
    html = re.sub(r'(href|src)=(["\'])/(js/)', r'\1=\2' + TELEGRAM_BASE + r"/\3", html)
    html = re.sub(r'(href|src)=(["\'])/(img/)', r'\1=\2' + TELEGRAM_BASE + r"/\3", html)
    html = re.sub(r'(href)=(["\'])/((?!/)[^"\']*)\2', lambda m: f'{m.group(1)}={m.group(2)}{TELEGRAM_BASE}/{m.group(3)}{m.group(2)}', html)
    return html


def rewrite_internal_links(html: str, anchor_to_section: dict, section_slug: str) -> str:
    """Rewrite href="#anchor" to href="section.html#anchor" and /path links to absolute."""

    def replace_href(m):
        full = m.group(0)
        prefix = m.group(1)
        quote = m.group(2)
        value = m.group(3)

        # Absolute or protocol-relative — leave alone
        if value.startswith(("http://", "https://", "//")):
            return full

        # Site-relative path like /bots/faq → absolute
        if value.startswith("/"):
            return f"{prefix}={quote}{TELEGRAM_BASE}{value}{quote}"

        # Internal anchor
        if value.startswith("#"):
            anchor = value[1:]
            target_section = anchor_to_section.get(anchor)
            if target_section:
                return f'{prefix}={quote}{target_section}.html#{anchor}{quote}'
            # Unknown anchor, keep as-is
            return f'{prefix}={quote}#{anchor}{quote}'

        return full

    return re.sub(
        r'((?:href|src))=(["\'])(#[^"\']*|/[^"\']*)\2',
        replace_href,
        html,
    )


def get_section_slug(anchor: str) -> str:
    """Convert an anchor name to a filename slug."""
    return anchor


def build_section_content(soup: BeautifulSoup, content_div: Tag) -> list:
    """Split the content div into ordered (h3_anchor, h3_text, [elements]) tuples."""
    sections = []
    current_h3_anchor = None
    current_h3_text = None
    current_elements = []

    for child in content_div.children:
        if isinstance(child, NavigableString):
            if current_h3_anchor is not None:
                current_elements.append(str(child))
            continue

        if not isinstance(child, Tag):
            continue

        # Check if this is an h3 — start a new section
        if child.name == "h3":
            anchor_tag = child.find("a", class_="anchor")
            if anchor_tag and anchor_tag.get("name"):
                # Save previous section
                if current_h3_anchor is not None:
                    sections.append((current_h3_anchor, current_h3_text, current_elements))
                current_h3_anchor = anchor_tag["name"]
                current_h3_text = child.get_text(strip=True)
                current_elements = [child]
                continue

        # Check if this h3 is nested in some wrapper (shouldn't happen but be safe)
        if current_h3_anchor is None:
            # Content before first h3 (intro blockquote, etc.) — skip or include
            continue

        current_elements.append(child)

    # Save last section
    if current_h3_anchor is not None:
        sections.append((current_h3_anchor, current_h3_text, current_elements))

    return sections


def build_page(
    head_block: str,
    title: str,
    content_elements: list,
    navbar_html: str,
    footer_html: str,
    scripts_html: str,
) -> str:
    """Assemble a complete HTML page."""
    content_html = "".join(str(el) for el in content_elements)
    return f"""<!DOCTYPE html>
<html class="" data-theme="light">
{head_block}
<body class="preload">
{navbar_html}
<div class="dev_page_wrap">
  <div class="container clearfix">
    <div class="dev_page">
      <div id="dev_page_content_wrap" class=" ">
        <div class="dev_page_bread_crumbs"><ul class="breadcrumb clearfix"><li><a href="{TELEGRAM_BASE}/bots">Telegram Bots</a></li><i class="icon icon-breadcrumb-divider"></i><li><a href="{TELEGRAM_BASE}/bots/api">Telegram Bot API</a></li></ul></div>
        <div id="dev_page_content">
{content_html}
        </div>
      </div>
    </div>
  </div>
{footer_html}
{scripts_html}
</div>
</body>
</html>"""


def main():
    print(f"Reading {INPUT_FILE}...")
    original_html = INPUT_FILE.read_text(encoding="utf-8")

    soup = BeautifulSoup(original_html, "html.parser")
    content_div = soup.find("div", id="dev_page_content")
    if not content_div:
        print("ERROR: Could not find <div id='dev_page_content'>")
        return

    head_block = extract_head(original_html)

    # Extract navbar
    navbar_match = re.search(
        r'(<div class="dev_page_head navbar.*?</div>\s*</div>\s*</div>)',
        original_html,
        re.DOTALL,
    )
    navbar_html = ""
    if navbar_match:
        navbar_html = rewrite_local_paths(navbar_match.group(1))

    # Extract footer
    footer_match = re.search(
        r'(<div class="footer_wrap">.*?</div>\s*</div>)',
        original_html,
        re.DOTALL,
    )
    footer_html = ""
    if footer_match:
        footer_html = rewrite_local_paths(footer_match.group(1))

    # Extract scripts block
    scripts_match = re.search(
        r'(<script src="/js/main\.js.*?</body>)',
        original_html,
        re.DOTALL,
    )
    scripts_html = ""
    if scripts_match:
        raw = scripts_match.group(1)
        scripts_html = rewrite_local_paths(raw)

    # Split into sections
    sections = build_section_content(soup, content_div)
    print(f"Found {len(sections)} sections:")
    for anchor, text, elements in sections:
        print(f"  - {anchor}: {text} ({len(elements)} elements)")

    # Build anchor→section mapping
    anchor_to_section = {}
    for anchor, text, elements in sections:
        anchor_to_section[anchor] = anchor

    # More robust: scan all h4 tags in the content div
    # Scan all heading levels (h4, h5, h6) to map anchors to their parent h3 section
    for heading in content_div.find_all(["h4", "h5", "h6"]):
        a = heading.find("a", class_="anchor")
        if a and a.get("name"):
            parent_anchor = None
            for prev in heading.find_all_previous("h3"):
                prev_a = prev.find("a", class_="anchor")
                if prev_a and prev_a.get("name"):
                    parent_anchor = prev_a["name"]
                    break
            if parent_anchor:
                anchor_to_section[a["name"]] = parent_anchor

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for anchor, text, elements in sections:
        slug = get_section_slug(anchor)
        filename = f"{slug}.html"
        filepath = OUTPUT_DIR / filename

        content_str = "".join(str(el) for el in elements)
        content_str = rewrite_internal_links(content_str, anchor_to_section, slug)
        # Re-wrap in elements for the page builder
        content_soup = BeautifulSoup(f"<div>{content_str}</div>", "html.parser")
        content_elements = list(content_soup.div.children)

        page = build_page(
            head_block,
            text,
            content_elements,
            navbar_html,
            footer_html,
            scripts_html,
        )
        filepath.write_text(page, encoding="utf-8")
        print(f"  Written: {filename}")

    print(f"\nDone! {len(sections)} section files in {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
