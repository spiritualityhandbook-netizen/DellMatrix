"use strict";
/* DellMatrix Studio frontend — vanilla JS over the Studio API. */

const $ = (sel) => document.querySelector(sel);
const state = {
  owner: "Operator",
  dells: new Map(),       // num -> dell record
  selected: null,         // selected dell record
  receipts: [],           // session receipts, newest first
  lastParse: null,        // last canonical parse rendered on the canvas
  lastOutcome: null,      // per-atom outcomes of the last run (see below)
  lastRunSeed: null,      // exact seed text the last outcome belongs to
};

/* Per-atom outcome evidence. Chain executions return
   result.atom_results: [{dell, ok, skipped, error, reason}] in
   execution order. Outcomes are matched to canvas cards by
   walking both lists in order on dell number — a card only
   gets a verdict when a real receipt names its Dell. Results
   without atom_results (single-atom Core I leaf runs) carry no
   per-atom evidence, so the canvas stays neutral rather than
   painting an inferred outcome. */
function buildOutcome(result) {
  if (!result || !Array.isArray(result.atom_results)) return null;
  return { receipts: result.atom_results.slice(), used: new Set(),
           ok: !!result.ok, partial: !!result.partial };
}

function outcomeFor(outcome, dellNum) {
  if (!outcome) return null;
  for (let i = 0; i < outcome.receipts.length; i++) {
    if (outcome.used.has(i)) continue;
    if (outcome.receipts[i] && outcome.receipts[i].dell === dellNum) {
      outcome.used.add(i);
      return outcome.receipts[i];
    }
  }
  return null;
}

function renderVerdict() {
  const el = $("#canvas-verdict");
  const outcome = state.lastOutcome;
  const current = $("#seed-editor").value.trim();
  if (!outcome || current !== state.lastRunSeed) {
    el.className = "verdict verdict-hidden";
    el.textContent = "";
    return;
  }
  const total = outcome.receipts.length;
  const skipped = outcome.receipts.filter((r) => r && r.skipped).length;
  const failed = outcome.receipts.filter((r) => r && !r.ok && !r.skipped).length;
  if (outcome.partial || skipped > 0) {
    el.className = "verdict verdict-partial";
    el.textContent = "◐ PARTIAL — " + skipped + " skipped of " + total + " atoms";
  } else if (outcome.ok && failed === 0) {
    el.className = "verdict verdict-ok";
    el.textContent = "✓ CHAIN OK — " + total + " atom" + (total === 1 ? "" : "s");
  } else {
    el.className = "verdict verdict-fail";
    el.textContent = "✗ FAILED — " + failed + " of " + total + " atoms";
  }
}

function logConsole(text) {
  const el = $("#console-log");
  el.textContent += text + "\n";
  el.scrollTop = el.scrollHeight;
}

/* One-line per-run console summary, derived ONLY from the same
   result object addReceipt consumes. Status uses addReceipt's
   own classification (partial when the result says partial or
   any_skipped, else ok / failed). Atom and skipped counts come
   from result.atom_results when the result carries per-atom
   receipts; results without them (single-atom Core I leaf runs)
   get NO counts — the summary says so instead of inferring a
   count the engine never reported. A top-level skipped result
   reports its own reason, mirroring addReceipt. */
function summarizeResult(result) {
  if (!result || typeof result !== "object") return "— no result object returned";
  const partial = !!(result.partial || result.any_skipped);
  let line = "— " + (partial ? "PARTIAL" : result.ok ? "OK" : "FAILED");
  if (Array.isArray(result.atom_results)) {
    const total = result.atom_results.length;
    const skipped = result.atom_results.filter((r) => r && r.skipped).length;
    line += " · " + total + " atom" + (total === 1 ? "" : "s")
      + " · " + skipped + " skipped";
  } else {
    line += " · no per-atom receipts in result";
    if (result.skipped) line += " · skipped: " + (result.reason || "honest refusal");
  }
  if (result.error) line += " · " + result.error;
  return line;
}

/* Clear is view-only: it empties the console log element and
   nothing else — receipts, program history and the history
   tail below the console are untouched. */
function clearConsole() {
  $("#console-log").textContent = "";
}

