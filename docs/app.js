"use strict";

const state = {
  data: null,
  byZ: new Map(),
  cells: new Map(),       // Z -> HTMLElement
  comparePick: null,      // Element or null
  quiz: {
    target: null,
    startedAt: null,
    score: 0,
    attempts: 0,
    timerId: null,
    handlerActive: false,
  },
};

// --- bootstrap ------------------------------------------------------------

(async function init() {
  const res = await fetch("elements.json");
  state.data = await res.json();
  state.data.elements.forEach(e => state.byZ.set(e.z, e));
  buildGrid();
  buildLegend();
  wireToolbar();
  wireModals();
})().catch(err => {
  document.body.innerHTML = `<pre style="padding:20px;color:#c00">Failed to load elements.json: ${err}</pre>`;
});

// --- grid ----------------------------------------------------------------

function buildGrid() {
  const grid = document.getElementById("grid");
  const { elements, category_colors, lanthanide_placeholder, actinide_placeholder } = state.data;

  for (const el of elements) {
    const cell = document.createElement("div");
    cell.className = "cell";
    cell.style.background = category_colors[el.category];
    cell.style.gridRow = (el.row + 1).toString();
    cell.style.gridColumn = (el.col + 1).toString();
    cell.dataset.z = el.z.toString();
    cell.innerHTML = `
      <div class="z">${el.z}</div>
      <div class="sym">${el.symbol}</div>
      <div class="mass">${formatMass(el.mass)}</div>
    `;
    cell.addEventListener("click", ev => onCellClick(el, ev));
    grid.appendChild(cell);
    state.cells.set(el.z, cell);
  }

  const ph1 = makePlaceholder("*", lanthanide_placeholder);
  const ph2 = makePlaceholder("**", actinide_placeholder);
  grid.appendChild(ph1);
  grid.appendChild(ph2);

  const banner = document.createElement("div");
  banner.className = "title-banner";
  banner.textContent = "Periodic Table of Elements";
  grid.appendChild(banner);
}

function makePlaceholder(text, [row, col]) {
  const el = document.createElement("div");
  el.className = "cell placeholder";
  el.style.gridRow = (row + 1).toString();
  el.style.gridColumn = (col + 1).toString();
  el.textContent = text;
  return el;
}

function formatMass(m) {
  if (m === null || m === undefined) return "";
  return m >= 100 ? m.toFixed(1) : m.toFixed(3);
}

function onCellClick(element, ev) {
  if (ev.shiftKey) return handleShiftClick(element);
  if (state.quiz.handlerActive) return handleQuizClick(element);
  openDetail(element);
}

// --- legend --------------------------------------------------------------

const LEGEND_ORDER = [
  "ALKALI_METAL", "ALKALINE_EARTH", "TRANSITION_METAL", "POST_TRANSITION",
  "METALLOID", "NONMETAL", "HALOGEN", "NOBLE_GAS",
  "LANTHANIDE", "ACTINIDE", "UNKNOWN",
];

const LEGEND_LABELS = {
  ALKALI_METAL: "alkali metal",
  ALKALINE_EARTH: "alkaline earth",
  TRANSITION_METAL: "transition metal",
  POST_TRANSITION: "post-transition metal",
  METALLOID: "metalloid",
  NONMETAL: "nonmetal",
  HALOGEN: "halogen",
  NOBLE_GAS: "noble gas",
  LANTHANIDE: "lanthanide",
  ACTINIDE: "actinide",
  UNKNOWN: "unknown",
};

function buildLegend() {
  const legend = document.getElementById("legend");
  for (const cat of LEGEND_ORDER) {
    const item = document.createElement("div");
    item.className = "legend-item";
    item.innerHTML = `
      <span class="legend-swatch" style="background:${state.data.category_colors[cat]}"></span>
      <span>${LEGEND_LABELS[cat]}</span>
    `;
    legend.appendChild(item);
  }
}

// --- toolbar (search, quiz, timeline) ------------------------------------

function wireToolbar() {
  const search = document.getElementById("search");
  search.addEventListener("input", () => highlight(search.value));

  document.getElementById("quiz-btn").addEventListener("click", openQuiz);

  const year = document.getElementById("year");
  const label = document.getElementById("year-label");
  year.addEventListener("input", () => {
    label.textContent = year.value;
    filterByYear(parseInt(year.value, 10));
  });

  document.getElementById("year-reset").addEventListener("click", () => {
    year.value = "2025";
    label.textContent = "2025";
    filterByYear(2025);
  });
}

