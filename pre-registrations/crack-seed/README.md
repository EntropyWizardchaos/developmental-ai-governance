# Crack Seed — Pre-Registered Experiments

Pre-registration artifacts for the Crack seed (structural metacognition experiment on the Society Womb v37.3.1 simulation). Housed here for tamper-evident timestamp via git commit, external to the household's iCloud workspace.

## What this is testing

Whether observer formation (bounded-pressure predictive self-modeling) produces behavioral effects that cannot be reproduced by a matched-magnitude non-predictive modulation. The architectural claim: observer predictions do real work in coupling an agent to its own trajectory. The kill criterion: hot (observer live) vs yoked (replay of hot's modulation into a different world) on cumulative burn-rate excess integral.

## Chain of pre-registrations

The Stage 1 calibration series produced four addenda before Stage 2. This directory holds the fifth addendum (Stage 2 pre-reg) and the design doc, plus the calibration JSONs they cite.

Full chain (first four addenda live in the household workspace):
1. `stage_1_prereg_2026-09-17.md` — original (not committed here)
2. `stage_1_prereg_addendum_2026-09-20.md` — XOR fix (not committed here)
3. `stage_1_prereg_second_addendum_2026-10-04.md` — canonical-channels fix (not committed here)
4. `stage_1_prereg_third_addendum_2026-10-04.md` — μ scope + memoir floor (not committed here)
5. `stage_1_prereg_fourth_addendum_2026-10-04.md` — N=50 fresh seeds + path 2 secondary (not committed here)
6. **`stage_1_prereg_fifth_addendum_2026-10-05.md`** ← this directory. Stage 2 four-arm design with both-ends-coherent stratification, LEAK_TEST_MODE positive control, Phase 5 ratification, external review attribution.
7. **`stage_1_prereg_sixth_addendum_2026-10-08.md`** ← this directory. Gate 1 target seed lock (seed 20) after pre-flight fallback.
8. **`stage_1_prereg_seventh_addendum_2026-10-08.md`** ← this directory. D_caution behavioral inertness finding; LEAK relocated D_caution → refusal_chance with activation counter + INVALID third state; per-channel behavioral activation audit as Phase 0.5 BLOCKER; ablation methodology for per-channel attribution.
9. **`stage_1_prereg_eighth_addendum_2026-10-09.md`** ← this directory. Five-arm design (adds reactive arm in replay mode); single-channel burn-decay-timing claim; LEAK relocated refusal_chance → burn_decay; dose gate zero-source-dose handling; Phase 5 ratification stratified by total-coherent-agent-steps; MODE_HOT crash softening + crash handling pre-reg; TOST equivalence at ±0.3σ; intersection-union test; Chord-reference detached from claim statement. Integrates six audit catches: Sal 012/013/014/015 + 5.5 cycles 4/5/6 + Iris cross-domain + Annie forge completions.

## Contents

- **`stage_1_prereg_fifth_addendum_2026-10-05.md`** — the governing pre-reg for Stage 2.
- **`stage_1_prereg_sixth_addendum_2026-10-08.md`** — Gate 1 target seed lock.
- **`stage_1_prereg_seventh_addendum_2026-10-08.md`** — D_caution inertness + LEAK relocation + per-channel audit + ablation methodology.
- **`stage_2_yoked_design_2026-10-05.md`** — architecture design document; implementation reference matching the pre-reg.
- **`pooled_sd_calibration_2026-10-05.json`** — source of the primary + secondary metric σ_pooled values cited in fifth addendum §3 (burn_excess_integral σ=339.49 → threshold 101.85; terminal_C σ=0.0185 → threshold 0.00554). Computed from no_obs arm only (control arm), 50 seeds (100-149).
- **`pop_mismatch_analysis_2026-10-05.json`** — source of the dose-tolerance empirical justification cited in fifth addendum §4 (empirical pop-mismatch under cyclic k=25 shift = 0.00%, every seed produces identical per-step population curve).
- **`matched_perturbation_calibration_locked_v2_n50_2026-10-04.json`** — source of the μ_c values cited in fifth addendum §9 for the matched arm (burn_decay −0.00227, refusal −0.00507, D_caution −1.657; recovery_rate excluded per fourth addendum).
- **`preflight_coherence_scan_2026-10-07.json`** — pre-flight on seeds 0-4 (0/5 coherent); fires fallback discipline cited in sixth addendum.
- **`secondary_preflight_seed_20_2026-10-08.json`** — seed 20 coherence verification on current v37.3.1 (max_coherent_steps=2873); referenced by sixth addendum.
- **`dampening_firing_probe_2026-10-08.json`** — probe measuring D_caution dampening firing rate across seeds {20, 22, 33}; 0/43,500 events; the finding driving the seventh addendum.

## External review attribution

All substantive design catches are attributed in the addendum §1 and design doc §15:
- **Opus 5.5** (external reviewer via Harley) — Catch 2 (identifiability confound), amended Finding 1 (positive control), amended Finding 2 (both-ends-coherent), dose-leak flip, SHA manifest, and more.
- **Salazaar** (household kill-shape audit cell) — 9 findings in audit letter 007, 2 sharpened amendments in 008, Addition A (Phase 5 ratification), pre-reg items B(1-4).
- **Annie-033** (household forge-partner audit) — independent pre-naming of Finding 2 fix 24 hours before Salazaar's audit; 0.3-multiplier interpretation note; dose-tolerance anchoring methodology.

## Pipeline (brief)

```
LOCK fifth addendum + design doc + commit to GitHub (this commit).
  ↓
PHASE 0 — sanity gates with LEAK_TEST_MODE positive control.
  ↓
PHASE 1 — hot runs starting at seed 200, stopping rule (K=40 coherent, cap 250).
  ↓
PHASE 2 — SHA-256 trace manifest, commit to GitHub.
  ↓
PHASE 3 — yoked runs on 40 coherent-subset seeds (half-shift mapping within coherent list).
  ↓
PHASE 4 — no_obs on ALL Phase-1 seeds (for Phase 5 Addition A) + matched on 40 coherent seeds.
  ↓
PHASE 5 — dose validity + Addition A ratification; then primary hot−yoked at CI t(df=39)=2.02.
```

Expected total compute: ~16 hours overnight.

## Status

**Fifth addendum: LOCKED.** Phase 1 compute may launch once v37.3.1 code integration lands (hooks, LEAK_TEST_MODE, rename of observer_D_caution to canonical_D_caution, MODE_HOT inverse assertion) + Phase 0 sanity gates pass.

Trace manifest commit will land in this directory after Phase 1.