/* ---------- Seed editor syntax tinting ----------
   Display-only underlay: a <pre> behind the (transparent-text)
   textarea, painted by highlightSeed. The tokenizer is a TEXT
   PATTERN highlighter — it executes nothing, decides nothing,
   and is not a parser: the flow canvas above stays the one
   canonical parse surface (/api/parse). Its contract is
   visible-text fidelity: stripping the spans from its output
   returns the exact input text, and every character of user
   text is HTML-escaped before any span is added. */
function escapeHtml(text) {
  return text.replace(/&/g, "&amp;").replace(/</g, "&lt;")
    .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

const TINT_RE = /("(?:[^"\\]|\\.)*")|(\d+)\[([^\]]*)\]|(<:>|>>>|<<|>>|:>|<:|::|>|<|:)|([A-Za-z_][\w-]*)(=)|(\b\d+(?:\.\d+)?\b)/g;

function highlightSeed(text) {
  if (!text) return "";
  let out = "";
  let last = 0;
  TINT_RE.lastIndex = 0;
  let m;
  while ((m = TINT_RE.exec(text)) !== null) {
    out += escapeHtml(text.slice(last, m.index));
    if (m[1] !== undefined) {
      out += "<span class='hl-string'>" + escapeHtml(m[1]) + "</span>";
    } else if (m[2] !== undefined) {
      out += "<span class='hl-num'>" + escapeHtml(m[2]) + "</span>"
        + "<span class='hl-bracket'>[</span>"
        + "<span class='hl-name'>" + escapeHtml(m[3]) + "</span>"
        + "<span class='hl-bracket'>]</span>";
    } else if (m[4] !== undefined) {
      out += "<span class='hl-flow'>" + escapeHtml(m[4]) + "</span>";
    } else if (m[5] !== undefined) {
      out += "<span class='hl-arg'>" + escapeHtml(m[5]) + "</span>"
        + "<span class='hl-flow'>=</span>";
    } else if (m[7] !== undefined) {
      out += "<span class='hl-number'>" + escapeHtml(m[7]) + "</span>";
    }
    last = m.index + m[0].length;
    if (m[0].length === 0) TINT_RE.lastIndex++;
  }
  out += escapeHtml(text.slice(last));
  // A trailing newline collapses in a <pre>; the pad keeps the
  // underlay's height (and scroll sync) matched to the textarea.
  if (text.endsWith("\n")) out += " ";
  return out;
}

/* Repaint the underlay from the editor's current text and keep
   its scroll position locked to the textarea's. */
function syncHighlight() {
  const editor = $("#seed-editor");
  const pre = $("#seed-highlight");
  const code = $("#seed-highlight-code");
  if (!editor || !pre || !code) return;
  code.innerHTML = highlightSeed(editor.value);
  pre.scrollTop = editor.scrollTop;
  pre.scrollLeft = editor.scrollLeft;
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
  let matched = 0;
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
      matched++;
      const item = document.createElement("button");
      item.className = "dell" + (state.selected && state.selected.num === dell.num ? " dell-selected" : "");
      item.innerHTML = "<span class='dell-num'>" + String(dell.num).padStart(2, "0") + "</span>"
        + "<span class='dell-name'>" + dell.name + "</span>";
      item.title = (dell.manor || dell.name) + " — click to insert, or drag into the seed editor";
      item.draggable = true;
      item.addEventListener("click", () => selectDell(dell, true));
      item.addEventListener("dragstart", (e) => {
        if (!e.dataTransfer) return;
        e.dataTransfer.setData(DELL_DRAG_TYPE, String(dell.num));
        e.dataTransfer.setData("text/plain", dellToken(dell));
        e.dataTransfer.effectAllowed = "copy";
        item.classList.add("dell-dragging");
      });
      item.addEventListener("dragend", () => {
        item.classList.remove("dell-dragging");
        $("#seed-editor").classList.remove("editor-drop-target");
      });
      group.appendChild(item);
    }
    rack.appendChild(group);
  }
  if (matched === 0) {
    const none = document.createElement("p");
    none.className = "dim";
    none.textContent = needle
      ? "No Dells match \"" + needle + "\". Press Esc to clear the search."
      : "No Dells loaded — is the Studio server running?";
    rack.appendChild(none);
  }
}