function matchElement(query, e) {
  const q = (query || "").trim();
  if (!q) return true;
  const ql = q.toLowerCase();
  if (e.symbol.toLowerCase() === ql) return true;
  if (e.name.toLowerCase().startsWith(ql)) return true;
  const n = parseInt(q, 10);
  if (!Number.isNaN(n) && n === e.z) return true;
  return false;
}

function highlight(query) {
  for (const el of state.data.elements) {
    const cell = state.cells.get(el.z);
    cell.classList.toggle("dim", !matchElement(query, el));
  }
}

function filterByYear(year) {
  for (const el of state.data.elements) {
    const cell = state.cells.get(el.z);
    const ok = el.discovered === 0 || el.discovered <= year;
    cell.classList.toggle("hidden", !ok);
  }
}

// --- modals --------------------------------------------------------------

function wireModals() {
  for (const btn of document.querySelectorAll("[data-close]")) {
    btn.addEventListener("click", () => {
      document.getElementById(btn.dataset.close).hidden = true;
    });
  }
  for (const modal of document.querySelectorAll(".modal")) {
    modal.addEventListener("click", ev => {
      if (ev.target === modal) modal.hidden = true;
    });
  }
  document.addEventListener("keydown", ev => {
    if (ev.key !== "Escape") return;
    for (const modal of document.querySelectorAll(".modal")) {
      modal.hidden = true;
    }
    if (state.comparePick) {
      state.cells.get(state.comparePick.z).classList.remove("compare-pick");
      state.comparePick = null;
    }
  });

  document.getElementById("show-atom").addEventListener("click", () => {
    const z = parseInt(document.getElementById("show-atom").dataset.z, 10);
    if (!Number.isNaN(z)) openAtom(state.byZ.get(z));
  });
}

// --- detail view ---------------------------------------------------------

const DETAIL_FIELDS = [
  ["Name", e => e.name],
  ["Symbol", e => e.symbol],
  ["Atomic number", e => e.z],
  ["Atomic mass", e => e.mass],
  ["Period", e => e.period],
  ["Group", e => e.group],
  ["Category", e => e.category_label],
  ["Electron config", e => e.electron_config],
  ["Electronegativity", e => e.electronegativity],
  ["Phase", e => e.phase],
  ["Discovered", e => e.discovered === 0 ? "antiquity" : e.discovered],
];

function fmt(v) {
  return v === null || v === undefined ? "—" : String(v);
}

function openDetail(element) {
  document.getElementById("detail-title").textContent = `${element.name} (${element.symbol})`;
  const dl = document.getElementById("detail-fields");
  dl.innerHTML = "";
  for (const [label, getter] of DETAIL_FIELDS) {
    const dt = document.createElement("dt");
    dt.textContent = label;
    const dd = document.createElement("dd");
    dd.textContent = fmt(getter(element));
    dl.appendChild(dt);
    dl.appendChild(dd);
  }
  document.getElementById("show-atom").dataset.z = element.z.toString();
  document.getElementById("detail-modal").hidden = false;
}

// --- atom view (Bohr) ----------------------------------------------------

const ATOM = { size: 600, nucleusR: 20, innerOffset: 30, outerMax: 250, electronR: 4 };
const SHELL_CAPS = [2, 8, 18, 32, 32, 18, 8];

function fillShells(z) {
  let remaining = z;
  const result = [];
  for (const cap of SHELL_CAPS) {
    if (remaining === 0) break;
    const n = Math.min(cap, remaining);
    result.push(n);
    remaining -= n;
  }
  return result;
}

function openAtom(element) {
  document.getElementById("atom-title").textContent = `Atom — ${element.name}`;
  document.getElementById("atom-modal").hidden = false;
  drawAtom(element);
}

function drawAtom(element) {
  const canvas = document.getElementById("atom-canvas");
  const ctx = canvas.getContext("2d");
  const cx = ATOM.size / 2;
  const cy = ATOM.size / 2;
  ctx.clearRect(0, 0, ATOM.size, ATOM.size);

  ctx.fillStyle = "#444";
  ctx.beginPath();
  ctx.arc(cx, cy, ATOM.nucleusR, 0, Math.PI * 2);
  ctx.fill();

  ctx.fillStyle = "#ffffff";
  ctx.font = "bold 11px sans-serif";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillText(element.symbol, cx, cy - 5);
  ctx.fillText(element.z.toString(), cx, cy + 7);

  const shells = fillShells(element.z);
  const step = Math.floor(ATOM.outerMax / shells.length);

  for (let i = 1; i <= shells.length; i++) {
    const r = ATOM.innerOffset + i * step;
    ctx.strokeStyle = "#999";
    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.stroke();

    const count = shells[i - 1];
    ctx.fillStyle = "#1f77b4";
    for (let n = 0; n < count; n++) {
      const theta = (2 * Math.PI * n) / count;
      const x = cx + r * Math.cos(theta);
      const y = cy + r * Math.sin(theta);
      ctx.beginPath();
      ctx.arc(x, y, ATOM.electronR, 0, Math.PI * 2);
      ctx.fill();
    }
  }
}

