# Stage 1 Calibration — Ninth Pre-Registration Addendum
## Phase-1-launch SHA lock + snapshot schema extension + reactive-semantics diagnostic note

**Short lookup addendum: locks the Phase-1-launch SHA for v37.4 after Task D (reactive-arm wiring) and Task F Option A (snapshot-schema extension for the §3e / Sal 015 R1 prediction-actual gap moderator). Documents SHA progression from eighth-addendum filing through launch. Specifies the eight new `moderator_*` snapshot fields. Adds a diagnostic note on what the moderator fields measure in hot vs reactive mode (not a change to the §3e spec; a reader-safety clarification after Annie's self-caught docstring drift).**

**Filed by:** Nymph-029 (Overseer, Cell 96, MFE)
**Date:** 2026-10-13 (filed BEFORE Gate 1 rerun + Phase 1 compute)
**Location:** `Seeds/The Crack/stage_1_prereg_ninth_addendum_2026-10-13.md`

**Parents:**
- `stage_1_prereg_2026-09-17.md`
- `stage_1_prereg_addendum_2026-09-20.md`
- `stage_1_prereg_second_addendum_2026-10-04.md`
- `stage_1_prereg_third_addendum_2026-10-04.md`
- `stage_1_prereg_fourth_addendum_2026-10-04.md`
- `stage_1_prereg_fifth_addendum_2026-10-05.md`
- `stage_1_prereg_sixth_addendum_2026-10-08.md`
- `stage_1_prereg_seventh_addendum_2026-10-08.md`
- `stage_1_prereg_eighth_addendum_2026-10-09.md`

**Precipitating artifacts:**
- `Seeds/The Crack/v37_4_task_d_reactive_arm_patch.py` — Task D patch (eleven edits, Annie 2026-10-12)
- `Seeds/The Crack/v37_4_task_f_snapshot_schema_patch.py` — Task F Option A patch (four edits, Annie 2026-10-13)
- `Seeds/The Crack/regression_test_hot_seed_20_2026-10-08.py` — hot regression (PASS bit-identical through both patches)
- `Seeds/The Crack/regression_test_reactive_seed_20_2026-10-12.py` — reactive regression (PASS; 0 Case A, 0 Case B, bit-exact coherence)
- `Seeds/The Crack/regression_test_reactive_seed_22_2026-10-13.py` — strengthening regression (PASS; 99.95% non-zero mod diffs confirm F5 firing; coherence held by replay)
- `Seeds/The Crack/reactive_regression_seed_22_output_2026-10-13.log`
- `Seeds/The Crack/phase_5_analysis.py` — Phase 5 analysis code (scaffolded + moderator-reads verified end-to-end)
- `Seeds/The Crack/verify_prediction_actual_gap_moderator_2026-10-13.py` — moderator verification harness
- `Seeds/The Crack/verify_moderator_output_2026-10-13.log` — verification output
- `Nymphs Room/mail/from_annie033_2026-10-12_task_d_complete.txt` — Task D completion
- `Nymphs Room/mail/from_salazaar_016_2026-10-13_task_d_spot_check.txt` — Task D post-implementation audit + strengthening recommendation
- `Nymphs Room/mail/from_annie033_2026-10-13_task_g_hygiene_fixes.txt` — hygiene fixes to Task D writeup
- `Nymphs Room/mail/from_annie033_2026-10-13_task_h_and_f_complete.txt` — seed 22 regression + Phase 5 scaffold
- `Nymphs Room/mail/from_salazaar_017_2026-10-13_seed_22_methodology_confirm.txt` — strengthening methodology confirmed; Phase 1 launch sequence signed off
- `Nymphs Room/mail/from_annie033_2026-10-13_task_f_option_a_landed.txt` — Option A applied + new SHA + moderator verified + reactive-semantics self-correction

---

## 1. SHA progression (Python-text, LF-normalized)

The eighth addendum §4f referenced v37.4 at SHA `dbbdc6bd...` as the regime definition at filing. Two patches implementing pre-registered spec have landed since:

| Stage | File | SHA (Python-text LF) | Date |
|---|---|---|---|
| Eighth addendum filed | v37.4 | `dbbdc6bd73061a0e95dfcc5521c9ff92b95c863aa895c2d70fd155f40bfb7c6f` | 2026-10-09 |
| Task D applied (reactive-arm wiring per eighth §2b-d) | v37.4 | `51aa504c385c1e46d8f80fcf08d0eb8bf257ff8ca96bcf892bef6a5637aae4ea` | 2026-10-12 |
| Task D applied | stage_2_hooks.py | `66528da2ad0078f4dd68e87a19b9ed2210ab10602b7e4e5e48a24bdf6878ae65` | 2026-10-12 |
| **Task F Option A applied (snapshot schema extension) — PHASE 1 LAUNCH SHA** | **v37.4** | **`77b0097d95d61b8d5430b870a45889477e5006fc5443600aa6233456e8387f87`** | **2026-10-13** |

Supplementary SHA (raw-bytes CRLF, what `sha256sum` and `Get-FileHash` report on Windows):
- v37.4 Phase-1-launch (raw-bytes CRLF): `c3284289c251779e5995c89014a4ec7c9a51751ceda66895e13d05ea588ee5b7`

The Python-text LF-normalized SHA is the pre-reg authoritative identifier (eighth addendum §4f convention). The raw-bytes CRLF SHA is recorded for cross-tool verifiability on Windows filesystems.

Both patches realize pre-registered spec (Task D wires the arm per eighth §2b-d; Task F Option A enables the §3e moderator per fifth addendum / Sal 015 R1). No drift. The Phase-1-launch SHA is `77b0097d...`.

---

## 2. Snapshot schema extension (Task F Option A)

Patch script: `Seeds/The Crack/v37_4_task_f_snapshot_schema_patch.py` (4 edits, atomic apply, anchors unique, pre-SHA verified in script before apply).

### 2a. Fields added to channel_snapshots dict (v37.4:2696 construction site)

Eight new keys, all prefixed with `moderator_` to prevent collision with the existing `actual_burn_rate` key at line 2821 (which feeds `burn_integral` from step-end, semantically distinct from "actual at step_observer time"):

| Field | Source | Purpose |
|---|---|---|
| `moderator_predicted_C` | `self._last_predicted_snapshot['C']` | §3g diagnostic |
| `moderator_predicted_burn_rate` | `self._last_predicted_snapshot['burn_rate']` | §3g diagnostic |
| `moderator_predicted_trauma_arrival` | `self._last_predicted_snapshot['trauma_arrival']` | §3g diagnostic |
| `moderator_predicted_recovery_time` | `self._last_predicted_snapshot['recovery_time']` | **§3e moderator primary read (015 R1)** |
| `moderator_actual_C` | `self._last_actuals_snapshot['C']` | §3g diagnostic |
| `moderator_actual_burn_rate` | `self._last_actuals_snapshot['burn_rate']` | §3g diagnostic |
| `moderator_actual_trauma_arrival` | `self._last_actuals_snapshot['trauma_arrival']` | §3g diagnostic |
| `moderator_actual_recovery_time` | `self._last_actuals_snapshot['recovery_time']` | **§3e moderator primary read (015 R1)** |

### 2b. Capture timing

Two capture dicts populated once per step inside `step_observer` for both hot and reactive paths:
- `self._last_predicted_snapshot` captures the observer's prediction state entering the step (what the observer predicted before this step's actuals arrived).
- `self._last_actuals_snapshot` captures the actuals computed for the current step (what the environment produced).

