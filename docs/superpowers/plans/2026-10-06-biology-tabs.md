# Biology Tabs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add Cells, Blood, Nervous System and Skeleton tabs to the website, each with clickable SVG diagrams that explain every part.

**Architecture:** One page with a tab bar. A hash-based router in a new `docs/topics.js` shows either the existing periodic table or a shared, data-driven diagram viewer. Each topic is a JSON text file in `docs/topics/` plus SVG drawings in `docs/diagrams/`; clickable regions are `<g data-part="id">` groups matched to JSON entries. A pytest contract test keeps drawings and text in sync.

**Tech Stack:** Plain HTML, CSS and JavaScript (classic scripts, no modules, no build step). Python 3 + pytest for the contract test (standard library only).

**Spec:** `docs/superpowers/specs/2026-10-06-biology-tabs-design.md`

## Global Constraints

- Website only: change nothing outside `docs/`, `tests/test_topics.py` and `README.md`.
- No frameworks, no build step, no new runtime dependencies, no third-party images.
- Tab hashes are exactly `#table`, `#cells`, `#blood`, `#nervous`, `#skeleton`. No hash or an unknown hash shows the Periodic Table.
- Reading level: between middle school and high school. Plain words, define any technical term the first time it appears. No clinical ranges beyond the counts listed in this plan.
- Every part has: `name`, one-sentence `summary`, `details` of 40–120 words, and 2–5 `facts`.
- SVG contract: has a `viewBox`; no `width`/`height` on the root; every clickable part is a `<g data-part="id">`; `data-part` groups are never nested inside each other; the same id may appear on several sibling groups; a part's label and leader line sit inside its group; no `<script>`, `<image>`, `<foreignObject>`, event attributes or external links.
- Responsive breakpoint is the site's existing `900px`.
- The Periodic Table tab must behave exactly as before.
- Work on branch `biology-tabs`. Do not push; pushing is a separate step the owner decides on.

## Review Focus

There is no JavaScript test runner in this project and the spec forbids adding dependencies, so these are pinned by explicit browser checks in the owning task rather than automated tests.

1. **Unknown or malformed hash** (`#foo`, `#cells/x`, `#CELLS`): the Periodic Table is shown, no error. Owner: Task 1, Step 9.
2. **Leaving the table mid-quiz or with a modal open:** the quiz timer stops, the panel and modals close, and on return a grid click opens element details, not a quiz answer. Owner: Task 1, Step 9.
3. **A topic or diagram file fails to load** (missing file, offline): a "Couldn't load this diagram" message with a working Retry button; tabs and the table keep working. Owner: Task 2, Step 7.
4. **Fast switching between tabs/diagrams while one is still loading:** the last one clicked is what ends up on screen. Owner: Task 2, Step 7.
5. **Phone width (375px):** the info panel stacks under the diagram, part buttons wrap, nothing scrolls sideways, and every part is still selectable via its button even when its drawn label is tiny. Owner: Tasks 2–6, browser-check steps.

## File Structure

| File | Responsibility |
|---|---|
| `docs/index.html` (modify) | Tab bar; wrap table controls and grid so they can be hidden; empty topic view skeleton |
| `docs/style.css` (modify) | Tab bar, topic layout, part highlight/selection styles |
| `docs/app.js` (modify) | One new function, `closeTableOverlays()` |
| `docs/topics.js` (create) | Tab router and the shared diagram viewer |
| `docs/topics/<topic>.json` (create ×4) | All text for one topic |
| `docs/diagrams/<diagram>.svg` (create ×10) | One drawing each |
| `tests/test_topics.py` (create) | Contract between `index.html`, topic JSON and SVG files |
| `README.md` (modify) | Describe the website and how to add a topic |

## Local setup (used by every task)

The contract test uses only the standard library, so it runs on the system Python even though the desktop app needs 3.10+.

```bash
python3 -m venv .venv
.venv/bin/pip install pytest
```

Run the contract test: `.venv/bin/pytest tests/test_topics.py -v`

Serve the site for browser checks (it uses `fetch`, so opening the file directly will not work):

```bash
python3 -m http.server 8000 --directory docs
```

Then open `http://localhost:8000/`.

---

### Task 1: Contract test and tab shell

**Files:**
- Create: `tests/test_topics.py`
- Create: `docs/topics.js`
- Modify: `docs/index.html` (header and `<main>`)
- Modify: `docs/style.css` (append)
- Modify: `docs/app.js` (add one function after `resetQuizUi`)

**Interfaces:**
- Produces: global `closeTableOverlays(): void` in `app.js`.
- Produces: in `topics.js`, `showTab(id: string): void`, `tabFromHash(): string`, and a call site `showTopic(id)` that Task 2 defines. In this task `showTopic` is a stub that clears the topic view.
- Produces: DOM ids `tabs`, `table-controls`, `table-view`, `topic-view`, `diagram-switcher`, `diagram-holder`, `part-buttons`, `info-panel`.

- [ ] **Step 1: Create the venv** (commands in "Local setup").

- [ ] **Step 2: Write the contract test**

Create `tests/test_topics.py`:

