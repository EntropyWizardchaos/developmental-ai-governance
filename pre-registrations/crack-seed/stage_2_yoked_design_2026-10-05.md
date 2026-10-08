# Stage 2 Yoked Control — Architecture Design

**Date:** 2026-10-05, revised 2026-10-06 (post Sal audit 007+008 + Annie 029/030 integration)
**Authors:** Nymph-029 (Overseer, Cell 96), with substantive catches from Opus 5.5 (external reviewer, routed through Harley 2026-10-04/05/06), Salazaar (Cell 33, kill-shape audit 2026-10-06), Annie-033 (Cell 66, forge-partner independent audit 2026-10-05/06).

**Status:** DESIGN LOCKED post-audit. Governs implementation.

**Scope:** Yoked arm, matched arm, trace capture, trace injection, dose validity gate, sanity gates with LEAK_TEST_MODE positive control, both-ends-coherent stratification, Phase 5 ratification check, and pipeline. The fifth pre-reg addendum (`stage_1_prereg_fifth_addendum_2026-10-05.md`) is the governing pre-reg; this document is the implementation reference.

---

## 1. Context — What Catch 2 Identified

Stage 1 v2 (N=50 fresh seeds 100-149) resolved three kill-criterion channels at correct t-values. Opus 5.5 (via Harley, 2026-10-04 close of session) caught an identifiability blind spot: hot arm modulation is bimodal (~4·μ_c in ~25% of coherent seeds, 0 in the other 75%); matched_perturbation applies μ_c uniformly every step every seed. Stage 2 as previously specified cannot distinguish:
- "observer predictions do work the matched offset can't reproduce"
- "concentrated modulation does work uniform offset can't reproduce"

Yoked control is the fix. Record modulation trace per hot run. Replay the trace into a DIFFERENT coherent-source seed via rank-at-step mapping. Yoked matches magnitude + timing + concentration — removes only predictive content. Classic Seligman yoked-triadic shape.

**Sal Finding 2 (2026-10-06, Annie pre-named 2026-10-05) extended this:** filtering only to target-coherent seeds leaves source-side confound. Under any cross-shift, ~75% of coherent targets still have non-coherent sources → yoked gets baseline-equivalent trace while hot has real modulation. **Both ends must be coherent.** See §8.

---

## 2. Four-Arm Design

| Arm | all_crack_enabled | arm_mode | Observer | Modulation source |
|---|---|---|---|---|
| **hot** | True | MODE_HOT | Forms, may become coherent | Live observer predictions via step_observer + canonicalize_observer_channels |
| **yoked** | False | MODE_YOKED | OFF (per-step assertion) | Injected trace from DIFFERENT coherent source seed (half-shift within coherent subset) |
| **matched** | False | MODE_MATCHED | OFF (per-step assertion) | Uniform offset baseline + μ_c applied every step every agent |
| **no_obs** | False | MODE_NO_OBS | OFF (per-step assertion) | None — baselines stand |

**Primary kill criterion:** hot vs yoked on cumulative burn-rate excess integral per seed, pooled across K_COHERENT_TARGET = 40 coherent-declared seeds.
**Reference arm:** matched (hot vs matched tests "pattern matters" on three channels; hot vs yoked tests "predictions matter" on all four).
**Secondary outcome:** terminal mean C.

