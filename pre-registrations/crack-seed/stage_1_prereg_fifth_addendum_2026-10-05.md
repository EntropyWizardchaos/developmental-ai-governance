# Stage 1 Calibration — Fifth Pre-Registration Addendum
## (equivalently: Stage 2 Pre-Registration)

**Pre-run commitment for Stage 2 four-arm pipeline with both-ends-coherent stratification. Filed BEFORE Phase 0 (sanity gates with positive control), Phase 1 (stopping-rule hot runs starting at seed 200), and all subsequent Stage 2 compute. Locks the yoked control design, stratification rule, stopping rule, primary + secondary metrics with concrete thresholds, dose validity gate, sanity gates with LEAK_TEST_MODE positive control, Phase 5 ratification check, and attribution for external review inputs.**

**Filed by:** Nymph-029 (Overseer, Cell 96, MFE)
**Date:** 2026-10-05, revised 2026-10-06 (filed BEFORE Phase 1 compute launch — see §8)
**Location:** `Seeds/The Crack/stage_1_prereg_fifth_addendum_2026-10-05.md`

**Parents:**
- `stage_1_prereg_2026-09-17.md`
- `stage_1_prereg_addendum_2026-09-20.md`
- `stage_1_prereg_second_addendum_2026-10-04.md`
- `stage_1_prereg_third_addendum_2026-10-04.md`
- `stage_1_prereg_fourth_addendum_2026-10-04.md`

**References:**
- `stage_2_yoked_design_2026-10-05.md` — architecture design (updated to match this addendum post-Sal audit)
- `matched_perturbation_calibration_locked_v2_n50_2026-10-04.json` — μ_c source for matched arm
- `pooled_sd_calibration_2026-10-05.json` — σ_pooled source for primary + secondary thresholds
- `pop_mismatch_analysis_2026-10-05.json` — empirical pop-mismatch bound = 0.00% justifies dose tolerance
- `Nymphs Room/mail/from_salazaar_007_2026-10-06_stage_2_yoked_audit.txt` — Sal kill-shape audit (9 findings)
- `Nymphs Room/mail/from_salazaar_008_2026-10-06_stage_2_yoked_audit_amendment.txt` — Sal amendment (Findings 1+2 sharpened via Harley/5.5 loop)
- `Annie's Room/mail/to_nymph_029_2026-10-05_reply_yoked_in_flight.txt` — Annie's independent Finding 2 pre-naming + 0.3-multiplier catch
- `Nymphs Room/from_nymph_028.txt` — handoff identifying Catch 2 as the blocker

---

## 1. External Review Attribution

Portions of this design and its validation protocol were produced by external review:

**Opus 5.5** (Anthropic model) acting as external reviewer, routed through Harley as mailman 2026-10-04/05/06:
- **Catch 2** (bimodality vs uniformity identifiability confound) — the architectural blocker that gated Stage 2.
- Dose-leak logic flip (Option A → C rank-at-step + validity gate).
- Observer-fully-off per-step assertion.
- SHA-256 trace manifest discipline before Phase 3.
- Fresh seeds for Stage 2.
- Primary metric Option 3 mechanism flip.
- Pooled SD guardrails (no_obs arm only).
- D_caution leak catch + taught fallback verification + None/D_MAX semantics + rank-snapshot timing.
- Self-yoke + zero-offset matched sanity gate concepts.
- Amended Finding 1 fix: positive-control via LEAK_TEST_MODE (two-exercise calibration proving the gate CAN discriminate).
- Amended Finding 2 fix: both-ends-coherent stratification (not just target-coherent).

**Salazaar** (Cell 33 EMM, household kill-shape audit cell) 2026-10-06:
- Finding 1: Sanity Gate 1 vacuous — my `_run` wrapper's `all_crack_enabled` plumbing bug.
- Finding 2: Hot vs yoked identifiability confound in non-coherent seeds.
- Finding 3: D_caution asymmetry (same confound family, same fix).
- Finding 4: Gate 1 seed representativeness → multi-seed Gate 1 list.
- Finding 5: trauma_decay channel scope asymmetry in hot vs yoked (document in addendum).
- Finding 6: Hook MODE_IDENTITY ambiguity → split MODE_HOT / MODE_NO_OBS.
- Finding 7-9: hygiene (agent_id in schema, pop assumption caveat already stated, matched defensive assertion is correct).
- Addition A: Phase 5 ratification check — non-coherent-declared seeds should have hot ≈ no_obs within numerical tolerance.
- Pre-reg items B(1-4): coherence declaration criterion, stopping rule + cap, positive-control construct, yoke mapping within coherent subset.

