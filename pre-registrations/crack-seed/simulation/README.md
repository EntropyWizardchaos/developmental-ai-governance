# Crack Seed Simulation Code

Runnable simulation code for the Crack seed Stage 2 pre-registered experiment. Pushed to GitHub for tamper-evident regime definition per the eighth addendum §4f ("SHA is the authoritative regime definition"). Phase-1-launch SHA locked by the ninth addendum (`stage_1_prereg_ninth_addendum_2026-10-13.md`).

## Files

### Simulation core
- **`v37.4_structural_metacognition_stage_2.py`** — the main Society Womb simulation with Stage 2 integrations (hooks for arm_mode plumbing, LEAK_TEST_MODE positive control via burn_decay channel, reactive-mode replay implementation, MODE_HOT crash softening + hook-integrity, canonical observer channels, `moderator_*` snapshot fields for §3e prediction-actual gap).
- **`observer.py`** — observer model (Observer class, step_predictions, maybe_promote_to_coherent, modulation functions `burn_decay_multiplier_from_observer` / `refusal_probability_from_observer` / `trauma_decay_exponent_from_observer`).
- **`stage_2_hooks.py`** — hook functions for arm_mode dispatch (capture_canonical, apply_canonical_override, assert_observer_off, etc.) with MODE_REACTIVE support.

### Patches (reproducible from pre-SHA to post-SHA)
- **`v37_4_task_d_reactive_arm_patch.py`** — atomic patch script for Task D reactive-arm wiring (eleven edits across v37.4 and stage_2_hooks.py). Takes v37.4 from `dbbdc6bd...` to `51aa504c...` and stage_2_hooks.py from `092c8442...` to `66528da2...`.
- **`v37_4_task_f_snapshot_schema_patch.py`** — atomic patch script for Task F Option A snapshot-schema extension (four edits on v37.4 only). Adds eight `moderator_*` fields to `channel_snapshots` dict construction for the §3e / Sal 015 R1 prediction-actual gap moderator. Takes v37.4 from `51aa504c...` to `77b0097d...` (Phase-1-launch SHA).

### Regression tests
- **`regression_test_hot_seed_20_2026-10-08.py`** — hot-mode regression. Confirms post-patch v37.4 remains bit-identical to pre-integration v37.3.1 on seed 20 under `LEAK_TEST_MODE=False`. Must PASS bit-identical through both Task D and Task F patches.
- **`regression_test_reactive_seed_20_2026-10-12.py`** — reactive-mode regression (benign-trajectory seed). Verifies replay drives coherence to a bit-exact match on the sticky-coherence state and per-agent coherent_steps.
- **`regression_test_reactive_seed_22_2026-10-13.py`** — reactive-mode regression (materially-divergent-trajectory seed, Salazaar 016 strengthening). Verifies replay still forces bit-exact coherence under non-trivial trajectory divergence; reports trajectory divergence metrics (mean |Δ burn_decay_mult|, burn_integral delta).

### Phase 5 analysis
- **`phase_5_analysis.py`** — analysis module with ten callable exports: dose validity (`compute_arm_dose`, `compute_source_dose_pool`, `compute_reactive_dose_verdict`), ratification (`ratify_seed`), primary metric (`compute_primary_metric`), moderator (`compute_prediction_actual_gap` — HOT runs only per 015 R1), fallback rates (`compute_fallback_rates`), diagnostic (`compute_all_channel_doses`), main entry (`analyze_phase_1_output`), CLI (`python phase_5_analysis.py --output-dir ... --seed-pool ...`).
- **`verify_prediction_actual_gap_moderator_2026-10-13.py`** — verification harness confirming `compute_prediction_actual_gap(hot_results)` runs end-to-end on a live hot sim trace, reads the `moderator_*` snapshot fields, and returns the expected quantity.
- **`verify_moderator_output_2026-10-13.log`** — verification output log.

## SHAs (Python-text, LF-normalized)

**Phase-1-launch state** (ninth addendum lock, Oct 13 2026):

- `v37.4_structural_metacognition_stage_2.py`: **`77b0097d95d61b8d5430b870a45889477e5006fc5443600aa6233456e8387f87`**
- `stage_2_hooks.py`: `66528da2ad0078f4dd68e87a19b9ed2210ab10602b7e4e5e48a24bdf6878ae65`

