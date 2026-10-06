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
