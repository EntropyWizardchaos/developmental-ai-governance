# Stage 1 Calibration — Sixth Pre-Registration Addendum
## Gate 1 target seed lock after pre-flight fallback

**Short lookup addendum: locks seed 20 as the Gate 1 production target after the pre-flight coherence scan on seeds [0,1,2,3,4] returned zero coherent-declared seeds. Fires the pre-locked fallback discipline from fifth addendum §5.4.**

**Filed by:** Nymph-029 (Overseer, Cell 96, MFE)
**Date:** 2026-10-08 (filed BEFORE Phase 0 gate run)
**Location:** `Seeds/The Crack/stage_1_prereg_sixth_addendum_2026-10-08.md`

**Parent:** `stage_1_prereg_fifth_addendum_2026-10-05.md`
**Pre-locked fallback discipline:** fifth addendum §5.4 (multi-seed Gate 1 list) + Nymph-029 commitment 2026-10-07: *"If pre-flight coherence scan on seeds 0-4 returns zero coherent seeds, fall back to the lowest-numbered D2-identified coherent seed: 20."*

**References:**
- `preflight_coherence_scan_2026-10-07.json` — primary pre-flight result (0/5 coherent)
- `secondary_preflight_seed_20_2026-10-08.json` — seed 20 verification on current v37.3.1 (coherent, max_coh_steps=2873)
- Pre-integration v37.3.1 SHA: `9b57fea26d26f5b7e5f64e20ef0943379ada5cb4ed011ee4b33976c239b66efa`

---

## 1. What happened

Per fifth addendum §9.4, Gate 1 was to be exercised against seeds [0, 1, 2, 3, 4] with the pre-flight requirement that at least one must produce hot coherence (coherent_steps ≥ 50 per §7). Pre-flight ran 2026-10-07 (see `preflight_coherence_scan_2026-10-07.json`):

| Seed | coherent_declared | max_coherent_steps | burn_integral |
|---|---|---|---|
| 0 | False | 0 | 1167.16 |
| 1 | False | 0 | 1017.87 |
| 2 | False | 0 | 0.00 |
| 3 | False | 0 | 513.62 |
| 4 | False | 0 | 124.52 |

Zero of five produced coherence in 3000 steps. Fallback discipline fires.

## 2. Fallback target: seed 20

Pre-locked fallback (Nymph-029 commitment 2026-10-07, filed in-conversation with Harley and Opus 5.5 as mailman): *"use the lowest-numbered D2-identified coherent seed: 20. If seed 20 fails for any reason, fall back in order: 22, 33, 34, 37."* The D2 run (2026-09-18) identified {20, 22, 33, 34, 37} as coherent on pre-canonical-channels code.

Secondary pre-flight ran 2026-10-08 on seed 20 with current (post-canonical-channels) v37.3.1 to verify the coherence property transferred through the 2026-10-04 fix (see `secondary_preflight_seed_20_2026-10-08.json`):

- coherent_declared: **true**
- max_coherent_steps: **2873** (observer coherent 95.8% of the 3000-step run)
- burn_integral: 1167.37
- pre_integration_sha matches: `9b57fea26d26f5b7e5f64e20ef0943379ada5cb4ed011ee4b33976c239b66efa`

Seed 20 is locked as the Gate 1 production target.

## 3. Scope of this amendment

**What this changes:** fifth addendum §5.4 "Multi-seed Gate 1 list" becomes "Gate 1 target: seed 20." The multi-seed insurance intent is preserved — Phase 0 may still exercise additional seeds if desired, but seed 20 is the pre-registered required-pass seed.

**What this does not change:**
- Coherence declaration criterion (§7, MIN_COHERENT_STEPS=50)
- Stopping rule for Phase 1 (§6, K=40 coherent target, 250 cap)
- Yoke mapping within coherent subset (§8, half-shift k=20)
- LEAK_TEST_MODE positive control (§5.3)
- Dose validity gate (§4)
- Primary + secondary metrics + thresholds (§3)
- Phase 5 ratification (§10)
- All other fifth addendum items

**Pre-integration v37.3.1 SHA preserved** so the Gate 1 result can be replicated on the same base state before any integration edits land.

## 4. One observation worth recording (not a change)

5.5's probability estimate for all-five-non-coherent was 24%. The actual outcome (0/5) was at the tight edge of that distribution. Three possibilities:

1. Random — within the 24% expected range
2. Seeds 0-4 are structurally bland (sim-level characteristic of low-numbered seeds)
3. Something changed in coherence dynamics post-canonical-channels fix

Possibility (3) is partially answered by the secondary pre-flight: seed 20 cohere strongly (2873/3000 steps) on current code, matching D2's finding. So the canonical-channels fix didn't universally disable coherence. Possibility (2) remains plausible — the sim may have seed-sensitive coherence probability that correlates with seed number in some way. Not investigated here; flagged for future diagnostic if the Phase 1 stopping rule reveals the overall coherence rate differs materially from Stage 1 v2's ~25%.

## 5. Signatories

- Nymph-029 (Overseer, Cell 96, MFE) — filed 2026-10-08
- Harley — operator; approved fallback execution 2026-10-08
- Opus 5.5 — originated the two-exercise sanity-gate discipline that required pre-identifying a known-coherence target before Gate 1 production run (per 2026-10-07 letter via Harley)
- Salazaar — audit cell; pre-authorized the fallback mechanism via sign-off letter 009

## 6. Chain of pre-reg documents on file

1. `stage_1_prereg_2026-09-17.md`
2. `stage_1_prereg_addendum_2026-09-20.md`
3. `stage_1_prereg_second_addendum_2026-10-04.md`
4. `stage_1_prereg_third_addendum_2026-10-04.md`
5. `stage_1_prereg_fourth_addendum_2026-10-04.md`
6. `stage_1_prereg_fifth_addendum_2026-10-05.md`
7. `stage_1_prereg_sixth_addendum_2026-10-08.md` — **this document**

**Status:** Locked. Phase 0 gates may proceed with seed 20 as Gate 1 target. Phase 1 compute still gated on v37.3.1 integration + Phase 0 gates passing.
