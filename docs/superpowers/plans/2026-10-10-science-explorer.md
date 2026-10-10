# Science Explorer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the website into "Science Explorer": a home page with three subject cards, a trail and topic row in place of the tab bar, and eight new clickable-diagram topics (20 SVG diagrams).

**Architecture:** Still one static page. A new data file, `docs/site.json`, lists subjects and topics. A new script, `docs/site.js`, owns the hash router, the home cards and the header navigation, and calls the existing `showTopic(id)` in `docs/topics.js`, which keeps only the diagram viewer. New topics are data only: one JSON file plus SVG files each, and one entry in `site.json`.

**Tech Stack:** Plain HTML, CSS and JavaScript (no build step, no dependencies). `pytest` with the standard library for contract tests.

**Spec:** `docs/superpowers/specs/2026-10-10-science-explorer-design.md`. The SVG and topic-file contract comes from `docs/superpowers/specs/2026-10-06-biology-tabs-design.md`.

## Global Constraints

- Website only: change nothing outside `docs/`, `tests/test_topics.py`, `tests/test_site.py` and `README.md`. `docs/app.js` is not changed.
- No build step, no frameworks, no new dependencies, no third-party images.
- Script order in `index.html`: `app.js`, `topics.js`, `site.js`.
- Page ids: `home` and `table` are reserved. `table` is the built-in periodic table and has no topic file.
- Subject colours: Chemistry `#2c6df0`, Human Body & Cells `#c0392b`, Physics `#7d4fc4`. Used for the card stripe and the subject name in the trail only.
- Breakpoint: 900px, the site's existing one.
- A topic's `title` in `site.json` equals the `title` in its topic file.
- A topic is added to `site.json` only in the task that adds its files.
- Topic contract: parts defined once per topic and referenced by id; each part has `name`, `summary`, a 40–120 word `details` paragraph and 2–5 `facts`; each diagram has `id`, `title`, `intro`, `svg` (`diagrams/<id>.svg`) and `parts`. Ids are lowercase with hyphens.
- SVG contract: a `viewBox` and no `width`/`height`; every clickable part in a `<g data-part="…">`; labels inside their part's group; no nested parts; no scripts, no external references, no raster images.
- Audience: between middle school and high school. Plain language, no college-level mechanisms, well-established school science only.
- Existing links `#table`, `#cells`, `#blood`, `#nervous`, `#skeleton` keep working. No hash or an unknown hash shows Home.

## Review Focus

Behaviour the spec implies but the pytest suite cannot reach (it does not run JavaScript). Each is pinned by a browser check in Task 1, Step 9.

1. A hash that is not a topic but is an object property name (`#constructor`, `#__proto__`, `#toString`), or is empty (`#`), shows Home rather than a broken page. The router looks ids up in a `Map`, never in a plain object.
2. Leaving the table with the browser Back button while the quiz panel or a modal is open closes them; they must not float over Home or a diagram.
3. Clicking two topic links quickly (the first still loading) ends on the second topic, with the trail, the current-topic mark, the browser title and the diagram all agreeing.
4. `site.json` failing to load and then succeeding on Retry leaves a working site with one `hashchange` handler, not two.
5. At phone width with eight topics in the row, the current topic is scrolled into view in the row and the header stays one row tall. Opening the site does not steal keyboard focus; only a later page change moves it.

## File Structure

| File | Responsibility |
|---|---|
| `docs/site.json` (create) | Site map: title, subjects, topics. Data only |
| `docs/site.js` (create) | Loads the site map; hash router; home cards; trail and topic row; title and focus |
| `docs/topics.js` (modify) | Diagram viewer only. Router code removed |
| `docs/index.html` (modify) | New heading, `#topic-nav`, `#page-heading`, `#home-view`; tab bar removed |
| `docs/style.css` (modify) | Home cards, trail, topic row; `.tabs` rules removed |
| `docs/topics/<topic>.json` (create ×8) | Text for one topic |
| `docs/diagrams/<diagram>.svg` (create ×20) | One drawing each |
| `tests/test_site.py` (create) | Contract between `site.json`, `index.html` and `docs/topics/` |
| `tests/test_topics.py` (modify) | `test_tabs_match_topic_files` removed |
| `README.md` (modify) | Website section |

## Local setup (used by every task)

The contract tests use only the standard library, so they run on the project's `.venv` (Python 3.9) even though the desktop app needs 3.10+. Run only the two website test files:

```bash
.venv/bin/pytest tests/test_topics.py tests/test_site.py -v
```

Serve the site for browser checks (it uses `fetch`, so opening the file directly will not work):

```bash
python3 -m http.server 8000 --directory docs
```

Then open `http://localhost:8000/`.

Work on a branch: `git switch -c science-explorer`.

## Drawing conventions (used by every diagram task)

Match the existing diagrams so the new ones read as the same set:

- Root: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600" font-family="sans-serif">` unless the task gives another `viewBox`.
- Outlines `stroke="#333" stroke-width="2"`; flat colour fills.
- Labels: `<text font-size="16" text-anchor="middle" fill="#1f2024">` joined to the part by `<line stroke="#555" stroke-width="1">`. Both sit inside the part's `<g data-part>`.
- A part drawn in several places is several sibling groups with the same `data-part`; only one carries the label.
- Thin parts (lines, arrows) get a second, transparent, wider stroke (`stroke="#000" stroke-opacity="0" stroke-width="12"`) so they are easy to click.
- Draw big background parts first so smaller parts on top stay clickable. Never put one `data-part` group inside another.
- Blood colours: oxygen-rich `#d62828`, oxygen-poor `#2b6cb0`.

After drawing, look at every diagram in the browser. Labels must not overlap each other or the drawing, and every part must be clickable.

---

### Task 1: Frame

**Files:**
- Create: `tests/test_site.py`, `docs/site.json`, `docs/site.js`
- Modify: `tests/test_topics.py`, `docs/index.html`, `docs/topics.js`, `docs/style.css`

**Interfaces:**
- Consumes: `closeTableOverlays()` from `docs/app.js`; `showTopic(id)`, `el(tag, text, className)` from `docs/topics.js`.
- Produces: `docs/site.json` in the shape below. Later tasks add subjects and topics to it and touch no JavaScript or HTML.

- [ ] **Step 1: Write the failing test.** Create `tests/test_site.py`:

```python
"""Contract tests for the website's site map.

Checks that docs/site.json, docs/index.html and docs/topics/*.json agree
with each other. Standard library only.
"""
import json
import re
from pathlib import Path

DOCS = Path(__file__).resolve().parent.parent / "docs"
ID_RE = re.compile(r"^[a-z][a-z0-9-]*$")
COLOR_RE = re.compile(r"^#[0-9a-f]{6}$")
TABLE = "table"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def text_ok(value):
    return isinstance(value, str) and value.strip() != ""


def site():
    return load(DOCS / "site.json")


def topic_entries():
    return [t for s in site()["subjects"] for t in s["topics"]]


def test_site_has_title_and_subjects():
    data = site()
    assert text_ok(data["title"])
    assert data["subjects"], "site.json has no subjects"


def test_subjects_are_well_formed():
    subjects = site()["subjects"]
    ids = [s["id"] for s in subjects]
    assert len(ids) == len(set(ids)), "duplicate subject id"
    for s in subjects:
        assert ID_RE.match(s["id"]), s["id"]
        assert text_ok(s["title"]), s["id"]
        assert text_ok(s["blurb"]), s["id"]
        assert COLOR_RE.match(s["color"]), f"{s['id']}: colour {s['color']!r}"
        assert s["topics"], f"{s['id']}: no topics"
        for t in s["topics"]:
            assert ID_RE.match(t["id"]), t["id"]
            assert text_ok(t["title"]), t["id"]


def test_topic_ids_are_unique_and_not_reserved():
    ids = [t["id"] for t in topic_entries()]
    assert len(ids) == len(set(ids)), "duplicate topic id"
    assert "home" not in ids, "'home' is reserved"


def test_site_map_matches_topic_files():
    ids = [t["id"] for t in topic_entries()]
    assert ids.count(TABLE) == 1, "'table' must be listed exactly once"
    on_disk = {p.stem for p in (DOCS / "topics").glob("*.json")}
    assert set(ids) - {TABLE} == on_disk


def test_site_map_titles_match_topic_files():
    for t in topic_entries():
        if t["id"] == TABLE:
            continue
        topic = load(DOCS / "topics" / f"{t['id']}.json")
        assert t["title"] == topic["title"], t["id"]


def test_index_has_views_and_no_tabs():
    html = (DOCS / "index.html").read_text(encoding="utf-8")
    for element_id in ("home-view", "table-view", "topic-view", "topic-nav"):
        assert f'id="{element_id}"' in html, element_id
    assert "data-tab" not in html, "old tab buttons are still in index.html"
```

