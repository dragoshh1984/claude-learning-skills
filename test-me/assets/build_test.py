"""Build a test-me recap page from its spec, and the recap overview.

A test lives in `<recap>/<test-id>/`:
    test.json     the spec, Claude-facing: questions + answer key + grading (never inlined into the page)
    fragment.html generated page source
    index.html    the page the user answers (built with concept-explainer's build_page.py)
    answers.md    written BY THE PAGE on every Submit (File System Access API); read by the grader

Usage:
    python build_test.py build <recap>/<test-id>      # page for one test + refresh the overview
    python build_test.py overview <recap>              # overview only
    python build_test.py check <recap>/<test-id>       # validate the spec, print the answer-mode mix

test.json schema (keys marked * are required):
    id*, title*, created* (YYYY-MM-DD), scope* (list of str), focus* (only|related|mixed|none),
    answers* (mix|choice|text), mix (fraction of choice questions, default 0.7),
    questions*: list of
        id* ("q1"…), kind* ("choice" | "text"), prompt* (HTML + $math$ allowed),
        topic* (learning-tree path, e.g. "fundamentals/layer_primitives/concepts/gating"),
        subtopic*, choices (choice only, list of HTML), multi (bool, choice only),
        key (choice: list of correct indices; text: omitted), key_points (text: list of str),
        explain* (the model answer, used when grading), ref* (page link + #anchor for review),
        from (the logged/session question this targets, or null)
    grading (written by the grader): {date, score, items: [{q, verdict, note}]}
"""

from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILD_PAGE = HERE.parent.parent / "concept-explainer" / "assets" / "build_page.py"
LETTERS = "ABCDEFGHIJ"
PUBLIC_KEYS = ("id", "kind", "prompt", "choices", "multi", "topic", "subtopic")

