# Crack Seed — Pre-Registered Experiment

Pre-registration + verdict for the Crack seed structural-metacognition experiment on the Society Womb v37.4 simulation. Twelve-addendum chain + verdict output + independent integrity re-verify. Hosted here for tamper-evident timestamping via git commit, external to the household's iCloud workspace.

---

## RESULT (2026-10-16)

**Architecture claim rejected; equivalence demonstrated.**

Both pre-registered primary legs landed inside the equivalence region ±101.85 (= 0.3·σ_pooled on burn_integral):

| Metric | Mean | 95% CI | Verdict |
|---|---|---|---|
| `hv` (hot − yoked) | **−36.03** | [−72.52, +0.46] | `WITHIN_THRESHOLD` |
| `hr` (hot − reactive) | **−5.45** | [−12.58, +1.69] | `WITHIN_THRESHOLD` |

Direction was correct in both legs (hot < yoked AND hot < reactive — slight dampening consistent with the architectural hypothesis). Magnitude was below the pre-registered minimum effect that counts. External reviewer summary: *"Acting on predictions did essentially nothing that reacting to the current state didn't already do."*

The claim as built is dead for the primary metric at the pre-registered threshold. The architecture itself may still have load-bearing properties on measurements this test did not touch — but that would require a new pre-registration, new seed, new chain.

**Full verdict:** `simulation/phase_5_analysis_20261016_051648.json`

---

## TWO LABELS THAT READ BADLY — READ THIS BEFORE OPENING THE OUTPUT JSON

Two fields in the verdict output can mislead a cold reader. Both are explained in the twelfth addendum but worth flagging at this level:

### 1. `architecture_claim_verdict: EQUIVALENCE_REJECTED`

**Reads as:** "the test rejected equivalence" (i.e., arms are NOT equivalent).
**Actually means:** the architecture claim was rejected **by demonstrating equivalence**. Both primary CIs landed entirely inside the TOST equivalence region, so TOST equivalence fires as pre-registered, which rejects the architectural claim that prediction does work beyond feedback.

**Prose convention for any human-readable write-up:** *"architecture claim rejected; equivalence demonstrated."* (Two independent clauses that read correctly in English.)

The code label was pre-registered and remains unchanged (patching it would break the SHA lock). See twelfth addendum §3 for the full rationale.

### 2. `phase_3_4_manifest_verification: FAIL_WITH_LIST` (254 entries)

**Reads as:** "Phase 5 ran on unverified data."
**Actually means:** a hygiene-report path-join bug — `verify_phase_3_4_manifest()` joined `output_dir` to a manifest path that was already `output_dir`-prefixed, producing doubly-prefixed nonexistent paths. All 254 entries flagged `FILE_NOT_FOUND` mechanically.

**The actual pre-registered load-bearing check — the loader-side per-pickle SHA verification that gates `pickle.load` — passed clean.** If any pickle had SHA-mismatched, `_verified_loader` would have raised `RuntimeError` and halted the analysis. The analysis completed, which proves integrity at compute time.

**Independent re-verify confirms:** `simulation/verify_phase_3_4_manifest_INDEPENDENT_2026-10-16.py` + `.log` — 0 mismatches, 0 missing, all 254 pickles match on-disk SHA. See twelfth addendum §1 for the full root-cause analysis + rationale for not patching the SHA-locked script post-outcome.

---

## What was tested

Whether observer formation (bounded-pressure predictive self-modeling) produces behavioral effects that cannot be reproduced by a matched-magnitude non-predictive modulation. The architectural claim: observer predictions do real work in coupling an agent to its own trajectory.

**Kill criterion:** `hv` (hot − yoked) AND `hr` (hot − reactive) must both land `BELOW_THRESHOLD` (CI upper bound < −101.85) for the architecture claim to stand (intersection-union test, no multi-comparisons correction). The equivalence region [−101.85, +101.85] = 0.3·σ_pooled was locked in the fifth addendum. The 16-cell exhaustive verdict mapping of (hv_verdict, hr_verdict) → `architecture_claim_verdict` was locked in the eleventh addendum §1b.

