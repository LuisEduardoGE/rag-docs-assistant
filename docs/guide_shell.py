"""Page shell for the build-along guide: styles, reader script, assembly.

Design direction -- technical instrument.

The guide's own argument is "measure it, or you are guessing", and the reader
is assembling a machine from numbered parts. So the page borrows from
technical drawings and instrument faces rather than from documentation sites:
drafting-sheet stock, DIN lettering (Bahnschrift is Microsoft's DIN), petrol
structural lines, and a brass indicator.

The signature element is the gauge rail: the progress indicator is a
tick-marked scale with a brass needle at your position and major gradations
at part boundaries. It replaces a generic progress bar with the instrument
the guide keeps telling you to build.
"""

from __future__ import annotations

CSS = r"""
  :root {
    /* Drafting sheet and instrument face. Deliberately cool and slightly
       green -- not the warm cream every generated page reaches for. */
    --sheet:      #EDEEE9;
    --card:       #F6F7F3;
    --card-2:     #E6E8E1;
    --code-bg:    #F2F3EE;
    --ink:        #14181A;
    --ink-2:      #4A5359;
    --ink-3:      #5A6266;   /* small text: 5.0:1 worst case */

    --petrol:     #33566B;   /* structure: diagram lines, notes */
    --petrol-wash:#DFE6EA;
    --brass:      #7E520F;   /* the indicator: you are here (5.4:1 worst case) */
    --brass-wash: #F0E5D2;
    --verified:   #35604A;   /* instrument green: done, correct */
    --verified-wash:#DDE8E0;
    --warn:       #A33A20;   /* the gotcha */
    --warn-wash:  #F6E3DC;

    --rule:       #D2D5CC;
    --rule-2:     #E1E3DC;

    /* Bahnschrift is Microsoft's DIN -- the lettering of technical drawings,
       machine plates and road signs. Candara answers it with humanist warmth
       so long prose stays readable. Cascadia Mono for anything typed. */
    --display: Bahnschrift, "DIN Alternate", "Franklin Gothic Book", "Segoe UI", sans-serif;
    --body:    Candara, "Segoe UI Variable Text", "Segoe UI", Corbel, sans-serif;
    --mono:    "Cascadia Mono", Consolas, "SF Mono", Menlo, monospace;

    --shadow: 0 1px 2px rgba(20,24,26,.045), 0 12px 28px -20px rgba(20,24,26,.4);
    --measure: 63ch;
  }

  @media (prefers-color-scheme: dark) {
    :root:not([data-theme="light"]) {
      --sheet: #10151A; --card: #171E24; --card-2: #1D262C; --code-bg: #131A20;
      --ink: #E6EAE6; --ink-2: #A7B1B4; --ink-3: #939DA1;
      --petrol: #8FB2C6; --petrol-wash: #1B2A34;
      --brass: #DCA954; --brass-wash: #2C2415;
      --verified: #6FBF95; --verified-wash: #16281F;
      --warn: #E58164; --warn-wash: #2E1A15;
      --rule: #2A343A; --rule-2: #202A30;
      --shadow: 0 1px 2px rgba(0,0,0,.3), 0 14px 32px -22px rgba(0,0,0,.85);
    }
  }
  :root[data-theme="dark"] {
    --sheet: #10151A; --card: #171E24; --card-2: #1D262C; --code-bg: #131A20;
    --ink: #E6EAE6; --ink-2: #A7B1B4; --ink-3: #939DA1;
    --petrol: #8FB2C6; --petrol-wash: #1B2A34;
    --brass: #DCA954; --brass-wash: #2C2415;
    --verified: #6FBF95; --verified-wash: #16281F;
    --warn: #E58164; --warn-wash: #2E1A15;
    --rule: #2A343A; --rule-2: #202A30;
    --shadow: 0 1px 2px rgba(0,0,0,.3), 0 14px 32px -22px rgba(0,0,0,.85);
  }

  * { box-sizing: border-box; }

  body {
    background: var(--sheet);
    color: var(--ink);
    font-family: var(--body);
    font-size: 20px;
    line-height: 1.68;
    margin: 0;
    -webkit-font-smoothing: antialiased;
    text-rendering: optimizeLegibility;
  }

  .wrap { max-width: 1240px; margin: 0 auto; padding: 0 clamp(1rem, 3.2vw, 2.25rem) 5rem; }

  h1, h2, h3, h4 { font-family: var(--display); font-weight: 600; margin: 0; text-wrap: balance; }
  p { margin: 0; }
  a { color: var(--brass); text-underline-offset: 3px; }
  strong { font-weight: 600; color: var(--ink); }
  em { font-style: italic; }
  :focus-visible { outline: 2px solid var(--brass); outline-offset: 3px; border-radius: 2px; }

  /* Plate labels: the small stamped text on an instrument face. */
  .label {
    font-family: var(--display); font-weight: 600; font-size: .7rem;
    letter-spacing: .17em; text-transform: uppercase; color: var(--ink-3); margin: 0;
  }

  code {
    font-family: var(--mono); font-size: .8em; background: var(--petrol-wash);
    color: var(--ink); padding: .14em .4em; border-radius: 2px;
  }

  /* ---------- masthead ---------- */

  .masthead { padding: clamp(1.75rem, 3.5vw, 2.75rem) 0 0; }
  .stamp { display: flex; align-items: center; gap: .85rem; flex-wrap: wrap; padding-bottom: 1.1rem; }
  .stamp hr { flex: 1; border: 0; border-top: 1px solid var(--rule); margin: 0; min-width: 1rem; }
  .stamp .label { color: var(--brass); }

  .masthead h1 {
    font-size: clamp(1.85rem, 4.4vw, 3.15rem);
    line-height: 1.03; letter-spacing: -.012em; max-width: 21ch;
  }
  .masthead .sub {
    color: var(--ink-2); font-size: 1.06rem; line-height: 1.55;
    max-width: 54ch; margin-top: .85rem;
  }

  /* Spec strip: what you will have built. Real numbers, no decoration. */
  .spec {
    display: flex; flex-wrap: wrap; margin-top: 1.7rem;
    border-top: 1px solid var(--ink); border-bottom: 1px solid var(--rule);
  }
  .spec div {
    padding: .8rem 1.5rem .85rem 0; margin-right: 1.5rem;
    border-right: 1px solid var(--rule-2); display: grid; gap: .15rem;
  }
  .spec div:last-child { border-right: 0; margin-right: 0; }
  .spec b {
    font-family: var(--display); font-size: 1.55rem; font-weight: 600;
    line-height: 1; letter-spacing: -.01em; font-variant-numeric: tabular-nums lining-nums;
  }
  .spec span {
    font-family: var(--display); font-size: .63rem; font-weight: 600;
    letter-spacing: .15em; text-transform: uppercase; color: var(--ink-3);
  }

  /* ---------- the gauge rail (signature) ---------- */

  .gauge {
    position: sticky; top: 0; z-index: 20;
    background: var(--sheet); padding: .75rem 0 .65rem;
    border-bottom: 1px solid var(--rule); margin-top: 1.6rem;
  }
  .gauge-row { display: flex; align-items: center; gap: 1.1rem; }
  .gauge-read {
    font-family: var(--display); font-weight: 600; font-size: .68rem;
    letter-spacing: .14em; text-transform: uppercase; color: var(--ink-2);
    white-space: nowrap; font-variant-numeric: tabular-nums;
  }
  .gauge-read b { color: var(--brass); font-weight: 600; }

  .scale { flex: 1; position: relative; height: 30px; min-width: 110px; display: flex; align-items: flex-end; }
  .scale::after {
    content: ""; position: absolute; left: 0; right: 0; bottom: 0;
    height: 1px; background: var(--rule);
  }
  .tick {
    flex: 1; position: relative; height: 100%; padding: 0; border: 0; background: none;
    cursor: pointer; display: flex; align-items: flex-end; justify-content: center;
  }
  .tick i {
    display: block; width: 2px; height: 9px; background: var(--rule);
    transition: height .18s ease, background .18s ease;
  }
  .tick.major i { height: 15px; background: var(--ink-3); }
  .tick.done i { background: var(--verified); height: 13px; }
  .tick.major.done i { height: 17px; }
  .tick:hover i { background: var(--brass); height: 19px; }
  .tick.here i { background: var(--brass); height: 26px; width: 3px; box-shadow: 0 0 0 3px var(--sheet); }
  .tick.here::before {
    content: ""; position: absolute; top: -1px; left: 50%; transform: translateX(-50%);
    border: 4px solid transparent; border-top-color: var(--brass);
  }

  .btn-plain {
    font-family: var(--display); font-weight: 600; font-size: .64rem;
    letter-spacing: .14em; text-transform: uppercase;
    background: none; border: 1px solid var(--rule); color: var(--ink-3);
    padding: .4rem .75rem; border-radius: 2px; cursor: pointer; white-space: nowrap;
  }
  .btn-plain:hover { color: var(--brass); border-color: var(--brass); }
  #storageNote { font-size: .8rem; color: var(--ink-3); margin: .5rem 0 0; }

  /* ---------- reader layout ---------- */

  .reader { display: grid; gap: 2rem; padding-top: 2rem; }
  @media (min-width: 1000px) { .reader { grid-template-columns: 236px minmax(0, 1fr); gap: 3.4rem; } }

  .toc-toggle {
    display: block; width: 100%; text-align: left;
    font-family: var(--display); font-weight: 600; font-size: .7rem;
    letter-spacing: .14em; text-transform: uppercase;
    background: var(--card); border: 1px solid var(--rule); color: var(--ink);
    padding: .8rem 1rem; border-radius: 2px; cursor: pointer;
  }
  @media (min-width: 1000px) { .toc-toggle { display: none; } }

  /* The manifest: a parts list, not a nav menu. */
  .rail { align-self: stretch; }
  .toc { display: grid; gap: 1.4rem; align-content: start; }
  @media (min-width: 1000px) {
    .toc { position: sticky; top: 4.4rem; max-height: calc(100vh - 5.8rem); overflow-y: auto; overflow-x: hidden; }
  }
  .toc[hidden] { display: none; }
  .toc-part > .label {
    color: var(--ink); border-bottom: 1px solid var(--ink);
    padding-bottom: .35rem; margin-bottom: .45rem; overflow-wrap: anywhere;
  }
  .toc ol { list-style: none; margin: 0; padding: 0; display: grid; }
  .toc-link {
    display: grid; grid-template-columns: 1.5rem 1fr; gap: .5rem; align-items: baseline;
    width: 100%; text-align: left; background: none; border: 0;
    border-left: 2px solid transparent; padding: .4rem .4rem .4rem .5rem; cursor: pointer;
    font-family: var(--body); font-size: .93rem; line-height: 1.36; color: var(--ink-2);
  }
  .toc-link:hover { background: var(--card); color: var(--ink); }
  .toc-link[aria-current="true"] {
    background: var(--card); color: var(--ink); border-left-color: var(--brass); font-weight: 600;
  }
  .toc-n { font-family: var(--mono); font-size: .68rem; color: var(--ink-3); font-variant-numeric: tabular-nums; }
  .toc-link[aria-current="true"] .toc-n { color: var(--brass); }
  .toc-link.is-done .toc-n { color: var(--verified); }
  .toc-link.is-done .toc-t { color: var(--ink-3); }
  .toc-link[aria-current="true"].is-done .toc-t { color: var(--ink); }
  .toc-t { overflow-wrap: anywhere; min-width: 0; }
  .toc-link.is-file .toc-t { font-family: var(--mono); font-size: .78rem; letter-spacing: -.01em; }

  /* ---------- chapters ---------- */

  .chapter[hidden] { display: none; }
  .chapter { animation: rise .28s cubic-bezier(.2,.7,.3,1) both; }
  @keyframes rise { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: none; } }
  @media (prefers-reduced-motion: reduce) {
    .chapter { animation: none; }
    .tick i { transition: none; }
  }

  .chapter > * + * { margin-top: 1.7rem; }

  .chapter-head { max-width: var(--measure); display: grid; gap: .55rem; margin-bottom: 2.1rem; }
  .chapter-head .eyebrow {
    font-family: var(--display); font-weight: 600; font-size: .68rem;
    letter-spacing: .18em; text-transform: uppercase; color: var(--brass);
  }
  .chapter-head h2 { font-size: clamp(1.6rem, 3.3vw, 2.3rem); line-height: 1.1; letter-spacing: -.014em; }
  .chapter-head h2:focus { outline: none; }
  .chapter-head .deck { color: var(--ink-2); font-size: 1.05rem; line-height: 1.55; max-width: 56ch; }

  /* The plate: what this step produces. Stamped, not badged. */
  .makes {
    display: inline-flex; justify-self: start; align-items: baseline; gap: .7rem; margin-top: .55rem;
    border: 1px solid var(--brass); border-left-width: 3px;
    padding: .4rem .85rem .45rem; background: var(--brass-wash);
  }
  .makes-label {
    font-family: var(--display); font-weight: 600; font-size: .6rem;
    letter-spacing: .16em; text-transform: uppercase; color: var(--brass);
  }
  .makes code { background: none; padding: 0; font-size: .82rem; color: var(--ink); font-weight: 600; }

  .col { display: grid; gap: 1.1rem; max-width: var(--measure); }
  h3 { font-size: 1.22rem; line-height: 1.25; letter-spacing: -.005em; }

  /* ---------- code ---------- */

  .code-block {
    background: var(--card); border: 1px solid var(--rule); border-radius: 2px;
    overflow: hidden; box-shadow: var(--shadow); max-width: 84ch;
  }
  .code-block .bar-label {
    background: var(--card-2); border-bottom: 1px solid var(--rule);
    padding: .45rem .95rem; display: flex; justify-content: space-between;
    gap: .8rem; flex-wrap: wrap; align-items: center;
  }
  .code-block .filename {
    color: var(--brass); font-family: var(--mono); letter-spacing: 0;
    text-transform: none; font-weight: 400; font-size: .74rem;
  }
  .code-block pre {
    margin: 0; padding: 1.05rem 1.15rem; font-family: var(--mono); font-size: .77rem;
    line-height: 1.75; overflow-x: auto; background: var(--code-bg); color: var(--ink); tab-size: 4;
  }
  .code-block.file pre { max-height: 30rem; overflow-y: auto; }
  .code-block pre .c { color: var(--ink-3); font-style: italic; }
  .code-block pre .k { color: var(--warn); }
  .code-block pre .s { color: var(--verified); }
  .code-block pre .n { color: var(--petrol); }
  .code-block pre .soft { color: var(--petrol); font-style: italic; }

  .copy {
    font-family: var(--display); font-weight: 600; font-size: .6rem; letter-spacing: .14em;
    text-transform: uppercase; background: none; border: 1px solid var(--rule);
    color: var(--ink-3); padding: .2rem .5rem; border-radius: 2px; cursor: pointer;
  }
  .copy:hover { color: var(--brass); border-color: var(--brass); }
  .copy.ok { color: var(--verified); border-color: var(--verified); }

  /* ---------- walkthrough: a file in numbered parts ---------- */

  .walkthrough { display: grid; gap: 1.9rem; max-width: 84ch; }
  .part { display: grid; }
  .part-head {
    display: flex; align-items: baseline; gap: .8rem; flex-wrap: wrap;
    padding-bottom: .5rem; margin-bottom: .55rem; border-bottom: 1px solid var(--ink);
  }
  .part-n {
    font-family: var(--mono); font-size: .68rem; letter-spacing: .04em;
    color: var(--brass); white-space: nowrap; font-variant-numeric: tabular-nums;
  }
  .part-head h4 { font-size: 1.02rem; line-height: 1.28; }
  .code-block.walk { border-radius: 2px 2px 0 0; border-bottom: 0; max-width: none; }
  .code-block.walk pre { padding-bottom: .4rem; }
  .part-why {
    background: var(--card-2); border: 1px solid var(--rule); border-top: 0;
    border-radius: 0 0 2px 2px; padding: 1rem 1.2rem 1.1rem;
    display: grid; gap: .5rem; font-size: .95rem; line-height: 1.62; color: var(--ink-2);
  }
  .part-why .label { color: var(--brass); }
  .part-why strong { color: var(--ink); }

  /* ---------- figures ---------- */

  .fig {
    margin: 0; max-width: 84ch; background: var(--card);
    border: 1px solid var(--rule); border-radius: 2px;
    padding: 1.3rem 1.4rem 1rem; box-shadow: var(--shadow); overflow-x: auto;
  }
  .fig svg { display: block; width: 100%; max-width: 100%; height: auto; min-width: 460px; }
  .fig figcaption {
    font-size: .91rem; line-height: 1.55; color: var(--ink-2);
    margin-top: .95rem; padding-top: .8rem; border-top: 1px solid var(--rule-2); max-width: 62ch;
  }
  .fig figcaption b { color: var(--ink); font-weight: 600; }
  .d-title { font-family: var(--display); font-weight: 600; font-size: 10.5px; letter-spacing: .15em; }
  .d-box   { font-family: var(--display); font-size: 14px; font-weight: 600; fill: var(--ink); }
  .d-sub   { font-family: var(--body); font-size: 12.5px; fill: var(--ink-2); }
  .d-edge  { font-family: var(--mono); font-size: 10px; letter-spacing: .04em; fill: var(--ink-3); }
  .d-mono  { font-family: var(--mono); font-size: 11.5px; fill: var(--ink); }

  /* ---------- the manifest tree ---------- */

  .tree {
    background: var(--card); border: 1px solid var(--rule); border-radius: 2px;
    padding: 1.1rem 1.3rem; max-width: var(--measure); font-family: var(--mono);
    font-size: .76rem; line-height: 1.85;
  }
  .tree .t-cap {
    font-family: var(--body); font-size: .92rem; color: var(--ink-2);
    margin-bottom: .75rem; line-height: 1.5; padding-bottom: .6rem;
    border-bottom: 1px solid var(--rule-2);
  }
  .t-row { display: flex; align-items: baseline; white-space: nowrap; }
  .t-ind { display: inline-block; width: 1.05rem; flex: none; }
  .t-tick { display: inline-block; width: 1.15rem; flex: none; color: var(--verified); }
  .t-plain .t-name { color: var(--ink); }
  .t-done .t-name { color: var(--ink-3); }
  .t-pending .t-name { color: var(--ink-3); opacity: .42; }
  .t-new .t-name { color: var(--brass); font-weight: 700; }
  .t-marker { color: var(--brass); margin-left: .8rem; font-size: .7rem; }

  /* ---------- notes ---------- */

  .aside {
    border-left: 3px solid var(--petrol); padding: 1rem 1.3rem 1.05rem;
    display: grid; gap: .5rem; max-width: var(--measure);
    font-size: .96rem; line-height: 1.62;
    background: var(--petrol-wash); color: var(--ink-2);
  }
  .aside strong { color: var(--ink); }
  .aside.gotcha { border-left-color: var(--warn); background: var(--warn-wash); }
  .aside.task   { border-left-color: var(--verified); background: var(--verified-wash); }
  .aside.note .label   { color: var(--petrol); }
  .aside.gotcha .label { color: var(--warn); }
  .aside.task .label   { color: var(--verified); }

  /* ---------- tables ---------- */

  .table-scroll { overflow-x: auto; max-width: var(--measure); }
  table { border-collapse: collapse; width: 100%; font-size: .94rem; }
  th, td {
    text-align: left; padding: .68rem 1rem .68rem 0;
    border-bottom: 1px solid var(--rule-2); vertical-align: top; color: var(--ink);
  }
  th {
    font-family: var(--display); font-weight: 600; font-size: .64rem; letter-spacing: .14em;
    text-transform: uppercase; color: var(--ink-3); border-bottom: 1px solid var(--ink);
  }
  td.num { text-align: right; font-variant-numeric: tabular-nums lining-nums; padding-right: 0; font-family: var(--mono); font-size: .86em; }
  th.num { text-align: right; padding-right: 0; }
  tr.best td { font-weight: 600; }
  tr.best td:first-child { color: var(--verified); }

  ul, ol.steps { margin: 0; padding-left: 1.3rem; display: grid; gap: .55rem; }
  li { padding-left: .25rem; }

  /* ---------- question and answer ---------- */

  .qa-wrap { max-width: 74ch; border-top: 1px solid var(--ink); }
  details.qa { border-bottom: 1px solid var(--rule); }
  details.qa summary {
    padding: .95rem .2rem; cursor: pointer; font-weight: 600;
    font-family: var(--display); font-size: 1.04rem; line-height: 1.3; list-style: none;
    display: flex; gap: .7rem; align-items: baseline;
  }
  details.qa summary::marker { content: ""; }
  details.qa summary::-webkit-details-marker { display: none; }
  details.qa summary::before { content: "+"; color: var(--brass); font-family: var(--mono); font-size: .9rem; }
  details.qa[open] summary::before { content: "\2212"; }
  details.qa .body {
    padding: 0 .2rem 1.15rem 1.55rem; font-size: .96rem; color: var(--ink-2);
    display: grid; gap: .7rem; line-height: 1.62;
  }
  details.qa .body strong { color: var(--ink); }

  /* ---------- chapter footer ---------- */

  .chapter-foot {
    max-width: 84ch; margin-top: 3rem; padding-top: 1.3rem; border-top: 1px solid var(--ink);
    display: flex; gap: .6rem; flex-wrap: wrap; align-items: center;
  }
  .btn {
    font-family: var(--display); font-weight: 600; font-size: .78rem;
    letter-spacing: .07em; text-transform: uppercase;
    padding: .62rem 1.15rem; border-radius: 2px; cursor: pointer;
    border: 1px solid var(--rule); background: var(--card); color: var(--ink);
    display: inline-flex; align-items: center; gap: .5rem;
  }
  .btn:hover { border-color: var(--ink-2); }
  .btn-done { background: var(--verified); border-color: var(--verified); color: var(--sheet); }
  .btn-done:hover { filter: brightness(1.09); border-color: var(--verified); }
  .btn-done.is-done { background: none; color: var(--verified); }
  .chapter-foot .spacer { flex: 1; }
  .btn[disabled] { opacity: .35; cursor: not-allowed; }

  #allDone {
    max-width: var(--measure); margin-top: 2rem; padding: 1.3rem 1.5rem;
    border: 1px solid var(--verified); border-left-width: 3px;
    background: var(--verified-wash); display: grid; gap: .5rem;
  }
  #allDone .label { color: var(--verified); }
  #allDone[hidden] { display: none; }

  footer {
    margin-top: 3.5rem; padding-top: 1.2rem; border-top: 1px solid var(--rule);
    display: flex; justify-content: space-between; gap: 1rem; flex-wrap: wrap;
  }

  /* ---------- print ---------- */
  @media print {
    .gauge, .toc, .toc-toggle, .chapter-foot, .copy, footer { display: none !important; }
    .chapter[hidden] { display: block !important; }
    .chapter { break-before: page; animation: none; }
    .reader { display: block; }
    .code-block.file pre { max-height: none; }
    body { background: #fff; font-size: 11pt; }
  }
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
  var scale     = document.getElementById("scale");
  var readout   = document.getElementById("readout");
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

  function pad(n) { return (n < 10 ? "0" : "") + n; }

  /* ---- the manifest ---- */

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

      var n = document.createElement("span");
      n.className = "toc-n";
      n.textContent = i === 0 ? "—" : pad(i);

      var t = document.createElement("span");
      t.className = "toc-t";
      var madeFile = ch.getAttribute("data-file");
      if (madeFile) { btn.classList.add("is-file"); t.textContent = madeFile; }
      else { t.innerHTML = ch.getAttribute("data-short"); }

      btn.appendChild(n);
      btn.appendChild(t);
      btn.addEventListener("click", function () {
        show(i);
        if (!isWide()) closeToc();
      });
      li.appendChild(btn);
      list.appendChild(li);
    });
  }

  /* ---- the gauge: one tick per chapter, major at part boundaries ---- */

  function buildScale() {
    var lastPart = null;
    chapters.forEach(function (ch, i) {
      var b = document.createElement("button");
      b.type = "button";
      b.className = "tick";
      var part = ch.getAttribute("data-part");
      if (part !== lastPart) { b.classList.add("major"); lastPart = part; }
      var name = ch.getAttribute("data-file") ||
                 ch.getAttribute("data-short").replace(/<[^>]+>/g, "");
      var label = (i === 0 ? "Preface" : "Chapter " + i) + " · " + name;
      b.title = label;
      b.setAttribute("aria-label", label);
      b.appendChild(document.createElement("i"));
      b.addEventListener("click", function () { show(i); });
      scale.appendChild(b);
    });
  }

  function render() {
    var links = toc.querySelectorAll(".toc-link");
    var ticks = scale.querySelectorAll(".tick");
    var count = 0;

    chapters.forEach(function (ch, i) {
      var isDone = !!done[ch.id];
      if (isDone) count++;
      var link = links[i];
      if (link) {
        link.classList.toggle("is-done", isDone);
        link.setAttribute("aria-current", i === current ? "true" : "false");
      }
      var tick = ticks[i];
      if (tick) {
        tick.classList.toggle("done", isDone);
        tick.classList.toggle("here", i === current);
        tick.setAttribute("aria-current", i === current ? "true" : "false");
      }
    });

    readout.innerHTML = "<b>" + pad(current) + "</b> / " + (chapters.length - 1) +
                        " · " + count + " built";

    var chapterDone = !!done[chapters[current].id];
    doneBtn.textContent = chapterDone ? "✓ Done" : "Mark as done";
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
  function isWide() { return window.matchMedia("(min-width: 1000px)").matches; }

  /* On wide screens the manifest is a permanent sidebar; on narrow screens a
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

  /* ---- copy buttons: commands are for running, not transcribing ---- */

  function addCopyButtons() {
    if (!navigator.clipboard) return;
    Array.prototype.forEach.call(document.querySelectorAll(".code-block"), function (block) {
      var bar = block.querySelector(".bar-label");
      var pre = block.querySelector("pre");
      if (!bar || !pre) return;
      var b = document.createElement("button");
      b.type = "button";
      b.className = "copy";
      b.textContent = "Copy";
      b.addEventListener("click", function () {
        navigator.clipboard.writeText(pre.textContent).then(function () {
          b.textContent = "Copied";
          b.classList.add("ok");
          setTimeout(function () { b.textContent = "Copy"; b.classList.remove("ok"); }, 1400);
        });
      });
      bar.appendChild(b);
    });
  }

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
  buildScale();
  addCopyButtons();
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


def render(chapters: list[dict], stats: dict | None = None) -> str:
    n = len(chapters)
    files = sum(1 for c in chapters if c.get("file"))
    stats = stats or {}

    articles = []
    for ch in chapters:
        short = ch["title"].split(" &mdash; ")[0]
        made = ch.get("file") or ""
        plate = (
            f'<p class="makes"><span class="makes-label">this step writes</span>'
            f"<code>{made}</code></p>" if made else ""
        )
        articles.append(
            f'<article class="chapter" id="{ch["id"]}" data-part="{ch["part"]}" '
            f'data-short="{short}" data-file="{made}" hidden>'
            '<div class="chapter-head">'
            f'<p class="eyebrow">{ch["eyebrow"]}</p>'
            f'<h2 tabindex="-1">{ch["title"]}</h2>'
            f'<p class="deck">{ch["deck"]}</p>'
            f"{plate}"
            "</div>"
            f'{ch["body"]}'
            "</article>"
        )

    spec = [
        (str(n - 1), "chapters"),
        (str(files), "files you write"),
        (stats.get("lines", "1,235"), "lines of python"),
        (stats.get("mrr", "0.943"), "MRR@4 at the end"),
    ]
    spec_html = "".join(f"<div><b>{v}</b><span>{k}</span></div>" for v, k in spec)

    return f"""<title>RAG from scratch &mdash; the build-along</title>