UI = r"""
<style>
.rq-meta { font: 13px/1.6 system-ui, sans-serif; color: var(--muted); }
.rq-save { position: sticky; top: 0; z-index: 5; display: flex; flex-wrap: wrap; gap: .6rem; align-items: center;
  padding: .55rem .8rem; margin: 1rem 0 1.6rem; background: var(--box); border: 1px solid var(--border); border-radius: 6px;
  font: 13px/1.5 system-ui, sans-serif; }
.rq-save .ok { color: var(--accent); font-weight: 600; }
.rq-save .warn { color: #d9822b; font-weight: 600; }
section.rq { border: 1px solid var(--border); border-radius: 8px; padding: .2rem 1.1rem 1rem; margin: 1.4rem 0; }
section.rq > h2 { margin: .6rem 0 0; padding-top: 0; border-top: 0; }
section.rq.done { border-color: var(--accent); }
section.rq.stale { border-color: #d9822b; }
.rq-tag { font: 12px system-ui, sans-serif; color: var(--muted); margin: 0 0 .5rem; }
.rq-choices { display: grid; gap: .35rem; margin: .7rem 0; }
.rq-choices label { display: flex; gap: .55rem; align-items: baseline; padding: .35rem .55rem; border: 1px solid var(--border);
  border-radius: 5px; cursor: pointer; }
.rq-choices label:hover { border-color: var(--accent); }
.rq-choices input { accent-color: var(--accent); }
.rq-text { width: 100%; box-sizing: border-box; min-height: 5.5em; font: 14px/1.5 system-ui, sans-serif; background: var(--bg);
  color: var(--fg); border: 1px solid var(--border); border-radius: 5px; padding: .45rem .6rem; resize: vertical; }
.rq-text.small { min-height: 3em; }
.rq-hint { font: 12px system-ui, sans-serif; color: var(--muted); margin: .5rem 0 .25rem; }
.rq-bar { display: flex; gap: .8rem; align-items: center; margin-top: .6rem; font: 13px system-ui, sans-serif; }
.rq-bar button, .rq-save button { font: 600 13px system-ui, sans-serif; padding: .35rem .9rem; border-radius: 5px; cursor: pointer;
  background: var(--accent); color: var(--bg); border: 0; }
.rq-save button.ghost { background: none; color: var(--accent); border: 1px solid var(--accent); }
.rq-status { color: var(--muted); }
</style>
<script>
(function () {
  const T = window.RECAP, KEY = 'recap:' + T.id;
  const $ = (s, el) => (el || document).querySelector(s), $$ = (s, el) => [...(el || document).querySelectorAll(s)];
  let state = { drafts: {}, subs: {} };
  try { state = Object.assign(state, JSON.parse(localStorage.getItem(KEY) || '{}')); } catch (e) { /* no storage: still works, just not persisted */ }
  const persist = () => { try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) { } };
  const plain = (h) => { const d = document.createElement('div'); d.innerHTML = h; return d.textContent.replace(/\s+/g, ' ').trim(); };

  function read(q) {
    const sec = document.getElementById(q.id);
    return { choice: $$('input[name="' + q.id + '"]', sec).filter(i => i.checked).map(i => +i.value), text: $('textarea', sec).value };
  }
  function write(q, v) {
    const sec = document.getElementById(q.id);
    $$('input[name="' + q.id + '"]', sec).forEach(i => { i.checked = (v.choice || []).includes(+i.value); });
    $('textarea', sec).value = v.text || '';
  }
  const same = (a, b) => a && b && JSON.stringify(a.choice) === JSON.stringify(b.choice) && a.text === b.text;
  function paint(q) {
    const sec = document.getElementById(q.id), s = state.subs[q.id], cur = read(q);
    const stale = s && !same(s, cur);
    sec.classList.toggle('done', !!s && !stale); sec.classList.toggle('stale', !!stale);
    $('.rq-status', sec).textContent = !s ? 'not submitted' : stale ? 'changed since your submit at ' + s.at.slice(11, 16) + ' — submit again to save it' : 'submitted ' + s.at.slice(0, 16).replace('T', ' ');
  }
  function serialize() {
    const n = T.questions.length, k = T.questions.filter(q => state.subs[q.id]).length, now = new Date().toISOString();
    const L = ['# Answers — ' + T.title, '', 'test: ' + T.id + ' · saved: ' + now + ' · submitted: ' + k + ' / ' + n, ''];
    for (const q of T.questions) {
      const s = state.subs[q.id], d = state.drafts[q.id];
      L.push('## ' + q.id + ' · ' + q.kind + (q.multi ? ' (multi)' : '') + ' · ' + q.topic + ' › ' + q.subtopic);
      L.push('**Q:** ' + plain(q.prompt));
      if (q.kind === 'choice') L.push('**Choices:** ' + q.choices.map((c, i) => LET[i] + ') ' + plain(c)).join(' | '));
      if (s) {
        if (q.kind === 'choice') L.push('**Selected:** ' + (s.choice.length ? s.choice.map(i => LET[i]).join(', ') : '(none)'));
        L.push('**Written:** ' + (s.text.trim() ? s.text.trim().replace(/\n/g, '\n> ') : '(nothing)'));
        L.push('**Status:** submitted ' + s.at);
      } else {
        L.push('**Status:** not submitted' + (d && (d.text.trim() || d.choice.length) ? ' (unsubmitted draft: ' + (d.choice.length ? d.choice.map(i => LET[i]).join(', ') + '; ' : '') + JSON.stringify(d.text.trim()) + ')' : ''));
      }
      L.push('');
    }
    L.push('```json', JSON.stringify({ id: T.id, saved: now, submitted: state.subs, drafts: state.drafts }, null, 1), '```', '');
    return L.join('\n');
  }
  const LET = 'ABCDEFGHIJ';

  // ── the answers file: File System Access API (Chrome/Edge), handle kept in IndexedDB ──
  let handle = null;
  // IndexedDB can be unavailable or never settle on file:// pages; never let it block a save.
  const idb = (mode, fn) => Promise.race([idbRaw(mode, fn), new Promise((_, rej) => setTimeout(() => rej(new Error('indexedDB timeout')), 1500))]);
  const idbRaw = (mode, fn) => new Promise((res, rej) => {
    const r = indexedDB.open('recap-files', 1);
    r.onupgradeneeded = () => r.result.createObjectStore('h');
    r.onsuccess = () => { try { const tx = r.result.transaction('h', mode); const st = tx.objectStore('h'); const q = fn(st); tx.oncomplete = () => res(q && q.result); tx.onerror = () => rej(tx.error); } catch (e) { rej(e); } };
    r.onerror = () => rej(r.error);
  });
  const bar = $('#rq-save-msg');
  const say = (cls, msg) => { bar.className = cls; bar.textContent = msg; };
  async function connect(force) {
    if (!window.showSaveFilePicker) return null;
    if (!handle && !force) { try { handle = await idb('readonly', st => st.get(T.id)); } catch (e) { handle = null; } }
    if (!handle || force) {
      handle = await window.showSaveFilePicker({ suggestedName: 'answers.md', types: [{ description: 'Markdown', accept: { 'text/markdown': ['.md'] } }] });
      try { await idb('readwrite', st => st.put(handle, T.id)); } catch (e) { /* re-asked next session */ }
    }
    if ((await handle.queryPermission({ mode: 'readwrite' })) !== 'granted' && (await handle.requestPermission({ mode: 'readwrite' })) !== 'granted') throw new Error('write permission refused');
    return handle;
  }
  // Saves run one at a time and serialize at write time, so a slow first save can never
  // land after a later one and overwrite newer answers with an older snapshot.
  let chain = Promise.resolve();
  const save = (force) => (chain = chain.then(() => saveNow(force), () => saveNow(force)));
  async function saveNow(force) {
    try {
      const h = await connect(force);
      if (h) {
        const w = await h.createWritable(); await w.write(serialize()); await w.close();
        say('ok', 'Saved to ' + h.name + ' (the whole test, overwritten). Expected location: ' + T.answers_path);
        return true;
      }
    } catch (e) {
      if (e && e.name === 'AbortError') { say('warn', 'No file chosen: nothing saved. Submit again and save it as ' + T.answers_path); return false; }
      say('warn', 'Could not write the file (' + (e && e.message || e) + '). Downloading it instead.');
    }
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([serialize()], { type: 'text/markdown' })); a.download = 'answers-' + T.id + '.md'; a.click();
    say('warn', 'This browser cannot write files directly: downloaded answers-' + T.id + '.md. Move it to ' + T.answers_path + ' (or tell the agent it is in Downloads).');
    return true;
  }
  window.__recap = { serialize, save, state };

  for (const q of T.questions) {
    const sec = document.getElementById(q.id);
    if (state.drafts[q.id]) write(q, state.drafts[q.id]);
    sec.addEventListener('input', () => { state.drafts[q.id] = read(q); persist(); paint(q); });
    $('.rq-submit', sec).addEventListener('click', async () => {
      const v = read(q);
      if (q.kind === 'choice' && !v.choice.length && !v.text.trim()) { $('.rq-status', sec).textContent = 'pick an answer (or write one) first'; return; }
      if (q.kind === 'text' && !v.text.trim()) { $('.rq-status', sec).textContent = 'write an answer first'; return; }
      state.subs[q.id] = Object.assign(v, { at: new Date().toISOString() }); state.drafts[q.id] = read(q); persist(); paint(q);
      await save(false);
    });
    paint(q);
  }
  $('#rq-connect').addEventListener('click', () => save(true));
  if (!window.showSaveFilePicker) say('warn', 'This browser has no direct file access: each Submit downloads the answers file. Chrome or Edge writes it in place.');
  else say('', 'First Submit asks where to save: choose ' + T.answers_path + '. After that every Submit overwrites it.');
})();
</script>
"""