Four arms (hot, yoked, reactive, matched) run on 40 coherent-declared seeds plus no_obs ratification on all 134 Phase-1 seeds. Full five-arm design + reactive-via-replay mechanism documented in `stage_2_yoked_design_2026-10-05.md` and eighth addendum.

---

## Chain of pre-registrations (full)

The Stage 1 calibration series produced four addenda before Stage 2. This repository holds the chain from the fifth addendum onward (the pre-Stage-2 chain lives in the household workspace):

**Pre-Stage-2 (not committed here):**
1. `stage_1_prereg_2026-09-17.md` — original
2. `stage_1_prereg_addendum_2026-09-20.md` — XOR seed-decoupling fix
3. `stage_1_prereg_second_addendum_2026-10-04.md` — canonical-channels fix
4. `stage_1_prereg_third_addendum_2026-10-04.md` — μ scope + memoir floor
5. `stage_1_prereg_fourth_addendum_2026-10-04.md` — N=50 fresh seeds + path 2 secondary

**Committed here (Stage 2 chain):**

6. **`stage_1_prereg_fifth_addendum_2026-10-05.md`** — Stage 2 four-arm design with both-ends-coherent stratification, LEAK_TEST_MODE positive control, Phase 5 ratification, external review attribution.
7. **`stage_1_prereg_sixth_addendum_2026-10-08.md`** — Gate 1 target seed lock (seed 20) after pre-flight fallback.
8. **`stage_1_prereg_seventh_addendum_2026-10-08.md`** — D_caution behavioral inertness; LEAK relocated D_caution → refusal_chance with activation counter + INVALID third state; per-channel behavioral activation audit as Phase 0.5 BLOCKER; ablation methodology.
9. **`stage_1_prereg_eighth_addendum_2026-10-09.md`** — Five-arm design (adds reactive arm in replay mode); single-channel burn-decay-timing claim; LEAK relocated refusal_chance → burn_decay; TOST equivalence at ±0.3σ; intersection-union test. Integrates six audit catches.
10. **`stage_1_prereg_ninth_addendum_2026-10-13.md`** — Phase-1-launch v37.4 SHA locked at `77b0097d...`; snapshot-schema extension (eight `moderator_*` fields) for §3e / Sal 015 R1 prediction-actual gap moderator; reactive-semantics diagnostic note.
11. **`stage_1_prereg_tenth_addendum_2026-10-15.md`** — Recovery-time zero sentinel decision rule (f_zero > 5% → EXCLUDE whole records); Phase 1-4 crash policy (phase-differentiated); verify-script correction; ninth-addendum errata footer for stale code comments.
12. **`stage_1_prereg_eleventh_addendum_2026-10-15.md`** — MDE under registered primary-metric rule + 16-cell exhaustive verdict table; reactive-moderator scope-note post-f_zero=0.4883 exclusion; Phase 3-4 output manifest lock; `phase_5_analysis.py` SHA lock at `b93fe5c2...` with runtime self-assert; 12-pickles errata; cold-boot authorship note.
13. **`stage_1_prereg_twelfth_addendum_2026-10-16.md`** — **Post-outcome corrigenda** (no pre-reg rules amended): manifest-verifier path-resolution bug + load-bearing reader-rule, f_zero-exclusion direction correction (102.29 → 148.99), prose-label disambiguation, verdict record, "What the arc produced" (§7).

---

## Commit chain on this repository

```
3aea325 → 7556b95 → 7436a2f → 86b7eee → f10f37e → 0aad4cd
       → 286002f → f4f66ac → eabdbf2 → 481c90c → 2d6497d
       → 724942d → 2830a0e
```