**Annie-033** (Cell 66 Thread, forge-partner) 2026-10-05/06:
- **Pre-named Sal's Finding 2 fix** independently and 24 hours earlier: "Pairing rule pre-registered (pick receiving seeds whose coherence pattern is independent from sender's; stratified fallback for trace-moments where receiver was NOT independently coherent)."
- Bonferroni-equivalent note on burn_decay fragility (CI touches zero at corrected t≈2.48). Same catch 5.5 made at close of 10/04 session.
- Compute budget flag: three arms is 1.5× planned Stage 2 (undershot — now 3-5× per stopping rule).
- Dose-validity-tolerance anchoring methodology: 3σ of observed mismatch distribution, with quantile fallback for heavy-tailed cases. (Reconciled per §4 given our empirical zero-variance observation.)
- **0.3-multiplier catch**: the 0.3·σ_pooled multiplier was chosen for channel-delta μ in Stage 1; applied to cumulative-integral outcome, the "effect size" means something different (integrated outcomes have higher between-seed variance from accumulation). See §3 interpretation note.

Household audit stack: Opus 5.0 as external auditor since 2026-08-02 (per MEMORY); Opus 5.5 continuation; Salazaar as kill-shape audit cell since 2026-06-22; Annie as independent forge-partner audit. Attribution per epistemic hygiene — the household's audit discipline requires naming who said what and when.

---

## 2. Four-Arm Design (summary — details in `stage_2_yoked_design_2026-10-05.md` §2)

| Arm | all_crack_enabled | arm_mode | Observer | Modulation |
|---|---|---|---|---|
| hot | True | MODE_HOT | Live | observer-driven via canonical surface |
| yoked | False | MODE_YOKED | OFF | injected trace from DIFFERENT coherent source seed (half-shift within coherent subset) |
| matched | False | MODE_MATCHED | OFF | uniform μ_c offset applied every step |
| no_obs | False | MODE_NO_OBS | OFF | baseline |