def load(test_dir: Path) -> dict:
    spec = json.loads((test_dir / "test.json").read_text())
    check(spec, test_dir)
    return spec


def check(spec: dict, test_dir: Path) -> None:
    for k in ("id", "title", "created", "scope", "focus", "answers", "questions"):
        if k not in spec:
            raise ValueError(f"test.json missing '{k}'")
    if spec["id"] != test_dir.name:
        raise ValueError(f"id {spec['id']!r} must equal the folder name {test_dir.name!r}")
    if spec["focus"] not in ("only", "related", "mixed", "none"):
        raise ValueError(f"focus must be only|related|mixed|none, got {spec['focus']!r}")
    if spec["answers"] not in ("mix", "choice", "text"):
        raise ValueError(f"answers must be mix|choice|text, got {spec['answers']!r}")
    ids = set()
    for q in spec["questions"]:
        for k in ("id", "kind", "prompt", "topic", "subtopic", "explain", "ref"):
            if k not in q:
                raise ValueError(f"question {q.get('id', '?')} missing '{k}'")
        if q["id"] in ids or not re.fullmatch(r"q\d+", q["id"]):
            raise ValueError(f"question ids must be unique q1, q2, …: {q['id']!r}")
        ids.add(q["id"])
        if q["kind"] == "choice":
            if len(q.get("choices", [])) < 2 or not q.get("key"):
                raise ValueError(f"{q['id']}: a choice question needs ≥2 choices and a key")
            if any(not (0 <= i < len(q["choices"])) for i in q["key"]):
                raise ValueError(f"{q['id']}: key index out of range")
            if not q.get("multi") and len(q["key"]) != 1:
                raise ValueError(f"{q['id']}: single-answer question with {len(q['key'])} keys; set multi: true")
        elif q["kind"] == "text":
            if not q.get("key_points"):
                raise ValueError(f"{q['id']}: a text question needs key_points")
        else:
            raise ValueError(f"{q['id']}: kind must be choice|text")
    if spec["answers"] == "choice" and any(q["kind"] != "choice" for q in spec["questions"]):
        raise ValueError("answers=choice but the test has text questions")
    if spec["answers"] == "text" and any(q["kind"] != "text" for q in spec["questions"]):
        raise ValueError("answers=text but the test has choice questions")


