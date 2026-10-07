"""Build the shareable page of the thesis outline from its Markdown record copy.

The record copy is `docs/THESIS_OUTLINE.md`; the published page (https://claude.ai/artifact/Tcm3t8kJAug3H44bXza6JX)
and its copy `docs/THESIS_OUTLINE.html` are generated from it — edit the Markdown, rebuild, publish the HTML again.

    venv/bin/python evaluation/agent/docs/thesis_outline_page.py evaluation/agent/docs/THESIS_OUTLINE.md \
        evaluation/agent/docs/THESIS_OUTLINE.html
"""
import html
import re
import sys
from html.parser import HTMLParser

src, out = sys.argv[1], sys.argv[2]
lines = open(src, encoding="utf-8").read().split("\n")

CHIP = {"done": "ok", "partly": "part", "planned": "plan", "dropped": "drop", "open": "open"}


def inline(t: str) -> str:
    t = html.escape(t, quote=False)
    codes = []

    def keep(m):
        codes.append(m.group(1))
        return f"\x00{len(codes) - 1}\x00"
    t = re.sub(r"`([^`]+)`", keep, t)

    def chip(m):
        label = m.group(1)
        return f'<span class="chip chip-{CHIP.get(label.split()[0].rstrip(","), "plan")}">{label}</span>'
    t = re.sub(r"\*\*\[([^\]]+)\]\*\*", chip, t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", t)
    return re.sub(r"\x00(\d+)\x00", lambda m: f"<code>{codes[int(m.group(1))]}</code>", t)


def slug(title: str) -> str:
    m = re.match(r"^(\d+)\s", title)
    if m:
        return f"s{m.group(1)}"
    return "s-" + re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:40]


def render_list(items):
    o, stack = [], []
    for level, kind, text in items:
        while stack and stack[-1][0] > level:
            o.append(f"</li></{stack.pop()[1]}>")
        if stack and stack[-1][0] == level:
            o.append("</li>")
            if stack[-1][1] != kind:
                o.append(f"</{stack.pop()[1]}>")
                o.append(f"<{kind}>")
                stack.append((level, kind))
        else:
            o.append(f"<{kind}>")
            stack.append((level, kind))
        o.append(f"<li>{inline(text)}")
    while stack:
        o.append(f"</li></{stack.pop()[1]}>")
    return "".join(o)


def render_table(rows):
    cells = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
    head, body = cells[0], cells[2:]
    o = ['<div class="table-wrap"><table><thead><tr>']
    o += [f"<th>{inline(c)}</th>" for c in head]
    o.append("</tr></thead><tbody>")
    for r in body:
        o.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>")
    o.append("</tbody></table></div>")
    return "".join(o)


