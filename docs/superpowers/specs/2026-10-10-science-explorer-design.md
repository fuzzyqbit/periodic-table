# Science Explorer — Design

Date: 2026-10-10
Scope: website only (`docs/`). The Tkinter desktop app is not changed.

## Goal

Grow the website from a periodic table with four biology tabs into a small
science site with a front page, three subjects and thirteen topics.

Two things are added:

1. **A frame.** A home page with one card per subject, and a way to move
   between the topics inside a subject. This replaces the row of five tabs,
   which has no room for more.
2. **Eight new topics** (20 new diagrams): Heart, Lungs, Digestion and
   Muscles in the body subject, and Inside the Atom, Circuits, Light & the
   Spectrum and Forces & Machines in a new Physics subject.

**Audience:** unchanged from the biology tabs. Between middle school and
high school: plain language a middle schooler can follow, a full set of
parts and a solid paragraph on each. No college-level mechanisms.

**Success looks like:** a student opens the site, sees the three subjects,
reaches any topic in one or two clicks, clicks any part of any diagram and
reads a clear, accurate explanation. The periodic table and the four
existing biology topics work exactly as they do today.

## Decisions made

| Question | Decision |
|---|---|
| Direction | Small frame first (home page + subjects), then more topics |
| Navigation | Home page with subject cards; trail and topic row inside a topic |
| Site name | "Science Explorer" |
| Subjects | Chemistry, Human Body & Cells, Physics |
| New topics | Heart, Lungs, Digestion, Muscles; Inside the Atom, Circuits, Light & the Spectrum, Forces & Machines |
| Physics interaction | Click a part to learn, same as biology. No simulations or sliders |
| Structure | Still one page. A site map file lists subjects and topics |
| Artwork | Hand-written SVG schematics, colour-coded, no third-party images |
| Amount | All 20 diagrams in this spec, built one topic at a time |

## Site structure

| Subject (id) | Topics (id) |
|---|---|
| Chemistry (`chemistry`) | Periodic Table (`table`) |
| Human Body & Cells (`body`) | Cells (`cells`), Blood (`blood`), Nervous System (`nervous`), Skeleton (`skeleton`), Heart (`heart`), Lungs (`lungs`), Digestion (`digestion`), Muscles (`muscles`) |
| Physics (`physics`) | Inside the Atom (`atom`), Circuits (`circuits`), Light & the Spectrum (`light`), Forces & Machines (`forces`) |

`table` is the one built-in topic: it is the existing periodic table view
and has no topic file. Every other topic is a diagram topic shown by the
existing viewer. `home` and `table` are reserved ids.

## User experience

**Name.** The page heading and the browser title change from "Periodic
Table of Elements" to "Science Explorer".