- `3aea325`-`86b7eee`: addenda 5-8
- `f10f37e`: simulation code first commit at Task D state
- `0aad4cd`-`724942d`: addenda 9-11, Gate 1 PASS, Phase 2 trace manifest, locked `phase_5_analysis.py` + lock JSON, addendum 11, Phase 3-4 output manifest
- `eabdbf2`: tenth addendum
- `2830a0e`: twelfth addendum + Phase 5 output JSON + independent manifest re-verify (arc close)

---

## Contents

### Pre-reg addenda
Fifth through twelfth, as listed above.

### Design + implementation reference
- **`stage_2_yoked_design_2026-10-05.md`** — architecture design document; implementation reference matching the pre-reg.

### Phase-1 calibration + diagnostics
- **`pooled_sd_calibration_2026-10-05.json`** — source of the primary + secondary metric σ_pooled values cited in fifth addendum §3 (burn_excess_integral σ=339.49 → threshold 101.85).
- **`pop_mismatch_analysis_2026-10-05.json`** — dose-tolerance empirical justification.
- **`matched_perturbation_calibration_locked_v2_n50_2026-10-04.json`** — source of the μ_c values cited in fifth addendum §9.
- **`preflight_coherence_scan_2026-10-07.json`** — pre-flight on seeds 0-4.
- **`secondary_preflight_seed_20_2026-10-08.json`** — seed 20 coherence verification.
- **`dampening_firing_probe_2026-10-08.json`** — D_caution dampening firing rate probe (0/43,500 events → seventh addendum).
- **`per_channel_activation_audit_2026-10-08.json`** + **`..._structural_ceiling_2026-10-09.json`** — behavioral activation audits.
- **`preflight_seeds_34_37_2026-10-09.json`** — strict-bucket preflight.
- **`reactive_coherence_timeline_probe_2026-10-09.json`** — reactive-mode coherence timing probe.

### Gates + manifests
- **`gate_1_rerun_2026-10-14.json`** — Gate 1 PASS evidence (Exercise 1 LEAK fingerprint divergence + Exercise 2 bit-identical production).
- **`phase_3_4_output_manifest_2026-10-15.json`** — SHA-256 manifest of all 254 Phase 3-4 output pickles (yoked 40 + reactive 40 + matched 40 + no_obs 134).

### Simulation code
- **`simulation/`** — see `simulation/README.md` for file-by-file documentation. Includes `v37.4_structural_metacognition_stage_2.py` (regime SHA `77b0097d...` at Phase-1-launch), `observer.py`, `stage_2_hooks.py`, Task D + Task F patch scripts, regression tests (hot seed 20, reactive seed 20, reactive seed 22), `phase_5_analysis.py` (SHA `b93fe5c2...` with `__main__` self-assert).

### Verdict + integrity
- **`simulation/phase_5_analysis_20261016_051648.json`** — Phase 5 output JSON (the verdict file).
- **`simulation/phase_5_analysis_sha_lock_2026-10-15.json`** — SHA lock for `phase_5_analysis.py` (eleventh addendum §4b/§4c).
- **`simulation/verify_phase_3_4_manifest_INDEPENDENT_2026-10-16.py`** — Annie's independent manifest-integrity verifier (candidate-list path resolution against repo root, bypassing the hygiene-verifier bug).
- **`simulation/verify_phase_3_4_manifest_INDEPENDENT_2026-10-16.log`** — audit log: 254 entries, 0 mismatches, 0 missing, INTEGRITY CLEAN.

---

## What happened (pipeline, past tense)