```python
"""Contract tests for the website's biology tabs.

Checks that docs/index.html, docs/topics/*.json and docs/diagrams/*.svg
agree with each other. Standard library only.
"""
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

DOCS = Path(__file__).resolve().parent.parent / "docs"
TOPIC_FILES = sorted((DOCS / "topics").glob("*.json"))
SVG = "{http://www.w3.org/2000/svg}"
ID_RE = re.compile(r"^[a-z][a-z0-9-]*$")
FORBIDDEN_TAGS = {"script", "image", "foreignObject"}


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def text_ok(value):
    return isinstance(value, str) and value.strip() != ""


def local(tag):
    return tag.split("}")[-1]


def test_tabs_match_topic_files():
    html = (DOCS / "index.html").read_text(encoding="utf-8")
    tabs = re.findall(r'data-tab="([^"]+)"', html)
    assert tabs, "index.html has no tab buttons"
    assert tabs[0] == "table"
    assert len(tabs) == len(set(tabs)), "duplicate tab"
    assert set(tabs[1:]) == {p.stem for p in TOPIC_FILES}


@pytest.mark.parametrize("path", TOPIC_FILES, ids=lambda p: p.stem)
def test_topic_shape(path):
    topic = load(path)
    assert topic["id"] == path.stem
    assert text_ok(topic["title"])
    assert topic["parts"], "topic has no parts"
    for part_id, part in topic["parts"].items():
        assert ID_RE.match(part_id), part_id
        assert text_ok(part["name"]), part_id
        assert text_ok(part["summary"]), part_id
        words = len(part["details"].split())
        assert 40 <= words <= 120, f"{part_id}: details has {words} words"
        assert 2 <= len(part["facts"]) <= 5, part_id
        assert all(text_ok(f) for f in part["facts"]), part_id
    assert topic["diagrams"], "topic has no diagrams"
    ids = [d["id"] for d in topic["diagrams"]]
    assert len(ids) == len(set(ids)), "duplicate diagram id"
    for d in topic["diagrams"]:
        assert ID_RE.match(d["id"]), d["id"]
        assert text_ok(d["title"]) and text_ok(d["intro"]), d["id"]
        assert d["svg"] == f"diagrams/{d['id']}.svg"
        assert d["parts"], d["id"]
        assert len(d["parts"]) == len(set(d["parts"])), d["id"]
        for part_id in d["parts"]:
            assert part_id in topic["parts"], f"{d['id']}: unknown part {part_id}"


@pytest.mark.parametrize("path", TOPIC_FILES, ids=lambda p: p.stem)
def test_no_unused_parts(path):
    topic = load(path)
    used = {p for d in topic["diagrams"] for p in d["parts"]}
    assert used == set(topic["parts"])


def nested_parts(el, inside=False):
    """Yield data-part ids that sit inside another data-part group."""
    here = el.get("data-part")
    if here and inside:
        yield here
    for child in el:
        yield from nested_parts(child, inside or bool(here))


@pytest.mark.parametrize("path", TOPIC_FILES, ids=lambda p: p.stem)
def test_diagram_svgs_follow_contract(path):
    topic = load(path)
    for d in topic["diagrams"]:
        svg_path = DOCS / d["svg"]
        assert svg_path.is_file(), d["svg"]
        root = ET.parse(svg_path).getroot()
        assert root.tag == SVG + "svg", d["svg"]
        assert root.get("viewBox"), f"{d['svg']}: missing viewBox"
        assert root.get("width") is None and root.get("height") is None, d["svg"]
        for el in root.iter():
            assert local(el.tag) not in FORBIDDEN_TAGS, f"{d['svg']}: <{local(el.tag)}>"
            for name, value in el.attrib.items():
                assert not local(name).startswith("on"), f"{d['svg']}: {name}"
                if local(name) == "href":
                    assert value.startswith("#"), f"{d['svg']}: external href"
        drawn = {el.get("data-part") for el in root.iter() if el.get("data-part")}
        assert drawn == set(d["parts"]), (
            f"{d['svg']}: only in drawing {sorted(drawn - set(d['parts']))}, "
            f"only in JSON {sorted(set(d['parts']) - drawn)}"
        )
        assert list(nested_parts(root)) == [], f"{d['svg']}: nested data-part"


def test_every_svg_file_is_used():
    used = {d["svg"] for p in TOPIC_FILES for d in load(p)["diagrams"]}
    on_disk = {f"diagrams/{p.name}" for p in (DOCS / "diagrams").glob("*.svg")}
    assert on_disk == used
```

- [ ] **Step 3: Run it and confirm it fails**

Run: `.venv/bin/pytest tests/test_topics.py -v`
Expected: `test_tabs_match_topic_files` FAILS with "index.html has no tab buttons". The parametrized tests are skipped (no topic files yet). `test_every_svg_file_is_used` passes.

- [ ] **Step 4: Restructure `docs/index.html`**

Replace the whole `<header>…</header>` and `<main>…</main>` (lines 10–28) with:

```html
  <header>
    <h1>Periodic Table of Elements</h1>
    <nav id="tabs" class="tabs" role="tablist" aria-label="Sections">
      <button type="button" role="tab" data-tab="table" aria-selected="true">Periodic Table</button>
    </nav>
    <div id="table-controls">
      <div class="toolbar">
        <input id="search" type="text" placeholder="Search by symbol, name, or atomic number…" autocomplete="off">
        <button id="quiz-btn">Quiz</button>
        <span class="hint">Shift+click two elements to compare.</span>
      </div>
      <div class="timeline">
        <label for="year">Show elements known by:</label>
        <input id="year" type="range" min="1600" max="2025" value="2025">
        <span id="year-label">2025</span>
        <button id="year-reset">Reset</button>
      </div>
    </div>
  </header>

  <main id="table-view">
    <div id="grid" aria-label="Periodic table grid"></div>
    <div id="legend" aria-label="Category legend"></div>
  </main>

  <main id="topic-view" hidden>
    <div id="diagram-switcher" class="diagram-switcher" role="group" aria-label="Diagrams"></div>
    <div class="topic-layout">
      <section class="diagram-col">
        <div id="diagram-holder" class="diagram-holder"></div>
        <div id="part-buttons" class="part-buttons" role="group" aria-label="Parts of this diagram"></div>
      </section>
      <aside id="info-panel" class="info-panel" aria-live="polite"></aside>
    </div>
  </main>
```

And at the bottom, load the new script after `app.js`:

```html
  <script src="app.js"></script>
  <script src="topics.js"></script>
```

The `table-controls` wrapper matters: `.toolbar` and `.timeline` are `display: flex`, which would override the `hidden` attribute if it were set on them directly.

- [ ] **Step 5: Add `closeTableOverlays` to `docs/app.js`**

Insert directly after the `resetQuizUi` function:

```js
// Called by topics.js when the user leaves the Periodic Table tab.
function closeTableOverlays() {
  for (const modal of document.querySelectorAll(".modal")) {
    modal.hidden = true;
  }
  document.getElementById("quiz-panel").hidden = true;
  if (state.quiz.timerId) cancelAnimationFrame(state.quiz.timerId);
  state.quiz.startedAt = null;
  state.quiz.handlerActive = false;
  state.quiz.target = null;
  resetQuizUi();
}
```

- [ ] **Step 6: Create `docs/topics.js` with the router**

```js
"use strict";

// --- tab router ------------------------------------------------------------

const TABLE_TAB = "table";

function tabButtons() {
  return [...document.querySelectorAll("#tabs [data-tab]")];
}

function tabFromHash() {
  const id = location.hash.replace(/^#/, "");
  return tabButtons().some(b => b.dataset.tab === id) ? id : TABLE_TAB;
}

function showTab(id) {
  for (const btn of tabButtons()) {
    btn.setAttribute("aria-selected", String(btn.dataset.tab === id));
  }
  const isTable = id === TABLE_TAB;
  document.getElementById("table-controls").hidden = !isTable;
  document.getElementById("table-view").hidden = !isTable;
  document.getElementById("topic-view").hidden = isTable;
  if (isTable) return;
  closeTableOverlays();
  showTopic(id);
}

function wireTabs() {
  for (const btn of tabButtons()) {
    btn.addEventListener("click", () => { location.hash = btn.dataset.tab; });
  }
  window.addEventListener("hashchange", () => showTab(tabFromHash()));
  showTab(tabFromHash());
}

// --- diagram viewer --------------------------------------------------------

function showTopic(id) {
  document.getElementById("diagram-holder").replaceChildren();
}

wireTabs();
```

- [ ] **Step 7: Append tab styles to `docs/style.css`**

Put the `[hidden]` rule near the top (after the `* { box-sizing … }` rule) and the rest before the `@media (max-width: 900px)` block:

```css
[hidden] { display: none !important; }
```

