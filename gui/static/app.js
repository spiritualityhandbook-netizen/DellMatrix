"use strict";
/* DellMatrix Studio frontend — vanilla JS over the Studio API. */

const $ = (sel) => document.querySelector(sel);
const state = {
  owner: "Operator",
  dells: new Map(),       // num -> dell record
  selected: null,         // selected dell record
  receipts: [],           // session receipts, newest first
};

function logConsole(text) {
  const el = $("#console-log");
  el.textContent += text + "\n";
  el.scrollTop = el.scrollHeight;
}

function setStatus(mode, text) {
  const led = $("#status-led");
  led.className = "led led-" + mode;
  $("#status-text").textContent = text;
}

async function api(path, options) {
  const res = await fetch(path, options);
  const data = await res.json().catch(() => ({ ok: false, error: "bad JSON from server" }));
  if (!data.ok) throw new Error(data.error || ("HTTP " + res.status));
  return data;
}

/* ---------- Dell rack ---------- */

function renderRack(filter) {
  const rack = $("#rack");
  rack.innerHTML = "";
  const needle = (filter || "").trim().toLowerCase();
  for (const core of ["I", "II"]) {
    const group = document.createElement("div");
    group.className = "rack-group";
    const head = document.createElement("div");
    head.className = "rack-group-head";
    head.textContent = core === "I" ? "CORE I — ACTION SPINE · 00–50" : "CORE II — INSTRUCTION ARCHITECTURE · 51–99";
    group.appendChild(head);
    for (const dell of state.dells.values()) {
      if (dell.core !== core) continue;
      if (needle && !(dell.name.toLowerCase().includes(needle)
          || String(dell.num).padStart(2, "0").includes(needle)
          || (dell.manor || "").toLowerCase().includes(needle))) continue;
      const item = document.createElement("button");
      item.className = "dell" + (state.selected && state.selected.num === dell.num ? " dell-selected" : "");
      item.innerHTML = "<span class='dell-num'>" + String(dell.num).padStart(2, "0") + "</span>"
        + "<span class='dell-name'>" + dell.name + "</span>";
      item.title = dell.manor || dell.name;
      item.addEventListener("click", () => selectDell(dell, true));
      group.appendChild(item);
    }
    rack.appendChild(group);
  }
}

function selectDell(dell, insert) {
  state.selected = dell;
  renderRack($("#rack-search").value);
  const insp = $("#inspector");
  insp.innerHTML = "";
  const title = document.createElement("div");
  title.className = "insp-title";
  title.textContent = String(dell.num).padStart(2, "0") + " · " + dell.name;
  insp.appendChild(title);
  const rows = [["Core", "Core " + dell.core],
                ["Manor", dell.manor || "—"],
                ["Family", dell.family || "—"],
                ["Effect", dell.effect || "—"],
                ["Root", dell.root || "—"]];
  for (const [k, v] of rows) {
    const row = document.createElement("div");
    row.className = "insp-row";
    row.innerHTML = "<span class='insp-k'></span><span class='insp-v'></span>";
    row.querySelector(".insp-k").textContent = k;
    row.querySelector(".insp-v").textContent = v;
    insp.appendChild(row);
  }
  if (insert) insertDell(dell);
}

function insertDell(dell) {
  const editor = $("#seed-editor");
  const token = String(dell.num).padStart(2, "0") + "[" + dell.name + "] :: ";
  const start = editor.selectionStart || editor.value.length;
  editor.value = editor.value.slice(0, start) + token + editor.value.slice(start);
  editor.focus();
  editor.selectionStart = editor.selectionEnd = start + token.length;
  refreshParse();
}

/* ---------- Flow canvas ----------
   The canvas renders the CANONICAL parse from /api/parse
   (form.mandell.seed.parse_seed): real atoms, real flow
   operators, arguments and segment labels. A parse refusal
   is shown with the parser's own reason — the canvas never
   guesses a chain the engine would reject. */

let parseSeq = 0;
let parseTimer = null;

