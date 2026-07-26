# Phase 3 Preform — Expression / Kaomoji Library

Status: **PREFORM**  
Source: Architect screenshots (Worrying · Pointing · Sparkling · Smiling · Love · Hugging · Flexing · Table Flipping · Disapproving · Crying · Classic).

Purpose: **freedom of expression** in seeds, Avatar mood, Tone 05, Show 09, and terminal/GodWorkSpace — pure text, offline, zero image dependency.

---

## 1. Categories (expression packs)

| Pack | Role in Mandell |
|------|-----------------|
| **Classic** | Baseline faces `:-)` `:^)` `^_^` `8-)` |
| **Smiling** | Positive / warm Tone |
| **Love** | Affection / bind-warm |
| **Hugging** | Embrace / merge-feel |
| **Flexing** | Strength / boast / drive |
| **Pointing** | Direction / Drive 19 / Map attention |
| **Sparkling** | Highlight · Pulse · discovery glitter |
| **Worrying** | Caution · Test fail soft signal |
| **Disapproving** | Reject · Logic block soft signal |
| **Crying** | Soft fail / empathy (optional) |
| **Table Flipping** | Hard reject / humor vent (optional, gated) |

These are **not new Dells**. They are **expression tokens** under **05 Tone** and **09 Show**, optional on Avatar entity face-state.

---

## 2. Sample tokens (copy-safe subset)

**Classic:** `:-)` `:^)` `^_^` `(^^)` `;-)` `8-)` `B-)` `:D` `;P`  
**Smiling:** `(^_^)` `(^∇^)` `◎_◎` `(∗‿∗)`  
**Love:** `(♥ω♥)` `(✿♥‿♥)`  
**Pointing:** `→_→` `←_←` `(→_→)`  
**Worrying:** `(;_;)` `(⊙_⊙)`  
**Disapproving:** `ಠ_ಠ` `ಠ⌣ಠ`  
**Sparkling:** `✧` `✦` `★` `☆` mixed with dots

Full grids stay in reference screenshots; runtime ships a **curated JSON pack** per category (Code P3).

---

## 3. Mandell use rules

| Rule | Detail |
|------|--------|
| Optional | Never required for valid seed |
| Tone link | `05[Tone][pack:Smiling]` or inline in Show |
| Avatar | Face-state field on entity (expression pack + frame index) |
| Efficiency | Prefer short tokens; long kaomoji = Hot only |
| Freedom | User/matrix may add custom packs (multi-matrix personal) |
| Gate | Table-flipping / harsh packs = optional filter in Surgical Mod |

---

## 4. Dynamic flow
Expression can **flow with** Cycle 06 / Pulse 25:
- Idle smile → walk neutral → error worry → success sparkle
- FSM hooks: on_state_change → set expression pack

---

## 5. Phase placement
| Work | Phase |
|------|--------|
| Pack JSON data files | Code P3 |
| Show/Tone accept expression field | Code P2–P3 |
| Avatar face-state | Code P2 stub · P3 animate |
| Custom pack load (personal matrix) | P3+ |
