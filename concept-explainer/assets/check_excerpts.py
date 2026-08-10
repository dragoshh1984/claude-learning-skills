"""Verify every code excerpt on a page against the file it claims to quote.

A page states `<div class="code-path">some/file.py:120-131</div>` above a
`<pre><code>` block. Both halves can rot: editing the .py shifts line numbers,
and editing the page can drift the quoted text. This checks both.

For each excerpt it verifies:
  1. the referenced file exists;
  2. the excerpt's first real line sits exactly at the stated start line;
  3. every quoted line (ignoring `...` elisions) appears in the file, in order,
     within the stated range.

Usage:
    python check_excerpts.py <fragment.html> [more.html ...]
    python check_excerpts.py --all          # every campaign fragment
Exit code 1 if any excerpt is stale.
"""

from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
PAIR = re.compile(
    r'<div class="code-path">(?P<ref>[^<]+)</div>\s*'
    r'<pre><code[^>]*>(?P<code>.*?)</code></pre>',
    re.S,
)
REF = re.compile(r'(?P<path>[\w./-]+\.py):(?P<start>\d+)(?:-(?P<end>\d+))?')


def resolve(path: str, fragment: Path) -> Path | None:
    """Page refs are either repo-relative or campaign-relative (official/...)."""
    for base in (REPO, fragment.parents[2], fragment.parents[3]):
        p = base / path
        if p.exists():
            return p
    return None


def check_fragment(fragment: Path) -> list[str]:
    problems: list[str] = []
    text = fragment.read_text()
    for m in PAIR.finditer(text):
        ref_text = m.group("ref")
        ref = REF.search(ref_text)
        if not ref:
            problems.append(f"{fragment.name}: unparsable code-path {ref_text!r}")
            continue
        target = resolve(ref.group("path"), fragment)
        if target is None:
            problems.append(f"{fragment.name}: missing file for {ref_text!r}")
            continue

        start = int(ref.group("start"))
        end = int(ref.group("end") or start)
        file_lines = target.read_text().splitlines()
        quoted = [html.unescape(l) for l in m.group("code").split("\n")]
        quoted = [l for l in quoted if l.strip() and l.strip() != "..."]
        if not quoted:
            continue

        if start - 1 >= len(file_lines):
            problems.append(f"{fragment.name}: {ref.group('path')}:{start} beyond EOF")
            continue
        # excerpts are often de-indented for readability: compare content, not indent
        if file_lines[start - 1].strip() != quoted[0].strip():
            problems.append(
                f"{fragment.name}: {ref.group('path')}:{start} starts with\n"
                f"      file: {file_lines[start - 1].strip()!r}\n"
                f"      page: {quoted[0].strip()!r}")
            continue

        window = [l.strip() for l in file_lines[start - 1:end]]
        cursor = 0
        for line in quoted:
            want = line.strip()
            while cursor < len(window) and window[cursor] != want:
                cursor += 1
            if cursor == len(window):
                problems.append(
                    f"{fragment.name}: {ref.group('path')}:{start}-{end} missing line\n"
                    f"      page: {want.strip()!r}")
                break
            cursor += 1
    return problems


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("fragments", nargs="*", type=Path)
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()

    frags = args.fragments
    if args.all:
        frags = sorted((REPO / "src/learning").glob("*/concepts/*/fragment.html"))
    problems: list[str] = []
    for f in frags:
        found = check_fragment(f)
        n_ex = len(PAIR.findall(f.read_text()))
        print(f"{f.parent.name:26s} {n_ex:2d} excerpts  "
              f"{'OK' if not found else str(len(found)) + ' STALE'}")
        problems += found
    for p in problems:
        print("  ✗", p)
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