```css
.tabs {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
  margin-bottom: 10px;
  border-bottom: 1px solid var(--border);
}

.tabs button {
  background: transparent;
  color: var(--muted);
  border-radius: 6px 6px 0 0;
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
}

.tabs button[aria-selected="true"] {
  color: var(--accent);
  border-bottom-color: var(--accent);
  font-weight: 600;
}
```

- [ ] **Step 8: Run the test and confirm it passes**

Run: `.venv/bin/pytest tests/test_topics.py -v`
Expected: `test_tabs_match_topic_files` PASSES (one tab, `table`; zero topic files).

- [ ] **Step 9: Browser check**

Serve the site and open `http://localhost:8000/`. Confirm:
- The table, search, timeline, Shift+click compare, element detail, Show atom and Quiz all work as before. No console errors.
- `#foo`, `#cells/x` and `#CELLS` in the address bar all show the Periodic Table.
- Start a quiz round, then run `showTab("cells")` in the console: the table and its controls disappear and the quiz panel closes. Run `showTab("table")`: the table returns, the quiz panel is closed, and clicking an element opens its detail modal (not counted as a quiz answer). Reopening Quiz shows "Press Start" and `0.0 s`.

- [ ] **Step 10: Commit**

```bash
git add tests/test_topics.py docs/index.html docs/style.css docs/app.js docs/topics.js
git commit -m "feat(web): add tab bar, hash router and topic contract test"
```

---

### Task 2: Diagram viewer and the animal cell

**Files:**
- Modify: `docs/topics.js` (replace the `showTopic` stub)
- Modify: `docs/style.css` (append)
- Modify: `docs/index.html` (add Cells tab button)
- Create: `docs/topics/cells.json`
- Create: `docs/diagrams/animal-cell.svg`

**Interfaces:**
- Consumes: DOM ids and `showTab` from Task 1.
- Produces: `showTopic(id: string, diagramId?: string): Promise<void>`. Later tasks add data files only and never touch `topics.js`.
- Produces: the topic JSON shape and SVG contract (see Global Constraints) that Tasks 3–6 follow.

- [ ] **Step 1: Add the Cells tab button** to `#tabs` in `docs/index.html`:

```html
      <button type="button" role="tab" data-tab="cells" aria-selected="false">Cells</button>
```

- [ ] **Step 2: Run the test and confirm it fails**

Run: `.venv/bin/pytest tests/test_topics.py -v`
Expected: `test_tabs_match_topic_files` FAILS (tab `cells` has no topic file).

- [ ] **Step 3: Write `docs/topics/cells.json`**

Shape:

```json
{
  "id": "cells",
  "title": "Cells",
  "parts": {
    "cell-membrane": {
      "name": "Cell membrane",
      "summary": "The thin, flexible skin that surrounds the cell.",
      "details": "…40–120 words…",
      "facts": ["…", "…"]
    }
  },
  "diagrams": [
    {
      "id": "animal-cell",
      "title": "Animal cell",
      "intro": "Animal cells have no rigid wall, so they are soft and come in many shapes. Each part inside, called an organelle, has its own job.",
      "svg": "diagrams/animal-cell.svg",
      "parts": ["cell-membrane", "cytoplasm", "nucleus", "nucleolus", "mitochondria", "ribosomes", "rough-er", "smooth-er", "golgi", "lysosomes", "centrioles", "cytoskeleton", "vesicles"]
    }
  ]
}
```

Write all 13 parts. Each entry must cover these points, in plain language:

| id | name | Must cover |
|---|---|---|
| `cell-membrane` | Cell membrane | Double layer of fat molecules (phospholipids) with proteins in it; controls what enters and leaves ("selectively permeable"); lets the cell sense signals |
| `cytoplasm` | Cytoplasm | Jelly-like fluid, mostly water, filling the cell; organelles float in it; many chemical reactions happen here |
| `nucleus` | Nucleus | Control centre; holds DNA (46 chromosomes in a human cell); wrapped in a double membrane with pores; sends instructions out as RNA |
| `nucleolus` | Nucleolus | Dense spot inside the nucleus; builds the pieces of ribosomes |
| `mitochondria` | Mitochondria | Release energy from glucose using oxygen (cellular respiration) and store it as ATP; folded inner membrane; have their own DNA; busy cells such as muscle have thousands |
| `ribosomes` | Ribosomes | Tiny protein-building machines; join amino acids following RNA instructions; float free or sit on rough ER; no membrane |
| `rough-er` | Rough endoplasmic reticulum | Folded membranes dotted with ribosomes; folds and transports new proteins; joined to the nucleus membrane |
| `smooth-er` | Smooth endoplasmic reticulum | No ribosomes; makes fats (lipids); breaks down toxins, so liver cells have a lot |
| `golgi` | Golgi apparatus | Stack of flattened sacs; finishes, sorts and packages proteins into vesicles; the cell's "post office" |
| `lysosomes` | Lysosomes | Sacs of digestive enzymes; break down worn-out parts, food and germs; the recycling crew; mostly in animal cells |
| `centrioles` | Centrioles | A pair of tiny tube bundles near the nucleus; organise the fibres that pull chromosomes apart when the cell divides; found in animal cells |
| `cytoskeleton` | Cytoskeleton | Network of protein fibres; gives shape, lets the cell move, and acts as tracks for moving things around |
| `vesicles` | Vesicles | Small membrane bubbles; carry materials between organelles and to the cell membrane for release |

- [ ] **Step 4: Draw `docs/diagrams/animal-cell.svg`**

Conventions for every diagram in this project:
- Root: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600" font-family="sans-serif">` (portrait diagrams use `0 0 500 800`).
- Outlines `stroke="#333" stroke-width="2"`; fills are soft, distinct colours per part.
- Each part: `<g data-part="id"> shapes… <line …leader/> <text font-size="18">Label</text> </g>`. Labels go in the margins with a thin leader line (`stroke="#555" stroke-width="1"`) to the part. No label may overlap another label or a different part.
- Parts are siblings, never nested. Draw the background part first so smaller parts sit on top and receive clicks.

Animal cell layout: a rounded, slightly irregular cell filling the middle (leave ~130px margins left and right for labels).
- `cytoplasm`: the pale yellow interior fill.
- `cell-membrane`: a thick tan outline ring on top of the cytoplasm edge (stroke only, `fill="none"`, `stroke-width="8"`).
- `nucleus`: large lavender circle left of centre with a dashed darker outline (pores).
- `nucleolus`: small dark purple circle drawn after the nucleus, as a sibling.
- `rough-er`: blue folded bands hugging the nucleus, with small dots along them.
- `smooth-er`: teal tubes without dots, further out.
- `golgi`: 4–5 stacked curved orange bands on the right, a few small circles beside it.
- `vesicles`: several small light-orange circles between the Golgi and the membrane (multiple groups share the id).
- `mitochondria`: three red-orange capsules with a zig-zag line inside (three sibling groups; only one carries the label).
- `lysosomes`: three small solid green circles.
- `ribosomes`: clusters of tiny dark dots in the cytoplasm.
- `centrioles`: two short striped cylinders at right angles near the nucleus.
- `cytoskeleton`: thin grey lines crossing the cytoplasm, drawn right after the cytoplasm so they sit behind the organelles.