function renderChain(parse) {
  const chain = $("#chain");
  chain.innerHTML = "";
  if (!parse) {
    chain.innerHTML = "<p class='dim'>The canvas mirrors your seed. Start typing, or click a Dell.</p>";
    return;
  }
  if (!parse.ok) {
    const box = document.createElement("div");
    box.className = "parse-error";
    box.textContent = "Seed does not parse: " + (parse.error || "unknown refusal");
    chain.appendChild(box);
    return;
  }
  parse.atoms.forEach((atom, i) => {
    if (i > 0) {
      const link = document.createElement("div");
      link.className = "atom-link";
      link.textContent = parse.flows[i - 1] || ">";
      chain.appendChild(link);
    }
    const card = document.createElement("button");
    card.className = "atom";
    card.type = "button";
    const dell = state.dells.get(atom.num);
    const head = document.createElement("div");
    head.className = "atom-head";
    head.innerHTML = "<span class='atom-num'></span><span class='atom-name'></span>";
    head.querySelector(".atom-num").textContent = String(atom.num).padStart(2, "0");
    head.querySelector(".atom-name").textContent = atom.name || (dell ? dell.name : "?");
    card.appendChild(head);
    const sub = document.createElement("div");
    sub.className = "atom-op";
    const bits = [];
    if (atom.term && atom.term !== atom.name) bits.push(atom.term);
    if (atom.label) bits.push(":: " + atom.label);
    sub.textContent = bits.length ? bits.join("  ") : "·";
    card.appendChild(sub);
    const argKeys = Object.keys(atom.args || {});
    if (argKeys.length) {
      const args = document.createElement("div");
      args.className = "atom-args";
      for (const k of argKeys) {
        const chip = document.createElement("span");
        chip.className = "arg-chip";
        chip.textContent = k + "=\"" + atom.args[k] + "\"";
        args.appendChild(chip);
      }
      card.appendChild(args);
    }
    if (atom.origin && atom.origin !== "atom") {
      const badge = document.createElement("div");
      badge.className = "atom-origin";
      badge.textContent = atom.origin;
      card.appendChild(badge);
    }
    card.addEventListener("click", () => { if (dell) selectDell(dell, false); });
    chain.appendChild(card);
  });
  if (parse.label && parse.atoms.length > 1) {
    const tail = document.createElement("div");
    tail.className = "chain-label";
    tail.textContent = "label: " + parse.label;
    chain.appendChild(tail);
  }
}

async function refreshParse() {
  const text = $("#seed-editor").value;
  const seq = ++parseSeq;
  if (!text.trim()) { renderChain(null); return; }
  try {
    const data = await api("/api/parse", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ seed: text }),
    });
    if (seq !== parseSeq) return;  // a newer edit already won
    renderChain(data.parse);
  } catch (err) {
    if (seq !== parseSeq) return;
    const chain = $("#chain");
    chain.innerHTML = "";
    const box = document.createElement("div");
    box.className = "parse-error";
    box.textContent = "Parse unavailable: " + err.message;
    chain.appendChild(box);
  }
}

function renderChainSoon() {
  clearTimeout(parseTimer);
  parseTimer = setTimeout(refreshParse, 150);
}

/* ---------- Store + state ---------- */

function renderStore(storeData) {
  const el = $("#store");
  const keys = Object.keys(storeData || {});
  $("#store-count").textContent = keys.length ? keys.length + " keys" : "";
  el.innerHTML = "";
  if (!keys.length) {
    el.innerHTML = "<p class='dim'>Store is empty. Try 55[Set] :: tempo=120</p>";
    return;
  }
  const table = document.createElement("table");
  table.className = "store-table";
  for (const k of keys.sort()) {
    const tr = document.createElement("tr");
    const tdK = document.createElement("td"); tdK.className = "store-k"; tdK.textContent = k;
    const tdV = document.createElement("td"); tdV.className = "store-v";
    tdV.textContent = typeof storeData[k] === "object" ? JSON.stringify(storeData[k]) : String(storeData[k]);
    tr.appendChild(tdK); tr.appendChild(tdV);
    table.appendChild(tr);
  }
  el.appendChild(table);
}

function applyState(st) {
  if (!st) return;
  state.owner = st.owner;
  $("#owner-input").value = st.owner;
  renderStore(st.store);
  const hist = $("#history-tail");
  if (hist) {
    const tail = st.history_tail || [];
    hist.textContent = tail.length
      ? tail.map((h) => typeof h === "object" ? JSON.stringify(h) : String(h)).join("\n")
      : "(no program history yet)";
  }
  setStatus("idle", "engine ready · owner " + st.owner
    + " · store " + st.store_count + " · plants " + st.plant_count
    + " · history " + st.history_count);
}

/* ---------- Execution ---------- */

function addReceipt(seed, result) {
  const when = new Date().toLocaleTimeString();
  state.receipts.unshift({ when, seed, result });
  const el = $("#receipts");
  el.innerHTML = "";
  for (const r of state.receipts.slice(0, 50)) {
    const row = document.createElement("div");
    const ok = r.result && r.result.ok;
    row.className = "receipt " + (ok ? "receipt-ok" : "receipt-fail");
    const skipped = r.result && r.result.skipped ? " · skipped: " + (r.result.reason || "honest refusal") : "";
    const err = r.result && r.result.error ? " · " + r.result.error : "";
    row.innerHTML = "<span class='receipt-when'></span><span class='receipt-seed'></span><span class='receipt-verdict'></span>";
    row.querySelector(".receipt-when").textContent = r.when;
    row.querySelector(".receipt-seed").textContent = r.seed;
    row.querySelector(".receipt-verdict").textContent = (ok ? "OK" : "FAILED") + skipped + err;
    el.appendChild(row);
  }
}