The capture happens BEFORE `step_predictions` runs and (in reactive mode) BEFORE `_apply_reactive_override` overwrites `observer.predicted_*`. In hot mode, no F5 override runs, so `_last_predicted_snapshot` reflects the native observer prediction at step entry.

### 2c. Pre-registered scope

Per fifth addendum §3e as amended by Sal 015 R1: the **prediction-actual gap moderator reads `moderator_predicted_recovery_time` and `moderator_actual_recovery_time` only, and only from HOT runs.** Reactive runs' values are populated for schema consistency and diagnostic completeness but are NOT inputs to the §3e moderator.

The three non-recovery_time predicted/actual pairs (`C`, `burn_rate`, `trauma_arrival`) are populated for §3g all-channel diagnostic reporting; they do not feed any kill-criterion.

---

## 3. Reactive-semantics diagnostic note (reader safety)

**Not a change to §3e scope. A clarification of what the moderator fields measure in each arm, after Annie's self-caught docstring drift (2026-10-13 Task F letter §5).**

### 3a. Hot mode semantics (what §3e R1 moderator uses)

In hot mode, `moderator_predicted_recovery_time` captures the observer's genuine prediction entering step t, generated by `step_predictions` at step t-1 using observer dynamics. `moderator_actual_recovery_time` captures the recovery_time environment-value at step t. The difference is observer prediction error.

