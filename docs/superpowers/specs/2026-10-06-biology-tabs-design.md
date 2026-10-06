# Biology Tabs — Design

Date: 2026-10-06
Scope: website only (`docs/`). The Tkinter desktop app is not changed.

## Goal

Add four biology tabs next to the existing periodic table on the website:
Cells, Blood, Nervous System and Skeleton. Each tab shows labelled diagrams
where clicking a part explains what it is and what it does.

**Audience:** between middle school and high school. Plain language a middle
schooler can follow, but a full set of parts and a solid paragraph on each,
not one-liners. No college-level mechanisms or clinical ranges.

**Success looks like:** a student can open a tab, click any part of a
diagram, and read a clear, accurate explanation; the periodic table works
exactly as it does today.

## Decisions made

| Question | Decision |
|---|---|
| Where | Website only |
| Depth | Middle-to-high school, detailed |
| Interaction | Click a part to learn (no diagram quiz in this version) |
| Artwork | Hand-written SVG schematics, colour-coded, no third-party images |
| Structure | One page with tabs; content in data files; one shared viewer |
| Extras | Plant cell and brain regions are included |

## Tabs and diagrams

Five tabs: **Periodic Table** (existing, unchanged), **Cells**, **Blood**,
**Nervous System**, **Skeleton**. Ten diagrams in total.

### Cells
- **Animal cell** — cell membrane, cytoplasm, nucleus, nucleolus,
  mitochondria, ribosomes, rough ER, smooth ER, Golgi apparatus, lysosomes,
  centrioles, cytoskeleton, vesicles.
- **Plant cell** — cell wall, cell membrane, cytoplasm, nucleus, nucleolus,
  chloroplasts, central vacuole, mitochondria, ribosomes, rough ER,
  smooth ER, Golgi apparatus.

### Blood
- **Blood in a vessel** — vessel wall, plasma, red blood cells, white blood
  cells, platelets.
- **Spun tube** (blood separated into layers) — plasma (about 55%), buffy
  coat (white cells and platelets, under 1%), red blood cells (about 45%).
- **White blood cell types** — neutrophil, lymphocyte, monocyte, eosinophil,
  basophil, each drawn with its recognisable nucleus shape.

Each blood part covers what it does, roughly how many there are, where it is
made and how long it lasts.

### Nervous System
- **Body overview** — brain, spinal cord, cranial nerves, spinal and
  peripheral nerves. Text explains central vs peripheral nervous system.
- **Neuron** — dendrites, cell body, nucleus, axon, myelin sheath, nodes of
  Ranvier, axon terminals, synapse.
- **Brain regions** — frontal lobe, parietal lobe, temporal lobe, occipital
  lobe, cerebellum, brainstem.

### Skeleton
- **Full skeleton** — skull, jaw (mandible), collarbone (clavicle), shoulder
  blade (scapula), breastbone (sternum), ribs, spine, humerus, radius, ulna,
  hand bones, pelvis, femur, kneecap (patella), tibia, fibula, foot bones.
- **Inside a long bone** — periosteum, compact bone, spongy bone, red
  marrow, yellow marrow (medullary cavity), articular cartilage, growth
  plate, blood vessels.

The skeleton and body overview are simplified schematic shapes, not
anatomical illustrations.

## User experience

**Tab bar.** Sits under the page title inside the sticky header. The search
box, Quiz button, compare hint and timeline are shown only on the Periodic
Table tab. Leaving the Periodic Table tab closes the quiz panel and any open
element modal.

**Links.** The active tab is stored in the URL hash: `#cells`, `#blood`,
`#nervous`, `#skeleton`. No hash, `#table`, or an unknown hash shows the
Periodic Table. Browser back/forward moves between tabs.

