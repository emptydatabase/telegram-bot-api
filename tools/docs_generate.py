#!/usr/bin/env python3
"""Fetch Telegram Bot API docs, update if changed, split and convert to Markdown."""

from pathlib import Path
from urllib.request import urlopen

DOCS_DIR = Path(__file__).parent.parent / "docs"
INPUT_FILE = DOCS_DIR / "main.html"
URL = "https://core.telegram.org/bots/api"

DOCS_DIR.mkdir(exist_ok=True)


def main():
    print(f"Fetching {URL}...")
    with urlopen(URL) as resp:
        remote_html = resp.read()

    if INPUT_FILE.exists():
        local_html = INPUT_FILE.read_bytes()

        remote = remote_html.splitlines()
        local = local_html.splitlines()

        if remote[:-1] == local[:-1]:
            print("Already up to date.")
            return

    print("New version found, updating...")
    INPUT_FILE.write_bytes(remote_html)

    from docs_split import main as split_main
    from docs_markdown import main as markdown_main

    split_main()
    markdown_main()


if __name__ == "__main__":
    main()