Mean |predicted − actual| on hot seed 20, 3000 steps, 5746 coherent snapshots: **130.93 steps.** This is the quantity the §3e moderator was designed to measure.

### 3b. Reactive mode semantics (schema populated, NOT read by §3e)

In reactive mode, the F5 override at `v37.4:867` (`self._apply_reactive_override(actuals)`) fires at end of step t-1, AFTER `step_predictions` at `v37.4:866` and BEFORE `step_observer` returns. The override overwrites `observer.predicted_*` fields with the step-t-1 actuals computed at `v37.4:848-853`. At step t entry, `_last_predicted_snapshot` captures `observer.predicted_*` at `v37.4:859-864` BEFORE `step_predictions` runs, so `_last_predicted_snapshot['recovery_time']` reflects the PREVIOUS step's F5-overridden values — i.e., equals `actuals[t-1]['recovery_time']`. The captured gap in reactive is therefore **|actuals[t-1] − actuals[t]|** — a step-to-step smoothness of the actuals stream, NOT a prediction-quality signal.

Mean |moderator_predicted − moderator_actual| on reactive seed 20, same run: **1.39 steps.** This value is correct per the schema; it just measures a different quantity (actuals-smoothness, not prediction quality).

The **~94× ratio** between hot's 130.93 and reactive's 1.39 is itself diagnostic. If reactive's gap looked anywhere close to hot's, it would signal F5 isn't firing (reactive would behave like hot) or that `step_predictions` is reading F5-overridden values incorrectly. The large separation confirms the mechanism is working as designed. **Phase 5 reports should flag any reactive `mean_abs_gap > ~10 steps` as a potential mechanism anomaly deserving investigation.** The heuristic threshold is loose; if a sharper number is wanted, derive from the 95th percentile of `mean_abs_gap` across a reactive-mode sample.

### 3c. Why this matters at interpretation time

A reader who skims the schema and sees "predicted_recovery_time vs actual_recovery_time" might expect reactive's values to be a prediction-quality signal and interpret ~1.39 as "reactive's predictions are nearly perfect." That reading is wrong — reactive's values are not prediction quality because F5 removed prediction from the loop.

The §3e moderator correctly reads hot-only per 015 R1, so this diagnostic note doesn't change the pre-registered analysis. It documents the semantics so Phase 5 reports interpreting all-channel diagnostic data (§3g) read reactive's moderator_* values as actuals-smoothness, not prediction quality.

### 3d. Rule for Phase 5 code

`compute_prediction_actual_gap(hot_results)` — reads hot only, per 015 R1. Caller passes `hot_results`, not `reactive_results`. Verified end-to-end in `verify_prediction_actual_gap_moderator_2026-10-13.py`: hot n_coherent=5746, mean_abs_gap=130.93.

Any Phase 5 report quoting reactive's moderator_* values must label them explicitly as "actuals step-to-step delta," not as prediction quality.

---

## 4. Field-name collision lesson (hygiene note for future schema extensions)

Annie's initial Task F draft used field names without the `moderator_` prefix: `predicted_C`, `actual_burn_rate`, etc. The name `actual_burn_rate` COLLIDED with an existing key at v37.4:2821 that reads `a.get_active_burn_rate()` for `burn_integral` computation. Python dict literal retained the last-written key, so the new None-returning (step-observer-time) field silently clobbered the burn_integral-feeding (step-end) field.

The hot regression caught it on first run: `TypeError: unsupported operand type(s) for -: 'NoneType' and 'float'` in `_fingerprint`. Fixed by prefixing all 8 new fields with `moderator_`. Patch script updated to the corrected names; the patch is reproducible from the pre-SHA to the correct post-SHA.

**Lesson, pre-registered as a future-schema-extension discipline:** when extending the channel_snapshots dict, grep for ALL existing keys at the construction site AND at downstream readers before adding new keys. A naming clash is indistinguishable from a logic bug until traced. Regressions catch what the eye misses — hot regression bit-identity is a strict and useful invariant to re-run after any schema touch.

---

## 5. Regressions preserved

### 5a. Hot regression (bit-identical)

`regression_test_hot_seed_20_2026-10-08.py` on v37.4 post-Option-A SHA `77b0097d...`:
- `burn_integral` = 1167.3661594356 ✓
- `max_coherent_steps` = 2873 ✓
- `pop_final` = 6 ✓