**Home page.** Shown when the site is opened. One card per subject, in the
order above. Each card has a colour stripe, the subject title, a one-line
description, and a link for every topic in that subject. Clicking a topic
link opens that topic. Three cards sit side by side on a wide screen and
stack in one column below 900px (the site's existing breakpoint).

**Inside a topic.** The sticky header shows, under the site heading:

- A trail: "⌂ Home › Human Body & Cells". "Home" is a link to the home
  page. The subject name is plain text in the subject's colour.
- A topic row: a link to every topic in the same subject, with the current
  one marked. The row is hidden when the subject has only one topic
  (Chemistry). Below 900px the row stays on one line and scrolls sideways,
  so the header does not grow tall.

Below the header nothing changes. Diagram topics show the diagram, the
diagram switcher, the part buttons and the info panel as today. The
periodic table shows its search box, Quiz button, compare hint and
timeline, and those controls appear only on the table.

**Links.** Each page has its own address in the URL hash: `#home`,
`#table`, `#cells`, `#heart`, `#circuits` and so on. Browser back and
forward move between pages. Existing links (`#cells`, `#blood`, `#nervous`,
`#skeleton`, `#table`) keep working.

**Behaviour change.** No hash, or an unknown hash, now shows the home page.
Today it shows the periodic table. `#table` still opens the table directly.

**Browser title.** Updates with the page: "Science Explorer" on Home,
"Heart – Science Explorer" on a topic.

**Keyboard and screen readers.** The trail and topic row are ordinary links
inside a `<nav>`; the current topic carries `aria-current="page"`. The tab
roles used by the old tab bar are removed. After a page change, keyboard
focus moves to the page's main heading so the new page is announced.
Diagram parts keep their existing keyboard behaviour.

## New topics and diagrams

Every topic follows the existing contract: parts are defined once per topic
and referenced by id from each diagram, each part has a name, a one-line
summary, a 40–120 word paragraph and 2–5 key facts, and each diagram has a
title and an intro shown before a part is selected. The part lists below
name the parts; part ids are lowercase with hyphens, chosen during the
build.

### Human Body & Cells

**Heart (`heart`)**

- `heart-inside` — *Inside the heart.* Right atrium, right ventricle, left
  atrium, left ventricle, tricuspid valve, pulmonary valve, mitral valve,
  aortic valve, septum, aorta, pulmonary artery, pulmonary veins, venae
  cavae.
- `circulation` — *The two loops of circulation.* Heart, lungs, body,
  arteries, veins, capillaries, the lung loop (pulmonary circulation), the
  body loop (systemic circulation).

**Lungs (`lungs`)**

- `breathing-system` — *The breathing system.* Nose and mouth, throat
  (pharynx), voice box (larynx), windpipe (trachea), bronchi, bronchioles,
  lungs, diaphragm, rib muscles (intercostals).
- `air-sac` — *Inside an air sac.* Air sac (alveolus), its thin wall,
  capillary, red blood cell, oxygen moving into the blood, carbon dioxide
  moving out.

**Digestion (`digestion`)**

- `digestive-system` — *The digestive system.* Mouth, salivary glands,
  oesophagus, stomach, liver, gallbladder, pancreas, small intestine, large
  intestine, appendix, rectum.
- `villi` — *Inside the small intestine.* Villi, the lining cells, blood
  capillaries, lacteal, muscle layer.

**Muscles (`muscles`)**

- `major-muscles` — *Major muscles, front and back.* Deltoid, pectorals,
  biceps, triceps, abdominals, trapezius, latissimus dorsi (lats),
  gluteals, quadriceps, hamstrings, calf muscle.
- `muscle-pair` — *Muscles work in pairs.* The upper arm bending and
  straightening: biceps, triceps, tendons, arm bones, elbow joint.
- `muscle-inside` — *Inside a muscle.* Whole muscle, bundle (fascicle),
  muscle fibre, myofibril, tendon, blood vessels.

Biceps and triceps appear in two diagrams and tendons in two; each has one
text entry.

### Physics

**Inside the Atom (`atom`)**

- `atom-model` — *An atom.* Nucleus, proton, neutron, electron, electron
  shells, empty space.
- `nucleus` — *Inside the nucleus.* Proton, neutron, up quark, down quark,
  the strong force.
- `hydrogen-isotopes` — *Hydrogen's three isotopes.* Protium, deuterium,
  tritium.

**Circuits (`circuits`)**

- `simple-circuit` — *A simple circuit.* Battery, wires, switch, bulb,
  resistor, ammeter, voltmeter, direction of current.
- `series-parallel` — *Series and parallel.* Series circuit, parallel
  circuit, branch, junction.

**Light & the Spectrum (`light`)**

- `em-spectrum` — *The electromagnetic spectrum.* Radio waves, microwaves,
  infrared, visible light, ultraviolet, X-rays, gamma rays.
- `wave-parts` — *Parts of a wave.* Crest, trough, wavelength, amplitude,
  frequency.
- `prism` — *A prism splitting light.* White light, prism, the spectrum of
  colours, bending (refraction).

**Forces & Machines (`forces`)**

- `box-forces` — *Forces on a pushed box.* Weight (gravity), the floor's
  push back (normal force), the push (applied force), friction, air
  resistance, overall (net) force.
- `simple-machines` — *The six simple machines.* Lever, wheel and axle,
  pulley, ramp (inclined plane), wedge, screw.
- `lever` — *Parts of a lever.* Pivot (fulcrum), effort, load, effort arm,
  load arm.

### Content rules

- Drawings are simplified schematics, not anatomical or engineering
  illustrations, and each diagram's intro says so where it matters (the
  atom is not to scale; shells are a simplified model).
- The heart is drawn as seen from the front, so the heart's right side is
  on the left of the picture. The intro states this.
- Red for oxygen-rich and blue for oxygen-poor blood is a drawing
  convention. Arteries are defined as vessels carrying blood away from the
  heart, so the pulmonary artery is drawn blue.
- The circuit text gives conventional current (positive to negative) and
  notes that electrons move the other way.
- Simple formulas may appear as key facts where they help: voltage =
  current × resistance; wave speed = frequency × wavelength. No worked
  problems.
- Facts are kept to well-established school-level science and reviewed
  diagram by diagram.

## Architecture

All files are under `docs/`. No build step, no frameworks, no new
dependencies; plain HTML, CSS and JavaScript like the rest of the site.

```
docs/
  index.html    tab buttons removed; home view and topic nav added
  style.css     home cards, trail, topic row, subject colours; .tabs rules removed
  app.js        unchanged
  site.json     NEW: the site map
  site.js       NEW: router, home page, trail and topic row
  topics.js     router code removed; diagram viewer only
  topics/       + heart, lungs, digestion, muscles, atom, circuits, light, forces (.json)
  diagrams/     + 20 SVG files, named by the diagram ids above
```

Script order in `index.html`: `app.js`, `topics.js`, `site.js`.

`index.html` gains `<main id="home-view">` beside the existing
`#table-view` and `#topic-view`, and `<nav id="topic-nav">` in the header
in place of `<nav id="tabs">`.

### Units

**Site map (`site.json`).** Data only.

