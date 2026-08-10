"""Assemble a self-contained explainer page from the template + a content fragment.

Replaces {{TITLE}} and {{CONTENT}} in template.html and inlines every local
<img src="..."> (resolved relative to --images-root) as a base64 data URI, so
the final index.html is a single portable file.

Usage:
    python build_page.py --content fragment.html --title "Flow matching" \
        --out .../index.html [--images-root .../concept_dir]
"""

from __future__ import annotations

import argparse
import base64
import re
from pathlib import Path

TEMPLATE = Path(__file__).parent / "template.html"


def inline_images(html: str, root: Path) -> str:
    def repl(m: re.Match[str]) -> str:
        src = m.group(1)
        if src.startswith(("data:", "http")):
            return m.group(0)
        path = root / src
        if not path.exists():
            raise FileNotFoundError(f"image referenced but missing: {path}")
        data = base64.b64encode(path.read_bytes()).decode()
        ext = path.suffix.lstrip(".").lower()
        return m.group(0).replace(src, f"data:image/{ext};base64,{data}")

    return re.sub(r'<img[^>]*?src="([^"]+)"', repl, html)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--content", type=Path, required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--images-root", type=Path, default=None)
    a = p.parse_args()

    html = TEMPLATE.read_text().replace("{{TITLE}}", a.title)
    content = a.content.read_text()
    if a.images_root:
        content = inline_images(content, a.images_root)
    html = html.replace("{{CONTENT}}", content)
    a.out.write_text(html)
    print(f"wrote {a.out} ({a.out.stat().st_size / 1e6:.2f} MB)")


if __name__ == "__main__":
    main()