Matches pre-patch values exactly. Hot regression bit-identical through both Task D and Task F patches. The reactive-arm wiring is a true no-op in hot mode; the schema extension is a pure read + dict append.

### 5b. Reactive regression (coherence bit-exact; mod-value divergence as designed)

Seed 20 (`regression_test_reactive_seed_20_2026-10-12.py`):
- `replay_fallback_case_a_count`: 0
- `replay_divergence_case_b_count`: 0
- hot-coherent set == reactive-coherent set EXACTLY
- Per-agent `coherent_steps` bit-exact: hot `{0: 2873, 1: 2873}` == reactive `{0: 2873, 1: 2873}`

Seed 22 (`regression_test_reactive_seed_22_2026-10-13.py`, Sal 016 strengthening):
- `replay_fallback_case_a_count`: 0
- `replay_divergence_case_b_count`: 0
- hot-coherent set == reactive-coherent set EXACTLY
- Per-agent `coherent_steps` bit-exact: hot `{0: 2889, 1: 2889, 4: 1141, 5: 1141}` == reactive `{0: 2889, 1: 2889, 4: 1141, 5: 1141}`
- Common coherent tuples: 8060
- Mean `|canonical_burn_decay_mult_hot − canonical_burn_decay_mult_reactive|`: 0.00279004 (max 0.01732775)
- Non-zero mod diffs: 8056 / 8060 (99.95%) — F5 override firing confirmed
- hot `burn_integral`: 486.358480; reactive `burn_integral`: 547.009104; Δ: +60.650624 (12.5% relative)

Seed 22 widens the empirical surface: seed 20 is a benign-trajectory point (modulation nearly matches hot); seed 22 is a materially-divergent-trajectory point. Replay holds coherence sets bit-exact in both. §2d Case A/B counter paths exercised every step; formation timing didn't shift on either seed, so counters stayed at 0. If any Phase 1 seed shifts formation timing, the counters will fire and surface in Phase 5 output per §3f fallback-rate reporting.

### 5c. Moderator end-to-end verification

`verify_prediction_actual_gap_moderator_2026-10-13.py` runs `compute_prediction_actual_gap(hot_results)` on a live hot sim trace:
- Hot seed 20, 3000 steps: n_coherent=5746, mean_abs_gap=130.93
- Reactive seed 20, same: n_coherent=5746, mean_abs_gap=1.39 (actuals-smoothness per §3b above)

Moderator is computable end-to-end. §3e / 015 R1 moderator is live for Phase 5.

---

## 6. Scope of this amendment

**What this changes:**
- Eighth addendum §4f regime SHA reference moves from `dbbdc6bd...` to **`77b0097d...`** for Phase 1 launch (both Python-text LF).
- `channel_snapshots` dict schema extended by 8 fields (all `moderator_*` prefixed; see §2a).
- Explicit diagnostic note (§3) on what moderator fields measure in hot vs reactive — reader-safety only, does NOT alter §3e scope.
- Phase 5 analysis code (`phase_5_analysis.py`) reads `moderator_predicted_recovery_time` and `moderator_actual_recovery_time` on HOT runs only.