- [ ] **Step 5: Replace the `showTopic` stub in `docs/topics.js`**

Replace everything from the `// --- diagram viewer` comment down to (not including) `wireTabs();` with:

```js
// --- diagram viewer --------------------------------------------------------

const viewer = {
  topics: new Map(),   // topic id -> parsed JSON
  svgs: new Map(),     // svg path -> SVG source text
  topic: null,
  diagram: null,
  partId: null,
  loadToken: 0,        // lets the newest request win
};

async function fetchText(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`${url}: HTTP ${res.status}`);
  return res.text();
}

async function showTopic(id, diagramId) {
  const token = ++viewer.loadToken;
  try {
    if (!viewer.topics.has(id)) {
      viewer.topics.set(id, JSON.parse(await fetchText(`topics/${id}.json`)));
    }
    const topic = viewer.topics.get(id);
    const diagram = topic.diagrams.find(d => d.id === diagramId) || topic.diagrams[0];
    if (!viewer.svgs.has(diagram.svg)) {
      viewer.svgs.set(diagram.svg, await fetchText(diagram.svg));
    }
    if (token !== viewer.loadToken) return;
    viewer.topic = topic;
    viewer.diagram = diagram;
    viewer.partId = null;
    renderDiagram();
    renderSwitcher();
    renderPartButtons();
    renderInfo();
  } catch (err) {
    if (token !== viewer.loadToken) return;
    console.error(err);
    renderLoadError(() => showTopic(id, diagramId));
  }
}

function el(tag, text, className) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
}

function renderSwitcher() {
  const box = document.getElementById("diagram-switcher");
  const { topic, diagram } = viewer;
  box.replaceChildren();
  box.hidden = topic.diagrams.length < 2;
  for (const d of topic.diagrams) {
    const btn = el("button", d.title, "switch-btn");
    btn.type = "button";
    btn.setAttribute("aria-pressed", String(d.id === diagram.id));
    btn.addEventListener("click", () => showTopic(topic.id, d.id));
    box.appendChild(btn);
  }
}

function renderDiagram() {
  const holder = document.getElementById("diagram-holder");
  const doc = new DOMParser().parseFromString(
    viewer.svgs.get(viewer.diagram.svg), "image/svg+xml");
  if (doc.documentElement.nodeName !== "svg") {
    throw new Error(`${viewer.diagram.svg} is not a valid SVG`);
  }
  const svg = document.adoptNode(doc.documentElement);
  svg.setAttribute("role", "group");
  svg.setAttribute("aria-label", viewer.diagram.title);
  holder.classList.remove("has-selection");
  holder.replaceChildren(svg);

  const focusable = new Set();
  for (const g of svg.querySelectorAll("[data-part]")) {
    const id = g.dataset.part;
    const part = viewer.topic.parts[id];
    if (!part) continue;   // unknown ids are ignored rather than fatal
    g.classList.add("part");
    g.addEventListener("click", () => selectPart(id));
    g.addEventListener("mouseenter", () => setHover(id, true));
    g.addEventListener("mouseleave", () => setHover(id, false));
    if (focusable.has(id)) continue;   // one keyboard stop per part
    focusable.add(id);
    g.setAttribute("tabindex", "0");
    g.setAttribute("role", "button");
    g.setAttribute("aria-label", part.name);
    g.addEventListener("keydown", ev => {
      if (ev.key !== "Enter" && ev.key !== " ") return;
      ev.preventDefault();
      selectPart(id);
    });
  }
}

function partGroups(id) {
  return [...document.querySelectorAll("#diagram-holder [data-part]")]
    .filter(g => g.dataset.part === id);
}

function setHover(id, on) {
  for (const g of partGroups(id)) g.classList.toggle("hover", on);
}

function renderPartButtons() {
  const box = document.getElementById("part-buttons");
  box.replaceChildren();
  for (const id of viewer.diagram.parts) {
    const btn = el("button", viewer.topic.parts[id].name);
    btn.type = "button";
    btn.dataset.part = id;
    btn.setAttribute("aria-pressed", "false");
    btn.addEventListener("click", () => selectPart(id));
    btn.addEventListener("mouseenter", () => setHover(id, true));
    btn.addEventListener("mouseleave", () => setHover(id, false));
    box.appendChild(btn);
  }
}

function selectPart(id) {
  viewer.partId = id;
  const holder = document.getElementById("diagram-holder");
  holder.classList.add("has-selection");
  for (const g of holder.querySelectorAll("[data-part]")) {
    g.classList.toggle("selected", g.dataset.part === id);
  }
  for (const btn of document.querySelectorAll("#part-buttons button")) {
    btn.setAttribute("aria-pressed", String(btn.dataset.part === id));
  }
  renderInfo();
}

function renderInfo() {
  const panel = document.getElementById("info-panel");
  const { topic, diagram, partId } = viewer;
  panel.replaceChildren();
  const part = partId ? topic.parts[partId] : null;
  if (!part) {
    panel.append(
      el("h2", diagram.title),
      el("p", diagram.intro),
      el("p", "Click a part of the diagram, or one of the names below it, to learn about it.", "muted"),
    );
    return;
  }
  const facts = el("ul");
  for (const fact of part.facts) facts.appendChild(el("li", fact));
  panel.append(
    el("h2", part.name),
    el("p", part.summary, "summary"),
    el("p", part.details),
    el("h3", "Key facts"),
    facts,
  );
}

function renderLoadError(retry) {
  document.getElementById("diagram-switcher").hidden = true;
  document.getElementById("part-buttons").replaceChildren();
  document.getElementById("info-panel").replaceChildren();
  const btn = el("button", "Retry");
  btn.type = "button";
  btn.addEventListener("click", retry);
  const holder = document.getElementById("diagram-holder");
  holder.classList.remove("has-selection");
  holder.replaceChildren(el("p", "Couldn't load this diagram."), btn);
}
```

- [ ] **Step 6: Append viewer styles to `docs/style.css`**

Before the `@media (max-width: 900px)` block:

```css
#topic-view { max-width: 1400px; margin: 0 auto; }

.diagram-switcher {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.switch-btn,
.part-buttons button {
  background: var(--card-bg);
  color: var(--text);
  border: 1px solid var(--border);
}

.switch-btn[aria-pressed="true"],
.part-buttons button[aria-pressed="true"] {
  background: var(--accent);
  color: var(--accent-fg);
  border-color: var(--accent);
}

.topic-layout {
  display: grid;
  grid-template-columns: minmax(0, 3fr) minmax(260px, 2fr);
  gap: 20px;
  align-items: start;
}

.diagram-holder {
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 12px;
}

.diagram-holder svg {
  display: block;
  width: 100%;
  height: auto;
  max-height: 72vh;
}

.part {
  cursor: pointer;
  outline: none;
  transition: opacity 120ms ease;
}

.part.hover,
.part:focus-visible {
  filter: brightness(1.1) drop-shadow(0 0 3px rgba(44, 109, 240, 0.9));
}

.has-selection .part:not(.selected) { opacity: 0.35; }

.part.selected { filter: drop-shadow(0 0 4px rgba(44, 109, 240, 1)); }

.part-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 12px;
}

.part-buttons button { padding: 5px 10px; font-size: 13px; }

.info-panel {
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 18px 20px;
  font-size: 15px;
  line-height: 1.5;
}

.info-panel h2 { margin: 0 0 6px 0; font-size: 20px; }
.info-panel h3 { margin: 14px 0 4px 0; font-size: 14px; }
.info-panel p { margin: 0 0 10px 0; }
.info-panel .summary { font-weight: 600; }
.info-panel .muted { color: var(--muted); }
.info-panel ul { margin: 0; padding-left: 20px; }
```

Inside the existing `@media (max-width: 900px)` block add:

```css
  .topic-layout { grid-template-columns: 1fr; }
```

- [ ] **Step 7: Run the test, then browser check**

Run: `.venv/bin/pytest tests/test_topics.py -v`
Expected: all PASS.

In the browser at `http://localhost:8000/#cells`:
- The animal cell shows with an intro in the panel. No diagram switcher (only one diagram so far).
- Click each of the 13 parts on the drawing, then each of the 13 buttons: the right part highlights, the rest dim, and the panel shows name, summary, paragraph and key facts. Clicking a label works too.
- Tab to a part with the keyboard and press Enter and Space: both select it.
- Back and forward buttons move between `#cells` and the table.
- Temporarily rename `docs/topics/cells.json`, reload `#cells`: "Couldn't load this diagram." with Retry. Rename it back and click Retry: the diagram loads. The Periodic Table tab works throughout.
- In DevTools, throttle the network to "Slow 3G", click Cells then immediately Periodic Table then Cells again: the final screen is the Cells diagram with no error.
- At 375px wide: the panel sits under the diagram, part buttons wrap, no sideways scrolling.

- [ ] **Step 8: Commit**

```bash
git add docs/index.html docs/style.css docs/topics.js docs/topics/cells.json docs/diagrams/animal-cell.svg
git commit -m "feat(web): add diagram viewer and animal cell"
```

---

### Task 3: Plant cell

**Files:**
- Modify: `docs/topics/cells.json`
- Create: `docs/diagrams/plant-cell.svg`

**Interfaces:**
- Consumes: the topic JSON shape and SVG contract from Task 2. No JavaScript or CSS changes.

- [ ] **Step 1: Add the diagram entry and three new parts to `cells.json`**

Append to `diagrams`:

```json
{
  "id": "plant-cell",
  "title": "Plant cell",
  "intro": "Plant cells have three things animal cells lack: a stiff cell wall, green chloroplasts that make food from sunlight, and one large central vacuole.",
  "svg": "diagrams/plant-cell.svg",
  "parts": ["cell-wall", "cell-membrane", "cytoplasm", "nucleus", "nucleolus", "chloroplasts", "central-vacuole", "mitochondria", "ribosomes", "rough-er", "smooth-er", "golgi"]
}
```

Add to `parts`:

| id | name | Must cover |
|---|---|---|
| `cell-wall` | Cell wall | Stiff outer layer made of cellulose, outside the membrane; gives support and a fixed shape; lets water through; animal cells have none |
| `chloroplasts` | Chloroplasts | Where photosynthesis happens; chlorophyll makes them green and traps light; light + carbon dioxide + water → glucose + oxygen; have their own DNA |
| `central-vacuole` | Central vacuole | Large water-filled sac, up to about 90% of the cell's volume; stores water, nutrients and waste; its pressure keeps the plant firm, and plants wilt when it shrinks |

- [ ] **Step 2: Run the test and confirm it fails**

Run: `.venv/bin/pytest tests/test_topics.py -v`
Expected: `test_diagram_svgs_follow_contract[cells]` FAILS (`diagrams/plant-cell.svg` missing).

- [ ] **Step 3: Draw `docs/diagrams/plant-cell.svg`**

`viewBox="0 0 800 600"`, same conventions as Task 2. Layout: a boxy, rounded-rectangle cell.
- `cell-wall`: thick green outer rectangle outline (`stroke-width="14"`, `fill="none"`).
- `cell-membrane`: thin tan outline just inside the wall.
- `cytoplasm`: pale yellow fill, drawn first.
- `central-vacuole`: large pale blue rounded shape taking up most of the centre-right.
- `nucleus` and `nucleolus`: pushed to the upper left, same colours as the animal cell.
- `chloroplasts`: four or five green ovals with darker stacked lines inside, around the edge.
- `mitochondria`, `rough-er`, `smooth-er`, `golgi`, `ribosomes`: same colours and style as the animal cell, fitted into the space around the vacuole.

- [ ] **Step 4: Run the test, then browser check**

Run: `.venv/bin/pytest tests/test_topics.py -v` — expected: all PASS.

At `#cells`: an "Animal cell | Plant cell" switcher appears. Switching clears the selection and shows the new intro. Click all 12 plant-cell parts and buttons. Shared parts (for example mitochondria) show the same text in both diagrams. Check 375px width.

- [ ] **Step 5: Commit**

```bash
git add docs/topics/cells.json docs/diagrams/plant-cell.svg
git commit -m "feat(web): add plant cell diagram"
```

- [ ] **Step 6: REVIEW CHECKPOINT — stop here**

Show the owner the Cells tab (both diagrams, desktop and phone width). Get their approval of the drawing style and level of written detail, and apply any changes they ask for, before starting Task 4.

---

### Task 4: Blood tab

**Files:**
- Modify: `docs/index.html` (add tab button)
- Create: `docs/topics/blood.json`
- Create: `docs/diagrams/blood-vessel.svg`, `docs/diagrams/blood-tube.svg`, `docs/diagrams/white-cell-types.svg`

**Interfaces:**
- Consumes: the topic JSON shape and SVG contract from Task 2.

- [ ] **Step 1: Add the tab button** after Cells in `#tabs`:

```html
      <button type="button" role="tab" data-tab="blood" aria-selected="false">Blood</button>
```

- [ ] **Step 2: Run the test and confirm it fails**

Run: `.venv/bin/pytest tests/test_topics.py -v`
Expected: `test_tabs_match_topic_files` FAILS.

- [ ] **Step 3: Write `docs/topics/blood.json`** (`"id": "blood"`, `"title": "Blood"`)

Diagrams:

| id | title | parts | intro must say |
|---|---|---|---|
| `blood-vessel` | Blood in a vessel | `vessel-wall`, `plasma`, `red-blood-cells`, `white-blood-cells`, `platelets` | Blood is a liquid tissue: cells floating in plasma. An adult has about 5 litres |
| `blood-tube` | Spun tube | `plasma`, `buffy-coat`, `red-blood-cells` | Spinning blood very fast in a tube (a centrifuge) separates it into layers by weight |
| `white-cell-types` | White blood cell types | `neutrophil`, `lymphocyte`, `monocyte`, `eosinophil`, `basophil` | There are five main kinds of white blood cell, told apart under a microscope by the shape of the nucleus and the grains inside |

