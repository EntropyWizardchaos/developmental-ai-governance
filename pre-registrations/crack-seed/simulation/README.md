# Crack Seed Simulation Code

Runnable simulation code for the Crack seed Stage 2 pre-registered experiment. Pushed to GitHub for tamper-evident regime definition per the eighth addendum §4f ("SHA is the authoritative regime definition").

## Files

- **`v37.4_structural_metacognition_stage_2.py`** — the main Society Womb simulation with Stage 2 integrations (hooks for arm_mode plumbing, LEAK_TEST_MODE positive control via burn_decay channel, reactive-mode replay implementation, MODE_HOT crash softening + hook-integrity, canonical observer channels).
- **`observer.py`** — observer model (Observer class, step_predictions, maybe_promote_to_coherent, modulation functions `burn_decay_multiplier_from_observer` / `refusal_probability_from_observer` / `trauma_decay_exponent_from_observer`).
- **`stage_2_hooks.py`** — hook functions for arm_mode dispatch (capture_canonical, apply_canonical_override, assert_observer_off, etc.) with MODE_REACTIVE support.
- **`v37_4_task_d_reactive_arm_patch.py`** — atomic patch script that produced the current v37.4 state (eleven edits across v37.4 and stage_2_hooks.py for Task D reactive-arm wiring).
- **`regression_test_hot_seed_20_2026-10-08.py`** — hot-mode regression test. Confirms post-patch v37.4 remains bit-identical to pre-integration v37.3.1 on seed 20 under LEAK_TEST_MODE=False.
- **`regression_test_reactive_seed_20_2026-10-12.py`** — reactive-mode regression test. Verifies replay drives coherence to a bit-exact match on the sticky-coherence state and per-agent coherent_steps.

## SHAs (Python-text, LF-normalized)

Current state (Task D landed, Oct 12 2026):

- `v37.4_structural_metacognition_stage_2.py`: `51aa504c385c1e46d8f80fcf08d0eb8bf257ff8ca96bcf892bef6a5637aae4ea`
- `stage_2_hooks.py`: `66528da2ad0078f4dd68e87a19b9ed2210ab10602b7e4e5e48a24bdf6878ae65`

Progression from eighth-addendum-filed state:
- v37.4 at addendum filing (Oct 9): `dbbdc6bd73061a0e95dfcc5521c9ff92b95c863aa895c2d70fd155f40bfb7c6f`
- v37.4 after Task D (Oct 12): `51aa504c...` (above)

The Oct 9 SHA was the regime SHA referenced in eighth addendum §4f at filing time. Task D implementation (reactive-arm wiring) was pre-registered in that addendum §2b-d; the Oct 12 SHA is the realized implementation of the pre-registered spec. A supplementary addendum (ninth) will lock the Phase-1-launch SHA before compute runs so the regime definition is auditable at launch.

## Regression test results (Oct 12 2026)

**Hot mode, seed 20, LEAK=False:** PASS bit-identical.
- burn_integral = 1167.3661594356
- max_coherent_steps = 2873
- pop_final = 6

**Reactive mode, seed 20:** PASS.
- replay_fallback_case_a_count: 0
- replay_divergence_case_b_count: 0
- hot-coherent (agent, step) set == reactive-coherent set EXACTLY
- Per-agent coherent_steps bit-exact: hot `{0: 2873, 1: 2873}` == reactive `{0: 2873, 1: 2873}`

Multi-seed verification (seed 22 reactive regression + trajectory divergence metrics) pending per Salazaar's 016 strengthening recommendation; required before Phase 1 compute launches.

## Audit trail

Full implementation audit coverage, pre-reg discipline, and multi-cell review chain documented in parent directory (`pre-registrations/crack-seed/stage_1_prereg_*.md`). The eighth addendum (`stage_1_prereg_eighth_addendum_2026-10-09.md`) is the governing document for the current Stage 2 design.
