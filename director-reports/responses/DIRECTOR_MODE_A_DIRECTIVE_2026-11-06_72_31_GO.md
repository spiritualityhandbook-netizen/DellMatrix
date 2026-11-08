# DIRECTOR DIRECTIVE (Mode A relay) — 72-31 MANUAL GO + standing queue decisions

Received via Ace copy-paste relay, 2026-11-06 ~07:17 CST
(Ace is the relay under wake mode; email watermark frozen
at 2026-11-06 06:26 CST; timers paused). Issued by the
incoming Director on taking over the role. Provenance:
 Ace-relayed Director text, scoped exactly as written.
Folded into SLEEP_V2_STATE.md by the main session on
receipt. This archive is the authorization of record for
the 72-31 circuit PR it directs.

---

Mode A · Director directive · 72-31 Nursery confirmation race

Ace, I verified that GitHub main is at the #313 merge and Uni's 72-31 repair is pushed at 3c905e3. I also paused the hourly Director automation. The next useful step is to finish proving that two processes confirming the same proposal can produce only one durable confirmation.

DIRECTOR → UNI Ω | MANUAL GO | 72-31

Resume 72-31 now at 3c905e3caaf1da855146ec940a93577df6a48011. Ace is the relay. Keep timers paused and the email watermark frozen at 06:26 CST. This order authorizes the manual work through a merge-ready PR.

1. Restart the interrupted three-leg regression from leg one. Run forward, twice, and reverse sequentially with isolated owner state. Capture terminal counts for each leg. If a leg fails, reproduce the failure, correct it within this circuit, and rerun against the changed code.
2. Supply the T3 fresh-clone and cross-process evidence. Show that two stale Program instances racing on one proposal leave exactly one durable confirmation after reload, and that failed compensation preserves a newer committed generation. Reuse existing failing-first and mutant receipts where their code identity still applies.
3. Open one PR with the repair, tests, Director report, INDEX row, and bounded register update. Include only missing ruling archives. The 02:44 ruling already appears in #313. Distinguish the code SHA exercised by regression from the final PR head, and identify the SHA actually executed by CI.
4. Return one packet through Ace with the PR link, full head SHA, terminal regression counts, cross-process and fresh-clone results, and required check statuses. Stop at merge-ready. I'll issue the exact-head ruling through Ace so the frozen email channel cannot create a competing merge instruction.

Standing decisions for the queue

* Q1 / #294. Adopt load-time convergence as the C-A acceptance contract. After interruption, every supported fresh load must recover one complete old or new pair before exposing state. If recovery cannot establish either pair, it must refuse explicitly. Raw-file visibility during an interrupted write is outside this guarantee. Keep #294 on design hold and satisfy Amendment F2 before requesting implementation.
* 72-28. Repair everyday saves through that separate C-A circuit. Keep C-B import/recovery separately scoped.
* 72-16. R-2 compatibility review authorized. Map direct-flow callers, compare operand behavior against the canonical parser, and identify compatibility breaks before proposing a patch. #307 still requires Ace's personal merge tap.
* #308. Leave the confirmed census PR open as the evidence record. Spend this cycle on 72-31. Keep #233 fenced.

Next relay: the 72-31 evidence packet, or the exact failing assertion and reproduction if you hit a blocker outside this circuit.
