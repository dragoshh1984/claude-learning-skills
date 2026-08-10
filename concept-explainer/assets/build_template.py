"""Build the self-contained explainer template (assets/template.html).

Inlines KaTeX (JS + CSS with woff2 fonts as data URIs), the auto-render
extension, and highlight.js (core + python) into a single HTML file with the
base explainer layout. Sources come from the committed `vendor/` dir, so this
never needs the network — rerun it after ANY change to the layout/palette below,
then rebuild every page with build_page.py (pages embed the template).

Usage:
    python build_template.py                    # vendor/ -> template.html
    python build_template.py --katex-dist <dir> --out <file>   # overrides
"""

from __future__ import annotations

import argparse
import base64
import re
from pathlib import Path

LAYOUT = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{TITLE}}</title>
<style>
/* ── vendored: KaTeX ── */
__KATEX_CSS__
/* ── vendored: highlight.js github themes ── */
@media (prefers-color-scheme: light) { __HLJS_CSS_LIGHT__ }
@media (prefers-color-scheme: dark) { __HLJS_CSS_DARK__ }
/* ── explainer layout ── */
:root {
  --bg: #fcfbf8; --fg: #1f1e1b; --muted: #6e6a62; --accent: #0d6e60;
  --link: #0d6e60; --link-visited: #7a5490;
  --box: #f4f2ec; --border: #ddd8ce; --code-bg: #f7f5f0;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #14171a; --fg: #dad8d2; --muted: #8b8f8d; --accent: #57c8b5;
    --link: #6bd3bf; --link-visited: #c2a8dc;
    --box: #1b1f22; --border: #2b3136; --code-bg: #151a1e;
  }
}
* { box-sizing: border-box; }
body {
  margin: 0; background: var(--bg); color: var(--fg);
  font: 17px/1.65 Georgia, 'Times New Roman', serif;
}
#toc {
  position: fixed; top: 0; left: 0; bottom: 0; width: 260px; overflow-y: auto;
  padding: 2rem 1.2rem; border-right: 1px solid var(--border);
  font: 14px/1.5 system-ui, sans-serif;
}
#toc a { display: block; color: var(--muted); text-decoration: none; padding: .18rem 0; }
#toc a.active { color: var(--accent); font-weight: 600; }
main { margin-left: 260px; max-width: 860px; padding: 2rem 3rem 6rem; }
/* links: never fall back to the browser's default blue */
main a {
  color: var(--link); text-decoration: underline; text-underline-offset: 2px;
  text-decoration-thickness: 1px;
  text-decoration-color: color-mix(in srgb, var(--link) 35%, transparent);
  transition: text-decoration-color .12s ease;
}
main a:hover { text-decoration-color: var(--link); }
main a:visited { color: var(--link-visited); }
main a:focus-visible { outline: 2px solid var(--link); outline-offset: 2px; border-radius: 2px; }
@media (max-width: 1000px) { #toc { display: none; } main { margin-left: 0; } }
h1 { font-size: 2rem; line-height: 1.25; }
h2 { margin-top: 3.5rem; padding-top: 1rem; border-top: 1px solid var(--border); }
section { scroll-margin-top: 1rem; }
.eq-box {
  background: var(--box); border: 1px solid var(--border); border-left: 4px solid var(--accent);
  border-radius: 6px; padding: .8rem 1.2rem; margin: 1.2rem 0; overflow-x: auto;
}
.cite { font: 13px/1.4 system-ui, sans-serif; color: var(--muted); margin-top: .3rem; }
.cite a { color: var(--link); }
table.notation { border-collapse: collapse; font-size: .95em; }
table.notation td, table.notation th { border: 1px solid var(--border); padding: .3rem .7rem; }
pre {
  background: var(--code-bg); border: 1px solid var(--border); border-radius: 6px;
  padding: .9rem 1.1rem; overflow-x: auto; font-size: 13.5px; line-height: 1.5;
}
code { font-family: ui-monospace, 'Cascadia Code', Menlo, monospace; }
.code-path {
  font: 12px/1.2 ui-monospace, monospace; color: var(--muted);
  margin-bottom: -0.6rem; padding: .3rem .2rem;
}
.interactive {
  border: 1px solid var(--border); border-radius: 8px; background: var(--box);
  padding: 1rem 1.2rem; margin: 1.4rem 0; font: 14px/1.5 system-ui, sans-serif;
}
.interactive canvas { max-width: 100%; display: block; margin: .6rem auto; }
.interactive .controls { display: flex; flex-wrap: wrap; gap: 1rem; align-items: center; }
.interactive label { display: flex; gap: .5rem; align-items: center; }
.interactive .val { font-variant-numeric: tabular-nums; color: var(--accent); min-width: 3.5em; }
/* form controls: override the browser's default blue */
.interactive input[type="range"], .interactive input[type="checkbox"] { accent-color: var(--accent); }
.interactive input[type="range"] { height: 1.1rem; }
.interactive button {
  font: inherit; color: var(--fg); background: var(--bg); cursor: pointer;
  border: 1px solid var(--border); border-radius: 5px; padding: .25rem .7rem;
  transition: border-color .12s ease, color .12s ease;
}
.interactive button:hover { border-color: var(--accent); color: var(--accent); }
.interactive button:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
/* ── collapsible deep-dives ── */
details.fold {
  border: 1px solid var(--border); border-radius: 6px; background: var(--box);
  padding: .45rem 1rem; margin: 1.4rem 0;
}
details.fold > summary {
  cursor: pointer; list-style: none; padding: .3rem 0;
  font: 600 14px/1.5 system-ui, sans-serif; color: var(--accent);
}
details.fold > summary::-webkit-details-marker { display: none; }
details.fold > summary::before { content: "▸ "; }
details.fold[open] > summary::before { content: "▾ "; }
details.fold[open] > summary {
  margin-bottom: .8rem; padding-bottom: .5rem; border-bottom: 1px solid var(--border);
}
details.fold pre { background: var(--bg); }
/* ── diagrams: everything is currentColor except skip/residual paths ── */
figure.diagram { margin: 1.8rem 0; }
figure.diagram svg { max-width: 100%; height: auto; display: block; margin: 0 auto; color: var(--fg); }
.dg-node { fill: var(--box); stroke: currentColor; stroke-width: 1.2; }
.dg-node-2 { fill: var(--code-bg); stroke: currentColor; stroke-width: 1.2; }
.dg-ghost { fill: none; stroke: var(--muted); stroke-width: 1.1; stroke-dasharray: 4 3; }
.dg-flow { fill: none; stroke: currentColor; stroke-width: 1.5; }
.dg-skip { fill: none; stroke: var(--accent); stroke-width: 2.2; }
.dg-cut { fill: none; stroke: var(--muted); stroke-width: 1.6; stroke-dasharray: 5 4; }
.dg-op { fill: var(--bg); stroke: var(--accent); stroke-width: 1.8; }
.dg-t { font: 12px system-ui, sans-serif; fill: currentColor; }
.dg-b { font: 600 12px system-ui, sans-serif; fill: currentColor; }
.dg-s { font: 10.5px system-ui, sans-serif; fill: var(--muted); }
.dg-k { font: 600 11px system-ui, sans-serif; fill: var(--accent); }
.dg-ka { fill: var(--accent); }
.dg-gm { fill: var(--muted); }
figure { margin: 1.4rem 0; text-align: center; }
figure img { max-width: 100%; border: 1px solid var(--border); border-radius: 6px; }
figcaption { font: 13px/1.5 system-ui, sans-serif; color: var(--muted); margin-top: .4rem; }
.keyhint { position: fixed; bottom: .8rem; right: 1rem; font: 12px system-ui, sans-serif; color: var(--muted); }
</style>
</head>
<body>
<nav id="toc"><strong style="display:block;margin-bottom:.8rem">{{TITLE}}</strong></nav>
<main>
{{CONTENT}}
</main>
<div class="keyhint">j / k — next / prev section</div>
<script>__KATEX_JS__</script>
<script>__AUTORENDER_JS__</script>
<script>__HLJS_JS__</script>
<script>__HLJS_PY_JS__</script>
<script>
renderMathInElement(document.querySelector('main'), {
  delimiters: [
    {left: '$$', right: '$$', display: true},
    {left: '\\\\[', right: '\\\\]', display: true},
    {left: '$', right: '$', display: false},
    {left: '\\\\(', right: '\\\\)', display: false},
  ],
  throwOnError: true,
});
hljs.highlightAll();
// TOC auto-built from <section id> + its <h2>
const toc = document.getElementById('toc');
const sections = [...document.querySelectorAll('main section[id]')];
for (const s of sections) {
  const h = s.querySelector('h2'); if (!h) continue;
  const a = document.createElement('a');
  a.href = '#' + s.id; a.textContent = h.textContent; a.dataset.sec = s.id;
  toc.appendChild(a);
}
const links = [...toc.querySelectorAll('a[data-sec]')];
const obs = new IntersectionObserver((es) => {
  for (const e of es) if (e.isIntersecting) {
    links.forEach(l => l.classList.toggle('active', l.dataset.sec === e.target.id));
  }
}, { rootMargin: '0px 0px -70% 0px' });
sections.forEach(s => obs.observe(s));
// j/k section navigation
document.addEventListener('keydown', (ev) => {
  if (ev.target.tagName === 'INPUT' || !'jk'.includes(ev.key)) return;
  const y = window.scrollY + 10;
  const idx = sections.findLastIndex(s => s.offsetTop <= y);
  const next = ev.key === 'j' ? Math.min(idx + 1, sections.length - 1) : Math.max(idx - 1, 0);
  sections[next].scrollIntoView({ behavior: 'smooth' });
});
</script>
</body>
</html>
"""


def inline_katex_css(katex_dist: Path) -> str:
    """KaTeX CSS with woff2 fonts as data URIs; woff/ttf fallbacks dropped."""
    css = (katex_dist / "katex.min.css").read_text()

    def repl(m: re.Match[str]) -> str:
        srcs = m.group(1)
        w = re.search(r"url\((fonts/[^)]+\.woff2)\) format\(['\"]?woff2['\"]?\)", srcs)
        if not w:
            raise ValueError(f"no woff2 in @font-face src: {srcs!r}")
        data = base64.b64encode((katex_dist / w.group(1)).read_bytes()).decode()
        return f"src:url(data:font/woff2;base64,{data}) format('woff2')"

    out = re.sub(r"src:(url\(fonts/[^;}]+)", repl, css)
    if "url(fonts/" in out:
        raise ValueError("unreplaced font url remains")
    return out


def build(katex_dist: Path, hljs_js: Path, hljs_python: Path, out: Path) -> None:
    parts = {
        "__KATEX_CSS__": inline_katex_css(katex_dist),
        "__KATEX_JS__": (katex_dist / "katex.min.js").read_text(),
        "__AUTORENDER_JS__": (katex_dist / "contrib/auto-render.min.js").read_text(),
        "__HLJS_JS__": hljs_js.read_text(),
        "__HLJS_PY_JS__": hljs_python.read_text(),
        "__HLJS_CSS_LIGHT__": (hljs_js.parent / "github.min.css").read_text(),
        "__HLJS_CSS_DARK__": (hljs_js.parent / "github-dark.min.css").read_text(),
    }
    html = LAYOUT
    for key, val in parts.items():
        html = html.replace(key, val, 1)
    out.write_text(html)
    print(f"wrote {out} ({out.stat().st_size / 1e6:.2f} MB)")


if __name__ == "__main__":
    vendor = Path(__file__).parent / "vendor"
    p = argparse.ArgumentParser()
    p.add_argument("--katex-dist", type=Path, default=vendor / "katex")
    p.add_argument("--hljs-js", type=Path, default=vendor / "highlight.min.js")
    p.add_argument("--hljs-python", type=Path, default=vendor / "hl-python.min.js")
    p.add_argument("--out", type=Path, default=Path(__file__).parent / "template.html")
    a = p.parse_args()
    build(a.katex_dist, a.hljs_js, a.hljs_python, a.out)
