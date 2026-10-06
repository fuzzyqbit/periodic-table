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

wireTabs();