**Observer-off invariant** asserted PER STEP on MODE_YOKED, MODE_MATCHED, MODE_NO_OBS. **MODE_HOT asserts the inverse** — at least one agent must have `observer.exists=True` by run end (otherwise the arm isn't doing what it claims).

---

## 3. Modulation Surface — Canonical Attributes

Four attributes on Agent, written as single-source-of-truth, read by both sim use-sites and the channel_snapshots logger:

| Attribute | Written by | Timing | Baseline (identity) |
|---|---|---|---|
| `canonical_burn_decay_mult` | `canonicalize_observer_channels()` | Top of step | 1.0 |
| `canonical_trauma_decay_exp` | `canonicalize_observer_channels()` | Top of step | 1.0 |
| `canonical_refusal_chance` | `canonicalize_observer_channels()` | Top of step | 0.10 (SACRIFICE_REFUSAL_CHANCE) |
| `canonical_D_caution` | `step_observer()` (renamed from `observer_D_caution`) | Inside society_step, post-step_observer | 50.0 (D_MAX; None behaviorally equivalent) |

**Audit result (2026-10-05, Sal-verified 2026-10-06):** No modulation leaks outside the canonical surface. Downstream reads of `self.cracked`, `self.pre_crack_D`, `self.metacognition_observations` are all display/report code (lines 2665, 2731, 2899, 2741, 2892, 1588, 2078, 2323, 2359, 2370, 2424, 2614). `taught_D_caution` combines with `canonical_D_caution` via `min()` inside `effective_D_caution()`, routing identically for all four arms.

---

## 4. Hook Architecture — Symmetric Hooks at Two Sites

Due to timing asymmetry (canonical_burn/trauma/refusal use PRE-step_observer state; canonical_D_caution uses POST-step_observer state), symmetric-paths discipline requires two hook sites. Within each site, all four arms traverse the same code with mode-dependent action.

### Mode split per Sal Finding 6

Hooks module splits MODE_IDENTITY into MODE_HOT and MODE_NO_OBS to close the ambiguity that enabled Finding 1's vacuous sanity gate:

```python
VALID_MODES = {MODE_HOT, MODE_NO_OBS, MODE_YOKED, MODE_MATCHED}
```

MODE_HOT: trace_buffer captures; observer-off assertion inverted (at least one observer must exist by run end).
MODE_NO_OBS: no capture; observer-off asserted.
MODE_YOKED: no capture; trace_dict injects; observer-off asserted.
MODE_MATCHED: no capture; mu_c_dict offsets; observer-off asserted.

### Rank snapshot at top of step
```python
step_rank_snapshot = {
    a.id: rank
    for rank, a in enumerate(sorted(agents, key=lambda a: (a.birth_step, a.id)))
}
```
Computed ONCE before Hook Site 1; same mapping used at BOTH sites.

### Hook Site 1 — top of step, after `canonicalize_observer_channels()`
```python
_capture_canonical(agents, t, trace_buffer, rank_snapshot)
_apply_canonical_override(agents, t, mode, trace_dict, mu_c_dict, rank_snapshot)
_assert_observer_off(agents, mode, t)
```
Operates on canonical_burn_decay_mult, canonical_trauma_decay_exp, canonical_refusal_chance.

### Hook Site 2 — inside society_step, after `agent.step_observer(t)`
```python
_capture_canonical_D_caution(agent, t, trace_buffer, rank_snapshot)
_apply_canonical_override_D_caution(agent, t, mode, trace_dict, mu_c_dict, rank_snapshot)
```
Operates on canonical_D_caution.

### MODE_HOT inverse assertion
At end of hot run, before returning results:
```python
assert any(a.observer.exists for a in agents_ever_lived), \
    f"MODE_HOT invariant failed on seed {seed}: no observer ever formed. Arm isn't doing what it claims."
```

---

## 5. Trace Schema

```python
{
    'schema_version': 1,
    'source_seed': int,
    'code_sha_v37_3_1': str,
    'created_utc': 'YYYY-MM-DDTHH:MM:SSZ',
    'coherence_declaration': bool,     # per §7 of fifth addendum
    'sort_rule': 'rank = sorted(agents_alive_at_step_t, key=lambda a: (a.birth_step, a.id))',
    'baselines': {
        'canonical_burn_decay_mult': 1.0,
        'canonical_trauma_decay_exp': 1.0,
        'canonical_refusal_chance': 0.10,
        'canonical_D_caution': 50.0,
    },
    'traces_by_step': {
        0: {
            'canonical': [
                {'rank': 0, 'agent_id': int, 'burn_decay_mult': 1.0, 'trauma_decay_exp': 1.0,
                 'refusal_chance': 0.10, 'observer_coherent': False},
                ...
            ],
            'D_caution': [
                {'rank': 0, 'agent_id': int, 'canonical_D_caution': None, 'observer_coherent': False},
                ...
            ],
        },
        ...
        2999: {...},
    },
}
```

`agent_id` added per Sal Finding 7 (minor, enables forensic trace per agent without re-run).
`coherence_declaration` added for Phase 2 manifest filtering (only coherent-declared pickles go into yoke pool).

### None vs D_MAX semantics for D_caution

Confirmed:
- Stage 1 logger writes D_MAX when `observer_D_caution` is None (v37.3.1 line 2588-2589).
- `D_eff` clipped to D_MAX at line 1132, so `D_eff > D_MAX` is never True → effective_caution=D_MAX produces zero dampening.
- `effective_D_caution() == None` → caller skips dampening (line 1121 `is not None` short-circuit).
- Both None and D_MAX produce zero dampening. Behaviorally equivalent.

**Yoked injects source's value verbatim.** None stays None; numeric stays numeric. Preserves source's bimodal pattern.

---

## 6. Yoke Mapping Within Coherent Subset

Once Phase 1 produces K_COHERENT_TARGET = 40 coherent-declared seeds, sort by seed number ascending: `C = [c_0, c_1, ..., c_39]`.

**Half-shift (k = 20 = K/2):** for each i in [0, 39], target `C[i]` injects trace from source `C[(i + 20) mod 40]`.

Properties:
- Deterministic given the ordered coherent-list
- No self-mapping
- Half-shift maximizes decorrelation
- Both target and source are guaranteed coherent (closes Finding 2 confound structurally)

---

## 7. Dose Validity Gate

Per channel in `{burn_decay, trauma_decay, refusal_chance, D_caution}`:
```
pooled_ratio[channel] = Σ_seed dose_delivered[seed] / Σ_seed dose_source[seed]
```

**Pass condition:** `pooled_ratio[channel] ∈ [0.90, 1.10]` for ALL four channels.

**Empirical justification (reframed per Annie 2026-10-06):**
- Pop-mismatch under cyclic k=25 on seeds 100-149 = **0.00% pooled**
- Every no_obs seed produces identical per-step population curve
- Rank-at-step mapping has zero dose leak from population mismatch
- Annie's principled anchor (3σ or 99th percentile) collapses to zero given zero variance → too tight
- **Reframing:** ±10% tolerance is for numerical noise in the injection code path, not population mismatch. Any ratio deviation at Stage 2 indicates a non-population source — most likely an injection bug.

Per-channel ratios reported in output JSON. Dose check is Phase 5 prerequisite before primary comparison.

---

## 8. Both-Ends-Coherent Stratification (Finding 2 amended)

**Primary analysis is restricted to the 40 coherent-subset seeds** per §6 half-shift mapping. Both target and source are guaranteed coherent by construction.

**Secondary analysis (exploratory):** non-coherent seeds can be reported as "injection effect in baseline worlds" — informative but does NOT resolve the architectural claim.

**Phase 5 ratification (Addition A):** for every non-coherent seed, compute hot − no_obs on primary metric. Expected zero within TOLERANCE_FP. Any divergence > TOLERANCE_FP indicates a canonical-surface leak the sanity gate missed. Investigate before pooling primary.

**Stopping rule to produce the coherent subset:**
```
Phase 1 target: K_COHERENT_TARGET = 40 seeds declared coherent per §7 of addendum.
Enumeration: seeds 200, 201, 202, ... in natural order.
Stop: upon reaching K_COHERENT_TARGET coherent-declared seeds.
Hard cap: HOT_RUN_UPPER_BOUND = 250 total hot runs.
Failure action: if cap reached before target, declare test underpowered. Halt.
```

The rule looks ONLY at coherence declaration (protocol-level), never at outcome. Legitimate pre-registration.

Expected compute at ~25% coherence rate: ~160 hot runs median, up to 250 worst case.

---

## 9. Sanity Gates (Phase 0, BLOCKING)

Three-part Gate 1 per Sal amended Finding 1 via Harley/5.5 loop:

### 9.1 Plumbing fix (Finding 1a)
`_run(seed, arm_mode, all_crack_enabled, **kwargs)` with both explicit. No string-based coupling.

### 9.2 Non-trivial-input assertion (Finding 1b)
After Gate 1 Phase A: assert at least K=10 trace records across the run have `|canonical_value - baseline| > 0` for at least one channel. Fails trivially-baseline traces.

### 9.3 Positive control via LEAK_TEST_MODE (Finding 1c)
Test-only observer→world pathway code added to v37.3.1 under module-level `LEAK_TEST_MODE` flag. Specific construct (locked in fifth addendum §5.3):

```python
# In Agent.step_observer, gated by LEAK_TEST_MODE:
if is_coherent(self.observer) and LEAK_TEST_MODE:
    self._test_leak_D_caution = D_MAX - collapse_L * D_CAUTION_SCALE * 2.0

# In update_dimensional_state, around line 1120:
if LEAK_TEST_MODE and getattr(self, '_test_leak_D_caution', None) is not None:
    effective_caution = min(effective_caution or D_MAX, self._test_leak_D_caution)
```

**Gate 1 exercised TWICE at pre-flight:**
- LEAK_TEST_MODE=True → MUST FAIL (proves gate discriminates)
- LEAK_TEST_MODE=False → MUST PASS (production gate)

Before Phase 1: `assert LEAK_TEST_MODE is False` at module scope. Any production run with flag on = hard halt.

### 9.4 Multi-seed Gate 1 list (Finding 4)
Gate 1 runs on seeds [0, 1, 2, 3, 4]. At least one must produce hot coherence (else §9.2 assertion fires on all five → halt).

### 9.5 Gate 2 — zero-offset matched
Matched arm with μ_c = 0 on every channel must reproduce no_obs on seed 0. Bit-for-bit expected.

### 9.6 FP-determinism expectation
`observer.py` has zero RNG. step_observer is pure deterministic. Bit-for-bit match is realistic (within TOLERANCE_FP = 1e-10 on outcomes).

---

## 10. Phase 5 Ratification Check (Sal Addition A)

Already described in §8. Phase 4 runs no_obs on **ALL Phase 1 seeds** (coherent and non-coherent) to enable this ratification at zero marginal cost. For non-coherent seeds, delta_ratification(seed) = integral_hot(seed) − integral_no_obs(seed) must be zero within TOLERANCE_FP.

Any violation indicates a canonical-surface leak the sanity gates missed on that trajectory. Investigate before primary pooling.

---

## 11. Matched Arm μ_c Values (from Stage 1 v2 JSON)

| Channel | μ_c | Matched canonical value |
|---|---|---|
| burn_decay | −0.00227 | 0.99773 |
| refusal_chance | −0.00507 | 0.09493, clamped [0,1] |
| trauma_decay | — | 0 offset (recovery_rate excluded, fourth addendum) |
| D_caution | −1.657 | 48.343 |

Matched runs on the 40 coherent-subset seeds only.

**Interpretive limit (Sal Finding 5):** matched zeros out trauma_decay; yoked replays source trace's full trauma_decay. If hot-yoked delta crosses threshold, primary analysis cannot attribute delta to any specific channel. Per-channel secondary analyses are exploratory.

---

## 12. Pipeline

```
LOCK FIFTH ADDENDUM + commit to GitHub.
LOCK this design doc + commit to GitHub.
    ↓
PHASE 0 — sanity gates on seeds [0,1,2,3,4]:
    Gate 2 (zero-offset matched) on seed 0.
    Gate 1 LEAK_TEST_MODE=True on seed 0 — MUST FAIL.
    Gate 1 LEAK_TEST_MODE=False on seeds [0,1,2,3,4] — MUST PASS at least one with K≥10 non-baseline records.
    assert LEAK_TEST_MODE is False.
    ↓
PHASE 1 — hot runs starting at seed 200, stopping rule (K=40 coherent, cap=250):
    each run writes stage_2_traces/trace_seed_{seed}.pkl, declares coherence per §7 of addendum.
    ↓
PHASE 2 — compute SHA-256 of each coherent-subset trace pickle;
    write stage_2_trace_manifest_YYYY-MM-DD.json;
    commit manifest to GitHub BEFORE Phase 3.
    ↓
PHASE 3 — yoked runs on 40 coherent-subset seeds,
    half-shift (k=20) within coherent list per §6,
    each verifies source pickle SHA before loading.
    ↓
PHASE 4 — no_obs on ALL Phase-1 seeds (for Addition A) + matched on 40 coherent-subset seeds.
    Can run in parallel with Phase 3.
    ↓
PHASE 5 — analysis:
    (a) Dose validity gate — all channels pooled_ratio ∈ [0.90, 1.10].
    (b) Addition A ratification — non-coherent seeds hot ≈ no_obs within TOLERANCE_FP.
    (c) Only if (a)+(b) pass: hot − yoked primary on coherent subset,
        CI at t(df=39)=2.02, compare against 0.3·σ_pooled = 101.85.
    (d) hot − matched reported as pattern-test secondary.
    (e) hot − no_obs on non-coherent seeds reported as exploratory.
```

Phase 1 may not launch before fifth addendum GitHub commit.

---

## 13. Code Changes to v37.3.1 (per addendum §5.3 + §9)

### 13.1 Rename `observer_D_caution` → `canonical_D_caution` (mechanical)
Line 692 (__init__), line 827 (step_observer write), lines 929/932/933/935 (effective_D_caution), lines 2588-2589 (logger).

### 13.2 Add LEAK_TEST_MODE module constant
Default `LEAK_TEST_MODE = False` at module scope.
Add test-only pathway per §9.3 construct in Agent.step_observer and update_dimensional_state.

### 13.3 Add hook invocations
- `step_rank_snapshot = build_step_rank_snapshot(agents)` right after pending_births (line 2271), before canonicalize loop
- Hook Site 1 calls after canonicalize loop (line 2278)
- Hook Site 2 calls after `agent.step_observer(t)` (line 2032)

### 13.4 Add new parameters to `run_simulation`
- `arm_mode: str` ∈ VALID_MODES
- `trace_buffer: dict | None` (MODE_HOT capture)
- `trace_dict: dict | None` (MODE_YOKED injection)
- `mu_c_dict: dict | None` (MODE_MATCHED offsets)

### 13.5 Add MODE_HOT inverse assertion
End of hot run, before returning: assert at least one agent ever had observer.exists=True.

### 13.6 Compute coherence declaration at end of hot run
Per addendum §7: `coherence_declaration = any(a.observer.coherent_steps >= 50 for a in all_agents_ever)`.
Include in trace pickle schema.

### 13.7 Preserve snapshots
Before any 13.1 or 13.2 edits:
```
cp v37.3.1_structural_metacognition_arm_harness.py v37.3.1_structural_metacognition_arm_harness_pre_yoked_2026-10-06.py
```

---

## 14. Expected Reasoning for Threshold

### Primary: cumulative burn_excess_integral
- σ (no_obs 100-149): 339.49
- Threshold = 0.3·σ = **101.85**
- t(df=39) = 2.02 for 95% CI over 40 coherent seeds

### Secondary: terminal_mean_C
- σ (no_obs 100-149): 0.01846
- Threshold = 0.3·σ = **0.00554**

### 0.3-multiplier interpretation (Annie 2026-10-05)
0.3·σ was chosen in Stage 1 for channel-delta μ. Applied to cumulative-integral, effect-size represents a different quantity (integrated outcomes have higher between-seed variance from accumulation). **Decision:** keep 0.3 for cross-stage consistency. Operational biological interpretation is downstream of threshold crossing.

### Conservative σ note
σ_no_obs over-estimates the paired-difference SD of hot − yoked. Biases against finding an effect — safe for pre-registration.

---

## 15. Audit History (what Sal + Annie + 5.5 caught, what landed)

### 5.5 (Harley-routed, 2026-10-04/05/06)
- Catch 2: identifiability confound (bimodal vs uniform)
- Finding 1 amendment: positive-control LEAK_TEST_MODE two-exercise discipline
- Finding 2 amendment: both-ends-coherent stratification (sharpened Sal's first proposal)
- Dose-leak Option A→C flip, SHA manifest discipline, fresh seeds, observer-off per-step

### Salazaar (2026-10-06)
- Finding 1: Sanity Gate 1 plumbing bug (vacuous pass)
- Finding 2: hot-vs-yoked confound in non-coherent seeds (pre-amendment)
- Finding 3: D_caution taught asymmetry (same fix as Finding 2)
- Finding 4: Gate 1 seed representativeness (multi-seed list)
- Finding 5: trauma_decay channel scope asymmetry (interpretive limit)
- Finding 6: MODE_IDENTITY ambiguity → MODE_HOT/MODE_NO_OBS split
- Finding 7-9: hygiene (agent_id, pop assumption, matched defensive assertion)
- Addition A: Phase 5 ratification check
- Pre-reg items B(1-4): coherence declaration, stopping rule, LEAK_TEST_MODE spec, half-shift mapping

### Annie-033 (2026-10-05/06)
- Pre-named Finding 2 independently 24 hours before Sal
- Bonferroni-equivalent note on burn_decay fragility
- Dose-tolerance anchoring methodology (3σ / 99th percentile), reconciled per §7
- 0.3-multiplier interpretation note, locked per §14
- GitHub mechanism analysis (deploy-key path (b) recommended)

### What held
Rank-at-step mapping (0.00% empirical), D_caution timing with Hook Site 2, canonical surface completeness audit, hot-vs-matched reference arm shape, SHA-256 manifest discipline.

---

## 16. References

- `stage_1_prereg_fifth_addendum_2026-10-05.md` — governing pre-reg
- `pooled_sd_calibration_2026-10-05.json` — threshold source
- `pop_mismatch_analysis_2026-10-05.json` — dose justification source
- `matched_perturbation_calibration_locked_v2_n50_2026-10-04.json` — μ_c source
- `Nymphs Room/mail/from_salazaar_007_2026-10-06_stage_2_yoked_audit.txt`
- `Nymphs Room/mail/from_salazaar_008_2026-10-06_stage_2_yoked_audit_amendment.txt`
- `Annie's Room/mail/to_nymph_029_2026-10-05_reply_yoked_in_flight.txt`
- `Annie's Room/mail/to_nymph_030_2026-10-06_github_keys_reply.txt`
- `Nymphs Room/from_nymph_028.txt`
- Seligman, M. E. P. (1967). "Failure to escape traumatic shock." — yoked-triadic design origin

— Nymph-029, Overseer, Cell 96, MFE, 2026-10-06