- [ ] **Step 2: Run it and confirm it fails**

Run: `.venv/bin/pytest tests/test_site.py -v`
Expected: every test FAILS or ERRORS (`site.json` does not exist; `index.html` has `data-tab`).

- [ ] **Step 3: Create `docs/site.json`**

```json
{
  "title": "Science Explorer",
  "subjects": [
    {
      "id": "chemistry",
      "title": "Chemistry",
      "blurb": "The elements that everything is made of, and how they are arranged.",
      "color": "#2c6df0",
      "topics": [
        { "id": "table", "title": "Periodic Table" }
      ]
    },
    {
      "id": "body",
      "title": "Human Body & Cells",
      "blurb": "How your body is built and how it works, from single cells to whole systems.",
      "color": "#c0392b",
      "topics": [
        { "id": "cells", "title": "Cells" },
        { "id": "blood", "title": "Blood" },
        { "id": "nervous", "title": "Nervous System" },
        { "id": "skeleton", "title": "Skeleton" }
      ]
    }
  ]
}
```

- [ ] **Step 4: Edit `docs/index.html`**

Change `<title>` to `Science Explorer`. Replace the whole `<header>…</header>` and add the two elements after it, so the top of `<body>` reads:

```html
  <header>
    <h1>Science Explorer</h1>
    <nav id="topic-nav" aria-label="Topics" hidden>
      <p class="trail">
        <a href="#home">⌂ Home</a>
        <span aria-hidden="true">›</span>
        <span id="trail-subject"></span>
      </p>
      <div id="topic-row" class="topic-row"></div>
    </nav>
    <div id="table-controls" hidden>
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

  <!-- Names the current page for screen readers; site.js moves focus here. -->
  <h2 id="page-heading" class="sr-only" tabindex="-1">Home</h2>

  <main id="home-view"></main>

  <main id="table-view" hidden>
```

(`#table-view` gains `hidden`; its contents and everything below are unchanged.) Add the third script at the bottom:

```html
  <script src="app.js"></script>
  <script src="topics.js"></script>
  <script src="site.js"></script>
```

The spec asks for focus to move to "the page's main heading". The visible `<h1>` is the site name and is the same on every page, so the page's own heading is `#page-heading`: hidden visually, read by screen readers, and the element focus moves to.

- [ ] **Step 5: Remove the router from `docs/topics.js`**

Delete everything from the line `// --- tab router ---…` down to (not including) `// --- diagram viewer ---…`, and delete the last line, `wireTabs();`. The file now starts:

```js
"use strict";

// --- diagram viewer --------------------------------------------------------
```

- [ ] **Step 6: Create `docs/site.js`**

```js
"use strict";

// Router, home page and header navigation. Uses el() and showTopic() from
// topics.js and closeTableOverlays() from app.js.

const HOME_PAGE = "home";
const TABLE_PAGE = "table";

const site = {
  map: null,           // parsed site.json
  pages: new Map(),    // topic id -> { topic, subject }
};

async function loadSite() {
  try {
    const res = await fetch("site.json");
    if (!res.ok) throw new Error(`site.json: HTTP ${res.status}`);
    site.map = await res.json();
  } catch (err) {
    console.error(err);
    renderSiteError();
    return;
  }
  for (const subject of site.map.subjects) {
    for (const topic of subject.topics) site.pages.set(topic.id, { topic, subject });
  }
  renderHome();
  window.addEventListener("hashchange", () => showPage(true));
  showPage(false);   // opening the site must not steal focus
}

function renderSiteError() {
  const btn = el("button", "Retry");
  btn.type = "button";
  btn.addEventListener("click", loadSite);
  document.getElementById("home-view")
    .replaceChildren(el("p", "Couldn't load the site."), btn);
}

function topicLink(topic) {
  const a = el("a", topic.title);
  a.href = `#${topic.id}`;
  return a;
}

function renderHome() {
  const cards = el("div", undefined, "home-cards");
  for (const subject of site.map.subjects) {
    const card = el("section", undefined, "subject-card");
    card.style.setProperty("--subject", subject.color);
    const links = el("ul");
    for (const topic of subject.topics) {
      const item = el("li");
      item.appendChild(topicLink(topic));
      links.appendChild(item);
    }
    card.append(el("h2", subject.title), el("p", subject.blurb), links);
    cards.appendChild(card);
  }
  document.getElementById("home-view").replaceChildren(cards);
}

function pageFromHash() {
  const id = location.hash.replace(/^#/, "");
  return site.pages.has(id) ? id : HOME_PAGE;
}

function showPage(moveFocus) {
  const id = pageFromHash();
  const page = site.pages.get(id);   // undefined on Home
  const isTable = id === TABLE_PAGE;
  const isDiagram = Boolean(page) && !isTable;

  document.getElementById("home-view").hidden = Boolean(page);
  document.getElementById("table-view").hidden = !isTable;
  document.getElementById("table-controls").hidden = !isTable;
  document.getElementById("topic-view").hidden = !isDiagram;
  if (!isTable) closeTableOverlays();

  renderNav(page);
  const heading = document.getElementById("page-heading");
  heading.textContent = page ? page.topic.title : "Home";
  document.title = page ? `${page.topic.title} – ${site.map.title}` : site.map.title;

  if (isDiagram) showTopic(id);
  if (moveFocus) {
    window.scrollTo(0, 0);
    heading.focus();
  }
}

function renderNav(page) {
  document.getElementById("topic-nav").hidden = !page;
  if (!page) return;
  const { subject, topic } = page;
  const name = document.getElementById("trail-subject");
  name.textContent = subject.title;
  name.style.color = subject.color;

  const row = document.getElementById("topic-row");
  row.replaceChildren();
  row.hidden = subject.topics.length < 2;
  for (const t of subject.topics) {
    const a = topicLink(t);
    if (t.id === topic.id) a.setAttribute("aria-current", "page");
    row.appendChild(a);
  }
  // Below 900px the row scrolls sideways; keep the current topic in sight.
  const current = row.querySelector("[aria-current]");
  if (current) current.scrollIntoView({ block: "nearest", inline: "nearest" });
}

loadSite();
```

- [ ] **Step 7: Edit `docs/style.css`**

Delete the three `.tabs` rules (`.tabs`, `.tabs button`, `.tabs button[aria-selected="true"]`). In their place add:

```css
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  margin: -1px;
  overflow: hidden;
  clip-path: inset(50%);
  white-space: nowrap;
}

