# DIRECTOR RULINGS — STUDIO SECURITY (PR #255)

Two rulings are archived here: the conditional acceptance with
bounded corrections, and the final certification after verification
of the corrected head.

---

## Ruling 1 — CONDITIONAL ACCEPTANCE (Mode C, bounded correction)

Reviewed head: 9008be219683abe2e552475dbbd24ec762a112ad

Security implementation provisionally accepted; browser acceptance
still open. All three GitHub CI checks passed at the reviewed head.
The implementation adds loopback Host validation, a per-launch POST
token, Origin and Content-Type checks, a 64 KiB request limit,
connection timeouts, and a guard against accidental non-loopback
binding. These measures address the original local-server security
findings; they do not establish that Studio is safe for network
deployment or that its interface has passed real-browser testing.

CI at the reviewed head: 226/226 suites forward, twice, and reverse;
security suite 35/35; Studio API suite 26/26. Evidence integrity:
21/21 published evidence-file digests verified. The MANIFEST.md
self-reference entry is invalid and must be removed (it does not
indicate corruption of the other files).

Design questions resolved: retain the per-launch POST token;
prohibit network-deployment claims; treat untrusted local processes
as outside this circuit; accept automated Chromium/CDP execution as
valid technical browser evidence when it genuinely runs the
interface. Browser acceptance itself remains unverified.

TWO CORRECTIONS REQUIRED BEFORE MERGE:

1. Origin implicit-port error: `_origin_ok()` permits an Origin
   without an explicit port even when the server runs on a
   non-default port. Resolve an omitted HTTP port as 80 and compare
   the effective port with the bound server port. Add a
   failing-first adversarial case: valid-token POST from
   `Origin: http://127.0.0.1` against port 8765 must refuse 403
   without mutation. Preserve legitimate same-origin behavior.
2. Evidence manifest: remove the invalid MANIFEST.md self-hash
   entry; preserve the verified evidence digests; make the count
   accurate.

Retained boundaries: localhost security only; real-browser UI
acceptance OPEN; DAF-09 WITHHELD; no whole-program certification.

---

## Ruling 2 — CERTIFICATION (Mode D)

Frozen HEAD: ace48bafc91f5778826fc8b02d06b0628644fb01
Frozen TREE: 76a9bd83296434d2761a71704610c979e9619b1c

RULING: **CERTIFIED — MERGE AUTHORIZED.**

Both required corrections verified:

| Certification gate | Result |
|---|---|
| Origin-port correction | VERIFIED |
| No-mutation regression test | PASS |
| Evidence manifest | 27/27 SHA-256 MATCH |
| Manifest self-reference | Removed |
| Studio security suite | 36/36 |
| Studio API compatibility | 26/26 |
| Complete regression | 226/226, all three passes |
| Exact-head CI | All three checks PASS |

The code resolves an omitted HTTP Origin port to 80 and compares it
against the server's bound port; the new regression test covers
rejection and unchanged state. The reported pre-fix mutation is a
concrete authorization-boundary failure; the corrected behavior
addresses that finding without changing the existing token
mechanism.

The certificate covers localhost security hardening only.
Real-browser acceptance, untrusted-local-process isolation, and
network deployment remain outside its scope.

Execution order: reconfirm exact head and CI; merge normally;
verify merged-main tree equals the certified tree; record
post-merge regression and terminal verdict; archive this ruling and
update INDEX; proceed with the GitHub Actions real-browser
acceptance circuit (Studio and Chromium on the same runner). Do not
claim browser acceptance until real page interaction, DOM
assertions, console checks, and screenshot evidence pass.

Executed: PR #255 merged as aef02d8; the certified content is
byte-identical on merged main (the merged tree additionally carries
the interleaved PR #253/#254 content, verified by path-restricted
diff).
