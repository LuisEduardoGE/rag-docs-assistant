"""Page shell for the build-along guide: styles, reader script, assembly."""

from __future__ import annotations

CSS = r"""
  :root {
    --paper:      #F1F3F4;
    --card:       #FCFDFD;
    --card-2:     #F5F7F8;
    --code-bg:    #F4F6F8;
    --ink:        #141C33;
    --ink-soft:   #55617D;
    --blue:       #33528F;
    --blue-wash:  #E1E8F3;
    --rose:       #C8415C;
    --rose-wash:  #FAE5EA;
    --green:      #27654E;
    --green-wash: #DEEEE6;
    --rule:       #D3D9DE;
    --rule-soft:  #E2E7EA;
    --shadow:     0 1px 1px rgba(20,28,51,.05), 0 10px 28px -18px rgba(20,28,51,.45);

    --display: "Sitka Banner", "Sitka Display", Constantia, Georgia, Cambria, serif;
    --heading: "Sitka Heading", "Sitka Display", Constantia, Georgia, Cambria, serif;
    --body:    "Sitka Text", Charter, Georgia, Constantia, Cambria, serif;
    --mono:    Consolas, "Cascadia Mono", "SF Mono", Menlo, monospace;
  }

  @media (prefers-color-scheme: dark) {
    :root:not([data-theme="light"]) {
      --paper: #0E1420; --card: #161E2C; --card-2: #1A2331; --code-bg: #121A27;
      --ink: #E8ECF4; --ink-soft: #A0ABC4; --blue: #9DB6E6; --blue-wash: #1D2840;
      --rose: #FF8FA3; --rose-wash: #35202A; --green: #7BD0A7; --green-wash: #162E25;
      --rule: #2A3448; --rule-soft: #1F2839;
      --shadow: 0 1px 1px rgba(0,0,0,.3), 0 12px 30px -18px rgba(0,0,0,.8);
    }
  }
  :root[data-theme="dark"] {
    --paper: #0E1420; --card: #161E2C; --card-2: #1A2331; --code-bg: #121A27;
    --ink: #E8ECF4; --ink-soft: #A0ABC4; --blue: #9DB6E6; --blue-wash: #1D2840;
    --rose: #FF8FA3; --rose-wash: #35202A; --green: #7BD0A7; --green-wash: #162E25;
    --rule: #2A3448; --rule-soft: #1F2839;
    --shadow: 0 1px 1px rgba(0,0,0,.3), 0 12px 30px -18px rgba(0,0,0,.8);
  }

  * { box-sizing: border-box; }

  body {
    background: var(--paper); color: var(--ink); font-family: var(--body);
    font-size: 19px; line-height: 1.75; margin: 0;
    -webkit-font-smoothing: antialiased; text-rendering: optimizeLegibility;
  }

  .wrap { max-width: 1220px; margin: 0 auto; padding: 0 clamp(1rem, 3.5vw, 2.5rem) 5rem; }

  h1, h2, h3, h4 { font-weight: 600; text-wrap: balance; margin: 0; }
  h1 { font-family: var(--display); }
  h2, h3, h4 { font-family: var(--heading); }
  p { margin: 0; }
  a { color: var(--rose); text-underline-offset: 3px; }
  strong { font-weight: 600; color: var(--ink); }
  em { font-style: italic; }
  :focus-visible { outline: 2px solid var(--rose); outline-offset: 3px; border-radius: 4px; }

  .label {
    font-family: var(--mono); font-size: .68rem; letter-spacing: .16em;
    text-transform: uppercase; color: var(--ink-soft); margin: 0;
  }

  code {
    font-family: var(--mono); font-size: .84em; background: var(--blue-wash);
    color: var(--ink); padding: .12em .38em; border-radius: 3px;
  }

  /* masthead + progress */
  .masthead { padding: clamp(1.75rem, 4vw, 2.75rem) 0 1.5rem; display: grid; gap: .9rem; }
  .rule-row { display: flex; align-items: center; gap: 1rem; }
  .rule-row hr { flex: 1; border: 0; border-top: 1px solid var(--rule); margin: 0; }
  .masthead h1 { font-size: clamp(1.7rem, 3.6vw, 2.6rem); line-height: 1.08; letter-spacing: -.02em; max-width: 22ch; }

  .progress-row {
    display: flex; align-items: center; gap: 1rem; flex-wrap: wrap;
    padding: .85rem 0 1rem; border-top: 1px solid var(--rule); border-bottom: 1px solid var(--rule);
  }
  .bar { flex: 1 1 180px; min-width: 140px; height: 7px; border-radius: 99px; background: var(--rule); overflow: hidden; }
  .bar > i { display: block; height: 100%; width: 0%; border-radius: 99px; background: var(--green); transition: width .35s ease; }
  .progress-row .count {
    font-family: var(--mono); font-size: .74rem; letter-spacing: .1em; text-transform: uppercase;
    color: var(--ink-soft); font-variant-numeric: tabular-nums;
  }
  .btn-ghost {
    font-family: var(--mono); font-size: .68rem; letter-spacing: .1em; text-transform: uppercase;
    background: none; border: 1px solid var(--rule); color: var(--ink-soft);
    padding: .35rem .7rem; border-radius: 99px; cursor: pointer;
  }
  .btn-ghost:hover { color: var(--rose); border-color: var(--rose); }
  #storageNote { flex-basis: 100%; font-size: .8rem; color: var(--ink-soft); margin: 0; }

  /* reader */
  .reader { display: grid; gap: 2rem; padding-top: 1.75rem; align-items: start; }
  @media (min-width: 960px) { .reader { grid-template-columns: 255px minmax(0, 1fr); gap: 3.5rem; } }

  .toc-toggle {
    display: block; width: 100%; text-align: left;
    font-family: var(--mono); font-size: .72rem; letter-spacing: .12em; text-transform: uppercase;
    background: var(--card); border: 1px solid var(--rule); color: var(--ink);
    padding: .7rem 1rem; border-radius: 8px; cursor: pointer;
  }
  @media (min-width: 960px) { .toc-toggle { display: none; } }

  .toc { display: grid; gap: 1.3rem; }
  @media (min-width: 960px) { .toc { position: sticky; top: 1.25rem; max-height: calc(100vh - 2.5rem); overflow-y: auto; } }
  @media (max-width: 959px) { .toc { margin-top: .75rem; } }
  .toc[hidden] { display: none; }

  .toc-part > .label { color: var(--rose); margin-bottom: .45rem; }
  .toc-part ol { list-style: none; margin: 0; padding: 0; display: grid; gap: .1rem; }
  .toc-link {
    display: grid; grid-template-columns: 1.35rem 1fr; gap: .55rem; align-items: start;
    width: 100%; text-align: left; background: none; border: 0;
    padding: .42rem .5rem .42rem .35rem; border-radius: 6px; cursor: pointer;
    font-family: var(--body); font-size: .92rem; line-height: 1.38; color: var(--ink-soft);
  }
  .toc-link:hover { background: var(--card); color: var(--ink); }
  .toc-link[aria-current="true"] { background: var(--card); color: var(--ink); font-weight: 600; box-shadow: inset 2px 0 0 var(--rose); }
  .toc-link .tick {
    width: 1.05rem; height: 1.05rem; margin-top: .18em; border-radius: 50%;
    border: 1.5px solid var(--rule); display: grid; place-items: center;
    font-size: .62rem; color: transparent; flex: none;
  }
  .toc-link.is-done .tick { background: var(--green); border-color: var(--green); color: var(--paper); }
  .toc-link.is-done > span:last-child { color: var(--ink-soft); text-decoration: line-through; text-decoration-color: var(--rule); }
  .toc-link[aria-current="true"].is-done > span:last-child { color: var(--ink); }

  /* chapters */
  .chapter[hidden] { display: none; }
  .chapter { animation: fade .25s ease both; }
  @keyframes fade { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: none; } }
  @media (prefers-reduced-motion: reduce) { .chapter { animation: none; } .bar > i { transition: none; } }

  .chapter > * + * { margin-top: 1.6rem; }

  .col { display: grid; gap: 1.15rem; max-width: 64ch; }
  .chapter-head { max-width: 64ch; display: grid; gap: .6rem; margin-bottom: 2rem; }
  .chapter-head .eyebrow { font-family: var(--mono); font-size: .7rem; letter-spacing: .18em; text-transform: uppercase; color: var(--rose); }
  .chapter-head h2 { font-size: clamp(1.55rem, 3.2vw, 2.15rem); line-height: 1.15; letter-spacing: -.015em; }
  .chapter-head h2:focus { outline: none; }
  .chapter-head .deck { color: var(--ink-soft); font-size: 1.05rem; line-height: 1.6; max-width: 56ch; }
  h3 { font-size: 1.2rem; line-height: 1.3; }

  /* code */
  .code-block {
    background: var(--card); border: 1px solid var(--rule); border-radius: 10px;
    overflow: hidden; box-shadow: var(--shadow); max-width: 82ch;
  }
  .code-block .bar-label {
    background: var(--card-2); border-bottom: 1px solid var(--rule); padding: .55rem 1.1rem;
    display: flex; justify-content: space-between; gap: 1rem; flex-wrap: wrap; align-items: baseline;
  }
  .code-block .filename { color: var(--rose); letter-spacing: .08em; }
  .code-block pre {
    margin: 0; padding: 1.15rem 1.2rem; font-family: var(--mono); font-size: .78rem;
    line-height: 1.72; overflow-x: auto; background: var(--code-bg); color: var(--ink); tab-size: 4;
  }
  .code-block.file pre { max-height: 30rem; overflow-y: auto; }
  .code-block pre .c { color: var(--ink-soft); font-style: italic; }
  .code-block pre .k { color: var(--rose); }
  .code-block pre .s { color: var(--green); }
  .code-block pre .n { color: var(--blue); }
  .code-block pre .soft { color: var(--blue); font-style: italic; }

  /* file tree */
  .tree {
    background: var(--card); border: 1px solid var(--rule); border-radius: 10px;
    padding: 1.1rem 1.3rem; max-width: 64ch; font-family: var(--mono); font-size: .78rem;
    line-height: 1.85;
  }
  .tree .t-cap { font-family: var(--body); font-size: .92rem; color: var(--ink-soft); margin-bottom: .7rem; line-height: 1.5; }
  .t-row { display: flex; align-items: baseline; white-space: nowrap; }
  .t-ind { display: inline-block; width: 1.1rem; flex: none; }
  .t-tick { display: inline-block; width: 1.2rem; flex: none; color: var(--green); }
  .t-name { }
  .t-plain .t-name { color: var(--ink); }
  .t-done .t-name { color: var(--ink-soft); }
  .t-pending .t-name { color: var(--ink-soft); opacity: .45; }
  .t-new .t-name { color: var(--rose); font-weight: 700; }
  .t-marker { color: var(--rose); margin-left: .8rem; font-size: .72rem; }

  /* callouts */
  .aside { border-radius: 10px; padding: 1.25rem 1.5rem; display: grid; gap: .6rem; max-width: 64ch; font-size: .98rem; line-height: 1.68; }
  .aside.note { background: var(--blue-wash); }
  .aside.gotcha { background: var(--rose-wash); }
  .aside.task { background: var(--green-wash); }
  .aside.note .label { color: var(--blue); }
  .aside.gotcha .label { color: var(--rose); }
  .aside.task .label { color: var(--green); }

  /* tables */
  .table-scroll { overflow-x: auto; max-width: 64ch; }
  table { border-collapse: collapse; width: 100%; font-size: .95rem; }
  th, td { text-align: left; padding: .72rem 1rem .72rem 0; border-bottom: 1px solid var(--rule-soft); vertical-align: top; color: var(--ink); }
  th { font-family: var(--mono); font-size: .66rem; letter-spacing: .13em; text-transform: uppercase; color: var(--ink-soft); font-weight: 400; border-bottom: 1px solid var(--rule); }
  td.num, th.num { text-align: right; font-variant-numeric: tabular-nums lining-nums; padding-right: 0; }
  tr.best td { font-weight: 600; }
  tr.best td:first-child { color: var(--green); }

  ul, ol.steps { margin: 0; padding-left: 1.35rem; display: grid; gap: .6rem; }
  li { padding-left: .25rem; }

  /* chapter footer */
  .chapter-foot {
    max-width: 82ch; margin-top: 3rem; padding-top: 1.4rem; border-top: 1px solid var(--rule);
    display: flex; gap: .7rem; flex-wrap: wrap; align-items: center;
  }
  .btn {
    font-family: var(--body); font-size: .95rem; font-weight: 600;
    padding: .62rem 1.15rem; border-radius: 8px; cursor: pointer;
    border: 1px solid var(--rule); background: var(--card); color: var(--ink);
    display: inline-flex; align-items: center; gap: .5rem;
  }
  .btn:hover { border-color: var(--ink-soft); }
  .btn-done { background: var(--green); border-color: var(--green); color: #fff; }
  .btn-done:hover { filter: brightness(1.08); border-color: var(--green); }
  .btn-done.is-done { background: transparent; color: var(--green); border-color: var(--green); }
  .chapter-foot .spacer { flex: 1; }
  .btn[disabled] { opacity: .4; cursor: not-allowed; }

  #allDone { max-width: 64ch; margin-top: 2rem; padding: 1.4rem 1.6rem; background: var(--green-wash); border-radius: 10px; display: grid; gap: .5rem; }
  #allDone .label { color: var(--green); }
  #allDone[hidden] { display: none; }

  footer { margin-top: 3.5rem; padding-top: 1.4rem; border-top: 1px solid var(--rule); display: flex; justify-content: space-between; gap: 1rem; flex-wrap: wrap; }
"""


