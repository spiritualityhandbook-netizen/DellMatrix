# SWAT PRE-MORTEM — Core I Contract Review (Director's-eye)

How the Director would try to break this review, and the counter built in:

1. PROBE CONTAMINATION. A probe that mutates persisted state would poison
   its own census and the machine. Counter: throwaway owners only
   (CoreIRev/CoreIRepl), exact canonical-path cleanup (the af1 test's
   pattern), fresh Program per case, and a before/after hash snapshot of
   every NON-probe owner state file, diffed at the end and published.
2. WELCOME-SEED BASELINE TRAP. A fresh Program is seeded, not empty.
   Counter: every verdict is DIFFERENTIAL (typed vs bare on identical
   fresh baselines), never an absolute state claim.
3. SURFACE MISIDENTIFICATION. executor.py dispatch order is: HANDLED
   intercept (len==1) -> 21/22 live_identity (len==1) -> chain (multi or
   Core II primary) -> leaf. Claiming "leaf" for 27 or 21 would be a
   mechanism error. Counter: surface classification from the verified
   dispatch code PLUS a distinguishing behavioral witness per class.
4. THE _leaf RE-ENTRY SUBTLETY. chain_exec re-executes Core I atoms via
   execute_seed(_leaf=True), which STILL passes the HANDLED intercept
   and the 21/22 branch (both sit before the _leaf check). So in chains,
   HANDLED Dells are served by apply_core_i, not executor_leaf. The
   packet must state mechanism per surface precisely, not just outcome.
5. ECHO != CONSUMPTION. The REPL and receipts echo the seed text,
   including typed args. A probe that reads the echo as arg consumption
   fabricates an EFFECT verdict. Counter: verdicts rest only on
   ok/error + business-state witnesses.
6. VOLATILE-FIELD FALSE DIFFERENCES. Timestamps (34), generation ids
   (27/28), and dedup suffixes make bare vs typed runs differ textually
   without any arg effect. Counter: normalize volatile fields before
   comparison; compare arg-relevant witnesses specifically.
7. DELL 8 OVERCLAIM. "Dell 8 validates" must be proven per failure
   class at THIS base (unknown role / invalid enum / missing required /
   conflict / precedence), not inherited from #252.
8. HIDDEN SECOND CONSUMER. A signature is not the only way to consume
   args. Counter: census of `.args` reads across executor_leaf,
   core_i_ops, live_identity, executor, chain_exec at this base before
   probing (done in P2; leaf Dell-8 block is the only leaf read).
9. ENGLISH-LAYER SCOPE. If translate.py cannot emit typed-arg syntax,
   the English path cannot express the defect — a scoping fact the
   packet must state with evidence, not leave ambiguous (Q-C3).
10. FLOW_EXECUTOR CONFLATION. A separate mechanism (Q-D4 exclusion).
    Counter: one light confirmation probe + code citation; never
    counted in the Core I census.