function selectDell(dell, insert) {
  state.selected = dell;
  renderRack($("#rack-search").value);
  if (state.lastParse) renderChain(state.lastParse);
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

/* Rack drag-and-drop: a drag carries ONLY the Dell's number
   under a Studio-specific MIME type. The drop handler resolves
   that number against the canonical rack registry (state.dells)
   and rebuilds the token itself — dragged text is never trusted
   as seed text. The text/plain payload exists only so the drag
   has a readable fallback outside the editor; the editor's drop
   path ignores it when the Dell number resolves. */
const DELL_DRAG_TYPE = "application/x-dellmatrix-dell";

function dellToken(dell) {
  return String(dell.num).padStart(2, "0") + "[" + dell.name + "] :: ";
}

/* Insert text at the editor's caret (or at the end when the
   caret position is unknown) and leave the caret right after
   the inserted text. Works on any editor-shaped object, which
   keeps the caret contract directly testable. */
function insertTextAtCaret(editor, token) {
  const start = typeof editor.selectionStart === "number"
    ? editor.selectionStart : editor.value.length;
  editor.value = editor.value.slice(0, start) + token + editor.value.slice(start);
  if (typeof editor.focus === "function") editor.focus();
  editor.selectionStart = editor.selectionEnd = start + token.length;
  return start + token.length;
}

function insertDell(dell) {
  insertTextAtCaret($("#seed-editor"), dellToken(dell));
  syncHighlight();
  refreshParse();
}

function isDellDrag(e) {
  return !!(e.dataTransfer && Array.from(e.dataTransfer.types || [])
    .includes(DELL_DRAG_TYPE));
}

function handleEditorDrop(e) {
  if (!isDellDrag(e)) return;
  e.preventDefault();
  $("#seed-editor").classList.remove("editor-drop-target");
  const num = parseInt(e.dataTransfer.getData(DELL_DRAG_TYPE), 10);
  const dell = state.dells.get(num);
  if (!dell) return;  // a number the rack does not hold inserts nothing
  selectDell(dell, false);
  insertDell(dell);
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
  state.lastParse = parse;
  if (state.lastOutcome) state.lastOutcome.used = new Set();  // re-match per render
  const chain = $("#chain");
  chain.innerHTML = "";
  renderVerdict();
  if (!parse) {
    chain.innerHTML = "<div class='canvas-empty'><p class='canvas-empty-title'>The canvas is empty</p>"
      + "<p class='dim'>Type a seed below, load an example, or click a Dell in the rack — "
      + "the chain appears here exactly as the engine parses it.</p></div>";
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
    if (state.selected && state.selected.num === atom.num) card.classList.add("atom-selected");
    const receipt = outcomeFor(state.lastOutcome, atom.num);
    if (receipt) {
      if (receipt.skipped) card.classList.add("atom-skipped");
      else if (receipt.ok) card.classList.add("atom-ok");
      else card.classList.add("atom-fail");
    }
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
    if (receipt) {
      const verdict = document.createElement("div");
      verdict.className = "atom-verdict";
      if (receipt.skipped) {
        verdict.textContent = "⊘ skipped — " + (receipt.reason || receipt.error || "honest refusal");
      } else if (receipt.ok) {
        verdict.textContent = "✓ ran";
      } else {
        verdict.textContent = "✗ " + (receipt.error || "failed");
      }
      card.appendChild(verdict);
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
  // Any edit makes the last run's outcome stale: unpaint it now so
  // no card keeps a verdict for a seed that no longer matches.
  if (state.lastOutcome) {
    state.lastOutcome = null;
    state.lastRunSeed = null;
    if (state.lastParse) renderChain(state.lastParse);
  }
  clearTimeout(parseTimer);
  parseTimer = setTimeout(refreshParse, 150);
}

/* ---------- Store + state ---------- */

function storeTypeOf(v) {
  if (v === null) return "null";
  if (Array.isArray(v)) return "list";
  return typeof v;  // string | number | boolean | object
}

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
    const v = storeData[k];
    const full = typeof v === "object" ? JSON.stringify(v) : String(v);
    const tr = document.createElement("tr");
    const tdK = document.createElement("td"); tdK.className = "store-k"; tdK.textContent = k;
    const tdT = document.createElement("td"); tdT.className = "store-t";
    const tag = document.createElement("span");
    tag.className = "type-tag type-" + storeTypeOf(v);
    tag.textContent = storeTypeOf(v);
    tdT.appendChild(tag);
    const tdV = document.createElement("td"); tdV.className = "store-v";
    if (full.length > 80) {
      const span = document.createElement("span");
      span.textContent = full.slice(0, 80) + "…";
      const btn = document.createElement("button");
      btn.className = "store-expand";
      btn.textContent = "expand";
      btn.addEventListener("click", () => {
        const open = btn.textContent === "collapse";
        span.textContent = open ? full.slice(0, 80) + "…" : full;
        btn.textContent = open ? "expand" : "collapse";
      });
      tdV.appendChild(span); tdV.appendChild(btn);
    } else {
      tdV.textContent = full;
    }
    tr.appendChild(tdK); tr.appendChild(tdT); tr.appendChild(tdV);
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
    const partial = !!(r.result && (r.result.partial || r.result.any_skipped));
    row.className = "receipt " + (partial ? "receipt-partial" : ok ? "receipt-ok" : "receipt-fail");
    const skipped = r.result && r.result.skipped ? " · skipped: " + (r.result.reason || "honest refusal") : "";
    const err = r.result && r.result.error ? " · " + r.result.error : "";
    row.innerHTML = "<span class='receipt-when'></span><span class='receipt-seed'></span><span class='receipt-verdict'></span>";
    row.querySelector(".receipt-when").textContent = r.when;
    row.querySelector(".receipt-seed").textContent = r.seed;
    row.querySelector(".receipt-verdict").textContent = (partial ? "PARTIAL" : ok ? "OK" : "FAILED") + skipped + err;
    // Click-to-reload: the handler closes over r.seed — the
    // session record of what was actually run — never the
    // row's rendered (ellipsized) text.
    row.title = "Load this seed into the editor — does not run it";
    row.tabIndex = 0;
    row.addEventListener("click", () => reloadReceiptSeed(r.seed));
    row.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); reloadReceiptSeed(r.seed); }
    });
    el.appendChild(row);
  }
}