JS = r"""
(function () {
  "use strict";

  var chapters  = Array.prototype.slice.call(document.querySelectorAll("article.chapter"));
  var toc       = document.getElementById("toc");
  var tocToggle = document.getElementById("tocToggle");
  var doneBtn   = document.getElementById("doneBtn");
  var prevBtn   = document.getElementById("prevBtn");
  var nextBtn   = document.getElementById("nextBtn");
  var foot      = document.getElementById("chapterFoot");
  var allDone   = document.getElementById("allDone");
  var barFill   = document.getElementById("barFill");
  var countLbl  = document.getElementById("countLabel");
  var resetBtn  = document.getElementById("resetBtn");
  var storageNote = document.getElementById("storageNote");

  var KEY = "rag-build-guide-progress-v1";
  var current = 0;
  var done = Object.create(null);

  /* localStorage is the right store for reading progress: per-reader and
     instant. It can also be unavailable (private windows, blocked storage in
     an embedded frame). Rather than pretend, fall back to memory and say so. */
  var storageOK = (function () {
    try {
      window.localStorage.setItem("__probe__", "1");
      window.localStorage.removeItem("__probe__");
      return true;
    } catch (e) { return false; }
  })();

  function load() {
    if (!storageOK) return;
    try {
      var raw = window.localStorage.getItem(KEY);
      if (!raw) return;
      var saved = JSON.parse(raw);
      if (saved && typeof saved === "object") {
        if (saved.done && typeof saved.done === "object") {
          for (var id in saved.done) {
            if (Object.prototype.hasOwnProperty.call(saved.done, id) && saved.done[id]) done[id] = true;
          }
        }
        if (typeof saved.current === "number") current = saved.current;
      }
    } catch (e) { /* corrupt value: start clean rather than crash */ }
  }

  function save() {
    if (!storageOK) return;
    try { window.localStorage.setItem(KEY, JSON.stringify({ done: done, current: current })); }
    catch (e) { /* quota or policy: progress still works this session */ }
  }

  function buildToc() {
    var lastPart = null, list = null;
    chapters.forEach(function (ch, i) {
      var part = ch.getAttribute("data-part");
      if (part !== lastPart) {
        var group = document.createElement("div");
        group.className = "toc-part";
        var h = document.createElement("p");
        h.className = "label";
        h.innerHTML = part;
        group.appendChild(h);
        list = document.createElement("ol");
        group.appendChild(list);
        toc.appendChild(group);
        lastPart = part;
      }
      var li = document.createElement("li");
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "toc-link";
      var tick = document.createElement("span");
      tick.className = "tick";
      tick.setAttribute("aria-hidden", "true");
      tick.textContent = "✓";
      var title = document.createElement("span");
      title.innerHTML = ch.getAttribute("data-short");
      btn.appendChild(tick);
      btn.appendChild(title);
      btn.addEventListener("click", function () {
        show(i);
        if (!isWide()) closeToc();
      });
      li.appendChild(btn);
      list.appendChild(li);
    });
  }

  function render() {
    var links = toc.querySelectorAll(".toc-link");
    var count = 0;
    chapters.forEach(function (ch, i) {
      var isDone = !!done[ch.id];
      if (isDone) count++;
      var link = links[i];
      if (!link) return;
      link.classList.toggle("is-done", isDone);
      link.setAttribute("aria-current", i === current ? "true" : "false");
    });

    var pct = chapters.length ? Math.round((count / chapters.length) * 100) : 0;
    barFill.style.width = pct + "%";
    countLbl.textContent = count + " of " + chapters.length + " done";
    document.querySelector(".bar").setAttribute("aria-valuenow", String(pct));

    var chapterDone = !!done[chapters[current].id];
    doneBtn.textContent = chapterDone ? "✓ Done — undo" : "Mark as done";
    doneBtn.classList.toggle("is-done", chapterDone);

    prevBtn.disabled = current === 0;
    nextBtn.disabled = current === chapters.length - 1;
    allDone.hidden = !(count === chapters.length);
  }

  function show(index, opts) {
    if (index < 0 || index >= chapters.length) return;
    current = index;
    chapters.forEach(function (ch, i) { ch.hidden = i !== index; });
    chapters[index].appendChild(foot);
    if (!opts || opts.scroll !== false) {
      window.scrollTo({ top: 0, behavior: reduceMotion() ? "auto" : "smooth" });
    }
    if (opts && opts.focus) chapters[index].querySelector(".chapter-head h2").focus();
    if (history.replaceState) history.replaceState(null, "", "#" + chapters[index].id);
    render();
    save();
  }

  function reduceMotion() { return window.matchMedia("(prefers-reduced-motion: reduce)").matches; }
  function isWide() { return window.matchMedia("(min-width: 960px)").matches; }

  /* On wide screens the contents are a permanent sidebar; on narrow screens a
     drawer that starts closed. Those need separate bookkeeping, or the
     sidebar's always-open state leaks into the narrow layout and the drawer
     springs open on load, pushing the chapter off screen. */
  var userOpenedToc = false;
  function syncToc() {
    var open = isWide() || userOpenedToc;
    toc.hidden = !open;
    tocToggle.setAttribute("aria-expanded", String(open));
  }
  function closeToc() { userOpenedToc = false; syncToc(); }

  doneBtn.addEventListener("click", function () {
    var id = chapters[current].id;
    if (done[id]) { delete done[id]; render(); save(); }
    else {
      done[id] = true; save();
      if (current < chapters.length - 1) show(current + 1, { focus: true });
      else render();
    }
  });
  prevBtn.addEventListener("click", function () { show(current - 1, { focus: true }); });
  nextBtn.addEventListener("click", function () { show(current + 1, { focus: true }); });
  resetBtn.addEventListener("click", function () { done = Object.create(null); save(); render(); });
  tocToggle.addEventListener("click", function () { userOpenedToc = toc.hidden; syncToc(); });
  window.addEventListener("resize", syncToc);

  document.addEventListener("keydown", function (e) {
    if (e.altKey || e.ctrlKey || e.metaKey) return;
    var tag = (e.target && e.target.tagName) || "";
    if (tag === "INPUT" || tag === "TEXTAREA") return;
    if (e.key === "ArrowRight" && current < chapters.length - 1) show(current + 1);
    if (e.key === "ArrowLeft" && current > 0) show(current - 1);
  });

  buildToc();
  load();

  var fromHash = -1;
  if (window.location.hash) {
    chapters.forEach(function (ch, i) { if ("#" + ch.id === window.location.hash) fromHash = i; });
  }
  var start = fromHash >= 0 ? fromHash : current;
  if (start < 0 || start >= chapters.length) start = 0;

  syncToc();
  show(start, { scroll: false });

  if (!storageOK) {
    storageNote.hidden = false;
    storageNote.textContent =
      "Storage is blocked in this view, so progress is kept for this session only and resets if you reload.";
  }
})();
"""


