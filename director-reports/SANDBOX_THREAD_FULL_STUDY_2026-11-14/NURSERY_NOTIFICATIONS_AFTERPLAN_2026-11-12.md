# Nursery Notifications — Afterplan Design Record (2026-11-12)

**Status: AFTERPLAN — parked by Ace (2026-11-12 22:58 CST) to be sequenced AFTER
the current Master Plan. NO implementation, NO PR, NO merge is authorized from
this record. The grounding below is preserved so the future circuit starts from
verified repository reality instead of rediscovery.**

Origin: Ace directive, 2026-11-12 22:53 CST — "Add notifications to nursery so
in addition to proposals you can get numbered notifications you can evoke via
chat." Ace placement ruling, same evening: it waits in the plan after the
Master Plan currently in progress (same channel as the HCN Afterplan).

## Grounding (read-only lane, clone verified at main d97a487, 2026-11-12)

- The Nursery is a single clean authority: `form/dell_matrix/nursery.py`.
  Proposals are keyed by content-derived slug IDs (`_slug`, nursery.py:74–86);
  statuses pending | confirmed | rejected; per-owner persistence at
  `form/state/nursery_<owner>.json` via crash-safe atomic write, an
  optimistic-concurrency guard (`NurseryConflictError`), and fail-closed load
  (`NurseryLoadError` — a corrupt file is never silently replaced).
- **Numbering is ABSENT.** Chat listings show transient enumerate indices
  (form/repl.py:525) that shift on any add/confirm/reject, cap at the first 20
  pending, and are not accepted as input (`confirm 3` passes "3" as a pid and
  fails). Nothing user-facing carries a stable per-owner sequential number.
- **No notification concept exists** (searched notify / notification / inbox /
  alert; the ambient-gate inbox and idea-event listeners are unrelated
  mechanisms). Notification store, unread/read/dismissed states, and
  evoke-by-number verbs are all ABSENT.
- **Structural precedent EXISTS:** the nursery file already carries a second,
  non-proposal record class under a reserved section key
  (`DISPOSITION_SECTION_KEY = "__conflict_dispositions__"`, DCC-XIX), staged
  separately on load. Notifications follow the same slot — same file, same
  save/load, no sidecar, no second store.
- **Honesty correction:** the Nursery ranking formula's 200 pending cap and
  eviction/tombstone machinery are NOT implemented in nursery.py at this HEAD
  (confirmed by Ace 2026-11-08, still awaiting its own circuit). There is no
  eviction hook to build on, and the proposals' 200 cap does NOT transfer to
  notifications — notifications need their own bound by ruling.

## Design shape (smallest extension of the existing authority)

- `form/dell_matrix/nursery.py`: `Notification` dataclass — `number` (per-owner
  sequential, NEVER reused), `kind`, `text` (bounded), `source`, `ref_id`
  (pointer to a proposal/session, display-only), `created`, `state`
  (unread | read | dismissed). Serialized under a new reserved section key
  `"__notifications__"` in the same save payload, staged in load() like the
  disposition section; a corrupt section fails closed with proposals intact.
  Dismiss flips state and RETAINS the record (tombstone — the number is
  retired, never recycled).
- API: `notify(kind, text, source="", ref_id=None)` with add()-grade
  save-or-rollback; `list_notifications(state=None)`, `get_notification(n)`,
  `mark_read(n)`, `dismiss(n)`. Event policy behind ONE gate
  (`NOTIFY_EVENTS` + `_should_notify`) so the event set flips in one place.
- Hooks (all EXIST-to-hook): proposal arrival via the single `Nursery.add()`
  funnel (covers RingedGrowth, inference dock, exchange import, AutoGrowth,
  Dell 37); confirm/deny outcomes at `Program.confirm_proposal` /
  `Program.reject_proposal` (form/open.py).
- Chat surface (form/repl.py, beside the proposals branch): `notes` /
  `notifications` (numbered list, unread first), `note <n>` (evoke in full +
  mark read), `dismiss <n>`. Program facades in form/open.py beside
  `list_proposals`. Uni can evoke from the same store in the Ace conversation.
- Authority boundary: notifications inform only. `ref_id` is a pointer, never
  an action path; only Ace's confirm moves a proposal.
- Deferred at design time: Dell 37 front-door arms (Psalm-evocable notes) —
  a later slice unless the future circuit rules otherwise.

## Open questions (parked WITH the feature — for the afterplan circuit)

1. **Which events notify?** Put to Ace 2026-11-12; unanswered when the feature
   was parked. Options presented: big moments only (proposals waiting +
   outcomes) / everything bundled per batch / every event its own note.
2. Notification bound + eviction order (200-retained is a precedent from other
   bounded registers, NOT a derivation — needs an Ace/Director ruling).
3. Numbering scope: per-owner global sequence (recommended — matches the
   per-owner file); whether numbers ever reset.
4. Auto-expiry: none in v1 proposed (Ace's 3/7/14/30-day ladder was ruled for
   proposals, not notifications).

## Failing-first test ideas (for the future circuit)

Sequential numbering + counter survival across save/load; dismissed #2 never
reused (next is #4); tombstone persisted in the owner file; corrupt section →
NurseryLoadError with proposals intact; stale-instance notify →
NurseryConflictError; add() emits exactly one arrival note with ref_id = pid;
a notification number passed to confirm_proposal fails (no authority path);
number stability under churn across reload; per-owner isolation.
Suite name reserved: `form/nursery_notifications_test.py`.