/* ---------- Receipt reload ----------
   Clicking a receipt reloads its seed into the editor so a
   past run can be inspected, edited and re-run. Reload is a
   pure editor action: it NEVER executes — running the seed
   stays the user's sovereign step (RUN button / Ctrl+Enter).
   If the reloaded seed is not the latest run's seed, that
   run's per-atom outcome is cleared first — the same
   staleness rule the editor's input path applies — so no
   canvas card can keep a verdict earned by different text.
   Reloading the latest run's own seed keeps its outcome:
   the verdicts genuinely belong to that exact text. */
function prepareReceiptReload(seed) {
  if (typeof seed !== "string" || !seed) return false;
  if (seed !== state.lastRunSeed) {
    state.lastOutcome = null;
    state.lastRunSeed = null;
  }
  return true;
}

function loadReceiptSeed(editor, seed) {
  if (!editor || typeof seed !== "string" || !seed) return false;
  editor.value = seed;
  if (typeof editor.focus === "function") editor.focus();
  editor.selectionStart = editor.selectionEnd = seed.length;
  return true;
}

function reloadReceiptSeed(seed) {
  if (!prepareReceiptReload(seed)) return;
  switchView("studio");
  if (!loadReceiptSeed($("#seed-editor"), seed)) return;
  syncHighlight();
  refreshParse();
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
    state.lastOutcome = buildOutcome(data.result);
    state.lastRunSeed = seed;
    if (state.lastParse) renderChain(state.lastParse);
    showResult(data.result);
    logConsole(JSON.stringify(data.result, null, 2));
    logConsole(summarizeResult(data.result));
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

/* Canonical growth stages, in order (form.dell_matrix.forces
   _STAGES; the lens in view_rooms attributes a stage only where
   plant identity is proven). Nodes without a proven stage are
   grouped last, under their honest stage_source — never assigned
   a stage the lens did not give them. */
const STAGE_ORDER = ["seed", "sprout", "stem", "branch", "leaf", "fruit"];

function groupByStage(nodes) {
  const groups = new Map();
  for (const stage of STAGE_ORDER) groups.set(stage, []);
  groups.set("__none__", []);
  for (const node of nodes || []) {
    if (node.stage && groups.has(node.stage)) groups.get(node.stage).push(node);
    else groups.get("__none__").push(node);
  }
  return [...groups.entries()].filter(([, items]) => items.length);
}

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
    for (const [stage, items] of groupByStage(nodes)) {
      const section = document.createElement("div");
      section.className = "growth-group";
      const head = document.createElement("div");
      head.className = "growth-group-head";
      head.textContent = stage === "__none__"
        ? "NO STAGE CLAIM — identity not proven"
        : stage.toUpperCase() + " · " + items.length;
      section.appendChild(head);
      const cards = document.createElement("div");
      cards.className = "growth-cards";
      for (const node of items) {
        const card = document.createElement("div");
        card.className = "plant";
        card.innerHTML = "<div class='plant-label'></div><div class='plant-stage'></div>";
        card.querySelector(".plant-label").textContent = node.label || node.id;
        card.querySelector(".plant-stage").textContent =
          node.stage ? ("stage: " + node.stage + (node.stage_source ? " · " + node.stage_source : "")) : "stage: —";
        cards.appendChild(card);
      }
      section.appendChild(cards);
      el.appendChild(section);
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
  syncHighlight();
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

function clearSelection() {
  state.selected = null;
  renderRack($("#rack-search").value);
  if (state.lastParse) renderChain(state.lastParse);
  $("#inspector").innerHTML = "<p class='dim'>Select a Dell in the rack, or run a seed.</p>";
}

document.addEventListener("DOMContentLoaded", () => {
  $("#rack-search").addEventListener("input", (e) => renderRack(e.target.value));
  document.addEventListener("keydown", (e) => {
    const tag = (e.target && e.target.tagName) || "";
    const typing = tag === "TEXTAREA" || tag === "INPUT" || tag === "SELECT";
    if (e.key === "/" && !typing) {
      e.preventDefault();
      $("#rack-search").focus();
      $("#rack-search").select();
    } else if (e.key === "Escape") {
      // Esc clears selection states: rack filter, Dell selection,
      // and focus — it never touches the seed text itself.
      if ($("#rack-search").value) { $("#rack-search").value = ""; renderRack(""); }
      if (state.selected) clearSelection();
      if (typing && e.target.blur) e.target.blur();
    }
  });
  $("#seed-editor").addEventListener("dragover", (e) => {
    if (!isDellDrag(e)) return;
    e.preventDefault();  // allow the drop; non-Dell drags keep native behavior
    if (e.dataTransfer) e.dataTransfer.dropEffect = "copy";
    $("#seed-editor").classList.add("editor-drop-target");
  });
  $("#seed-editor").addEventListener("dragleave", () => {
    $("#seed-editor").classList.remove("editor-drop-target");
  });
  $("#seed-editor").addEventListener("drop", handleEditorDrop);
  $("#seed-editor").addEventListener("input", () => { syncHighlight(); renderChainSoon(); });
  $("#seed-editor").addEventListener("scroll", syncHighlight);
  $("#seed-editor").addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") { e.preventDefault(); execute(); }
  });
  $("#execute-btn").addEventListener("click", execute);
  $("#clear-btn").addEventListener("click", () => { $("#seed-editor").value = ""; syncHighlight(); refreshParse(); });
  $("#examples").addEventListener("change", (e) => {
    if (e.target.value) { $("#seed-editor").value = e.target.value; syncHighlight(); refreshParse(); }
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
      state.lastOutcome = null;
      state.lastRunSeed = null;
      if (state.lastParse) renderChain(state.lastParse);
      state.receipts = [];
      $("#receipts").innerHTML = "<p class='dim'>No runs yet for this owner.</p>";
      if (!$("#view-growth").classList.contains("view-hidden")) loadGrowth();
      logConsole("Switched owner to " + owner);
    } catch (err) { setStatus("error", err.message); }
  });
  for (const tab of document.querySelectorAll(".tab")) {
    tab.addEventListener("click", () => switchView(tab.dataset.view));
  }
  $("#growth-refresh").addEventListener("click", loadGrowth);
  $("#console-clear").addEventListener("click", clearConsole);
  init();
});