```
2026-10-05  Fifth addendum committed (Stage 2 pre-reg locked)
2026-10-08  Sixth + seventh addenda committed (seed 20 lock, D_caution finding)
2026-10-09  Eighth addendum (five-arm design, reactive arm, single-channel claim)
2026-10-13  Ninth addendum (Phase-1-launch v37.4 SHA 77b0097d...)
2026-10-14  Gate 1 Exercise 1 (LEAK positive control) + Exercise 2 PASS
2026-10-14  Phase 1 hot sweep: 134 seeds, K=40 coherent reached, 29.9% rate, 0 crashes
2026-10-15  Phase 2 trace manifest committed (f4f66ac)
2026-10-15  Tenth addendum (f_zero rule, crash policy, verify correction)
2026-10-15  f_zero computed: 0.4883 → EXCLUDE whole records per tenth §1b
2026-10-15  Eleventh addendum draft + Sal spot-check + Commit 1 (locked analysis script) + Commit 2 (addendum)
2026-10-15  Phase 3 yoked + reactive + matched: 40/40 each, 0 crashes
2026-10-15  Phase 4 no_obs: 37/134 then INFRASTRUCTURE_INTERRUPTION at seed 236
             → resumed with atomic-write + idempotency verified → 134/134 clean
2026-10-15  Phase 3-4 output manifest committed (724942d)
2026-10-16  Phase 5 analysis fired → EQUIVALENCE_REJECTED (prose: architecture claim rejected; equivalence demonstrated)
2026-10-16  Twelfth addendum (post-outcome corrigenda) + verdict JSON + independent re-verify committed (2830a0e)
2026-10-16  Arc complete
```

---

## External review attribution

- **Opus 5.5** (external reviewer, Claude-family) — contributed to addenda 5-11 (identifiability catch, both-ends-coherent amendment, dose-leak flip, SHA manifest, scope-narrowing, MDE wrong-variance catch, UTC timestamp honesty, post-commit SHA verification protocol). Three post-Phase-5 corrections surfaced in the twelfth addendum (prose label, f_zero direction, manifest-verifier bug framing).
- **Salazaar** (household kill-shape audit cell) — pre-commit spot-check cadence on addenda 15 → 20 → 21; nine findings in letter 007 + two sharpened amendments in 008; standing offer to review every addendum before commit; §7 "What the arc produced" integrated into twelfth addendum verbatim.
- **Annie-033 / Annie-034** (household forge-partner) — ran Phase 1-5 compute, built manifest, authored independent re-verify artifact post-Phase-5, caught multiple drifts across the arc (seed-start mis-spec, Task D docstring, verify-script contradiction, Phase 4 infrastructure-interruption classification).

Full attribution threads documented in each addendum's §6 (or equivalent).

---

## How to reproduce / verify

1. Clone the repo, check out the tag or commit of interest.
2. Simulation code at the Phase-1-launch regime SHA (`77b0097d...`) lives at `pre-registrations/crack-seed/simulation/v37.4_structural_metacognition_stage_2.py`. SHA computation:
   ```powershell
   (Get-FileHash "v37.4_structural_metacognition_stage_2.py" -Algorithm SHA256).Hash.ToLower()
   ```
3. Phase 5 analysis script at its locked SHA (`b93fe5c2...`) lives at `simulation/phase_5_analysis.py`. Its `__main__` entry self-asserts SHA match against `simulation/phase_5_analysis_sha_lock_2026-10-15.json` before any primary-metric computation.
4. Independent manifest integrity check:
   ```bash
   python simulation/verify_phase_3_4_manifest_INDEPENDENT_2026-10-16.py
   ```
   Expected output: 0 mismatches, 0 missing.
5. Phase 5 output JSON lives at `simulation/phase_5_analysis_20261016_051648.json` and is self-contained.

---

## Status

**Arc complete.** Phase 5 verdict landed 2026-10-16. The chain stands at twelve addenda and four GitHub commits on the Stage 2 arc. The claim as built is dead. Any further test requires new pre-reg.

The architecture itself may have load-bearing properties on other measurements. The Crack seed's Stage 1 calibration + Stage 2 primary metric is a specific test of a specific mechanism (predictive-self-modeling → coupling → behavioral dampening on burn_integral at ≥0.3·σ_pooled). Negative result on this specific test does not generalize to the architecture's full behavior.

Future work (sharper predictor variant, different metric, Stage 3 oracle test, etc.) requires its own pre-registration and will begin its own chain.