NUMBER_WORDS = {
    14: "fourteen", 15: "fifteen", 16: "sixteen", 17: "seventeen", 18: "eighteen",
}


def render(chapters: list[dict]) -> str:
    n = len(chapters)
    n_word = NUMBER_WORDS.get(n, str(n))
    articles = []
    for ch in chapters:
        short = ch["title"].split(" &mdash; ")[0]
        articles.append(
            f'<article class="chapter" id="{ch["id"]}" data-part="{ch["part"]}" '
            f'data-short="{short}" hidden>'
            '<div class="chapter-head">'
            f'<p class="eyebrow">{ch["eyebrow"]}</p>'
            f'<h2 tabindex="-1">{ch["title"]}</h2>'
            f'<p class="deck">{ch["deck"]}</p>'
            "</div>"
            f'{ch["body"]}'
            "</article>"
        )

    return f"""<title>RAG from scratch &mdash; the build-along</title>

<style>{CSS}</style>

<div class="wrap">

  <header class="masthead">
    <div class="rule-row">
      <p class="label">Build-along &middot; {n_word} chapters</p>
      <hr>
      <p class="label">Every command &middot; every file</p>
    </div>
    <h1>RAG from scratch: every command, every file</h1>
  </header>

  <div class="progress-row">
    <span class="count" id="countLabel">0 of {n} done</span>
    <span class="bar" role="progressbar" aria-labelledby="countLabel"><i id="barFill"></i></span>
    <button type="button" class="btn-ghost" id="resetBtn">Reset progress</button>
    <p id="storageNote" hidden></p>
  </div>

  <div class="reader">
    <div>
      <button type="button" class="toc-toggle" id="tocToggle" aria-expanded="false" aria-controls="toc">Contents</button>
      <nav class="toc" id="toc" aria-label="Chapters"></nav>
    </div>

    <main id="main">
      {"".join(articles)}

      <div class="chapter-foot" id="chapterFoot">
        <button type="button" class="btn btn-done" id="doneBtn">Mark as done</button>
        <span class="spacer"></span>
        <button type="button" class="btn" id="prevBtn">&larr; Previous</button>
        <button type="button" class="btn" id="nextBtn">Next &rarr;</button>
      </div>

      <div id="allDone" hidden>
        <p class="label">Every chapter done</p>
        <p>You now have a working retrieval system, a number that says how well it retrieves, and the
        reasoning behind every decision in it. The last thing left is the one this guide cannot do for
        you: point it at your own documents and see what breaks.</p>
      </div>
    </main>
  </div>

  <footer>
    <p class="label">Build-along &middot; {n_word} chapters</p>
    <p class="label">Measure retrieval &middot; then ship</p>
  </footer>
</div>

<script>{JS}</script>
"""