async function execute() {
  const seed = $("#seed-editor").value.trim();
  if (!seed) { setStatus("idle", "type a seed first"); return; }
  setStatus("busy", "running…");
  logConsole("> " + seed);
  try {
    const data = await api("/api/execute", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ seed, owner: state.owner }),
    });
    addReceipt(seed, data.result);
    applyState(data.state);
    showResult(data.result);
    logConsole(JSON.stringify(data.result, null, 2));
    setStatus("idle", "done · " + (data.result.ok ? "ok" : "failed — see receipts"));
  } catch (err) {
    setStatus("error", "server error: " + err.message);
    logConsole("ERROR " + err.message);
  }
}

function showResult(result) {
  const insp = $("#inspector");
  insp.innerHTML = "";
  const title = document.createElement("div");
  title.className = "insp-title";
  title.textContent = "Last result — " + (result.ok ? "OK" : "FAILED");
  insp.appendChild(title);
  const pre = document.createElement("pre");
  pre.className = "insp-json";
  pre.textContent = JSON.stringify(result, null, 2);
  insp.appendChild(pre);
}

/* ---------- Growth view ---------- */

async function loadGrowth() {
  const el = $("#growth");
  el.innerHTML = "<p class='dim'>loading the field…</p>";
  try {
    const data = await api("/api/growth?owner=" + encodeURIComponent(state.owner));
    const nodes = (data.growth && data.growth.nodes) || [];
    el.innerHTML = "";
    if (!nodes.length) {
      el.innerHTML = "<p class='dim'>No plants in this owner's field yet. Growth appears as ideas are planted and grown.</p>";
      return;
    }
    for (const node of nodes) {
      const card = document.createElement("div");
      card.className = "plant";
      card.innerHTML = "<div class='plant-label'></div><div class='plant-stage'></div>";
      card.querySelector(".plant-label").textContent = node.label || node.id;
      card.querySelector(".plant-stage").textContent =
        node.stage ? ("stage: " + node.stage + (node.stage_source ? " · " + node.stage_source : "")) : "stage: —";
      el.appendChild(card);
    }
  } catch (err) {
    el.innerHTML = "<p class='dim'>Growth unavailable: " + err.message + "</p>";
  }
}

/* ---------- Wiring ---------- */

function switchView(name) {
  for (const tab of document.querySelectorAll(".tab")) {
    tab.classList.toggle("tab-active", tab.dataset.view === name);
  }
  for (const view of document.querySelectorAll(".view")) {
    view.classList.toggle("view-hidden", view.id !== "view-" + name);
  }
  if (name === "growth") loadGrowth();
}

async function init() {
  try {
    const data = await api("/api/dells");
    for (const dell of data.dells) state.dells.set(dell.num, dell);
    renderRack("");
    refreshParse();
    const st = await api("/api/state");
    applyState(st.state);
    logConsole("DellMatrix Studio connected. 100 Dells in the rack.");
  } catch (err) {
    setStatus("error", "cannot reach the Studio server: " + err.message);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  $("#rack-search").addEventListener("input", (e) => renderRack(e.target.value));
  $("#seed-editor").addEventListener("input", renderChainSoon);
  $("#seed-editor").addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") { e.preventDefault(); execute(); }
  });
  $("#execute-btn").addEventListener("click", execute);
  $("#clear-btn").addEventListener("click", () => { $("#seed-editor").value = ""; refreshParse(); });
  $("#examples").addEventListener("change", (e) => {
    if (e.target.value) { $("#seed-editor").value = e.target.value; refreshParse(); }
    e.target.value = "";
  });
  $("#owner-apply").addEventListener("click", async () => {
    const owner = $("#owner-input").value.trim();
    if (!owner) return;
    try {
      const data = await api("/api/owner", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ owner }),
      });
      applyState(data.state);
      state.receipts = [];
      $("#receipts").innerHTML = "<p class='dim'>No runs yet for this owner.</p>";
      logConsole("Switched owner to " + owner);
    } catch (err) { setStatus("error", err.message); }
  });
  for (const tab of document.querySelectorAll(".tab")) {
    tab.addEventListener("click", () => switchView(tab.dataset.view));
  }
  $("#growth-refresh").addEventListener("click", loadGrowth);
  init();
});