// --- compare -------------------------------------------------------------

function handleShiftClick(element) {
  if (state.comparePick === null) {
    state.comparePick = element;
    state.cells.get(element.z).classList.add("compare-pick");
    return;
  }
  const first = state.comparePick;
  state.cells.get(first.z).classList.remove("compare-pick");
  state.comparePick = null;
  if (first.z === element.z) return;
  openCompare(first, element);
}

function openCompare(a, b) {
  const table = document.getElementById("compare-table");
  table.innerHTML = "";

  const head = document.createElement("tr");
  head.innerHTML = `<th></th><th>${a.name} (${a.symbol})</th><th>${b.name} (${b.symbol})</th><th>Δ</th>`;
  table.appendChild(head);

  for (const [label, getter] of DETAIL_FIELDS) {
    const va = getter(a);
    const vb = getter(b);
    const tr = document.createElement("tr");
    const differs = va !== vb;
    tr.classList.toggle("differs", differs);
    tr.innerHTML = `
      <td class="label">${label}</td>
      <td>${fmt(va)}</td>
      <td>${fmt(vb)}</td>
      <td class="delta">${deltaLabel(va, vb)}</td>
    `;
    table.appendChild(tr);
  }

  document.getElementById("compare-modal").hidden = false;
}

function deltaLabel(a, b) {
  if (typeof a === "number" && typeof b === "number") {
    const d = b - a;
    const sign = d >= 0 ? "+" : "";
    return `${sign}${(+d.toFixed(4)).toString()}`;
  }
  return a === b ? "✓" : "≠";
}

// --- quiz ----------------------------------------------------------------

function openQuiz() {
  document.getElementById("quiz-modal").hidden = false;
  resetQuizUi();
  state.quiz.score = 0;
  state.quiz.attempts = 0;
  updateScore();
}

function resetQuizUi() {
  document.getElementById("quiz-prompt").textContent = "Press Start";
  document.getElementById("quiz-timer").textContent = "0.0 s";
  const action = document.getElementById("quiz-action");
  action.textContent = "Start";
  action.onclick = quizStart;
}

function quizStart() {
  const list = state.data.elements;
  state.quiz.target = list[Math.floor(Math.random() * list.length)];
  state.quiz.startedAt = performance.now();
  state.quiz.handlerActive = true;

  const t = state.quiz.target;
  document.getElementById("quiz-prompt").textContent =
    `Find: ${t.name}  (${t.symbol}, Z=${t.z})`;

  const action = document.getElementById("quiz-action");
  action.textContent = "Skip";
  action.onclick = quizSkip;

  quizTick();
}

function quizTick() {
  if (state.quiz.startedAt === null) return;
  const elapsed = (performance.now() - state.quiz.startedAt) / 1000;
  document.getElementById("quiz-timer").textContent = `${elapsed.toFixed(1)} s`;
  state.quiz.timerId = requestAnimationFrame(quizTick);
}

function handleQuizClick(element) {
  const target = state.quiz.target;
  if (!target) return;
  state.quiz.attempts++;
  const correct = element.z === target.z;
  flashCell(element.z, correct ? "flash-correct" : "flash-wrong");
  if (correct) {
    state.quiz.score++;
    endQuizRound(true);
  }
  updateScore();
}

function quizSkip() {
  if (!state.quiz.target) return;
  state.quiz.attempts++;
  endQuizRound(false);
  updateScore();
}

function endQuizRound(correct) {
  state.quiz.handlerActive = false;
  if (state.quiz.timerId) cancelAnimationFrame(state.quiz.timerId);
  state.quiz.startedAt = null;

  const promptEl = document.getElementById("quiz-prompt");
  promptEl.textContent += correct ? "  — correct!" : "  — skipped.";

  const action = document.getElementById("quiz-action");
  action.textContent = "Next";
  action.onclick = quizStart;
}

function updateScore() {
  document.getElementById("quiz-score").textContent =
    `Score: ${state.quiz.score} / ${state.quiz.attempts}`;
}

function flashCell(z, className) {
  const cell = state.cells.get(z);
  cell.classList.add(className);
  setTimeout(() => cell.classList.remove(className), 450);
}
