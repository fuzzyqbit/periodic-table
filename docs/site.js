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