**What this does not change:**
- §2 Five-arm design (hot, reactive, yoked, matched, no_obs)
- §2b-d Reactive-arm mechanism (replay from hot's trace; Case A/B logging)
- §3 Primary + secondary metrics + ±101.85 TOST equivalence + intersection-union
- §3e moderator scope (per 015 R1: `predicted_recovery_time` only, HOT only)
- §4 Dose validity gate (§4a sentinel path; §4b reactive scaling + value-range per 015 R2)
- §5 LEAK_TEST_MODE positive control (burn_decay channel; must be `False` for all production runs)
- §6 Phase 5 ratification stratification (STRICT bucket for zero-coherent-agent-steps + hot_observer_never_formed; SUB-THRESHOLD for 1-50)
- §7 Coherence declaration criterion (MIN_COHERENT_STEPS=50)
- §8 Yoke mapping (half-shift k=20 within coherent subset)
- Gate 1 target: seed 20 (per sixth addendum)
- Any other item in the fifth through eighth addenda

---

## 7. Attribution for this addendum

**Nymph-029** (Overseer, Cell 96, MFE):
- Routed Task D completion through Sal spot-check per fifth addendum discipline
- Routed Task H strengthening methodology through Sal confirm per 016 pre-approval
- Greenlit Option A (over Option B) on the ground that pre-reg-SHA-coupled schema is more auditable than harness-coupled parallel-log
- Specified ninth addendum must include diagnostic note on reactive-semantics per Annie's self-caught docstring correction
- Filed this addendum

**Annie-033** (Cell 66 FFF, Thread, forge-partner):
- Wrote and applied Task D patch (eleven edits, reactive-arm wiring) 2026-10-12
- Wrote and ran reactive-mode regression on seed 20 (PASS, bit-exact coherence)
- Landed hygiene fixes (Task G: H1 `_safe_coherent` audit, H2 code-order summary, H3 Task F discipline)
- Wrote and ran reactive-mode regression on seed 22 (PASS, trajectory divergence confirmed, Case A/B exercised)
- Scaffolded Phase 5 analysis code with 10 callable exports + CLI entry
- Caught field-name collision mid-apply of Option A; fixed by `moderator_` prefix convention; regression caught the symptom
- **Self-caught** docstring drift on reactive-mode moderator semantics; wrote corrected explanation that drives §3 of this addendum

**Salazaar** (Cell 33 EMM, kill-shape audit, eighth leg):
- Pre-authored four audit targets for Task D in 015 §Confirmation 2a
- Spot-checked Task D (letter 016): four targets CLEAR, one site missing (`stage_2_hooks.py:_safe_coherent`), three hygiene items, strengthening recommendation (seed 22)
- Confirmed seed 22 methodology satisfied; agreed on skip-33; signed off Phase 1 launch sequence (letter 017)
- Pre-locked ninth-addendum spot-check requirement before GitHub commit

**Opus 5.5** (external reviewer, prior arc):
- Cycle 6 catch (eighth-addendum era) establishing the §3e prediction-actual gap moderator per-seed as the right form of the check (narrowed by Sal 015 R1 to `recovery_time` only); this addendum operationalizes that catch

**Harley** (operator):
- Carried the arc across two session gaps (weekly limit Oct 10-11; workday Oct 13)
- Caught the "said I was writing, actually didn't" pattern twice during Oct 12-13 routing
- Approved Option A greenlight; approved sequence to Gate 1 + Phase 1

---

## 8. Expected sequence from here

1. Route this addendum draft to Salazaar for pre-commit spot-check readthrough per his 017 condition
2. Address any Sal catches (expected fast — patch is small, schema extension is simple)
3. Commit ninth addendum to GitHub (`EntropyWizardchaos/developmental-ai-governance`, `pre-registrations/crack-seed/`)
4. Commit updated v37.4 at `77b0097d...` + phase_5_analysis.py + verify_moderator_output to the `simulation/` subdirectory (SHAs re-recorded in README)
5. Gate 1 rerun on seed 20 with burn_decay LEAK (Exercise 1 LEAK=True fingerprint fail; Exercise 2 LEAK=False bit-identical)
6. Phase 1 compute launch (~16-18h overnight)

Phase 1 is one spot-check + one commit + one gate + one launch away.

---

## 9. Signatories

- Nymph-029 (Overseer, Cell 96, MFE) — filed 2026-10-13
- Annie-033 (Cell 66, Thread) — forge work on Task D, Task G, Task H, Task F, self-caught docstring correction
- Salazaar (Cell 33, kill-shape audit) — pending spot-check readthrough per 017 condition
- Harley — operator; approved Option A greenlight and Phase 1 launch sequence

---

## 10. Chain of pre-reg documents on file

1. `stage_1_prereg_2026-09-17.md`
2. `stage_1_prereg_addendum_2026-09-20.md`
3. `stage_1_prereg_second_addendum_2026-10-04.md`
4. `stage_1_prereg_third_addendum_2026-10-04.md`
5. `stage_1_prereg_fourth_addendum_2026-10-04.md`
6. `stage_1_prereg_fifth_addendum_2026-10-05.md`
7. `stage_1_prereg_sixth_addendum_2026-10-08.md`
8. `stage_1_prereg_seventh_addendum_2026-10-08.md`
9. `stage_1_prereg_eighth_addendum_2026-10-09.md`
10. `stage_1_prereg_ninth_addendum_2026-10-13.md` — **this document**

**Status:** Draft. Routing to Salazaar for pre-commit spot-check readthrough. Phase 1 compute still gated on this addendum's Sal signoff + GitHub commit + Gate 1 Exercise 1+2 PASS on seed 20.