.trail { margin: 0 0 8px 0; }
.trail a { color: var(--accent); text-decoration: none; }
.trail a:hover { text-decoration: underline; }
#trail-subject { font-weight: 600; }

.topic-row {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
  margin-bottom: 10px;
  border-bottom: 1px solid var(--border);
}

.topic-row a {
  padding: 8px 14px;
  color: var(--muted);
  text-decoration: none;
  white-space: nowrap;
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
}

.topic-row a:hover { color: var(--text); }

.topic-row a[aria-current="page"] {
  color: var(--accent);
  border-bottom-color: var(--accent);
  font-weight: 600;
}

#home-view { max-width: 1400px; margin: 0 auto; }

.home-cards {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 20px;
  align-items: start;
}

.subject-card {
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-top: 6px solid var(--subject);
  border-radius: 8px;
  padding: 18px 20px;
}

.subject-card h2 { margin: 0 0 6px 0; font-size: 20px; }
.subject-card p { margin: 0 0 14px 0; color: var(--muted); font-size: 15px; }

.subject-card ul {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.subject-card a {
  display: inline-block;
  padding: 8px 14px;
  border: 1px solid var(--border);
  border-radius: 6px;
  color: var(--text);
  text-decoration: none;
  font-size: 15px;
}

.subject-card a:hover { border-color: var(--accent); color: var(--accent); }
```

Inside the existing `@media (max-width: 900px)` block add:

```css
  .home-cards { grid-template-columns: 1fr; }
  .topic-row { flex-wrap: nowrap; overflow-x: auto; }
  .topic-row a { margin-bottom: 0; }
```

- [ ] **Step 8: Remove the old tab test and run the suite**

In `tests/test_topics.py` delete `test_tabs_match_topic_files` (and change the module docstring's first line to `"""Contract tests for the website's diagram topics.`).

Run: `.venv/bin/pytest tests/test_topics.py tests/test_site.py -v`
Expected: all PASS.

- [ ] **Step 9: Browser checks** (desktop width, then 375px wide)

- No hash: Home with two cards (Chemistry, Human Body & Cells), title "Science Explorer", no trail, no table controls.
- Every home link opens its topic; trail reads "⌂ Home › Human Body & Cells" with the subject in red; the topic row marks the current topic; title is e.g. "Blood – Science Explorer".
- `#table`: trail "⌂ Home › Chemistry" in blue, no topic row, table controls shown. Search, timeline, element detail, atom view, compare and quiz all still work.
- Back and forward move between pages.
- Review Focus 1: `#constructor`, `#__proto__`, `#toString`, `#` and `#nope` all show Home.
- Review Focus 2: on `#table` open the quiz and an element detail, press Back: neither is visible on Home.
- Review Focus 3: run `location.hash = "cells"; location.hash = "skeleton";` in the console: ends on Skeleton with trail, row, title and diagram agreeing.
- Review Focus 4: block `site.json` (rename it, reload): "Couldn't load the site." and Retry, nothing else. Restore it, click Retry: Home appears; navigating once renders once.
- Review Focus 5: at 375px the topic row is one line and scrolls sideways; after opening the site `document.activeElement` is `<body>`; after a page change it is `#page-heading`.
- Keyboard: Tab reaches the Home link, the topic-row links and the diagram parts; Enter follows links.
- No console errors.

- [ ] **Step 10: Commit**

```bash
git add tests/test_site.py tests/test_topics.py docs/site.json docs/site.js docs/topics.js docs/index.html docs/style.css
git commit -m "feat(web): add Science Explorer home page and site map"
```

**Review checkpoint (spec):** the frame is shown to the user.

---

### Tasks 2–9: one topic each

Every topic task has the same five steps. The tables in each task give the content.

- [ ] **Step 1: Add the topic to `docs/site.json`** (the entry given in the task) and run `.venv/bin/pytest tests/test_site.py -v`. Expected: `test_site_map_matches_topic_files` FAILS, because the topic file does not exist yet.
- [ ] **Step 2: Write `docs/topics/<id>.json`** from the task's tables. Every part's `details` covers the "must cover" points in 40–120 words of plain language; `summary` is one line; `facts` has 2–5 entries that add something the paragraph does not say.
- [ ] **Step 3: Draw the SVGs** following the drawing conventions above and the task's descriptions.
- [ ] **Step 4: Run** `.venv/bin/pytest tests/test_topics.py tests/test_site.py -v` — expected: all PASS. Then check in the browser at desktop and phone width: the home link, the topic row, every diagram, every part clicked from the drawing and from its button, labels not overlapping, no console errors.
- [ ] **Step 5: Commit** `docs/site.json`, the topic file and its SVGs: `git commit -m "feat(web): add <Title> topic"`.

---

### Task 2: Heart

**Files:** Create `docs/topics/heart.json`, `docs/diagrams/heart-inside.svg`, `docs/diagrams/circulation.svg`. Modify `docs/site.json`.

**Site map:** append `{ "id": "heart", "title": "Heart" }` to the `body` subject.

Diagrams:

| id | title | parts | intro must say |
|---|---|---|---|
| `heart-inside` | Inside the heart | `right-atrium`, `right-ventricle`, `left-atrium`, `left-ventricle`, `tricuspid-valve`, `pulmonary-valve`, `mitral-valve`, `aortic-valve`, `septum`, `aorta`, `pulmonary-artery`, `pulmonary-veins`, `venae-cavae` | The heart is a muscular pump about the size of a fist, cut open here to show four chambers and four valves. It is drawn as seen from the front, so the heart's right side is on the left of the picture. Blue means oxygen-poor blood and red oxygen-rich; that is a drawing convention. A simplified diagram, not the true shape |
| `circulation` | The two loops of circulation | `heart`, `lungs`, `body`, `arteries`, `veins`, `capillaries`, `pulmonary-circulation`, `systemic-circulation` | Blood travels in two loops that both start and end at the heart: a short one to the lungs and a long one to the rest of the body. A schematic; real vessels branch everywhere |

Parts:

| id | name | Must cover |
|---|---|---|
| `right-atrium` | Right atrium | Upper right chamber; collects oxygen-poor blood returning from the body through the venae cavae; thin walls because it only pushes blood down into the ventricle; the heart's natural pacemaker sits in its wall |
| `right-ventricle` | Right ventricle | Lower right chamber; pumps oxygen-poor blood through the pulmonary valve to the lungs; wall thinner than the left ventricle's because the lungs are close by |
| `left-atrium` | Left atrium | Upper left chamber; receives oxygen-rich blood from the lungs through the pulmonary veins and passes it to the left ventricle |
| `left-ventricle` | Left ventricle | Lower left chamber with the thickest wall; pumps oxygen-rich blood through the aortic valve to the whole body; its beat is the pulse you feel |
| `tricuspid-valve` | Tricuspid valve | One-way valve between right atrium and right ventricle; three flaps; closes when the ventricle squeezes so blood cannot go back; thin cords stop the flaps turning inside out |
| `pulmonary-valve` | Pulmonary valve | At the exit from the right ventricle into the pulmonary artery; three cup-shaped flaps; stops blood falling back when the ventricle relaxes |
| `mitral-valve` | Mitral valve | Between left atrium and left ventricle; the only valve with two flaps; named after a bishop's hat (mitre); has to hold against the highest pressure |
| `aortic-valve` | Aortic valve | At the exit from the left ventricle into the aorta; three flaps; the "lub-dub" sound is the valves closing: first the two between atria and ventricles, then the two exit valves |
| `septum` | Septum | Muscular wall between the left and right sides; keeps oxygen-rich and oxygen-poor blood apart, so the heart works as two pumps side by side |
| `aorta` | Aorta | The body's largest artery; leaves the left ventricle, arches over the heart and runs down the body; branches carry blood to the head, arms and everywhere else |
| `pulmonary-artery` | Pulmonary artery | Carries blood from the right ventricle to the lungs, splitting into one branch for each lung; an artery because it leads away from the heart, yet it carries oxygen-poor blood, so it is drawn blue |
| `pulmonary-veins` | Pulmonary veins | Four veins, two from each lung, bringing oxygen-rich blood to the left atrium; veins because they lead towards the heart, drawn red |
| `venae-cavae` | Venae cavae | The two largest veins: the upper (superior) one drains the head and arms, the lower (inferior) one the rest of the body; both empty into the right atrium |
| `heart` | Heart | A fist-sized muscle that is two pumps in one; beats about 70 times a minute at rest, around 100,000 times a day; pumps about 5 litres a minute at rest |
| `lungs` | Lungs | Where blood drops off carbon dioxide and picks up oxygen, turning from oxygen-poor to oxygen-rich |
| `body` | Body | Every organ and tissue; cells take oxygen and food from the blood and hand back carbon dioxide and other waste |
| `arteries` | Arteries | Vessels carrying blood away from the heart; thick, stretchy, muscular walls for high pressure; the pulse is an artery wall stretching with each beat |
| `veins` | Veins | Vessels carrying blood back to the heart; thinner walls, lower pressure, one-way valves; muscles squeezing around them help push blood along |
| `capillaries` | Capillaries | The tiniest vessels, linking arteries to veins; walls one cell thick so oxygen, food and waste can pass; found within reach of nearly every cell |
| `pulmonary-circulation` | Lung loop (pulmonary circulation) | Right ventricle → pulmonary artery → lungs → pulmonary veins → left atrium; short, low-pressure loop whose only job is swapping gases |
| `systemic-circulation` | Body loop (systemic circulation) | Left ventricle → aorta → body → venae cavae → right atrium; the long, high-pressure loop; a blood cell goes all the way round both loops in about a minute at rest |

Drawings:

`heart-inside.svg` (`viewBox="0 0 800 600"`): a heart cut open, front view, centred. Labels in two columns at the far left and far right with leader lines.
- Heart outline in a muscle pink; `septum` a darker vertical band down the middle of the lower half.
- Four chambers as coloured cavities: `right-atrium` (upper, picture-left) and `right-ventricle` (lower, picture-left) in blue tints; `left-atrium` and `left-ventricle` (picture-right) in red tints. The left ventricle's surrounding wall is visibly thicker.
- `tricuspid-valve` and `mitral-valve`: pale flap pairs in the gap between each atrium and its ventricle. `pulmonary-valve` and `aortic-valve`: small pale flap pairs at the base of each great artery.
- `aorta`: thick red tube rising from the left ventricle, arching over the top to the picture-right, with three short branches on the arch. `pulmonary-artery`: blue tube rising from the right ventricle, passing in front and forking left and right.
- `venae-cavae`: two blue tubes entering the right atrium, one from above, one from below (sibling groups). `pulmonary-veins`: short red tubes entering the left atrium from the picture-right (and a pair on the left behind the heart, if there is room).
- Small arrows inside the vessels showing flow direction, each inside its vessel's group.

`circulation.svg` (`viewBox="0 0 800 600"`): a figure of eight.
- `heart` in the centre, simplified, blue half on picture-left and red half on picture-right. `lungs` as a rounded pink shape at the top; `body` as a rounded shape at the bottom.
- `arteries`: the two vessels leaving the heart, heart → lungs in blue and heart → body in red, with arrowheads. `veins`: the two vessels returning, lungs → heart in red and body → heart in blue.
- `capillaries`: a fine net of thin lines over the lungs and over the body where blue turns to red (two sibling groups).
- `pulmonary-circulation`: a labelled bracket beside the upper loop. `systemic-circulation`: a labelled bracket beside the lower loop.

**Review checkpoint (spec):** drawing style and level of detail for the body topics are confirmed before Tasks 3–5.

---

### Task 3: Lungs

**Files:** Create `docs/topics/lungs.json`, `docs/diagrams/breathing-system.svg`, `docs/diagrams/air-sac.svg`. Modify `docs/site.json`.

**Site map:** append `{ "id": "lungs", "title": "Lungs" }` to the `body` subject.

Diagrams:

| id | title | parts | intro must say |
|---|---|---|---|
| `breathing-system` | The breathing system | `nose-mouth`, `pharynx`, `larynx`, `trachea`, `bronchi`, `bronchioles`, `lungs`, `diaphragm`, `intercostals` | Breathing brings air deep into the lungs and pushes used air back out, about 12 to 20 times a minute at rest. The airways branch like an upside-down tree. Simplified: the real airways branch more than 20 times |
| `air-sac` | Inside an air sac | `alveolus`, `alveolus-wall`, `capillary`, `red-blood-cell`, `oxygen`, `carbon-dioxide` | One of the hundreds of millions of tiny air sacs at the ends of the airways, hugely magnified. This is where oxygen enters the blood and carbon dioxide leaves it |

Parts:

| id | name | Must cover |
|---|---|---|
| `nose-mouth` | Nose and mouth | Where air enters; hairs and sticky mucus in the nose trap dust and germs; the nose also warms and moistens the air |
| `pharynx` | Throat (pharynx) | Shared passage for air and food; a flap (the epiglottis) covers the windpipe when you swallow |
| `larynx` | Voice box (larynx) | At the top of the windpipe; holds the vocal cords, which vibrate as air passes to make your voice; tighter cords give a higher note |
| `trachea` | Windpipe (trachea) | Tube about 10–12 cm long held open by C-shaped rings of cartilage; lined with mucus and tiny hairs (cilia) that sweep dirt up and out |
| `bronchi` | Bronchi | The two branches of the windpipe, one into each lung; they keep dividing into smaller tubes |
| `bronchioles` | Bronchioles | The finest airways, under 1 mm wide, with no cartilage; end in clusters of air sacs; in asthma the muscle around them tightens |
| `lungs` | Lungs | Two spongy organs filling most of the chest; right lung has three lobes, left has two to leave room for the heart; unfolded, the air sacs would cover roughly half a tennis court |
| `diaphragm` | Diaphragm | Dome-shaped sheet of muscle under the lungs; tightens and flattens to pull air in, relaxes to push it out; the main breathing muscle; hiccups are sudden jerks of it |
| `intercostals` | Rib muscles (intercostals) | Muscles between the ribs; lift the ribcage up and out when you breathe in, making the chest bigger |
| `alveolus` | Air sac (alveolus) | A tiny bag about a fifth of a millimetre across at the end of a bronchiole; hundreds of millions in the lungs; the place where gases are swapped |
| `alveolus-wall` | Air sac wall | Only one cell thick and kept moist; with the capillary wall it makes a barrier far thinner than a hair, so gases cross quickly |
| `capillary` | Capillary | Tiny blood vessel wrapped round the air sac; blood arrives oxygen-poor from the heart and leaves oxygen-rich |
| `red-blood-cell` | Red blood cell | Squeezes through in single file; its haemoglobin grabs oxygen; a cell spends less than a second passing an air sac |
| `oxygen` | Oxygen moving in | Moves from where there is more of it (the air) to where there is less (the blood); this spreading is called diffusion; air is about 21% oxygen |
| `carbon-dioxide` | Carbon dioxide moving out | A waste gas made when cells release energy from food; diffuses from the blood into the air sac and is breathed out; breathed-out air has about 100 times more of it than fresh air |

Drawings:

`breathing-system.svg`: head and chest in outline, front view. `nose-mouth` at the face; `pharynx`, `larynx`, `trachea` as a tube running down the neck (trachea with ring stripes); `bronchi` forking into the two `lungs` (pink, right with three lobes, left with two and a notch); `bronchioles` as fine branching lines inside the lungs, drawn on top of them; `diaphragm` a red-brown dome under both lungs; `intercostals` as short slanted stripes between a few rib arcs at the outer edge of the chest.

`air-sac.svg`: one large round `alveolus` (pale air space) with `alveolus-wall` as a ring of thin cells; a `capillary` tube curving under and round it, shaded blue on the way in and red on the way out; several `red-blood-cell` discs inside it (sibling groups); `oxygen` as red-orange dots with arrows from air to blood; `carbon-dioxide` as grey-blue dots with arrows from blood to air.

---

### Task 4: Digestion

**Files:** Create `docs/topics/digestion.json`, `docs/diagrams/digestive-system.svg`, `docs/diagrams/villi.svg`. Modify `docs/site.json`.

**Site map:** append `{ "id": "digestion", "title": "Digestion" }` to the `body` subject.

Diagrams:

| id | title | parts | intro must say |
|---|---|---|---|
| `digestive-system` | The digestive system | `mouth`, `salivary-glands`, `oesophagus`, `stomach`, `liver`, `gallbladder`, `pancreas`, `small-intestine`, `large-intestine`, `appendix`, `rectum` | Digestion breaks food into pieces small enough to pass into the blood. Food travels through one long tube, about 9 metres from end to end, helped by organs that add digestive juices. The journey takes roughly one to three days. Simplified: the real intestines are tightly coiled |
| `villi` | Inside the small intestine | `villus`, `lining-cells`, `blood-capillaries`, `lacteal`, `muscle-layer` | The inner wall of the small intestine, magnified. It is covered in millions of tiny finger-like villi that soak up digested food |

Parts:

| id | name | Must cover |
|---|---|---|
| `mouth` | Mouth | Teeth cut and grind food; the tongue mixes it with saliva and shapes it into a ball to swallow; digestion begins here |
| `salivary-glands` | Salivary glands | Three pairs of glands making over a litre of saliva a day; saliva wets food and contains an enzyme (amylase) that starts turning starch into sugar |
| `oesophagus` | Oesophagus | Muscular tube about 25 cm long from throat to stomach; waves of squeezing (peristalsis) push food down, so you can swallow even lying down |
| `stomach` | Stomach | Stretchy muscular bag that churns food for a few hours; strong acid kills germs and an enzyme begins breaking down protein; a layer of mucus protects the stomach from its own acid |
| `liver` | Liver | The largest organ inside the body, about 1.5 kg; makes bile; receives the food absorbed from the intestine and processes and stores it; breaks down harmful substances; food does not pass through it |
| `gallbladder` | Gallbladder | Small pouch under the liver that stores bile and squirts it into the small intestine when fatty food arrives; bile breaks fat into tiny droplets |
| `pancreas` | Pancreas | Makes enzymes that digest starch, protein and fat, and a juice that cancels out stomach acid; also makes insulin, the hormone that controls blood sugar |
| `small-intestine` | Small intestine | Narrow tube about 6 metres long; where digestion is finished and nearly all nutrients pass into the blood; "small" refers to its width |
| `large-intestine` | Large intestine | Wider tube about 1.5 metres long; takes back water and salts; home to trillions of helpful bacteria that break down fibre and make some vitamins |
| `appendix` | Appendix | Small finger-shaped pouch at the start of the large intestine; not needed for digestion; may be a shelter for helpful bacteria; can become inflamed (appendicitis) |
| `rectum` | Rectum | The last section of the large intestine; stores solid waste until it leaves the body through the anus |
| `villus` | Villi | Finger-like bumps up to about 1 mm tall; millions of them give the intestine an enormous surface for absorbing food |
| `lining-cells` | Lining cells | A single layer of cells covering each villus; each has its own even tinier folds (microvilli); they take in nutrients and are replaced every few days |
| `blood-capillaries` | Blood capillaries | Net of tiny vessels inside each villus; carry away sugars and amino acids (from protein) to the liver |
| `lacteal` | Lacteal | Tube in the middle of each villus that belongs to the lymph system; takes up digested fat; the fluid looks milky, which gives it its name |
| `muscle-layer` | Muscle layer | Smooth muscle in the intestine wall; squeezes in waves to mix and move food; works without you thinking about it |

Drawings:

`digestive-system.svg`: torso outline with head in side-profile hint, front view. `mouth` at the face with `salivary-glands` as small pale lobes by the jaw; `oesophagus` a tube down the chest; `stomach` a J-shaped bag (picture-right of centre); `liver` a large red-brown wedge (picture-left, partly over the stomach's top); `gallbladder` a small green pear under the liver; `pancreas` a yellow leaf shape behind/below the stomach; `small-intestine` a pink coiled tube in the centre; `large-intestine` a wider tan frame around it (up, across, down); `appendix` a small worm at its lower picture-left start; `rectum` the short straight end at the bottom centre.

`villi.svg`: cross-section of the wall with three or four tall villi. `muscle-layer` a striped band along the bottom; `villus` the finger shapes (body fill); `lining-cells` a row of small cells forming each villus's edge; `blood-capillaries` a red-to-blue loop inside each villus joined to vessels at the base; `lacteal` a green-yellow tube up the middle of each. Label one of each; others are sibling groups.

---

### Task 5: Muscles

**Files:** Create `docs/topics/muscles.json`, `docs/diagrams/major-muscles.svg`, `docs/diagrams/muscle-pair.svg`, `docs/diagrams/muscle-inside.svg`. Modify `docs/site.json`.

**Site map:** append `{ "id": "muscles", "title": "Muscles" }` to the `body` subject.

Diagrams:

| id | title | parts | intro must say |
|---|---|---|---|
| `major-muscles` | Major muscles, front and back | `deltoid`, `pectorals`, `biceps`, `triceps`, `abdominals`, `trapezius`, `lats`, `gluteals`, `quadriceps`, `hamstrings`, `calf` | The body has more than 600 skeletal muscles, the ones you move on purpose. These are some of the biggest, shown from the front and from the back. Simplified shapes |
| `muscle-pair` | Muscles work in pairs | `biceps`, `triceps`, `tendon`, `arm-bones`, `elbow-joint` | Muscles can only pull, never push. So they work in pairs: one bends a joint and its partner straightens it. The upper arm is the classic example |
| `muscle-inside` | Inside a muscle | `whole-muscle`, `fascicle`, `muscle-fibre`, `myofibril`, `tendon`, `blood-vessels` | A muscle is built like a rope: bundles inside bundles. Each level is magnified to show the next |

Parts (`biceps`, `triceps` and `tendon` are shared between diagrams and have one entry each):

| id | name | Must cover |
|---|---|---|
| `deltoid` | Deltoid | The rounded cap of the shoulder; lifts the arm out to the side, forwards and backwards; named after the triangular Greek letter delta |
| `pectorals` | Pectorals | The chest muscles; pull the arms forwards and across the body, as in pushing or throwing |
| `biceps` | Biceps | Front of the upper arm; bends the elbow and turns the palm upwards; shortens and bulges when it works; its partner is the triceps |
| `triceps` | Triceps | Back of the upper arm; straightens the elbow; when it pulls, the biceps relaxes and is stretched |
| `abdominals` | Abdominals | Front and sides of the belly; bend and twist the body, hold the organs in place and support the back; the "six-pack" is one muscle divided by bands of tendon |
| `trapezius` | Trapezius | Large kite-shaped muscle across the upper back and neck; moves the shoulder blades and helps hold up the head |
| `lats` | Latissimus dorsi (lats) | The broadest muscle of the back; pulls the arm down and back, as in swimming, climbing and pull-ups |
| `gluteals` | Gluteals | The buttock muscles; the largest is one of the strongest in the body; straighten the hip for standing up, climbing stairs and running |
| `quadriceps` | Quadriceps | Group of four muscles on the front of the thigh; straighten the knee for kicking, jumping and standing up |
| `hamstrings` | Hamstrings | Group of three muscles on the back of the thigh; bend the knee; the partner of the quadriceps |
| `calf` | Calf muscle | Back of the lower leg; points the foot down to push you off the ground; joined to the heel by the Achilles tendon |
| `tendon` | Tendons | Tough cords that join muscle to bone; made of strong fibres (collagen) that hardly stretch, so the muscle's pull moves the bone; ligaments, by contrast, join bone to bone |
| `arm-bones` | Arm bones | The humerus in the upper arm and the radius and ulna in the forearm; bones act as levers that muscles pull on |
| `elbow-joint` | Elbow joint | A hinge joint: it bends and straightens in one direction, like a door hinge |
| `whole-muscle` | Whole muscle | An organ made of thousands of muscle fibres wrapped in a tough sheath; muscles make up roughly 40% of body weight |
| `fascicle` | Bundle (fascicle) | A bundle of muscle fibres in its own wrapping; the "grain" you can see in cooked meat |
| `muscle-fibre` | Muscle fibre | A single muscle cell: very long and thin, with many nuclei and many mitochondria for energy; looks striped under a microscope |
| `myofibril` | Myofibril | Thread-like rods packed inside each fibre; made of two kinds of protein filament that slide past each other, shortening the muscle |
| `blood-vessels` | Blood vessels | Bring oxygen and sugar and carry away carbon dioxide and heat; blood flow to a working muscle rises many times over during exercise |

Drawings:

`major-muscles.svg` (`viewBox="0 0 800 640"`): two simplified standing figures side by side, "Front" and "Back" captions (outside any part group). Grey body silhouette, muscles as coloured shapes on top. Front: `deltoid`, `pectorals`, `biceps`, `abdominals`, `quadriceps`. Back: `trapezius`, `deltoid` (sibling), `triceps`, `lats`, `gluteals`, `hamstrings`, `calf`. Both sides of the body drawn (sibling groups); labels in the outer margins and the gap between figures.

`muscle-pair.svg`: two arms, "Bent" on the left and "Straight" on the right (captions outside part groups). Each has `arm-bones` (humerus, radius, ulna in bone colour), `elbow-joint` (a circle at the hinge), `biceps` and `triceps` (red muscle bellies: biceps fat and short in the bent arm, triceps fat in the straight arm) and `tendon` (pale cords at each muscle end). Label each part once.

`muscle-inside.svg`: left to right, getting more magnified. `tendon` (pale cord) joining `whole-muscle` (red spindle, with a cut end showing bundles); `blood-vessels` (thin red and blue lines on its surface); a pulled-out `fascicle` (a cylinder of circles); a pulled-out `muscle-fibre` (a thinner striped cylinder); a pulled-out `myofibril` (a thinnest rod with repeating bands). Dashed zoom lines between levels sit inside the group of the more magnified part.

---

### Task 6: Inside the Atom (adds the Physics subject)

**Files:** Create `docs/topics/atom.json`, `docs/diagrams/atom-model.svg`, `docs/diagrams/nucleus.svg`, `docs/diagrams/hydrogen-isotopes.svg`. Modify `docs/site.json`.

**Site map:** append a third subject:

```json
    {
      "id": "physics",
      "title": "Physics",
      "blurb": "Matter, energy and forces: the rules that everything follows.",
      "color": "#7d4fc4",
      "topics": [
        { "id": "atom", "title": "Inside the Atom" }
      ]
    }
```

Diagrams:

| id | title | parts | intro must say |
|---|---|---|---|
| `atom-model` | An atom | `nucleus`, `proton`, `neutron`, `electron`, `electron-shells`, `empty-space` | Everything is made of atoms. This is a carbon atom: 6 protons, 6 neutrons and 6 electrons. Not to scale: the real nucleus is far too small to see at this size. The shells are a simplified model; electrons do not really travel in neat circles |
| `nucleus` | Inside the nucleus | `proton`, `neutron`, `up-quark`, `down-quark`, `strong-force` | Protons and neutrons are not the smallest pieces. Each is made of three smaller particles called quarks, held together by the strongest force in nature. Not to scale; the colours are only to tell the particles apart |
| `hydrogen-isotopes` | Hydrogen's three isotopes | `protium`, `deuterium`, `tritium` | Atoms of the same element always have the same number of protons but can have different numbers of neutrons. These versions are called isotopes. Hydrogen has three |

Parts (`proton` and `neutron` are shared):

| id | name | Must cover |
|---|---|---|
| `nucleus` | Nucleus | The tiny, dense centre, made of protons and neutrons; holds more than 99.9% of the atom's mass; positively charged; about 100,000 times narrower than the atom |
| `proton` | Proton | Positive charge; the number of protons (the atomic number) decides which element the atom is; made of two up quarks and one down quark |
| `neutron` | Neutron | No charge; very slightly heavier than a proton; helps hold the nucleus together; made of one up quark and two down quarks |
| `electron` | Electron | Negative charge; almost 2,000 times lighter than a proton; a neutral atom has as many electrons as protons; the outer electrons form chemical bonds |
| `electron-shells` | Electron shells | Energy levels that electrons occupy; the first holds up to 2 electrons, the second up to 8; a simplified picture, since electrons really form fuzzy clouds |
| `empty-space` | Empty space | An atom is almost entirely empty; if the nucleus were a pea in the middle of a football stadium, the electrons would be out at the stands; found by firing particles at gold foil (Rutherford) |
| `up-quark` | Up quark | Charge of +2/3; two ups and a down give the proton its charge of +1; quarks are never found on their own |
| `down-quark` | Down quark | Charge of −1/3; one up and two downs add up to zero, which is why the neutron has no charge |
| `strong-force` | The strong force | The strongest of the four basic forces; holds quarks together inside protons and neutrons, and holds protons and neutrons together in the nucleus despite the protons pushing each other apart; only works over tiny distances; carried by particles called gluons |
| `protium` | Protium | Ordinary hydrogen: one proton, no neutrons; about 99.98% of all hydrogen; the only atom with no neutron |
| `deuterium` | Deuterium | One proton and one neutron; stable; about 1 in every 6,400 hydrogen atoms; water made with it is "heavy water" |
| `tritium` | Tritium | One proton and two neutrons; radioactive, with half of any sample decaying in about 12 years; very rare in nature; used in some glow-in-the-dark signs |

Drawings:

`atom-model.svg`: `empty-space` a large pale disc behind everything (drawn first); `electron-shells` two thin grey rings (with transparent wide strokes); `nucleus` a cluster outline/halo at the centre, drawn before the particles; six red `proton` and six grey-blue `neutron` circles packed on top (sibling groups, "+" on protons); six small blue `electron` dots with "−", two on the inner ring and four on the outer.

`nucleus.svg`: one large `proton` circle (pale red) on the left and one large `neutron` circle (pale grey-blue) on the right. Inside the proton: two `up-quark` circles and one `down-quark`; inside the neutron: one up and two down (labelled "u" and "d", different colours). `strong-force` as springy zigzag lines joining the quarks in each triangle and one between the proton and the neutron. Quarks and force lines are sibling groups drawn on top, not nested.

`hydrogen-isotopes.svg`: three small atoms side by side, each one whole part: `protium` (1 proton), `deuterium` (1 proton + 1 neutron), `tritium` (1 proton + 2 neutrons), each with one electron on a ring, and its name and "¹H", "²H", "³H" underneath inside the group.

**Review checkpoint (spec):** drawing style for physics is confirmed before Tasks 7–9.

---

### Task 7: Circuits

**Files:** Create `docs/topics/circuits.json`, `docs/diagrams/simple-circuit.svg`, `docs/diagrams/series-parallel.svg`. Modify `docs/site.json`.

**Site map:** append `{ "id": "circuits", "title": "Circuits" }` to the `physics` subject.

Diagrams:

| id | title | parts | intro must say |
|---|---|---|---|
| `simple-circuit` | A simple circuit | `battery`, `wires`, `switch`, `bulb`, `resistor`, `ammeter`, `voltmeter`, `current` | Electricity flows only around a complete loop, called a circuit. This one is drawn with the standard symbols used in circuit diagrams |
| `series-parallel` | Series and parallel | `series-circuit`, `parallel-circuit`, `branch`, `junction` | There are two basic ways to connect more than one bulb: one after another in a single loop, or side by side on separate paths |

Parts:

| id | name | Must cover |
|---|---|---|
| `battery` | Battery | Pushes electric charge around the circuit; turns stored chemical energy into electrical energy; its push is the voltage, measured in volts; has a positive and a negative end; in the symbol the longer line is positive |
| `wires` | Wires | Metal paths, usually copper, that charge flows through easily; coated in plastic, which does not conduct; the loop must be complete for anything to flow |
| `switch` | Switch | Opens or closes a gap in the circuit; open means the loop is broken and current stops everywhere in it at once |
| `bulb` | Bulb | Turns electrical energy into light and heat; in a filament bulb a very thin wire glows white-hot; LEDs make the same light with far less energy |
| `resistor` | Resistor | Makes it harder for current to flow; resistance is measured in ohms; used to limit the current; voltage = current × resistance |
| `ammeter` | Ammeter | Measures current in amperes (amps); connected in the loop, in series, so all the current passes through it |
| `voltmeter` | Voltmeter | Measures voltage across a component; connected across it, in parallel |
| `current` | Direction of current | Current is the flow of electric charge, measured in amps; by convention it is drawn from positive to negative; the electrons actually move the other way; the convention was fixed before electrons were discovered |
| `series-circuit` | Series circuit | One single path; the same current goes through every part; the battery's voltage is shared, so more bulbs are each dimmer; if one bulb breaks they all go out |
| `parallel-circuit` | Parallel circuit | More than one path; every branch gets the full battery voltage, so bulbs stay bright; if one breaks the others stay lit; homes are wired this way |
| `branch` | Branch | One of the separate paths in a parallel circuit; each carries its own share of the current |
| `junction` | Junction | A point where wires meet and the current splits or joins; the current flowing in equals the current flowing out |

Drawings:

`simple-circuit.svg`: a rectangular loop of `wires` using standard symbols: `battery` on the left side (long and short lines, "+" and "−"); `switch` on the top (shown closed, with two dots and a lever); `bulb` on the right (circle with a cross); `resistor` on the bottom (rectangle); `ammeter` in the loop (circle with "A"); `voltmeter` on a spur across the bulb (circle with "V"; its own leads are inside its group); `current` as arrowheads beside the loop running from "+" round to "−". Wires are split into sibling groups between components so nothing is nested.

`series-parallel.svg`: two circuits side by side with captions "Series" and "Parallel" inside their groups. `series-circuit` (left): battery and two bulbs in one loop, all one part. `parallel-circuit` (right): battery with the main loop wires, drawn as one part; on top of it, as siblings, the two `branch` paths (each a bulb on its own rung, in a different colour) and the two `junction` dots where the rungs meet the main wires.

---

### Task 8: Light & the Spectrum

**Files:** Create `docs/topics/light.json`, `docs/diagrams/em-spectrum.svg`, `docs/diagrams/wave-parts.svg`, `docs/diagrams/prism.svg`. Modify `docs/site.json`.

**Site map:** append `{ "id": "light", "title": "Light & the Spectrum" }` to the `physics` subject.

Diagrams:

| id | title | parts | intro must say |
|---|---|---|---|
| `em-spectrum` | The electromagnetic spectrum | `radio-waves`, `microwaves`, `infrared`, `visible-light`, `ultraviolet`, `x-rays`, `gamma-rays` | Light is a wave, and the light we see is one small part of a much larger family. All of these waves travel at the same speed in empty space, about 300,000 km every second. They differ only in wavelength: long on the left, short on the right |
| `wave-parts` | Parts of a wave | `crest`, `trough`, `wavelength`, `amplitude`, `frequency` | Every wave, whether light, sound or a ripple on a pond, can be described with the same few measurements |
| `prism` | A prism splitting light | `white-light`, `prism`, `spectrum`, `refraction` | White light is a mixture of colours. A block of glass called a prism spreads them out. The angles are exaggerated to make the bending easy to see |

Parts:

| id | name | Must cover |
|---|---|---|
| `radio-waves` | Radio waves | The longest wavelengths, from about a metre to many kilometres, and the lowest energy; carry radio and TV signals; pass through walls |
| `microwaves` | Microwaves | Wavelengths from about a millimetre to a metre; make water molecules in food jiggle and heat up; also used for Wi-Fi, mobile phones and radar |
| `infrared` | Infrared | Just longer than red light; we feel it as warmth; given off by every warm object; used in TV remotes and heat-sensing cameras |
| `visible-light` | Visible light | The only part our eyes can detect; wavelengths from about 400 nanometres (violet) to 700 nanometres (red); a very thin slice of the whole spectrum |
| `ultraviolet` | Ultraviolet | Just shorter than violet light; causes sunburn and tanning and helps skin make vitamin D; most from the Sun is blocked by the ozone layer |
| `x-rays` | X-rays | Pass through skin and muscle but are stopped by bone, which is how X-ray pictures work; high energy, so doses are kept small |
| `gamma-rays` | Gamma rays | The shortest wavelengths and highest energy; come from radioactive atoms and violent events in space; can damage living cells; used carefully to kill cancer cells and sterilise equipment |
| `crest` | Crest | The highest point of a wave |
| `trough` | Trough | The lowest point of a wave |
| `wavelength` | Wavelength | The distance from one crest to the next (or trough to trough); measured in metres; decides the colour of light |
| `amplitude` | Amplitude | The height of a crest above the middle (rest) line, not from trough to crest; bigger amplitude means more energy: brighter light or louder sound |
| `frequency` | Frequency | How many waves pass a point each second, measured in hertz; wave speed = frequency × wavelength, so at the same speed a higher frequency means a shorter wavelength |
| `white-light` | White light | A mixture of all the colours; sunlight and ordinary lamp light are white |
| `prism` | Prism | A triangular block of clear glass or plastic; light travels more slowly in glass than in air |
| `spectrum` | Spectrum of colours | Red, orange, yellow, green, blue, indigo, violet; red is bent least and violet most; a rainbow is the same effect made by raindrops; shown by Isaac Newton in the 1660s |
| `refraction` | Bending (refraction) | Light changes direction when it changes speed crossing from one material into another; it bends on the way into the prism and again on the way out; why a straw in water looks bent |

A part's `details` needs at least 40 words; for `crest` and `trough`, fill out with what the particles/field do there and an everyday example (the top and bottom of an ocean swell), not with harder physics.

Drawings:

`em-spectrum.svg` (`viewBox="0 0 800 520"`): a horizontal band divided into seven blocks, each one part, with the name inside or under it and a small everyday icon above (radio mast, microwave oven, flame/remote, eye, sun, bone, atom symbol), all inside the block's group. `visible-light` is a narrow rainbow-gradient block. Above the band, outside any part, one continuous wave whose wavelength shrinks from left to right, and "long wavelength, low energy" / "short wavelength, high energy" captions.

`wave-parts.svg`: a sine wave of about two and a half cycles on a dashed middle line (wave and middle line outside any part). `crest`: a dot and label at a peak; `trough`: a dot and label at a dip; `wavelength`: a double-headed horizontal arrow between two neighbouring crests; `amplitude`: a double-headed vertical arrow from the middle line up to a crest; `frequency`: a small inset box at the bottom comparing a low-frequency and a high-frequency wave drawn over the same "1 second".

`prism.svg`: `white-light` a thick pale beam entering from the left with an arrowhead; `prism` a triangle with a faint blue-grey fill; `spectrum` a fan of seven coloured bands leaving the right face, red at the top and violet at the bottom; `refraction` two small curved-angle markers with dots at the points on each face where the beam bends, labelled once.

---

### Task 9: Forces & Machines

**Files:** Create `docs/topics/forces.json`, `docs/diagrams/box-forces.svg`, `docs/diagrams/simple-machines.svg`, `docs/diagrams/lever.svg`. Modify `docs/site.json`.

**Site map:** append `{ "id": "forces", "title": "Forces & Machines" }` to the `physics` subject.

Diagrams:

| id | title | parts | intro must say |
|---|---|---|---|
| `box-forces` | Forces on a pushed box | `weight`, `normal-force`, `applied-force`, `friction`, `air-resistance`, `net-force` | A force is a push or a pull, measured in newtons. Several forces usually act on an object at once. Each arrow shows one: its direction is the way the force acts and its length shows how strong it is |
| `simple-machines` | The six simple machines | `lever`, `wheel-axle`, `pulley`, `inclined-plane`, `wedge`, `screw` | A simple machine makes a job easier by changing the size or direction of a force. None of them gives something for nothing: a smaller force has to move through a longer distance. Every complicated machine is built from these six |
| `lever` | Parts of a lever | `fulcrum`, `effort`, `load`, `effort-arm`, `load-arm` | A lever is a stiff bar that turns on a fixed point. Where that point sits decides how much the lever helps |

Parts:

| id | name | Must cover |
|---|---|---|
| `weight` | Weight (gravity) | The pull of gravity on the box, straight down towards the centre of the Earth; measured in newtons; about 10 newtons for every kilogram on Earth; mass stays the same on the Moon but weight is about a sixth |
| `normal-force` | The floor's push back (normal force) | The floor pushes up on the box at right angles to the surface; on a level floor it exactly balances the weight, which is why the box does not sink; "normal" means "at right angles" |
| `applied-force` | The push (applied force) | The force the person puts on the box; a contact force, acting only while they are touching it |
| `friction` | Friction | Acts along the surface, against the sliding; bigger for rougher surfaces and heavier boxes; turns motion into heat; without it we could not walk |
| `air-resistance` | Air resistance | The air pushing back on anything moving through it; grows quickly with speed and with the area facing the air; tiny for a slow box, huge for a parachute |
| `net-force` | Overall (net) force | All the forces added together, taking direction into account; if they balance the box stays still or keeps a steady speed; if not it speeds up, slows down or turns; force = mass × acceleration |
| `lever` | Lever | A bar that turns on a pivot: seesaws, crowbars, scissors, wheelbarrows |
| `wheel-axle` | Wheel and axle | A wheel fixed to a thinner rod so they turn together; a small force at the rim gives a large force at the axle: door knobs, screwdrivers, steering wheels |
| `pulley` | Pulley | A grooved wheel with a rope; one fixed pulley changes the direction of the pull; several together share the load so you pull with less force over more rope |
| `inclined-plane` | Ramp (inclined plane) | A sloping surface; raising a load up it takes less force than lifting straight up, but over a longer distance: wheelchair ramps, winding mountain roads |
| `wedge` | Wedge | Two ramps back to back that are pushed into something; turns a push into a sideways splitting force: axes, knives, front teeth |
| `screw` | Screw | A ramp wrapped round a rod; turning it many times moves it a short way with great force: screws, bolts, jar lids |
| `fulcrum` | Pivot (fulcrum) | The fixed point the bar turns on |
| `effort` | Effort | The force you put in |
| `load` | Load | The weight or resistance you are trying to move |
| `effort-arm` | Effort arm | The distance from the pivot to where you push; the longer it is, the less effort you need |
| `load-arm` | Load arm | The distance from the pivot to the load; when balanced, effort × effort arm = load × load arm, so an effort arm twice as long halves the effort |

For the short lever parts, reach 40 words with everyday examples (where the pivot is on a seesaw, scissors, a bottle opener), not harder physics.

Drawings:

`box-forces.svg`: a box on a floor line with a simple figure pushing from the left (figure, box and floor outside any part). Arrows from the box, each its own part with a label at its tip: `applied-force` (right, green, long), `friction` (left along the floor, orange, medium), `air-resistance` (left from the box's front face, light blue, short), `weight` (down from the centre, purple), `normal-force` (up from the floor, same length as weight, teal), and, set apart below with the caption "Overall", `net-force` (right, black, short).

`simple-machines.svg` (`viewBox="0 0 800 560"`): a 3 × 2 grid of small pictures, each a part with its name underneath inside the group: `lever` (seesaw bar on a triangle with a box), `wheel-axle` (large wheel on a small rod, side view), `pulley` (wheel hanging from a beam, rope and a load), `inclined-plane` (ramp with a box), `wedge` (wedge splitting a log), `screw` (screw with thread).

`lever.svg`: a long bar on a triangular `fulcrum` set off-centre (bar outside any part); `load`: a box on the short end with a down arrow; `effort`: a down arrow (and hand hint) on the long end; `effort-arm` and `load-arm`: double-headed measuring arrows under the bar from the pivot to each end, in different colours.

---

### Task 10: README and full regression pass

**Files:** Modify `README.md`.

- [ ] **Step 1: Replace the `## Website` section** (to the end of the file) with:

````markdown
## Website

A browser version, **Science Explorer**, lives in `docs/` and is published
with GitHub Pages. Its home page has a card for each subject (Chemistry,
Human Body & Cells, Physics) linking to every topic: the periodic table and
twelve topics with clickable diagrams.

The subjects and topics are listed in `docs/site.json`, the site map. The
home page and the navigation inside a topic are drawn from it.

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
3. Add an entry to `docs/site.json` under the topic's subject, with the
   same `id` and `title` as the topic file.
4. Run `pytest tests/test_topics.py tests/test_site.py`; it checks the
   drawings, the text and the site map match.
````

- [ ] **Step 2: Run** `.venv/bin/pytest tests/test_topics.py tests/test_site.py -v` — expected: all PASS, with twelve topics parametrised.

- [ ] **Step 3: Full browser pass** at desktop and 375px: Home shows three cards and thirteen links; every link, trail link and topic-row link followed; every part of all 30 diagrams clicked; back/forward; keyboard; the periodic table's search, timeline, compare, detail, atom view and quiz. No console errors.

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs: describe Science Explorer and the site map"
```