def answers_path(test_dir: Path) -> str:
    """Where the user should save answers.md, shown relative to the project when possible."""
    full = str(test_dir / "answers.md")
    return "src/learning/" + full.split("src/learning/", 1)[1] if "src/learning/" in full else full


def fragment(spec: dict, test_dir: Path) -> str:
    public = {
        "id": spec["id"], "title": spec["title"],
        "answers_path": answers_path(test_dir),
        "questions": [{k: q[k] for k in PUBLIC_KEYS if k in q} for q in spec["questions"]],
    }
    n = len(spec["questions"]); nc = sum(q["kind"] == "choice" for q in spec["questions"])
    out = [f"<h1>{html.escape(spec['title'])}</h1>",
           f'<p class="rq-meta">Recap test · {spec["created"]} · {n} questions ({nc} with choices, {n - nc} written) · '
           f'scope: {html.escape(", ".join(spec["scope"]))} · focus: {spec["focus"]} · <a href="../index.html">all tests</a></p>',
           '<p>Answer each question, then press its <strong>Submit</strong>. Every Submit saves the whole test to '
           '<code>answers.md</code> in this folder. Then come back to the conversation and say '
           f'<em>"grade test {spec["id"]}"</em>. Where there are choices, you can also write your reasoning: '
           'it is graded too. Drafts are kept in this browser if you leave and come back.</p>',
           '<div class="rq-save"><span id="rq-save-msg"></span><button id="rq-connect" class="ghost">choose answers file…</button></div>']
    for i, q in enumerate(spec["questions"], 1):
        multi = q.get("multi", False)
        tag = ("choose all that apply" if multi else "choose one") if q["kind"] == "choice" else "written answer"
        out.append(f'<section id="{q["id"]}" class="rq" data-kind="{q["kind"]}">')
        out.append(f'<h2>Q{i}</h2><p class="rq-tag">{tag}</p>')
        out.append(f'<div class="rq-prompt">{q["prompt"]}</div>')
        if q["kind"] == "choice":
            typ = "checkbox" if multi else "radio"
            out.append('<div class="rq-choices">' + "".join(
                f'<label><input type="{typ}" name="{q["id"]}" value="{j}"><span><strong>{LETTERS[j]})</strong> {c}</span></label>'
                for j, c in enumerate(q["choices"])) + "</div>")
            out.append('<p class="rq-hint">Why? (optional, but it is graded: a right pick for the wrong reason is only partly right)</p>'
                       '<textarea class="rq-text small" spellcheck="true"></textarea>')
        else:
            out.append('<textarea class="rq-text" spellcheck="true" placeholder="Your answer, in your own words"></textarea>')
        out.append('<div class="rq-bar"><button class="rq-submit">Submit</button><span class="rq-status"></span></div>')
        out.append("</section>")
    out.append(f"<script>window.RECAP = {json.dumps(public, ensure_ascii=False)};</script>")
    out.append(UI)
    return "\n".join(out)