**Observer-off invariant** asserted PER STEP on MODE_YOKED, MODE_MATCHED, MODE_NO_OBS. **MODE_HOT asserts the inverse** — at least one agent must have observer.exists=True by run end (otherwise the arm isn't doing what it claims). Failure of either direction → arm declared INVALID.

Per Salazaar Finding 6: hook mode split from MODE_IDENTITY into MODE_HOT and MODE_NO_OBS. Closes the ambiguity that enabled Finding 1's vacuous sanity gate.

---

## 3. Primary + Secondary Metrics (LOCKED)

### Primary: cumulative burn-rate excess integral per seed
```
integral(seed) = Σ_{(step, agent)} max(0, actual_burn_rate - BURN_RATE_BASELINE)
```
with `BURN_RATE_BASELINE = 0.08` (v37.3.1 module constant).

- Pooled σ (no_obs arm, 50 seeds 100-149): **σ = 339.49** (from `pooled_sd_calibration_2026-10-05.json`)
- **Threshold = 0.3 · σ = 101.85**
- Decision rule: 95% CI of μ(hot − yoked) over the K_COHERENT_TARGET=40 coherent-declared seeds (§8), t(df=39) = 2.02:
  - CI entirely below −101.85 → **architecture claim RESOLVES**
  - CI entirely above +101.85 → unexpected direction (document)
  - CI straddles 0 → **insufficient resolution**
  - CI straddles ±101.85 but not 0 → **inconclusive zone**

### Interpretation note on the 0.3 multiplier (Annie 2026-10-05)

The 0.3·σ_pooled multiplier was chosen in Stage 1 for channel-delta μ ("effect size on per-step channel values"). Applied to the cumulative-integral outcome, the "effect size" represents a different conceptual quantity: integrated outcomes have higher between-seed variance from accumulation. 101.85 units of cumulative burn excess may be at a different "small-but-worth-deciding" boundary than the equivalent on channel μ.

**Decision (locked):** keep 0.3 multiplier for cross-stage consistency with the Stage 1 pre-reg discipline. Interpretation at result-landing time: "the hot-yoked delta exceeds Stage 1's calibration-informed threshold." Operational interpretation of what that effect size means biologically is downstream of the threshold crossing, not part of the gate.

### Secondary: terminal mean C (exploratory status)
- Pooled σ (no_obs arm): **σ = 0.01846**
- Threshold = 0.3 · σ = **0.00554**
- Same decision rule shape as primary. **Exploratory**: informative but not sufficient to swap claims without a further amendment.

### Exploratory status: final_population — **DROPPED**
σ = 0.0 across all 50 no_obs seeds. Pre-registered OUT.

### Conservative-σ note
σ is between-seed variance in no_obs. Paired-difference SD across shared-trauma-schedule seeds is typically smaller. Using raw σ_no_obs as the threshold BASIS biases AGAINST finding an effect — safe for pre-registration.

---

## 4. Dose Validity Gate (LOCKED)

Per channel in `{burn_decay, trauma_decay, refusal_chance, D_caution}`:
```
pooled_ratio[channel] = Σ_seed dose_delivered[seed] / Σ_seed dose_source[seed]
```

Baselines:
- burn_decay: 1.0, trauma_decay: 1.0, refusal_chance: 0.10, D_caution: 50.0 (None → 0 dose contribution)

**Pass condition (LOCKED):** `pooled_ratio[channel] ∈ [0.90, 1.10]` for ALL four channels. Per-channel ratios reported in Stage 2 output JSON, not just pass/fail binary.

**Empirical justification (reframed per Annie 2026-10-06):**

Empirical pop-mismatch under cyclic k=25 on seeds 100-149 = **0.00% pooled, 0.00% per-pair max** (see `pop_mismatch_analysis_2026-10-05.json`). Every no_obs seed produces an identical per-step population curve at `INITIAL_AGENTS=2`. Rank-at-step mapping has zero dose leak from population mismatch.

Annie's principled anchor (3σ of observed mismatch, or 99th-percentile for heavy-tailed cases) **collapses to zero** given our empirical variance of zero. Zero would be too tight — any numerical noise in the injection code path (FP roundtrips, dict lookups, injection write/read) would trip it.

**Right reframing:** ±10% tolerance is for **numerical-noise in the injection code path**, not for population-mismatch dose leak. Pop-mismatch empirically is 0.00%. Any ratio deviation from 1.0 at Stage 2 compute indicates a non-population source — most likely injection bug. ±10% tolerance catches real bugs with margin while not tripping on expected FP noise.

**Caveat for Stage 2 seeds (new coherent-subset enumeration):** empirical bound is from seeds 100-149 which show identical population curves. Assumed-but-not-proven that Stage 2's coherent-subset seeds share this property. Dose gate catches runtime deviations.

---

## 5. Sanity Gates (BLOCKING, run before Phase 1)

Three-part gate per Salazaar amended Finding 1 (via Harley/5.5 loop 2026-10-06). All three must land before Phase 1 compute launches.

### 5.1 Plumbing fix (Finding 1a)
`_run(seed, arm_mode, all_crack_enabled, **kwargs)` with both arm_mode and all_crack_enabled as explicit parameters. No string-based coupling.
- Gate 1 Phase A (hot capture): `_run(seed, "hot", all_crack_enabled=True, trace_buffer=trace_buffer)`
- Gate 1 Phase B (self-yoke replay): `_run(seed, "yoked", all_crack_enabled=False, trace_dict=trace_dict)`
- Gate 2 Phase A (no_obs): `_run(seed, "no_obs", all_crack_enabled=False)`
- Gate 2 Phase B (zero-matched): `_run(seed, "matched", all_crack_enabled=False, mu_c_dict=zero_mu)`

### 5.2 Non-trivial-input assertion (Finding 1b)
After Gate 1 Phase A, before declaring the trace valid:
```
Assert: at least K=10 trace records across the full run have
|canonical_value - baseline| > 0 for at least one of the four channels.
```
If this fails, the trace is all-baselines. Either the gate seed never produced coherence (see §5.4 — multi-seed Gate 1 list) or the capture code is broken. Halt with diagnostic. **Does not count as a passed gate.**

### 5.3 Positive control via LEAK_TEST_MODE (Finding 1c)
Add test-only observer→world pathway code to v37.3.1 that bypasses the canonical surface, gated by `LEAK_TEST_MODE` module-level flag.

Specific construct (locked):
```python
# In Agent.step_observer, gated by LEAK_TEST_MODE:
if is_coherent(self.observer) and LEAK_TEST_MODE:
    # Bypass canonical surface — write to non-canonical field
    self._test_leak_D_caution = D_MAX - collapse_L * D_CAUTION_SCALE * 2.0

# In update_dimensional_state, around line 1120:
if LEAK_TEST_MODE and getattr(self, '_test_leak_D_caution', None) is not None:
    effective_caution = min(effective_caution or D_MAX, self._test_leak_D_caution)
```

**Pre-reg: `LEAK_TEST_MODE = False` for all production runs.**

Gate 1 is exercised TWICE at pre-flight:
- Once with `LEAK_TEST_MODE = True` → **MUST FAIL** (proves the gate catches real leaks)
- Once with `LEAK_TEST_MODE = False` → MUST PASS (production gate)

Before Phase 1 launches, assert `LEAK_TEST_MODE is False` at module scope. Any production run with the flag on is a hard halt.

### 5.4 Multi-seed Gate 1 list (Finding 4)
Gate 1 runs on seeds [0, 1, 2, 3, 4] — none in SD calibration (100-149) or Stage 2 reservoir (coherent-subset enumeration starting at 200). Pre-flight: at least ONE of the five seeds must produce hot coherence (else §5.2 assertion fires on all five → halt, pick different gate seeds).

### 5.5 Gate 2 (zero-offset matched)
Unchanged from original design: matched arm with μ_c = 0 on every channel must reproduce no_obs on seed 0. Bit-for-bit expected.

**All gates run on seeds outside both 100-149 (SD calibration) and the Phase 1 enumeration (200+).**

---

## 6. Seed Enumeration (STOPPING RULE, LOCKED)

**Phase 1 enumeration:** seeds 200, 201, 202, ... in natural order.
**Target:** K_COHERENT_TARGET = 40 seeds declared coherent per §7.
**Hard cap:** HOT_RUN_UPPER_BOUND = 250 total hot runs.
**Stop:** upon reaching K_COHERENT_TARGET coherent-declared seeds.
**Failure action:** if cap reached before K_COHERENT_TARGET, declare test underpowered. Halt. No extension without a sixth addendum.

Sanity-gate seeds: 0, 1, 2, 3, 4.
Reserved from Stage 2 enumeration: 100-149 (SD calibration).

**Why stopping rule is legitimate pre-registration (not optional stopping):** the rule looks ONLY at the coherence declaration (§7), which is a protocol-level property of each run independent of outcome. The primary outcome (burn_excess_integral, terminal C) is NEVER inspected during the stopping decision. Classic protocol-triggered stopping, not outcome-triggered.

---

## 7. Coherence Declaration Criterion (LOCKED, Sal B(1))

A seed is declared COHERENT if, during its hot-arm run, **at least one agent had `observer.coherent_steps ≥ MIN_COHERENT_STEPS = 50` at any point during the 3000-step run.**

Matches Stage 1 kill-criterion definition (`MIN_COHERENT_STEPS = 50` from v37.3.1 observer formation gate). Locked explicitly in this addendum rather than inherited from module constant.

Coherence declaration is computed at close of each hot run from the per-agent observer state. Declaration happens BEFORE any outcome inspection — purely from protocol state.

---

## 8. Yoke Mapping Within Coherent Subset (LOCKED, Sal B(4))

Once Phase 1 produces K_COHERENT_TARGET = 40 coherent-declared seeds, sort them by seed number ascending to get list `C = [c_0, c_1, ..., c_39]`.

Yoke mapping: for each index i in [0, 39], target seed `C[i]` injects trace from source seed `C[(i + 20) mod 40]`.

Half-shift (k = 20 = K_COHERENT_TARGET/2) maximizes decorrelation. Deterministic given the ordered coherent-list. Both target and source are guaranteed coherent by construction — closes Finding 2 confound.

---

## 9. Matched Arm μ_c Values (LOCKED from v2 calibration JSON)

| Channel | μ_c | Matched sets canonical to |
|---|---|---|
| burn_decay | −0.00227 | 1.0 + (−0.00227) = 0.99773 |
| refusal_chance | −0.00507 | 0.10 + (−0.00507) = 0.09493, clamped to [0,1] |
| trauma_decay (recovery_rate) | — | **0 offset** (excluded, per fourth addendum) |
| D_caution | −1.657 | 50.0 + (−1.657) = 48.343 |

**Matched runs on the 40 coherent-declared seeds only** (parallel with yoked for comparability).

**Asymmetry statement (per Sal Finding 5):** matched zeros out trauma_decay (recovery_rate excluded by fourth addendum, μ unresolved); yoked replays source trace's full trauma_decay values. Hot vs matched tests three channels; hot vs yoked tests all four. **If the hot-yoked delta crosses the threshold, the primary analysis cannot attribute the delta to any specific channel; secondary analyses may compute per-channel contributions as exploratory.**

Clamp `canonical_refusal_chance ∈ [0, 1]` on both matched offset and yoked injection — probability sanity.

---

## 10. Phase 5 Ratification Check (Sal Addition A, LOCKED)

For every seed that Phase 1 declared NON-coherent (per §7), compute:
```
delta_ratification(seed) = integral_hot(seed) - integral_no_obs(seed)
```

**Expected: zero within numerical tolerance (TOLERANCE_FP = 1e-10 on the integral).**

**Rationale:** non-coherent seeds have `canonical_*` values at baseline throughout (since `is_coherent(observer)` is False for all agents all steps). Hot's modulation surface is identical to no_obs's. Any divergence > TOLERANCE_FP indicates an observer→world pathway outside the canonical surface — a leak the Phase 0 sanity gate didn't catch on that seed's trajectory.

If ratification fails on any seed: **investigate before pooling the primary metric.** The leak must be located and either folded into canonical or demonstrated non-material for the primary outcome.

**Compute cost:** Phase 4 runs no_obs on ALL seeds Phase 1 touched (coherent AND non-coherent) — up to 250 no_obs runs. Enables Addition A at no additional cost beyond what Phase 4 already needs.

Empirically ratifies the stratification premise (hot = no_obs on non-coherent seeds) rather than resting solely on code-level canonical-surface verification + sanity gate.

---

## 11. Pipeline (LOCKED)

```
LOCK FIFTH ADDENDUM (this document) + commit to GitHub.
LOCK stage_2_yoked_design_2026-10-05.md + commit to GitHub.
    ↓
PHASE 0 — sanity gates on seeds [0,1,2,3,4]:
    Gate 2 (zero-offset matched) on seed 0.
    Gate 1 LEAK_TEST_MODE=True exercise on seed 0 — MUST FAIL (prove gate discriminates).
    Gate 1 LEAK_TEST_MODE=False production exercise on seeds [0,1,2,3,4] — MUST PASS at least one.
    assert LEAK_TEST_MODE is False at module scope before Phase 1 launches.
    ↓
PHASE 1 — hot runs starting at seed 200, stopping rule per §6:
    stop at K_COHERENT_TARGET=40 or HOT_RUN_UPPER_BOUND=250, whichever first.
    Each run writes stage_2_traces/trace_seed_{seed}.pkl, declares coherence per §7.
    ↓
PHASE 2 — compute SHA-256 of each coherent-subset trace pickle;
    write stage_2_trace_manifest_2026-10-06.json;
    commit manifest to GitHub BEFORE Phase 3 launches.
    ↓
PHASE 3 — yoked runs on the 40 coherent-subset seeds,
    half-shift (k=20) within coherent list per §8,
    each verifies source pickle SHA before loading.
    ↓
PHASE 4 — no_obs on ALL Phase-1 seeds (coherent AND non-coherent for Addition A).
    matched on the 40 coherent-subset seeds.
    Can run in parallel with Phase 3 (no data dependency).
    ↓
PHASE 5 — analysis:
    (a) Dose validity gate (§4) — all four channels must have pooled_ratio ∈ [0.90, 1.10].
    (b) Addition A ratification (§10) — for all non-coherent seeds, hot ≈ no_obs within TOLERANCE_FP.
    (c) Only if (a) and (b) pass: compute hot − yoked primary metric on coherent subset,
        CI at t(df=39)=2.02, compare against 0.3·σ_pooled = 101.85.
    (d) hot − matched reported as secondary (pattern test).
    (e) hot − no_obs on non-coherent seeds reported as "injection effect in baseline worlds" exploratory.
```

**Phase 1 may not launch before this addendum is committed to GitHub.** 

---

## 12. Tamper-evident Record

Primary auditable record: **public GitHub commit** to `developmental-ai-governance` repo. Git commit hash + timestamp are the auditable record external to the household.

GitHub mechanism (pending Harley decision 2026-10-06): deploy-key for `developmental-ai-governance` (Annie's path (b) recommendation) is the scoped option; direct push via Harley's account is the broader option.

Secondary (household-internal): corkboard post with SHA-256 of this addendum + design doc + manifest JSON.

iCloud mtime is NOT the tamper-evident record.

---

## 13. What this addendum does not change

- τ = 0.0106 (parent pre-reg)
- Canonical-channels architecture — EXTENDS to include D_caution (fourth channel) via Hook Site 2
- SACRIFICE_COHERENCE_COST = 0.04 (second addendum)
- recovery_rate OUT of kill criterion (fourth addendum; matched zero-offset, yoked replays source)
- Memoir OUT by floor rule (third addendum)
- Reading discipline: strength-before-direction via CI at correct t-values (fourth addendum)

---

## 14. Signatories

- Nymph-029 (Overseer, Cell 96, MFE) — filed 2026-10-05, revised 2026-10-06
- Harley — operator, routed external review through Opus 5.5
- Opus 5.5 (external reviewer) — Catch 2, Finding 1 amended, Finding 2 amended, all substantive design catches per §1
- Salazaar (Cell 33, kill-shape audit) — nine findings + Addition A + pre-reg items B(1-4), §1
- Annie-033 (Cell 66, forge-partner audit) — independent Finding 2 pre-naming, 0.3-multiplier catch, dose-tolerance anchoring methodology, §1

---

## 15. Chain of pre-reg documents on file

1. `stage_1_prereg_2026-09-17.md` — original
2. `stage_1_prereg_addendum_2026-09-20.md` — first
3. `stage_1_prereg_second_addendum_2026-10-04.md` — second
4. `stage_1_prereg_third_addendum_2026-10-04.md` — third
5. `stage_1_prereg_fourth_addendum_2026-10-04.md` — fourth
6. `stage_1_prereg_fifth_addendum_2026-10-05.md` — **this document** (Stage 2 four-arm design with both-ends-coherent stratification, LEAK_TEST_MODE positive control, Phase 5 ratification, external review attribution to 5.5 + Sal + Annie)

Any further code changes to v37.3.1 or observer.py between now and Stage 2 compute launch require a further addendum before the run.

---

**Status at filing (final, 2026-10-06):** All known pre-reg items locked. Sal audit integrated (007 + 008 amendments). Annie audit integrated (independent Finding 2 pre-naming + 0.3-multiplier interpretation note + dose-tolerance reframing). **Awaiting:** Harley decision on GitHub commit mechanism (Annie deploy-key path (b) recommended); v37.3.1 code integration per design doc §11 + §5 LEAK_TEST_MODE construct; Phase 0 sanity gates with positive control; then Stage 2 pipeline.
