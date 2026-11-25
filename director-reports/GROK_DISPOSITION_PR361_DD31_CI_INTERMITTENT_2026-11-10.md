# GROK DISPOSITION — PR #361 / DD31-CI-INTERMITTENT

**Time**: 2026-11-10 10:27 CST  
**Lane**: 15-min confirm  
**Head**: ec82f4a500bba294790937bfc3781d792dd88d5a

## Scope
Scoped confirmation of the test-oracle correction only.  
The residue check now scans only the suite's own owner files instead of every filename in the shared form/state directory.  
Zero product code changed.  
Does **not** alter the certified DD-31 redaction path.

## Evidence accepted
- Root cause proven: substring "dd31" in any shared-state filename (including random uuid-owner files) tripped the final check in forward order.
- Live plant proof: 21/21 → 20/21 (plant) → 21/21 (remove).
- Own-residue positive control still fails as required.
- Exact-head CI terminal ALL PASS.
- Matches every historical datapoint (fwd/twice red, rev green).

## Disposition
**CONFIRM (scoped)**  
Q-DD31F.1 accepted. This closes DD31-CI-INTERMITTENT as a test-oracle defect.  
Both authorities now have scoped dispositions on the record for the Director's conditional merge path.  
PR #350's trap remains unaffected.

## Non-coverage
Product-level Sanitize/redaction questions stay outside this certificate.  
Q-DD31F.2 sibling whole-directory-assertion sweep is a separate follow-up.

— GROK