def status(test_dir: Path, spec: dict) -> str:
    g = spec.get("grading")
    if g:
        return f"graded {g.get('date', '')}: {g.get('score', '?')}"
    a = test_dir / "answers.md"
    if a.exists():
        m = re.search(r"submitted: (\d+) / (\d+)", a.read_text())
        return f"answered {m.group(1)}/{m.group(2)}, not graded" if m else "answers file present"
    return "new"


def build_page(frag: Path, title: str, out: Path) -> None:
    subprocess.run([sys.executable, str(BUILD_PAGE), "--content", str(frag), "--title", title, "--out", str(out)], check=True)


def overview(recap: Path) -> None:
    rows = []
    for tj in sorted(recap.glob("*/test.json"), reverse=True):
        spec = json.loads(tj.read_text())
        d = tj.parent
        rows.append(f'<tr><td>{spec["created"]}</td><td><a href="{d.name}/index.html">{html.escape(spec["title"])}</a></td>'
                    f'<td>{html.escape(", ".join(spec["scope"]))}</td><td>{len(spec["questions"])}</td>'
                    f'<td>{spec["focus"]}</td><td>{html.escape(status(d, spec))}</td></tr>')
    body = ("<table class=\"notation\"><tr><th>date</th><th>test</th><th>scope</th><th>questions</th><th>focus</th><th>status</th></tr>"
            + "".join(rows) + "</table>") if rows else "<p>No tests yet.</p>"
    frag = recap / "fragment.html"
    frag.write_text(
        "<h1>Recap tests</h1>\n<p>Tests generated by <code>test-me</code> from the learning pages and from the questions you asked. "
        "Each one is a page you answer and submit; your answers are saved to <code>answers.md</code> next to it, and the agent grades "
        "them in the conversation. Newest first.</p>\n<section id=\"tests\">\n<h2>All tests</h2>\n" + body + "\n</section>\n")
    build_page(frag, "Recap tests", recap / "index.html")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("cmd", choices=["build", "overview", "check"])
    p.add_argument("path", type=Path)
    a = p.parse_args()
    if a.cmd == "overview":
        overview(a.path.resolve())
        return
    test_dir = a.path.resolve()
    spec = load(test_dir)
    qs = spec["questions"]; nc = sum(q["kind"] == "choice" for q in qs)
    print(f"{spec['id']}: {len(qs)} questions, {nc} choice ({nc / len(qs):.0%}), {len(qs) - nc} text; target mix {spec.get('mix', 0.7):.0%} choice")
    if a.cmd == "check":
        return
    frag = test_dir / "fragment.html"
    frag.write_text(fragment(spec, test_dir))
    build_page(frag, spec["title"], test_dir / "index.html")
    overview(test_dir.parent)


if __name__ == "__main__":
    main()