```json
{
  "title": "Science Explorer",
  "subjects": [
    {
      "id": "body",
      "title": "Human Body & Cells",
      "blurb": "One line shown on the home card.",
      "color": "#c0392b",
      "topics": [
        { "id": "cells", "title": "Cells" },
        { "id": "heart", "title": "Heart" }
      ]
    }
  ]
}
```

A topic's `title` here must equal the `title` in its topic file; the test
suite enforces it. Titles are repeated in the site map so the home page
can be drawn without loading every topic file. Subject colours: Chemistry
`#2c6df0` (the existing accent), Human Body & Cells `#c0392b`, Physics
`#7d4fc4`. Colour is used for the card stripe and the subject name in the
trail only.

**Router and navigation (`site.js`).** Loads `site.json` once. On load and
on every `hashchange` it resolves the hash to a page — `home`, `table`, or
a topic id found in the site map; anything else is `home` — then:

- shows exactly one of the home view, the table view and the topic view;
- shows the table controls only for `table`;
- calls `closeTableOverlays()` (in `app.js`) when leaving the table;
- calls `showTopic(id)` (in `topics.js`) for a diagram topic;
- draws the trail and topic row for the page's subject, or hides them on
  Home;
- sets `document.title` and moves focus to the page heading.

It draws the home cards from the site map once. It knows nothing about
diagram content.

**Diagram viewer (`topics.js`).** Unchanged apart from losing the tab
router (`tabButtons`, `tabFromHash`, `showTab`, `wireTabs`). It still
exposes `showTopic(id)` and is still entirely data-driven.

**Topic data and diagrams.** Same formats and the same SVG contract as the
biology tabs spec (2026-10-06): a `viewBox` and no fixed size, every
clickable part in a `<g data-part="…">`, labels inside their part's group,
no nested parts, no scripts, no external references, no raster images.

### Data flow

Page load → `site.js` fetches `site.json` → draws home cards → resolves the
hash → shows the matching view. Link click → hash changes → `site.js`
resolves it → for a diagram topic, `showTopic(id)` fetches the topic file
and SVG as today.

Adding a topic later needs a topic file, its SVG files and one entry in
`site.json`. No JavaScript or HTML changes.

### Error handling

- `site.json` fails to load: the page shows "Couldn't load the site" with a
  Retry button in place of the home view. Nothing else is shown until it
  loads.
- A topic file or SVG fails to load: unchanged. The topic view shows
  "Couldn't load this diagram" with Retry; Home, the trail and other topics
  keep working.
- Unknown hash: shows Home.
- A topic listed in the site map with no file, or a file not listed, is
  prevented by the tests below.

## Testing

**Automated (`pytest`, standard library only).**

`tests/test_topics.py`: `test_tabs_match_topic_files` is removed, since the
tab buttons no longer exist. All other tests there stay and, being driven
by the files in `docs/topics/`, cover the eight new topics with no change.

New `tests/test_site.py`:

- `site.json` parses and has a non-empty title and at least one subject.
- Every subject has a valid id, non-empty title and blurb, a `#rrggbb`
  colour and at least one topic. Subject ids are unique.
- Topic ids are unique across the whole site map, and none is `home`.
- The set of topic ids, minus `table`, equals the set of files in
  `docs/topics/`. `table` appears exactly once.
- For every diagram topic, the site map title equals the topic file title.
- `index.html` contains `#home-view`, `#table-view`, `#topic-view` and
  `#topic-nav`, and no `data-tab` buttons.

The desktop app's tests are not touched.

**In the browser, at each build stage.** Home and every topic so far at
desktop and phone width: every part clicked; every home link, trail link
and topic-row link followed; hash links and back/forward checked; keyboard
use checked. The periodic table's search, timeline, compare, detail and
atom views and quiz re-checked for regressions.

## Build order

The site works and can be published after every stage. A topic is added to
`site.json` only in the stage that adds its files, so Home never links to a
topic that does not exist.

1. **Frame.** `site.json` with the five existing topics, `site.js`, home
   page, trail and topic row, router moved out of `topics.js`, old tab bar
   and its test removed, `tests/test_site.py` added. **Review checkpoint.**
2. **Heart.** **Review checkpoint:** drawing style and level of detail for
   the body topics are confirmed before the rest are drawn.
3. Lungs.
4. Digestion.
5. Muscles.
6. **Inside the Atom**, which adds the Physics subject. **Review
   checkpoint:** drawing style for physics is confirmed.
7. Circuits.
8. Light & the Spectrum.
9. Forces & Machines.
10. README: describe the home page and site map, and update "Adding a
    topic" (step 3 becomes "add an entry to `docs/site.json`").

## Out of scope

- Interactive physics (working switches, sliders, simulations).
- Quizzes for diagrams.
- Search across topics, progress tracking, dark mode.
- Links from one topic to another (for example iron in Blood to Fe).
- Richer element pages, isotopes data and orbital views for the periodic
  table.
- Any change to the desktop (Tkinter) app.
- Further subjects (earth science, space).