blocks, toc = [], []
intro, title = [], ""
i, n = 0, len(lines)
seen_h2 = False
while i < n:
    ln = lines[i]
    if not ln.strip():
        i += 1
        continue
    if ln.startswith("# "):
        title = ln[2:].strip()
        i += 1
        continue
    if ln.strip() == "---":
        i += 1
        continue
    if ln.startswith("## "):
        seen_h2 = True
        text = ln[3:].strip()
        m = re.match(r"^(.*?)\s*\(([^()]*)\)\s*$", text)
        name, meta = (m.group(1), m.group(2)) if m else (text, "")
        sid = slug(name)
        num = re.match(r"^(\d+)\s+(.*)$", name)
        label = (f'<span class="num">{num.group(1)}</span>{inline(num.group(2))}' if num else inline(name))
        blocks.append(f'<h2 id="{sid}">{label}' + (f'<span class="meta">{html.escape(meta)}</span>' if meta else "") + "</h2>")
        toc.append((sid, num.group(1) if num else "", num.group(2) if num else name))
        i += 1
        continue
    if ln.startswith("|"):
        rows = []
        while i < n and lines[i].startswith("|"):
            rows.append(lines[i])
            i += 1
        (blocks if seen_h2 else intro).append(render_table(rows))
        continue
    m = re.match(r"^(\s*)(-|\d+\.)\s+(.*)$", ln)
    if m:
        items = []
        while i < n:
            m = re.match(r"^(\s*)(-|\d+\.)\s+(.*)$", lines[i])
            if m:
                items.append([len(m.group(1)) // 2, "ul" if m.group(2) == "-" else "ol", m.group(3)])
                i += 1
            elif lines[i].strip() and lines[i].startswith(" ") and items:
                items[-1][2] += " " + lines[i].strip()
                i += 1
            else:
                break
        (blocks if seen_h2 else intro).append(render_list(items))
        continue
    para = []
    while i < n and lines[i].strip() and not lines[i].startswith(("#", "|", "- ")) and lines[i].strip() != "---" \
            and not re.match(r"^\d+\.\s", lines[i]):
        para.append(lines[i].strip())
        i += 1
    (blocks if seen_h2 else intro).append(f"<p>{inline(' '.join(para))}</p>")

m = re.match(r"^(.*?)\s*—\s*(.*)$", title)
h1, eyebrow = (m.group(1), m.group(2)) if m else (title, "")
eyebrow = re.sub(r"\s*\(([^()]*)\)\s*$", r" · \1", eyebrow)
eyebrow = eyebrow[:1].upper() + eyebrow[1:]
toc_html = "".join(f'<li><a href="#{sid}"><span class="num">{num}</span>{html.escape(name)}</a></li>' for sid, num, name in toc)

CSS = """
/* layout: one reading column of thesis prose with a contents rail beside it; tables may run wider than the prose */
:root {
  --paper: #fbfcfd; --panel: #f0f3f7; --ink: #16202b; --soft: #536171; --rule: #d3dbe5; --accent: #1d5a9e;
  --ok: #17734d; --ok-bg: #dff3ea; --part: #8a5a00; --part-bg: #fbedcf; --plan: #4f49ad; --plan-bg: #e7e6fa;
  --drop: #5d6672; --drop-bg: #e6e9ee; --open: #a53a1c; --open-bg: #fbe3da;
  --serif: "Source Serif 4", "Iowan Old Style", Georgia, serif;
  --sans: "IBM Plex Sans", "Segoe UI", system-ui, sans-serif;
  --mono: "IBM Plex Mono", ui-monospace, "SF Mono", Menlo, monospace;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --paper: #10151b; --panel: #19212b; --ink: #e5eaf0; --soft: #9aa8b7; --rule: #2b3745; --accent: #86b7f0;
    --ok: #6ad3a2; --ok-bg: #153a2b; --part: #e6b65c; --part-bg: #3d2f10; --plan: #aaa6f5; --plan-bg: #272553;
    --drop: #a3adb9; --drop-bg: #252e39; --open: #f29373; --open-bg: #452015; color-scheme: dark;
  }
}
:root[data-theme="dark"] {
  --paper: #10151b; --panel: #19212b; --ink: #e5eaf0; --soft: #9aa8b7; --rule: #2b3745; --accent: #86b7f0;
  --ok: #6ad3a2; --ok-bg: #153a2b; --part: #e6b65c; --part-bg: #3d2f10; --plan: #aaa6f5; --plan-bg: #272553;
  --drop: #a3adb9; --drop-bg: #252e39; --open: #f29373; --open-bg: #452015; color-scheme: dark;
}
*, *::before, *::after { box-sizing: border-box; }
body { background: var(--paper); color: var(--ink); font-family: var(--serif); font-size: 1.0625rem; line-height: 1.6; }
.page { max-width: 78rem; margin-inline: auto; padding-inline: clamp(1rem, 4vw, 2.5rem); padding-block: 2.5rem 5rem; }
.masthead { border-bottom: 2px solid var(--ink); padding-bottom: 1.5rem; margin-bottom: 2rem; }
.eyebrow { font-family: var(--sans); font-size: 0.78rem; letter-spacing: 0.09em; text-transform: uppercase; color: var(--soft); margin: 0 0 0.6rem; }
h1 { font-size: clamp(2rem, 5vw, 3rem); line-height: 1.08; font-weight: 600; letter-spacing: -0.01em; margin: 0 0 1rem; text-wrap: balance; }
.masthead p { max-width: 46rem; margin: 0 0 0.8rem; color: var(--soft); font-size: 0.98rem; }
.masthead p:last-child { margin-bottom: 0; }
.layout { display: grid; grid-template-columns: 15.5rem minmax(0, 1fr); gap: 3rem; align-items: start; }
.toc { position: sticky; top: calc(env(safe-area-inset-top, 0px) + 1rem); font-family: var(--sans); font-size: 0.86rem; max-height: calc(100vh - 2rem); overflow-y: auto; }
.toc h2 { font-size: 0.72rem; letter-spacing: 0.09em; text-transform: uppercase; color: var(--soft); margin: 0 0 0.6rem; font-weight: 600; border: 0; padding: 0; display: block; }
.toc ol { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 0.1rem; }
.toc a { display: flex; gap: 0.55rem; padding: 0.28rem 0.5rem; border-radius: 4px; color: var(--ink); text-decoration: none; line-height: 1.3; }
.toc a:hover { background: var(--panel); }
.toc a:focus-visible, .doc a:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
.toc .num { flex: 0 0 1.3rem; color: var(--soft); font-variant-numeric: tabular-nums; }
.doc { min-width: 0; }
.doc h2 { display: flex; flex-wrap: wrap; align-items: baseline; gap: 0.4rem 0.9rem; font-size: 1.5rem; line-height: 1.2; font-weight: 600; margin: 3rem 0 1rem; padding-top: 1rem; border-top: 1px solid var(--rule); text-wrap: balance; scroll-margin-top: 1rem; }
.doc h2:first-child { margin-top: 0; }
.doc h2 .num { font-family: var(--sans); font-size: 0.95rem; font-weight: 600; color: var(--paper); background: var(--ink); border-radius: 3px; padding: 0.1rem 0.5rem; font-variant-numeric: tabular-nums; }
.doc h2 .meta { font-family: var(--sans); font-size: 0.8rem; font-weight: 400; color: var(--soft); margin-left: auto; }
.doc p, .doc > ul, .doc > ol { max-width: 46rem; }
.doc p { margin: 0 0 0.9rem; }
.doc ul, .doc ol { margin: 0 0 1rem; padding-left: 1.25rem; }
.doc li { margin-bottom: 0.45rem; }
.doc li > ul, .doc li > ol { margin: 0.45rem 0 0.2rem; }
.doc li li { font-size: 0.97rem; margin-bottom: 0.3rem; }
.doc strong { font-weight: 600; }
code { font-family: var(--mono); font-size: 0.86em; background: var(--panel); border-radius: 3px; padding: 0.08em 0.32em; overflow-wrap: anywhere; }
.chip { display: inline-block; font-family: var(--sans); font-size: 0.72rem; font-weight: 600; letter-spacing: 0.02em; line-height: 1.5; padding: 0 0.5rem; border-radius: 999px; white-space: nowrap; vertical-align: 0.08em; }
.chip-ok { color: var(--ok); background: var(--ok-bg); }
.chip-part { color: var(--part); background: var(--part-bg); }
.chip-plan { color: var(--plan); background: var(--plan-bg); }
.chip-drop { color: var(--drop); background: var(--drop-bg); }
.chip-open { color: var(--open); background: var(--open-bg); }
.table-wrap { overflow-x: auto; margin: 0 0 1.25rem; border: 1px solid var(--rule); border-radius: 6px; }
table { border-collapse: collapse; width: 100%; font-family: var(--sans); font-size: 0.86rem; line-height: 1.45; font-variant-numeric: tabular-nums; }
th, td { text-align: left; vertical-align: top; padding: 0.5rem 0.75rem; border-bottom: 1px solid var(--rule); }
th { background: var(--panel); font-weight: 600; white-space: nowrap; }
tbody tr:last-child td { border-bottom: 0; }
td:first-child { white-space: nowrap; font-weight: 600; }
@media (max-width: 60rem) {
  .layout { grid-template-columns: minmax(0, 1fr); gap: 1.5rem; }
  .toc { position: static; max-height: none; border: 1px solid var(--rule); border-radius: 6px; padding: 0.9rem; }
  .toc ol { display: grid; grid-template-columns: repeat(auto-fill, minmax(12rem, 1fr)); }
  td:first-child { white-space: normal; }
  .doc h2 .meta { margin-left: 0; }
}
@media (prefers-reduced-motion: no-preference) { html { scroll-behavior: smooth; } }
"""

page = f"""<title>Agentic DiscoPoP Thesis Outline</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono&family=IBM+Plex+Sans:wght@400;600&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap">
<style>{CSS}</style>
<div class="page">
  <header class="masthead">
    <p class="eyebrow">{html.escape(eyebrow)}</p>
    <h1>{html.escape(h1)}</h1>
    {''.join(intro)}
  </header>
  <div class="layout">
    <nav class="toc" aria-label="Contents"><h2>Contents</h2><ol>{toc_html}</ol></nav>
    <main class="doc">
{chr(10).join(blocks)}
    </main>
  </div>
</div>
"""
open(out, "w", encoding="utf-8").write(page)


class Balance(HTMLParser):
    VOID = {"link", "meta", "br", "hr", "img", "input"}

    def __init__(self):
        super().__init__()
        self.stack, self.problems = [], []

    def handle_starttag(self, tag, attrs):
        if tag not in self.VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if not self.stack or self.stack[-1] != tag:
            self.problems.append(f"</{tag}> closes {self.stack[-1] if self.stack else 'nothing'}")
        else:
            self.stack.pop()


b = Balance()
b.feed(page)
print(f"{out}: {len(page)} bytes, {len(toc)} sections, {page.count('<table>')} tables, {page.count('class=' + chr(34) + 'chip ')} chips; "
      f"unbalanced tags: {b.problems[:5] or 'none'}; left open: {b.stack or 'none'}")
left = re.findall(r"\*\*|(?<![\w/])\*(?=\w)", re.sub(r"<style>.*?</style>", "", page, flags=re.S))
print("markdown markers left in the page:", len(left))