<style>{CSS}</style>

<div class="wrap">

  <header class="masthead">
    <div class="stamp">
      <p class="label">Build-along</p>
      <hr>
      <p class="label">Python &middot; FastAPI &middot; Claude</p>
    </div>
    <h1>Build a retrieval system you can defend</h1>
    <p class="sub">Every command, and every file written piece by piece with the reasoning attached &mdash;
    ending in an evaluation harness, so you finish with a number rather than a hope.</p>
    <div class="spec">{spec_html}</div>
  </header>

  <div class="gauge">
    <div class="gauge-row">
      <span class="gauge-read" id="readout">00 / {n - 1}</span>
      <span class="scale" id="scale" role="group" aria-label="Chapter progress"></span>
      <button type="button" class="btn-plain" id="resetBtn">Reset</button>
    </div>
    <p id="storageNote" hidden></p>
  </div>

  <div class="reader">
    <div class="rail">
      <button type="button" class="toc-toggle" id="tocToggle" aria-expanded="false" aria-controls="toc">Manifest</button>
      <nav class="toc" id="toc" aria-label="Chapters"></nav>
    </div>

    <main id="main">
      {"".join(articles)}

      <div class="chapter-foot" id="chapterFoot">
        <button type="button" class="btn btn-done" id="doneBtn">Mark as done</button>
        <span class="spacer"></span>
        <button type="button" class="btn" id="prevBtn">&larr; Prev</button>
        <button type="button" class="btn" id="nextBtn">Next &rarr;</button>
      </div>

      <div id="allDone" hidden>
        <p class="label">Every chapter done</p>
        <p>You have a working retrieval system, a number that says how well it retrieves, and the reasoning
        behind every decision in it. The last thing left is the one this guide cannot do for you: point it at
        your own documents and see what breaks.</p>
      </div>
    </main>
  </div>

  <footer>
    <p class="label">Measure retrieval, then ship</p>
    <p class="label">{files} files &middot; {n - 1} chapters</p>
  </footer>
</div>

<script>{JS}</script>
"""