Parts:

| id | name | Must cover |
|---|---|---|
| `vessel-wall` | Blood vessel wall | The tube that carries blood; arteries carry blood away from the heart, veins carry it back, and capillaries are tiny vessels one cell thick where exchange with tissues happens |
| `plasma` | Plasma | Pale yellow liquid, about 55% of blood, about 90% water; carries nutrients, hormones, waste, carbon dioxide and proteins such as antibodies and clotting proteins |
| `red-blood-cells` | Red blood cells | Carry oxygen from the lungs using haemoglobin, an iron-containing protein that makes blood red; disc shape dented on both sides; no nucleus; about 45% of blood; about 5 million in a drop the size of a pinhead (one cubic millimetre); made in red bone marrow; last about 120 days |
| `white-blood-cells` | White blood cells | Defend the body against germs; have a nucleus; far fewer than red cells (roughly 1 for every 600–700); made in bone marrow; five main types (point to the third diagram) |
| `platelets` | Platelets | Small fragments of larger bone-marrow cells, not whole cells; clump at a cut and help form a clot to stop bleeding; last about 8–10 days |
| `buffy-coat` | Buffy coat | Thin whitish layer between plasma and red cells; less than 1% of blood; contains the white blood cells and platelets |
| `neutrophil` | Neutrophil | Most common white cell (about 50–70%); nucleus with several lobes; first to arrive at an infection; swallows bacteria (phagocytosis); short-lived; dead neutrophils are a main part of pus |
| `lymphocyte` | Lymphocyte | About 20–40% of white cells; large round nucleus filling most of the cell; B cells make antibodies, T cells kill infected cells and direct the response; memory cells are why vaccines work |
| `monocyte` | Monocyte | Largest white cell; about 2–8%; kidney-bean-shaped nucleus; moves into tissues and becomes a macrophage that swallows germs and dead cells |
| `eosinophil` | Eosinophil | About 1–4%; two-lobed nucleus and pink-red grains; attacks parasites such as worms; involved in allergies and asthma |
| `basophil` | Basophil | Rarest, under 1%; packed with dark blue-purple grains; releases histamine, which causes the swelling and itching of an allergic reaction |

- [ ] **Step 4: Draw the three SVGs** (`viewBox="0 0 800 600"`)

`blood-vessel.svg`: a horizontal vessel cut open lengthwise.
- `vessel-wall`: two thick pink-red bands along the top and bottom.
- `plasma`: pale yellow fill between them, drawn first.
- `red-blood-cells`: about ten red discs with a darker centre dimple, at varied angles (sibling groups, one labelled).
- `white-blood-cells`: two larger off-white circles with a purple lobed nucleus.
- `platelets`: several small irregular purple-tan flecks.

`blood-tube.svg`: a tall test tube centred, with three labelled layers and a percentage beside each. Keep the label text inside each part's group.
- `plasma`: top 55%, pale yellow.
- `buffy-coat`: a thin off-white band (draw it about 12px tall so it can be clicked).
- `red-blood-cells`: bottom 45%, dark red.

`white-cell-types.svg`: five cells in a row, each a pale circle about 110px across with its name underneath (inside the group).
- `neutrophil`: nucleus of 3–4 connected purple lobes, fine pale grains.
- `lymphocyte`: slightly smaller cell, one large round dark purple nucleus leaving a thin rim.
- `monocyte`: largest cell, kidney-shaped nucleus.
- `eosinophil`: two-lobed nucleus, many pink-red dots.
- `basophil`: many dark blue-purple dots partly covering the nucleus.

- [ ] **Step 5: Run the test, then browser check**

Run: `.venv/bin/pytest tests/test_topics.py -v` — expected: all PASS.

At `#blood`: three-way switcher; click every part and button in each diagram; `plasma` and `red-blood-cells` show the same text in the vessel and the tube. Confirm the thin buffy coat band is clickable. Check 375px width.

- [ ] **Step 6: Commit**

```bash
git add docs/index.html docs/topics/blood.json docs/diagrams/blood-vessel.svg docs/diagrams/blood-tube.svg docs/diagrams/white-cell-types.svg
git commit -m "feat(web): add Blood tab"
```

---

### Task 5: Nervous System tab

**Files:**
- Modify: `docs/index.html` (add tab button)
- Create: `docs/topics/nervous.json`
- Create: `docs/diagrams/nervous-body.svg`, `docs/diagrams/neuron.svg`, `docs/diagrams/brain.svg`

**Interfaces:**
- Consumes: the topic JSON shape and SVG contract from Task 2.

- [ ] **Step 1: Add the tab button** after Blood:

```html
      <button type="button" role="tab" data-tab="nervous" aria-selected="false">Nervous System</button>
```

- [ ] **Step 2: Run the test and confirm it fails**

Run: `.venv/bin/pytest tests/test_topics.py -v`
Expected: `test_tabs_match_topic_files` FAILS.

- [ ] **Step 3: Write `docs/topics/nervous.json`** (`"id": "nervous"`, `"title": "Nervous System"`)

Diagrams:

| id | title | parts | intro must say |
|---|---|---|---|
| `nervous-body` | Body overview | `brain`, `spinal-cord`, `cranial-nerves`, `peripheral-nerves` | Two divisions: the central nervous system (brain and spinal cord) and the peripheral nervous system (all the nerves branching out to the body) |
| `neuron` | Neuron | `dendrites`, `cell-body`, `neuron-nucleus`, `axon`, `myelin-sheath`, `nodes-of-ranvier`, `axon-terminals`, `synapse` | A neuron is a nerve cell; signals travel one way, in through the dendrites and out along the axon |
| `brain` | Brain regions | `frontal-lobe`, `parietal-lobe`, `temporal-lobe`, `occipital-lobe`, `cerebellum`, `brainstem` | The large wrinkled part (cerebrum) is divided into four lobes; the cerebellum and brainstem sit below it. Side view, front of the head on the left |

Parts:

| id | name | Must cover |
|---|---|---|
| `brain` | Brain | Control centre; about 86 billion neurons; about 1.4 kg in an adult; protected by the skull; uses about a fifth of the body's energy |
| `spinal-cord` | Spinal cord | Thick bundle of nerve tissue running inside the backbone, about 45 cm long in adults; carries messages between brain and body; handles quick reflexes on its own |
| `cranial-nerves` | Cranial nerves | 12 pairs that come straight from the brain; serve the head and neck (sight, smell, hearing, taste, face movement); the vagus nerve reaches the heart and gut |
| `peripheral-nerves` | Spinal and peripheral nerves | 31 pairs of spinal nerves branch from the spinal cord to the whole body; sensory nerves carry information in, motor nerves carry commands out to muscles |
| `dendrites` | Dendrites | Short branching fibres that receive signals from other neurons; more branches means more connections |
| `cell-body` | Cell body | Also called the soma; holds the nucleus and most organelles; adds up incoming signals and decides whether to fire |
| `neuron-nucleus` | Nucleus | Holds the neuron's DNA and directs its activity; most neurons do not divide, so they must last a lifetime |
| `axon` | Axon | Single long fibre carrying the electrical signal away from the cell body; the longest run about a metre, from the base of the spine to the toes |
| `myelin-sheath` | Myelin sheath | Fatty insulating wrapping around the axon; makes signals much faster, up to about 120 metres per second; gives "white matter" its colour |
| `nodes-of-ranvier` | Nodes of Ranvier | Small gaps between sections of myelin; the signal jumps from gap to gap, which is what speeds it up |
| `axon-terminals` | Axon terminals | Branched ends of the axon; release chemical messengers called neurotransmitters |
| `synapse` | Synapse | Tiny gap between one neuron and the next cell; neurotransmitters cross it and fit into receptors on the other side; a single neuron can have thousands |
| `frontal-lobe` | Frontal lobe | Thinking, planning, decisions, personality, self-control; starts voluntary movement; helps produce speech; last part to finish maturing, in the mid-twenties |
| `parietal-lobe` | Parietal lobe | Processes touch, temperature and pain; awareness of where the body is in space |
| `temporal-lobe` | Temporal lobe | Hearing, understanding language, and forming memories (the hippocampus lies deep inside it) |
| `occipital-lobe` | Occipital lobe | Vision: turns signals from the eyes into the images you see; at the back of the head |
| `cerebellum` | Cerebellum | "Little brain"; balance, posture and smooth, coordinated movement; about a tenth of the brain's volume but more than half its neurons |
| `brainstem` | Brainstem | Connects the brain to the spinal cord; controls automatic functions: breathing, heartbeat, swallowing, sleep and wakefulness |

- [ ] **Step 4: Draw the three SVGs**

`nervous-body.svg` (`viewBox="0 0 500 800"`): a simple grey front-facing body silhouette (not a part), with the nervous system in yellow-orange on top.
- `brain`: pink wrinkled oval in the head.
- `spinal-cord`: thick orange line from the head to the lower back.
- `cranial-nerves`: a few short yellow lines from the brain to the face and neck.
- `peripheral-nerves`: yellow branching lines from the spinal cord down both arms and both legs to hands and feet, plus a few across the trunk.

`neuron.svg` (`viewBox="0 0 800 600"`): cell body on the left, axon running right.
- `cell-body`: lavender blob.
- `neuron-nucleus`: darker circle inside, drawn after it as a sibling.
- `dendrites`: branching tapered lines from the cell body (one group).
- `axon`: a long line from cell body to terminals, drawn before the myelin.
- `myelin-sheath`: five yellow rounded sausages along the axon (one group).
- `nodes-of-ranvier`: small transparent-fill rectangles with a dark outline over each gap between the sausages (so the gaps are clickable).
- `axon-terminals`: branches ending in small bulbs on the right.
- `synapse`: at the far right, one bulb facing a small piece of the next cell with a few dots in the gap.

`brain.svg` (`viewBox="0 0 800 600"`): side view, front on the left. Four lobes as adjoining coloured regions of one wrinkled dome: `frontal-lobe` (blue, front), `parietal-lobe` (yellow, top back), `temporal-lobe` (green, lower middle), `occipital-lobe` (red-pink, back). `cerebellum`: striped purple oval under the back. `brainstem`: tan stalk going down from the centre.

- [ ] **Step 5: Run the test, then browser check**

Run: `.venv/bin/pytest tests/test_topics.py -v` — expected: all PASS.

At `#nervous`: three-way switcher; click every part and button in each diagram. Confirm the thin nerve lines and the nodes of Ranvier can be clicked directly, and that their buttons work. Check 375px width.

- [ ] **Step 6: Commit**

```bash
git add docs/index.html docs/topics/nervous.json docs/diagrams/nervous-body.svg docs/diagrams/neuron.svg docs/diagrams/brain.svg
git commit -m "feat(web): add Nervous System tab"
```

---

### Task 6: Skeleton tab

**Files:**
- Modify: `docs/index.html` (add tab button)
- Create: `docs/topics/skeleton.json`
- Create: `docs/diagrams/skeleton.svg`, `docs/diagrams/long-bone.svg`

**Interfaces:**
- Consumes: the topic JSON shape and SVG contract from Task 2.

- [ ] **Step 1: Add the tab button** after Nervous System:

```html
      <button type="button" role="tab" data-tab="skeleton" aria-selected="false">Skeleton</button>
```

- [ ] **Step 2: Run the test and confirm it fails**

Run: `.venv/bin/pytest tests/test_topics.py -v`
Expected: `test_tabs_match_topic_files` FAILS.

- [ ] **Step 3: Write `docs/topics/skeleton.json`** (`"id": "skeleton"`, `"title": "Skeleton"`)

Diagrams:

| id | title | parts | intro must say |
|---|---|---|---|
| `skeleton` | Full skeleton | `skull`, `mandible`, `clavicle`, `scapula`, `sternum`, `ribs`, `spine`, `humerus`, `radius`, `ulna`, `hand-bones`, `pelvis`, `femur`, `patella`, `tibia`, `fibula`, `foot-bones` | An adult has 206 bones. They support the body, protect organs, let muscles move you, store minerals and make blood cells |
| `long-bone` | Inside a long bone | `periosteum`, `compact-bone`, `spongy-bone`, `red-marrow`, `yellow-marrow`, `articular-cartilage`, `growth-plate`, `bone-blood-vessels` | Bone is living tissue. This is a long bone such as the femur, cut open lengthwise to show its layers |

Parts:

| id | name | Must cover |
|---|---|---|
| `skull` | Skull | 22 bones; 8 form the case around the brain and 14 form the face; joined by immovable joints called sutures |
| `mandible` | Jaw (mandible) | Lower jaw; the only skull bone that moves; holds the lower teeth; used for chewing and speaking |
| `clavicle` | Collarbone (clavicle) | Links the breastbone to the shoulder blade; holds the shoulder out from the body; one of the most often broken bones |
| `scapula` | Shoulder blade (scapula) | Flat triangular bone on the upper back; forms the shoulder socket; many arm and back muscles attach to it |
| `sternum` | Breastbone (sternum) | Flat bone down the centre of the chest; ribs join it through flexible cartilage; shields the heart |
| `ribs` | Ribs | 12 pairs forming a cage around the heart and lungs; the top 7 pairs attach directly to the breastbone, the last 2 pairs are "floating"; they lift and fall as you breathe |
| `spine` | Spine | 33 vertebrae: 24 separate ones plus 9 fused at the base (sacrum and tailbone); protects the spinal cord; cushioning discs between vertebrae; gentle S-shaped curve absorbs shock |
| `humerus` | Humerus | Upper arm bone, shoulder to elbow; ball at the top fits the shoulder socket |
| `radius` | Radius | Forearm bone on the thumb side; rotates around the ulna so you can turn your palm up and down |
| `ulna` | Ulna | Forearm bone on the little-finger side; its top end is the point of the elbow |
| `hand-bones` | Hand bones | 27 in each hand: 8 wrist bones (carpals), 5 palm bones (metacarpals), 14 finger bones (phalanges) |
| `pelvis` | Pelvis | Hip bones forming a bowl; carries the weight of the upper body to the legs; protects the bladder and intestines; holds the hip sockets |
| `femur` | Femur | Thigh bone; the longest and strongest bone, about a quarter of a person's height |
| `patella` | Kneecap (patella) | Small bone set inside a tendon in front of the knee; protects the joint and gives the thigh muscles better leverage |
| `tibia` | Tibia | Shinbone; the larger lower-leg bone; carries most of the body's weight |
| `fibula` | Fibula | Thin bone on the outer side of the lower leg; carries little weight; anchors muscles and steadies the ankle |
| `foot-bones` | Foot bones | 26 in each foot: 7 ankle bones (tarsals), 5 metatarsals, 14 toe bones (phalanges); arches absorb shock |
| `periosteum` | Periosteum | Thin, tough membrane covering the outside of the bone; rich in nerves and blood vessels; contains cells that grow and repair bone |
| `compact-bone` | Compact bone | Dense, hard outer layer that gives bone its strength; made of collagen fibres hardened with calcium minerals, arranged in tiny tubes |
| `spongy-bone` | Spongy bone | Honeycomb-like lattice inside the ends of the bone; light but strong; its spaces hold red marrow |
| `red-marrow` | Red marrow | Soft tissue that makes red cells, white cells and platelets, hundreds of billions every day; in adults mostly in the pelvis, ribs, breastbone, spine and the ends of the long bones |
| `yellow-marrow` | Yellow marrow | Fatty tissue filling the hollow shaft (the medullary cavity); an energy store; can turn back into red marrow after severe blood loss |
| `articular-cartilage` | Articular cartilage | Smooth, slippery cap on the bone ends at a joint; reduces friction and cushions impact; has no blood supply, so it heals slowly |
| `growth-plate` | Growth plate | Disc of cartilage near each end of a child's bone where new bone is added, making it longer; hardens into bone in the late teens, when growth in height stops |
| `bone-blood-vessels` | Blood vessels | Enter the bone through small holes; bring oxygen and nutrients to bone cells and carry new blood cells out of the marrow |

- [ ] **Step 4: Draw the two SVGs**

`skeleton.svg` (`viewBox="0 0 500 800"`): front-facing, arms slightly out, simplified off-white bones with `#333` outlines. Labels alternate left and right margins so 17 labels do not collide; use `font-size="15"` here.
- `skull`: rounded cranium with eye sockets. `mandible`: separate jaw shape below it.
- `spine`: a column of small stacked rounded rectangles from skull to pelvis, drawn first so ribs sit on top.
- `ribs`: curved pairs on both sides (one group). `sternum`: narrow vertical plate in the centre, drawn after the ribs.
- `clavicle`: two near-horizontal bars from the sternum top to the shoulders (one group). `scapula`: two triangles behind the upper ribs, drawn before the ribs but offset outward so part of each is visible and clickable.
- `humerus`, `radius`, `ulna`: both arms, each bone a long rounded shape with knobs at the ends; radius on the thumb (outer) side.
- `hand-bones`: a cluster of small wrist shapes plus five lines of finger segments per hand.
- `pelvis`: butterfly shape at the base of the spine.
- `femur`, `tibia`, `fibula`: both legs; fibula thin and on the outer side. `patella`: small circle over each knee, drawn after the leg bones.
- `foot-bones`: a wedge of small shapes per foot.
- Paired bones (left and right) are separate sibling groups sharing one id; only one carries the label.

`long-bone.svg` (`viewBox="0 0 800 600"`): a bone lying horizontally, cut lengthwise.
- `periosteum`: thin pink outline around the shaft, with one section drawn peeled back so it is easy to click.
- `compact-bone`: thick cream band forming the wall of the shaft.
- `yellow-marrow`: yellow fill in the hollow centre of the shaft.
- `spongy-bone`: cross-hatched lattice filling both knobbly ends.
- `red-marrow`: red patches within the lattice spaces at both ends (drawn after the spongy bone, as siblings).
- `growth-plate`: a thin pale blue curved band across each end where the knob meets the shaft.
- `articular-cartilage`: light blue cap over each end.
- `bone-blood-vessels`: a red and a blue line entering through the shaft wall and branching in the marrow.

- [ ] **Step 5: Run the test, then browser check**

Run: `.venv/bin/pytest tests/test_topics.py -v` — expected: all PASS.

At `#skeleton`: two-way switcher; click every part and button in both diagrams. Hovering one femur highlights both. Confirm thin parts (fibula, growth plate, periosteum, blood vessels) are clickable directly. Check 375px width: the tall skeleton fits within the screen height (`max-height: 72vh`) and all 17 buttons wrap.

- [ ] **Step 6: Commit**

```bash
git add docs/index.html docs/topics/skeleton.json docs/diagrams/skeleton.svg docs/diagrams/long-bone.svg
git commit -m "feat(web): add Skeleton tab"
```

---

### Task 7: README and full regression pass

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Add a Website section to `README.md`** after the "Tests" section:

````markdown
## Website

A browser version lives in `docs/` and is published with GitHub Pages. As
well as the periodic table it has Cells, Blood, Nervous System and Skeleton
tabs with clickable diagrams.

Preview it locally:

```bash
python3 -m http.server 8000 --directory docs
```

Then open http://localhost:8000/.

### Adding a topic

1. Draw each diagram as an SVG in `docs/diagrams/`. Wrap every clickable
   part in `<g data-part="some-id">`.
2. Write `docs/topics/<topic>.json` with the text for each part and the
   list of diagrams.
3. Add a tab button with `data-tab="<topic>"` to `docs/index.html`.
4. Run `pytest tests/test_topics.py`; it checks the drawings and text match.
````

- [ ] **Step 2: Run the contract test**

Run: `.venv/bin/pytest tests/test_topics.py -v`
Expected: all PASS, with parametrized cases for `blood`, `cells`, `nervous`, `skeleton`.

- [ ] **Step 3: Full browser regression**

At desktop width and at 375px:
- Periodic Table: search, timeline slider and Reset, Shift+click compare, element detail, Show atom, Quiz (start, wrong answer, right answer, skip, drag the panel, close).
- Each of the four biology tabs: every diagram loads, switcher works, one part selected per diagram.
- Hash links `#table`, `#cells`, `#blood`, `#nervous`, `#skeleton` each open the right tab on a fresh page load; back and forward work.
- No console errors or failed network requests anywhere.

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs: describe the website and how to add a topic"
```