**Topic view.** Diagram on the left, info panel on the right. Below 900px
wide (the site's existing breakpoint) the panel stacks under the diagram.
Tabs with more than one diagram show a switcher above it (for example
"Animal cell | Plant cell"); the first diagram is shown by default.

**Selecting a part.**
- Hovering a part highlights it.
- Clicking a part marks it selected, slightly dims the rest of the diagram,
  and fills the info panel.
- A row of buttons under the diagram lists every part in that diagram, so
  small parts are easy to pick. Clicking a button does the same as clicking
  the part.
- Before anything is selected, the panel shows a short introduction to the
  diagram and a "click a part" prompt.
- Switching diagram or tab clears the selection.

**Info panel content for a part:** name, one-line summary, a paragraph on
what it does (roughly 40–120 words), and 2–5 "key facts" bullets.

**Keyboard and screen readers.** The tab bar uses tab roles. Each clickable
part is focusable, has a spoken label, and responds to Enter and Space. The
info panel announces updates.

## Architecture

All new files are under `docs/`. No build step, no frameworks, no new
dependencies; plain HTML, CSS and JavaScript like the rest of the site.

```
docs/
  index.html        tab bar added; table controls and grid wrapped so they can be hidden
  style.css         tab bar, topic layout, part highlight styles
  app.js            unchanged except a small hook so the quiz/modals can be closed on tab change
  topics.js         NEW: tab routing + the shared diagram viewer
  topics/           NEW: one JSON file per topic
    cells.json  blood.json  nervous.json  skeleton.json
  diagrams/         NEW: one SVG file per diagram
    animal-cell.svg  plant-cell.svg
    blood-vessel.svg  blood-tube.svg  white-cell-types.svg
    nervous-body.svg  neuron.svg  brain.svg
    skeleton.svg  long-bone.svg
```

### Units

**Tab router (in `topics.js`).** Reads the hash, shows either the table view
or the topic view, updates the tab bar's active state, and tells the viewer
which topic to show. Knows nothing about diagram content.

**Diagram viewer (in `topics.js`).** Given a topic id: loads its JSON (once,
then cached), builds the diagram switcher, loads the chosen SVG (once, then
cached), inserts it into the page, wires hover/click/keyboard on its parts,
builds the part button row, and renders the info panel. It is entirely
data-driven: adding a future topic needs a JSON file, SVG files and one tab
button, with no viewer changes.

**Topic data (`topics/*.json`).** Text only.

```json
{
  "id": "cells",
  "title": "Cells",
  "parts": {
    "mitochondria": {
      "name": "Mitochondria",
      "summary": "The cell's power stations.",
      "details": "A paragraph on what it does…",
      "facts": ["Fact one.", "Fact two."]
    }
  },
  "diagrams": [
    {
      "id": "animal-cell",
      "title": "Animal cell",
      "intro": "Shown before a part is selected.",
      "svg": "diagrams/animal-cell.svg",
      "parts": ["cell-membrane", "nucleus", "mitochondria"]
    }
  ]
}
```

Parts are defined once per topic and referenced by id from each diagram, so
organelles shared by the animal and plant cell have one text entry.

**Diagrams (`diagrams/*.svg`).** Contract with the viewer:
- A `viewBox` and no fixed width/height, so it scales to its container.
- Every clickable part is a `<g data-part="part-id">`. The same id may
  appear on several groups (for example several mitochondria); they
  highlight and select together.
- Label text and leader lines for a part sit inside that part's group, so
  clicking the label works too.
- No scripts, no external references, no embedded raster images.

### Data flow

Tab click or hash change → router shows topic view → viewer fetches
`topics/<id>.json` → viewer fetches the diagram's SVG and inserts it →
user clicks a `data-part` group or a part button → viewer looks up the part
in the topic's `parts` and renders the info panel.

### Error handling

- Topic JSON or SVG fails to load: the topic view shows a short "Couldn't
  load this diagram" message with a Retry button. The tab bar and the
  Periodic Table keep working.
- A part id in an SVG with no text entry (or the reverse) is prevented by
  the automated test below; at runtime the viewer ignores unknown ids
  rather than breaking.

## Testing

**Automated (`tests/test_topics.py`, runs with the existing `pytest`).**
- Every topic JSON parses and has the required fields with non-empty text;
  each part has a details paragraph and at least two facts.
- Every diagram's SVG file exists, is well-formed XML, has a `viewBox`, and
  contains no `<script>` or external references.
- For every diagram, the set of `data-part` ids in the SVG equals the
  diagram's `parts` list, and every listed id exists in the topic's `parts`.
- No part in a topic is unused.
- The tab buttons in `index.html` match the topic files present.

**In the browser.** Each tab and diagram opened at desktop width and phone
width: every part clicked, hash links and back/forward checked, keyboard
selection checked, and the Periodic Table's search, timeline, compare,
detail/atom view and quiz re-checked for regressions.

**Content accuracy.** Facts are kept to well-established school-level
biology and reviewed diagram by diagram.

## Build order

1. Tab framework, shared viewer, automated test, and the **Cells** tab
   (animal and plant cell). **Review checkpoint:** drawing style and level
   of detail are confirmed before the remaining diagrams are drawn.
2. Blood tab (three diagrams).
3. Nervous System tab (three diagrams).
4. Skeleton tab (two diagrams).

## Out of scope

- Quizzes for the biology diagrams.
- Any change to the desktop (Tkinter) app.
- Searching across biology topics.
- Animations, zoom/pan, dark mode.
- Other body systems (heart, lungs, digestion, muscles).