Supplementary SHA (raw-bytes CRLF, what `sha256sum` and `Get-FileHash` report on Windows):
- `v37.4_structural_metacognition_stage_2.py`: `c3284289c251779e5995c89014a4ec7c9a51751ceda66895e13d05ea588ee5b7`

### Progression from eighth-addendum-filed state

| Stage | File | SHA (Python-text LF) | Date |
|---|---|---|---|
| Eighth addendum filed | v37.4 | `dbbdc6bd73061a0e95dfcc5521c9ff92b95c863aa895c2d70fd155f40bfb7c6f` | 2026-10-09 |
| Task D applied | v37.4 | `51aa504c385c1e46d8f80fcf08d0eb8bf257ff8ca96bcf892bef6a5637aae4ea` | 2026-10-12 |
| Task D applied | stage_2_hooks.py | `66528da2ad0078f4dd68e87a19b9ed2210ab10602b7e4e5e48a24bdf6878ae65` | 2026-10-12 |
| **Task F Option A applied (PHASE 1 LAUNCH SHA)** | **v37.4** | **`77b0097d95d61b8d5430b870a45889477e5006fc5443600aa6233456e8387f87`** | **2026-10-13** |

Both patches realize pre-registered spec: Task D wires the reactive arm per eighth addendum §2b-d; Task F Option A enables the §3e / 015 R1 prediction-actual gap moderator per fifth addendum. No drift. The Phase-1-launch SHA is `77b0097d...`.

## Regression test results

### Hot mode, seed 20, LEAK=False — PASS bit-identical through BOTH patches
- `burn_integral` = 1167.3661594356
- `max_coherent_steps` = 2873
- `pop_final` = 6

Values preserved exactly through Task D (observer-off in hot) and Task F (schema extension is pure dict append).

### Reactive mode, seed 20 (benign trajectory) — PASS
- `replay_fallback_case_a_count`: 0
- `replay_divergence_case_b_count`: 0
- hot-coherent (agent, step) set == reactive-coherent set EXACTLY
- Per-agent `coherent_steps` bit-exact: hot `{0: 2873, 1: 2873}` == reactive `{0: 2873, 1: 2873}`

### Reactive mode, seed 22 (materially-divergent trajectory, Sal 016 strengthening) — PASS
- `replay_fallback_case_a_count`: 0
- `replay_divergence_case_b_count`: 0
- hot-coherent (agent, step) set == reactive-coherent set EXACTLY
- Per-agent `coherent_steps` bit-exact: hot `{0: 2889, 1: 2889, 4: 1141, 5: 1141}` == reactive `{0: 2889, 1: 2889, 4: 1141, 5: 1141}`
- Common coherent tuples: 8060
- Mean `|canonical_burn_decay_mult_hot − canonical_burn_decay_mult_reactive|`: **0.00279004** (max 0.01732775)
- Non-zero mod-value diffs: **8056 / 8060 (99.95%)** — F5 override firing confirmed
- hot `burn_integral`: 486.358480; reactive `burn_integral`: 547.009104; Δ: **+60.650624** (12.5% relative)

Seed 22 widens the empirical surface relative to seed 20: materially-divergent modulation values, coherence held bit-exact by replay construction, counter paths exercised every step. Interpretation walked in ninth addendum §3.

### Moderator end-to-end verification — PASS
`compute_prediction_actual_gap(hot_results)` on hot seed 20, 3000 steps:
- `n_coherent`: 5746
- `mean_abs_gap`: **130.93 steps** (genuine prediction error)

Same on reactive seed 20 (not read by §3e; populated for schema consistency):
- `n_coherent`: 5746
- `mean_abs_gap`: **1.39 steps** (actuals step-to-step smoothness per ninth addendum §3b)

The ~94× ratio is diagnostic: it confirms F5 is firing and `step_predictions` is reading non-F5-overridden values. Phase 5 reports should flag any reactive `mean_abs_gap > ~10 steps` as a potential mechanism anomaly (ninth addendum §3b).

## Audit trail

Full implementation audit coverage, pre-reg discipline, and multi-cell review chain documented in parent directory (`pre-registrations/crack-seed/stage_1_prereg_*.md`). The eighth addendum (`stage_1_prereg_eighth_addendum_2026-10-09.md`) is the governing document for the current Stage 2 design. The ninth addendum (`stage_1_prereg_ninth_addendum_2026-10-13.md`) locks the Phase-1-launch SHA, specifies the snapshot schema extension, and documents reactive-semantics for reader safety.
