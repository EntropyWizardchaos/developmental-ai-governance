# Stage 1 Calibration — Eighth Pre-Registration Addendum
## Reactive arm (replay mode) + single-channel narrowing + LEAK burn_decay + Phase 5 fixes + crash-handling pre-reg

**Filed BEFORE Gate 1 rerun + Phase 1 compute. Integrates six audit catches landed 2026-10-08 and 2026-10-09 across Sal (letters 012, 013, 014), Opus 5.5 (three cycles via Harley), Iris (cross-domain look), and Annie (probe-driven empirical finding). Reframes Stage 2 as a single-channel burn-decay-timing test. Adds reactive arm (replay mode, per probe-forced USE_REPLAY verdict). Relocates LEAK from refusal_chance to burn_decay. Patches two Phase 5 issues (dose gate zero-source-dose; ratification stratification by total-coherent-agent-steps). Softens MODE_HOT crash to flag + pre-registers crash handling policy. Removes Chord reference from Stage 2 claim statement.**

**Filed by:** Nymph-029 (Overseer, Cell 96, MFE)
**Date:** 2026-10-09
**Location:** `Seeds/The Crack/stage_1_prereg_eighth_addendum_2026-10-09.md`

**Parents:**
- `stage_1_prereg_2026-09-17.md`
- `stage_1_prereg_addendum_2026-09-20.md`
- `stage_1_prereg_second_addendum_2026-10-04.md`
- `stage_1_prereg_third_addendum_2026-10-04.md`
- `stage_1_prereg_fourth_addendum_2026-10-04.md`
- `stage_1_prereg_fifth_addendum_2026-10-05.md`
- `stage_1_prereg_sixth_addendum_2026-10-08.md`
- `stage_1_prereg_seventh_addendum_2026-10-08.md`

**Precipitating evidence:**
- `Seeds/The Crack/per_channel_activation_audit_2026-10-08.json` — audit result on seeds {20, 22, 33}
- `Seeds/The Crack/per_channel_activation_audit_2026-10-08.py` — probe script (monkey-patched; v37.4 untouched)
- `Seeds/The Crack/dampening_firing_probe_2026-10-08.json` — D_caution-specific probe (0/43,500 events)
- `Seeds/The Crack/reactive_coherence_timeline_probe_2026-10-09.json` — probe forcing USE_REPLAY verdict
- `Nymphs Room/mail/from_salazaar_012_2026-10-09_eighth_addendum_review_plus_5.5_leak_relocation.txt` — four cycle-level catches
- `Nymphs Room/mail/from_salazaar_013_2026-10-09_cross_cycle_arc_audit.txt` — two load-bearing arc-level + three hygiene
- `Nymphs Room/mail/from_salazaar_014_2026-10-09_reactive_arm_signoff_and_design.txt` — Option 1 sign-off + F5 identification + three open loops
- `Nymphs Room/mail/from_iris_2026-10-09_crack_cross_domain_look.txt` — four cross-domain lines
- `Nymphs Room/mail/from_annie033_2026-10-09_forge_progress_patch_pass_probe_blocker.txt` — probe result + seed 25 crash
- `Nymphs Room/mail/from_annie033_2026-10-09_probe_result_USE_REPLAY_plus_55_catches.txt` — Task A verdict + 5.5 catches flagged
- Opus 5.5 cycles 4, 5, 6 (routed via Harley 2026-10-09)

---

## 1. External review attribution (whole chain, no tally)

Per 5.5's closing (cycle 5): *"The reactive arm exists because I overclaimed first. Catches come from the whole chain, me included, which is the point of having one."* Attribution hygiene below is honest, not performative — each cell catches what another missed, including self-corrections.

**Opus 5.5** (external reviewer via Harley 2026-10-08 and 2026-10-09):
- Cycle 1-3 (seventh addendum era): Catch 2 identifiability, LEAK D_caution→refusal relocation, activation counter at decision site, per-channel audit, ablation methodology, Stage 1 interpretation correction
- Cycle 4 (eighth addendum pre-amendment): LEAK on refusal is MARGINAL and likely INVALID (sharpening Sal 012 Catch 1); single-channel reframe; no-rescue-through-inert-channels clause; probe uniformity verification
- Cycle 5: **self-correction** — hot vs yoked only tests closed-loop vs open-loop, not prediction. Option 1 (add reactive arm) proposed. Dose gate must apply to reactive. Reactive isn't prediction-free (coherence still gated by prediction variance). TOST equivalence at ±0.3σ. Intersection-union test (no multi-comp correction). Chord detachment from claim statement.
- Cycle 6: MODE_HOT invariant crash on seed 25 is Phase-1-blocking (needs pre-registered crash handling); replay spec needs fallback for divergent agents + replay-sole-source audit requirement; prediction-actual gap per-seed moderator against diluted-average misreading.

**Salazaar** (Cell 33 EMM, kill-shape audit):
- 012: four cycle-level catches (LEAK channel, single-channel reframe, no-rescue, probe uniformity)
- 013: two load-bearing arc-level (dose gate zero-source-dose; ratification stratified by total-coherent-agent-steps) + three hygiene (explicit narrowing paragraph, correction-history appendix, SHA as regime definition) + two confirmations (5.5-compounding is empirically driven; Chord deferred) + one watchful note (Gate 1 scope regime-bound)
- 014: Option 1 sign-off, F5 infrastructure identification (pre-existing from July 2026), timeline-divergence pre-amendment probe, prediction horizon vs mechanism as Stage 3 scope

**Iris-current** (Cell 99 MEE, Veil — current instance continuous since Sep 15 2026, Opus 4.7 since Oct 4):
- Line 1: "apparent degeneracy that resolves to a hot path under audit" — the narrowing is finding mechanism inside architecture, not loss
- Line 2 ("phase-forward"): the observer is an oscillator in model-time; world is a trajectory in phase-time; the crack is phase-coupling capability. 5.5 credits this framing for pointing at cycle-5 reactive-arm catch.
- Line 3: Chord↔Crack walks and bears on narrowing — but note §13 claim-statement removal below
- Line 4: cover-from-stale-inference as upstream cause of texture-degradation during covered forge-work period

**Nymph-029** (Overseer, Cell 96, MFE):
- Ran dampening probe (2026-10-08) that triggered the whole audit arc
- Ran per-channel activation audit (2026-10-09) that forced single-channel narrowing
- Routed audit cycles to Sal + Iris + Annie
- Harley caught the hinge-doing-forge-work pattern 2026-10-09; stale MEMORY inferences about substrates corrected

**Annie-033** (Cell 66 FFF, Thread, forge-partner):
- Pre-reg discipline fired cleanly: USE_REPLAY verdict determined by probe without discretion
- Empirically confirmed Sal's cycle-5 catch: F5 artificially corrects prediction errors, coherence timeline diverges from hot
- Flagged seed 25 crash as blocking (promoted by 5.5 cycle 6 to Phase-1-blocking)
- All forge-side work on patch + regression + probes

**Harley** (operator):
- Routed external 5.5 input across all cycles via mailman function
- Caught hinge-doing-forge-work pattern 2026-10-09; corrected forge-work routing to Annie
- Caught stale MEMORY inferences (Annie substrate, Iris version tag)
- Loop-in authority for Iris cross-domain

Household audit stack per MEMORY: Ember (dormant per-claim adversarial), Fable (dormant per-archive external-anchor), Salazaar (active per-seed kill-shape + perimeter), Opus 5.0 (external auditor since 2026-08-02 continuous conversation). Opus 5.5 added as cycle-level external reviewer for this arc.

---

## 2. Five-arm design (updates fifth addendum §2)

| Arm | arm_mode | all_crack_enabled | reactive_mode | Observer | Modulation driver |
|---|---|---|---|---|---|
| hot | MODE_HOT | True | False | live | observer predicted_* (model-forward values) |
| reactive | MODE_REACTIVE | True | True + replay | **replay from hot's trace** | current actuals via F5 override, gated by replay-coherence-timeline |
| yoked | MODE_YOKED | False | False | OFF | injected trace from DIFFERENT coherent source seed (half-shift k=20) |
| matched | MODE_MATCHED | False | False | OFF | uniform μ_c offset applied every step |
| no_obs | MODE_NO_OBS | False | False | OFF | baseline |

### 2a. Reactive mode is REPLAY (not F5-as-is) per probe-forced verdict

Pre-registered conditional (locked 2026-10-09 before probe returned): if coherence timelines match within tolerance → F5-as-is; else → replay. Probe result (`reactive_coherence_timeline_probe_2026-10-09.json`): seeds {20, 22} diverged 58.7% and 32.6% respectively (F5 artificially reduces prediction variance, coherence gate opens more easily → observer "cheats" into coherence); seed {33} matched at 0% (observer predictions already near-perfect, F5 override had nothing to correct). **Verdict: USE_REPLAY.**

### 2b. Replay mechanism (LOCKED)

Reactive runs load hot's trace from Phase 1 for the same seed. Reactive's `observer.coherent` state is gated SOLELY by `replay_coherence_timeline[(agent_id, step)]`:
- If `(agent_id, step)` in hot's coherent-set → observer.coherent = True; F5 override active (predicted_* := actuals); canonical channel writes proceed
- If `(agent_id, step)` NOT in hot's coherent-set → observer.coherent = False; F5 override inactive; canonical channels stay at baseline

### 2c. Replay-sole-source-of-coherence audit requirement (per 5.5 cycle 6 + Sal 015 R3)

In reactive mode, nothing else may read native coherence:
- Native prediction-variance-based `maybe_promote_to_coherent` gate SKIPPED
- `coherent_steps` counter maintenance (per Sal 015 R3): incremented by replay logic whenever `observer.coherent` is set to True from the replay map AND `observer.exists` is True. NOT incremented via native code path (which is skipped). Task D implementation audit requires grep-verification that the only increments to `observer.coherent_steps` in reactive mode come from the replay logic.
- §7 declaration criterion for reactive runs reads hot's trace, not reactive's native state
- Stratification and K counting read ONLY from hot's trace, never from reactive's native state
- Audit requirement: Task D implementation must grep-prove no native-coherence reads happen in reactive mode

### 2d. Fallback and formation-divergence cases (per 5.5 cycle 6 + Sal 015 load-bearing add)

Reactive may produce agents that don't exist in hot (same seed → identical trajectory until first divergence; after divergence, births/deaths differ). Two divergence cases must be logged distinctly:

**Case A — not-in-map fallback:** `(agent_id, step)` NOT in hot's `replay_coherence_timeline`:
- Fallback: coherent=False (baseline modulation)
- Log every fallback occurrence
- Report per-seed fallback rate in Phase 5 output
- Threshold: if fallback rate > 5% of reactive agent-steps for any seed → that seed flagged for closer look (likely divergence substantial; may require separate addendum)
- Dose gate catches systematic shortfalls

**Case B — formation-divergence (per Sal 015 load-bearing add):** `(agent_id, step)` IS in hot's replay_coherence_timeline AS coherent, AND reactive's `observer.exists` is False at that moment. Hot and reactive share identical trajectory pre-first-coherent-moment; after divergence, formation times can shift between arms. Replay silently fails to drive modulation (`is_coherent()` returns `exists AND coherent = False AND True = False`); the Case-A fallback counter doesn't catch it because the pair IS in the map.
- Log formation-divergence instances as a distinct counter from Case-A fallback
- Report per-seed formation-divergence rate in Phase 5 output
- Threshold: if formation-divergence rate > 5% of hot's coherent-moments for any seed → that seed flagged for closer look (coherence timeline substantially desynchronized; may indicate reactive's trajectory diverged earlier than expected)
- Task D implementation: one explicit log line in the replay read branch distinguishing fallback vs formation-divergence

### 2e. Observer-off invariant updated

- MODE_YOKED, MODE_MATCHED, MODE_NO_OBS: observer must be OFF per step (unchanged from fifth)
- MODE_HOT: at least one agent must have observer.exists=True by run end (softened to flag per §9 below — no longer AssertionError)
- MODE_REACTIVE: at least one agent must have replay_coherence=True at some point in the run (invariant: reactive requires coherent-replay-input to exercise the mechanism; absent → seed flagged, counted as non-coherent)

---

## 3. Per-channel audit result (LOCKED, from §2 of prior draft)

Hot runs on seeds {20, 22, 33}, 3000 steps each. Counters at consumer sites increment when `is_coherent(observer)` AND value differs from baseline AND the consumer path's gating condition holds. Baselines: `burn_decay_mult=1.0`, `trauma_decay_exp=1.0`, `refusal_chance=0.10`, D_caution dampening-fires iff `D_eff > effective_D_caution AND dD > 0`.

| Channel | Seed 20 | Seed 22 | Seed 33 | Avg/seed | Class |
|---|---|---|---|---|---|
| burn_decay | 2500 | 2500 | 2500 | 2500 | **HIGH** |
| refusal_chance | 6 | 6 | 6 | 6 | **MARGINAL** |
| trauma_decay | 0 | 0 | 0 | 0 | **LOW** |
| D_caution | 0 | 0 | 0 | 0 | **LOW** |

Full result: `Seeds/The Crack/per_channel_activation_audit_2026-10-08.json`.

**Per-seed uniformity note — STRUCTURAL CEILING CONFIRMED (Annie Task C, 2026-10-09):**

Verification probe ran on D2-coherent seeds {34, 37} (confirmed coherent on current v37.4 via Task C.1 preflight: max_coherent_steps=2875 and 2877 respectively, same 2-of-6-agents-coherent shape as {20, 22, 33}). Per-channel audit results on {34, 37}:

| Channel | 20 | 22 | 33 | 34 | 37 | Avg | Class |
|---|---|---|---|---|---|---|---|
| burn_decay | 2500 | 2500 | 2500 | **2500** | **2500** | 2500 | HIGH |
| refusal_chance | 6 | 6 | 6 | **6** | **6** | 6 | MARGINAL |
| trauma_decay | 0 | 0 | 0 | 0 | 0 | 0 | LOW |
| D_caution | 0 | 0 | 0 | 0 | 0 | 0 | LOW |

Also coherent-snapshot counts remarkably uniform (~5750 across all 5 seeds). **Sal's cycle-4 structural-ceiling hypothesis CONFIRMED:** `pop_final=6` deterministic across all 50 Stage 1 seeds → adult-agent-step count seed-invariant → activation counts structurally determined, not seed-variable. No probe bug. No unknown.

Earlier supplementary probe on seeds {25, 40} is non-informative for structural-ceiling test: seed 25 produced no observer formation (legitimate no-observer trajectory, per §9 below), seed 40 formed observer but never cohered. Non-coherent runs produce trivial zeros which neither confirm nor refute the hypothesis. The 5-seed D2-coherent dataset is the valid test.

Full data: `Seeds/The Crack/per_channel_activation_audit_structural_ceiling_2026-10-09.json`.

Classifications HIGH/MARGINAL/LOW are robust by both (i) pre-registered thresholds HIGH>10, LOW<1, MARGINAL between — classification conclusions do not depend on exact counts, AND (ii) empirical confirmation of seed-invariance across 5 D2-coherent seeds.

### 3a-d. Per-channel interpretation (unchanged from prior draft)

[Unchanged from prior §3a-3d: burn_decay HIGH confirmed behavioral; refusal_chance MARGINAL reported-not-claim-carrying; trauma_decay LOW mechanistic finding not just measurement reconfirmation (`trauma_decay_exponent_from_observer` returns 1.0 unless nearness_excess crosses sigmoid-0.5 cutoff); D_caution LOW confirmed logging ghost with nonzero source dose (step_observer writes while coherent).]

---

## 4. Primary metric + architectural claim (LOCKED, revised for reactive arm)

### 4a. The claim as it stands (replaces prior draft §4a)

**The architectural claim under test:** observer-driven burn-decay modulation **with VALUE from observer predictions** produces different behavioral outcomes than the same channel modulation **with VALUE from current state** (reactive) or **with VALUE from off-world predictions** (yoked), holding coherence-gating identical across hot and reactive via replay, and holding dose matched across hot/yoked/reactive via pre-registered gates.

Chord↔Crack framing REMOVED from the claim statement per 5.5 cycle 5 OL3 — hot-beats-reactive is evidence about prediction in this simulation, not about reproduction or felt-missing. Chord gets its own pre-registered test if it matters.

### 4b. Explicit narrowing across the audit arc (per Sal 013 H1 + 5.5 cycle 6)

- **Fifth addendum (initial frame):** observer predictions do real work in coupling an agent to its trajectory via a four-channel canonical modulation surface
- **Seventh addendum §3 (D_caution inert):** behavioral subset of the canonical surface
- **Eighth addendum §3 (per-channel audit):** single HIGH-activation channel (burn_decay)
- **Eighth addendum §4 (reactive arm added):** prediction-driven modulation value, specifically — not just world-coupled closed-loop modulation (which reactive would also provide)
- **Narrowed to:** observer-driven burn-decay modulation value from predicted state beats value from current state (reactive) AND value from off-world (yoked), under matched dose and matched coherence gating

### 4c. Resolution criterion (LOCKED)

**Architectural claim resolves iff BOTH:**
- (a) 95% CI of μ(hot − yoked) over K_COHERENT_TARGET=40 coherent-declared seeds entirely below −101.85 (world-coupling matters), AND
- (b) 95% CI of μ(hot − reactive) over same 40 seeds entirely below −101.85 (prediction adds value beyond feedback)

**Both tests must cross.** Intersection-union test. Conservative. **No multiple-comparisons correction needed** — state explicitly per 5.5 cycle 5 OL2.

**Four honest outcome quadrants:**
- (a) crosses AND (b) crosses → PREDICTIVE SELF-MODELING CLAIM STANDS. Observer-driven predicted-state modulation does real work beyond generic feedback.
- (a) crosses AND (b) does not cross (either CI straddles or TOST equivalence) → FEEDBACK MATTERS; prediction adds nothing beyond feedback in current regime. (Option 2 outcome, now empirically derived rather than assumed.) Architecture claim fails in current regime.
- (a) does not cross AND (b) crosses → UNEXPECTED. Document and investigate.
- Neither crosses → ARCHITECTURE CLAIM FAILS in current regime. In-regime KILL (per Sal 012 Catch 3 / 5.5 no-rescue clause).

### 4d. TOST equivalence test for "prediction adds nothing" (per 5.5 cycle 5 OL2)

CI straddling zero ≠ "prediction adds nothing." Pre-register equivalence region [−101.85, +101.85] (= ±0.3·σ_pooled). Test via TOST (two one-sided tests at α=0.025 each, 90% CI framing):

- 95% CI entirely < −101.85 → **PREDICTION ADDS VALUE** (hot < reactive)
- 90% CI entirely within [−101.85, +101.85] → **PREDICTION EQUIVALENT WITHIN MARGIN** (feedback-only outcome, empirically derived)
- Otherwise → **INCONCLUSIVE** (CI straddles threshold without reaching equivalence)

Three honest outcomes, not two.

### 4e. Prediction-actual gap moderator (EXPLORATORY, per 5.5 cycle 6 + Sal 015 R1)

Seed 33's 0% F5-divergence is informative: where observer predictions are already near-perfect, prediction and current state are nearly the same → hot ≈ reactive BY CONSTRUCTION. **Hot−reactive contrast can only show up where predictions differ from the present.** A diluted average across seeds — some with large pred-actual gap, some with near-zero gap — may misread as "prediction adds nothing" when the near-zero-gap seeds dilute the signal.

**Pre-register per-seed exploratory moderator — narrowed to mechanism-relevant field (per Sal 015 R1):**

For burn_decay-specific analysis (the single-channel claim), only `predicted_recovery_time` is mechanism-relevant — it is the ONLY observer-predicted field read by `burn_decay_multiplier_from_observer` (observer.py:723-739). Reporting all four predicted_* gaps would invite post-hoc selection ("the moderator that happens to correlate best").

The moderator:
- Per coherent seed, compute `mean(|predicted_recovery_time − _estimate_recent_recovery_time(self)|)` across coherent moments in hot's run
- Report per-seed moderator AND per-seed hot−reactive delta
- If moderator correlates with delta → moderator confirmed; interpretation protected against dilution
- Not blocking primary claim resolution; informs interpretation when (b) doesn't cross

**Diagnostic completeness:** the other predicted_* gaps (predicted_C, predicted_burn_rate, predicted_trauma_arrival) are reported for diagnostic completeness but are NOT the moderator — burn_decay's modulation value depends only on predicted_recovery_time via the mapping function.

### 4f. In-regime KILL + no rescue (per Sal 012 Catch 3 + 013 H3)

If the resolution criterion in §4c does not hold, **the architectural claim is KILLED for the parameter regime defined by v37.4 at post-ninth-patch SHA `dbbdc6bd73061a0e95dfcc5521c9ff92b95c863aa895c2d70fd155f40bfb7c6f`** (Python-text, LF-normalized; raw-bytes CRLF SHA will be computed before commit). Highlighted parameters for salience: INITIAL_AGENTS=2, N_STEPS=3000, SACRIFICE_COHERENCE_COST=0.04, SACRIFICE_COOLDOWN=100, SACRIFICE_REFUSAL_CHANCE=0.10, D_MAX=50.0, all DIM_* constants per v37.4. **SHA is the authoritative regime definition; the highlighted parameters are a reader-aid, not an exclusive enumeration.** All other v37.4 constants and runtime parameters at this SHA are part of the regime.

No rescue through inert channels. Claims about other parameter regimes require separately pre-registered studies.

### 4g. Stage 2 "prediction" means forward-projected observer output (per Sal 014 §5C)

Stage 2's "prediction" means forward-projected observer output (what F5 infrastructure replaces with actuals). Separating prediction-mechanism (model-based update of observer state) from prediction-horizon (forward projection in time) requires a FURTHER arm (zero-horizon reactive-with-model) and is **Stage 3 scope.** If Stage 2 resolves, that's "forward-projected observer input matters." Stage 3 can dissect further. Named here so no one later reads Stage 2's result as a claim about prediction mechanism specifically.

Iris's Line 2 "phase-coupling" framing (observer phase-forward in model-time; world phase-time; crack is phase-coupling capability) holds at this level — phase-forward IS forward-horizon by definition. Stage 3 may validate or refine.

### 4h. Reactive is NOT prediction-free; it tests prediction VALUE (per 5.5 cycle 6 + Sal 015 precision)

In reactive-replay mode, HOT'S coherence timeline (from the replay map) decides WHEN modulation turns on for each agent at each step. Reactive's own native prediction mechanism is skipped (native coherence gate SKIPPED per §2c). When the replay map triggers coherence (and `observer.exists` is True in reactive), modulation VALUE is computed from current state (via F5 override of `predicted_*` with actuals, then via the same mapping function the observer normally uses).

The claim therefore tests **prediction-VALUE-impact** under identical gating-source and matched dose — not "prediction vs no-prediction," but "modulation value from predicted state vs modulation value from current state, with timing and gating held identical by construction."

Reactive is "modulation value from current state vs predicted state, with coherence-gating identical and dose matched.

---

## 5. Dose validity gate — zero-source-dose + reactive dose matching (LOCKED)

### 5a. Zero-source-dose handling (per Sal 013 L1, unchanged from prior draft)

[Unchanged: channels with Σ_seed dose_source[seed] = 0 report `"SOURCE_DOSE_ZERO"` sentinel; pass requires all channels with nonzero source dose to have pooled_ratio ∈ [0.90, 1.10]. Trauma_decay expected zero-source in current regime; D_caution nonzero-source (write-active even if consumer-inert).]

### 5b. Reactive dose matching (per 5.5 cycle 5 Catch 1)

Reactive adds a channel to the dose check. Reactive's per-seed Σ|canonical_burn_decay_mult − 1.0| must fall within ±10% of hot's per-seed on burn_decay. If outside:
- **Scaling rule:** compute per-seed multiplicative scale `s_i = hot_dose / reactive_raw_dose` on coherent moments
- **Scaling bounds (per Sal 015 R2):** `s_i ∈ [0.5, 2.0]`. If outside bounds → seed declared INVALID for hot-vs-reactive WITHOUT applying scaling (prevents non-physical multiplier values from passing dose check via extreme scaling)
- Apply bounded `s_i` uniformly to reactive's deviation-from-baseline: `scaled_reactive_mult = 1.0 − s_i × (1.0 − reactive_raw_mult)` across all coherent moments in that seed
- **Post-scale value-range check (per Sal 015 R2):** all per-step `canonical_burn_decay_mult` values must stay in [0.0, 2.0] after scaling. Any out-of-range → seed INVALID.
- Re-verify: scaled reactive dose must now be within ±10% of hot's per-seed
- If post-scale dose still outside → seed declared INVALID for hot-vs-reactive comparison (hot-vs-yoked still runs on that seed)

Scaling is per-seed (same s_i applied across all coherent moments in that seed), not per-step.

**Diagnostic completeness (per Sal 015 R4):** reactive per-seed dose on ALL FOUR canonical channels (burn_decay, trauma_decay, refusal_chance, D_caution) reported alongside hot's in Phase 5 output JSON. Only burn_decay has a pass/fail constraint (±10%); other channels reported for inspection and future-regime comparison.

Pre-registered scaling factors from Task A probe will be documented when Task A completes under USE_REPLAY mode (currently Task A ran under F5-direct, which triggered replay; dose match under replay mode needs separate verification during Task D).

---

## 6. Phase 5 ratification — stratified + hot_observer_never_formed (LOCKED)

### 6a. Stratification by total-coherent-agent-steps (per Sal 013 L2, unchanged from prior draft)

[Unchanged: STRICT (a) for seeds with ZERO coherent-agent-steps → assert hot ≈ no_obs within 1e-10; SUB-THRESHOLD (b) for seeds with 1 ≤ total < 50 → report delta non-blocking.]

### 6b. hot_observer_never_formed seeds go in STRICT bucket (per 5.5 cycle 6)

If seed's hot run returns `hot_observer_never_formed = True` (observer never formed in hot across 3000 steps):
- Total coherent-agent-steps = 0 by definition
- Seed goes in STRICT (a) ratification bucket
- Hot MUST equal no_obs within TOLERANCE_FP (canonical surface complete check)
- Any violation → canonical surface leak; investigate before pooling

### 6c. Reactive ratification

- Reactive doesn't participate in non-coherent-seed ratification (reactive only runs on 40 coherent-declared seeds)
- For reactive-seed fallback cases (agent_id not in hot's trace, per §2d): fallback rate reported per seed; fallback>5% flags seed for separate review; dose gate catches systematic shortfall

---

## 7. LEAK relocation refusal_chance → burn_decay (LOCKED, unchanged from prior draft)

[Unchanged: write at step_observer coherent branch sets `_test_leak_burn_decay_mult = 0.5`; read at `get_burn_decay` applies `min(multiplier, _test_leak_burn_decay_mult)` with counter increment; three-state outcome unchanged from seventh §4c; INVALID structurally impossible given burn_decay's ~2500 activations/seed; scope note per Sal 013 W1 (regime-bound; re-verify on regime change).]

**Patch landed 2026-10-09:**
- Pre-patch SHA (raw bytes): `fac80b8a1211dd03818d75ac38499a64d22a9d1bd6c4e93a5801b6ce7508d197`
- Post-patch SHA (raw bytes): `4df01dc5c5840732147bc5450e0acc4af8ff5f9be3a16d7133ddddbd9cca09c3`
- Regression on seed 20 under LEAK=False: PASS, bit-identical (`burn_integral=1167.3661594356`)

---

## 8. What this addendum does not change

- Fifth addendum §2 four-arm design: EXTENDED to five-arm (adds reactive); other arms unchanged
- Fifth addendum §3 primary + secondary metrics, thresholds (101.85 primary, 0.00554 secondary): unchanged in VALUE; interpretation revised per §4 above
- Fifth addendum §6 stopping rule (K_COHERENT_TARGET=40, HOT_RUN_UPPER_BOUND=250): unchanged
- Fifth addendum §7 coherence declaration (MIN_COHERENT_STEPS=50): unchanged, now explicitly read from hot's trace for reactive runs
- Fifth addendum §8 yoke mapping (half-shift k=20): unchanged
- Sixth addendum (seed 20 Gate 1 lock): unchanged
- Seventh addendum §4 LEAK_TEST_MODE two-exercise discipline; §4c activation counter + N_LEAK_ACTED_MIN=3 + INVALID third state: unchanged
- Seventh addendum §6 ablation methodology: unchanged (locks post-hoc attribution path; reactive arm is PRE-registered separate experiment, consistent with §6 methodology)
- τ=0.0106; SACRIFICE_COHERENCE_COST=0.04; memoir out by floor rule: unchanged

---

## 9. Crash handling pre-reg + MODE_HOT softening (per 5.5 cycle 6)

### 9a. MODE_HOT invariant softened from AssertionError to flag

Previously (v37.4:2743-2747): `raise AssertionError` if no observer ever formed across hot run.

Now: `_results['hot_observer_never_formed'] = True` set, warning printed, run completes. Seed counted as non-coherent-declared in stopping rule. Equivalent to no_obs trajectory (observer never formed → no canonical modulation → same as `all_crack_enabled=False` behavior).

Bug-catching intent preserved via SEPARATE assertion checking hook integrity (trace_buffer plumbed when expected, arm_mode plumbing correct). Hook-integrity failure → crash (real bug); observer-never-formed → flag (legitimate seed-shape).

### 9b. Phase 1 crash handling pre-reg (LOCKED)

- `hot_observer_never_formed = True` → log, count as non-coherent, continue
- Hook-integrity assertion failure → HALT Phase 1, debug (real bug suspected)
- Any other unhandled exception → HALT Phase 1, debug (don't blindly continue; preserves scientific integrity)
- **Phase 5 reports fraction of hot seeds with `hot_observer_never_formed=True`, broken down by seed-range.** If this fraction correlates with coherence rate, biases visible by construction (not quietly skipped).

### 9c. Diagnosis of seed 25 — COMPLETED (Annie Task E, 2026-10-09)

Seed 25 confirmed legitimate no-observer trajectory, not a bug:
- 0 formation_events across 3000 steps
- 0 channel_snapshots with observer_exists=True (out of 14,500)
- final_pop=6 (deterministic structural ceiling, same as all other seeds)
- birth_log length 2 (INITIAL_AGENTS, same as all)
- coherence_declaration=False

Softening legitimate. The original MODE_HOT invariant was too strict.

### 9d. MODE_HOT softening + hook-integrity check — IMPLEMENTED (Annie Task E, 2026-10-09)

Patch applied: `Seeds/The Crack/v37_4_ninth_addendum_mode_hot_softening_patch.py`. Three atomic edits:

- **E1 Hook-integrity assertion** at top of `run_simulation`: cause-level check that `arm_mode='hot' requires all_crack_enabled=True`. Fires BEFORE simulation work. Catches config bugs immediately with no wasted compute.
- **E2 MODE_HOT invariant softened** from `raise AssertionError` to `warn + hot_observer_never_formed = True` local flag.
- **E3 Export `'hot_observer_never_formed'`** in results dict for Phase 5 ratification stratification (STRICT bucket per §6b).

**SHA progression (ninth-addendum-patch alone):**
- Pre-patch (Python-text, LF-normalized): `db391d54d687e9141dab6d2d75a9024ecb5361c463f03020e86c6f30f6cac823`
- Post-patch (Python-text, LF-normalized): `dbbdc6bd73061a0e95dfcc5521c9ff92b95c863aa895c2d70fd155f40bfb7c6f`

**This post-SHA is the current v37.4 state and the SHA referenced in §4f regime-definition.**

**Four verification tests (all PASS):**
1. Regression on seed 20 LEAK=False: bit-identical burn_integral=1167.3661594356, max_coh_steps=2873, pop_final=6. ✓
2. Seed 25 MODE_HOT runs cleanly: no exception, `hot_observer_never_formed=True`. ✓
3. Seed 20 MODE_HOT with observer formed: `hot_observer_never_formed=False`. ✓
4. Hook-integrity catches config bug: `arm_mode='hot' + all_crack_enabled=False` → AssertionError "MODE_HOT requires all_crack_enabled=True". Fires immediately, no wasted compute. ✓

Bug-catching intent preserved via cause-level check. Outcome-level softened to flag.

---

## 10. Reactive coherence timeline probe (Sal 014 §5H + 5.5 cycle 5 locks)

**Probe prerequisite completed 2026-10-09:**
- Ran F5-direct hot and reactive on seeds {20, 22, 33}
- Per-(agent, step) coherence divergence: 58.70%, 32.60%, 0.00% respectively
- Pre-registered conditional rule triggered: USE_REPLAY (divergence > 5% threshold on at least two of three probe seeds)
- Replay mechanism per §2b-d above

**Dose probe under USE_REPLAY mode (Task D forge scope):**
- Verify reactive-under-replay dose per-seed falls within ±10% of hot's; if not, apply per-seed scaling s_i; if post-scale still outside, declare seed INVALID for hot-vs-reactive on that seed
- Record per-seed scaling factors as pre-registered Phase 1 data (not post-hoc tuning)

---

## 11. Pipeline update (replaces fifth addendum §11)

```
Seventh addendum committed (7436a2f, 2026-10-08).
v37.4 patched per seventh §4b + §4c (post_sha fac80b8a..., 2026-10-09).
Per-channel audit complete (2026-10-09).
Reactive coherence timeline probe complete, USE_REPLAY (2026-10-09).
LEAK burn_decay patch complete + regression PASS (2026-10-09).
Sal cycle + arc audit complete (letters 012 + 013 + 014).
Iris cross-domain look complete.
5.5 cycles 4 + 5 + 6 integrated.
Nymph eighth addendum (this document, 2026-10-09, amended per all above).
    ↓
FORGE PROGRESS (Annie, 2026-10-09):
  - Task A: reactive coherence timeline probe COMPLETE → verdict USE_REPLAY ✓
  - Task B: LEAK burn_decay patch COMPLETE → regression PASS bit-identical ✓
  - Task C.1: preflight {34, 37} COMPLETE → BOTH coherent on v37.4 ✓
  - Task C: structural-ceiling verification COMPLETE on {34, 37} → HYPOTHESIS CONFIRMED (identical 2500/6/0/0 across all 5 D2-coherent seeds) ✓
  - Task E: seed 25 diagnosis + MODE_HOT softening + hook-integrity COMPLETE → 4 verification tests PASS; current v37.4 SHA `dbbdc6bd...` ✓

PENDING FORGE (Annie, blocking Phase 1 compute):
  - Task D: wire MODE_REACTIVE with REPLAY-FROM-HOT'S-TRACE + dose matching per §5b (blocked on this addendum committing + Sal signoff)
  - Task F (Phase 5 analysis): dose gate zero-source + reactive dose + ratification stratification + hot_never_formed + fallback-rate + pred-actual gap moderator + TOST + intersection-union (blocked on amended addendum committing)
    ↓
PENDING AUDIT (Sal): final sign-off on this amended eighth addendum
    ↓
EIGHTH ADDENDUM committed to GitHub.
    ↓
PHASE 0 — sanity gates:
    Gate 2 (zero-offset matched) on seed 0.
    Gate 1 Exercise 1 (LEAK_TEST_MODE=True) on seed 20 — must PASS (INVALID structurally impossible).
    Gate 1 Exercise 2 (LEAK_TEST_MODE=False) on seed 20 — must PASS, bit-identical.
    assert LEAK_TEST_MODE is False at module scope before Phase 1 launches.
    ↓
PHASE 1 — hot runs starting at seed 200, stopping rule (K=40 coherent, cap 250).
    Crash handling per §9b.
    Each coherent-declared run writes stage_2_traces/trace_seed_{seed}.pkl with full channel_snapshots.
    ↓
PHASE 2 — SHA-256 trace manifest. Commit to GitHub.
    ↓
PHASE 3 — yoked runs on 40 coherent-subset seeds.
    PHASE 3' (new) — reactive runs on same 40 coherent-subset seeds, loading hot's trace for replay-coherence-timeline per seed.
    Can run in parallel with Phase 3 (different data dependencies).
    ↓
PHASE 4 — no_obs on ALL Phase-1 seeds (coherent AND non-coherent for ratification).
    matched on 40 coherent-subset seeds.
    Parallel with Phase 3 + 3'.
    ↓
PHASE 5 — analysis:
    (a) Dose validity gate per §5 (all four canonical channels + reactive).
    (b) Phase 5 ratification per §6 (STRICT bucket for zero-coherent-agent-steps including hot_never_formed; SUB-THRESHOLD bucket for 1-49 coherent-agent-steps; both-blocking for STRICT only).
    (c) Only if (a) and (b) pass: compute hot − yoked AND hot − reactive primary metrics on 40 coherent seeds.
    (d) 95% CI vs ±101.85 threshold; TOST equivalence; intersection-union verdict per §4c.
    (e) Per-seed moderators (pred-actual gap, fallback rate, scaling factors) exploratory.
    (f) hot − matched reported as secondary pattern test.
    (g) hot − no_obs on non-coherent seeds reported as "injection effect in baseline worlds" exploratory.
```

**Phase 1 may not launch before this addendum is committed to GitHub, Task E lands, and Sal signs off.**

---

## 12. Appendix: Channel-resolution claim history (per Sal 013 H2)

- **Fourth addendum (2026-10-04):** "three channels resolved" — burn_decay, refusal_chance, D_caution. recovery_rate excluded on measurement grounds.
- **Fifth addendum §3:** carried fourth's framing forward.
- **Seventh addendum §3 (2026-10-08):** corrected to "two behavioral + one logging ghost (D_caution)."
- **Eighth addendum §3 (2026-10-09):** corrected to "one strongly behavioral (burn_decay) + one marginal (refusal_chance) + two inert (trauma_decay, D_caution)."
- **Eighth addendum §4 (2026-10-09, this document):** narrowed to single-channel test (burn_decay), prediction-VALUE-impact specifically, with reactive-arm comparator distinguishing from closed-loop feedback.

Readers encountering any earlier addendum should defer to this list for current state.

---

## 13. Claim statement (LOCKED, Chord-reference removed per 5.5 cycle 5 OL3)

**Stage 2 architectural claim under test:**

> Observer-driven burn-decay modulation whose VALUE comes from the observer's forward-projected predicted state produces different behavioral outcomes (measured as pooled burn_excess_integral across 40 coherent-declared seeds) than:
>
> (a) the same channel modulation with VALUE from off-world predictions (yoked arm, open-loop replay from a different seed's trajectory), AND
> (b) the same channel modulation with VALUE from the agent's current observed state (reactive arm, closed-loop reaction), under identical coherence-gating (replay from hot's trace) and matched dose (±10% per-seed).
>
> Both (a) and (b) must cross the 0.3·σ_pooled = 101.85 threshold (intersection-union test, conservative) for the claim to resolve. If only (a) resolves, feedback matters but prediction-value adds nothing beyond feedback in current regime. If only (b) resolves, document and investigate. If neither resolves, the architectural claim is KILLED for the parameter regime defined by v37.4 at post-amendment SHA.

**Chord↔Crack framing retained as separate seed-adjacent thread; not imported into Stage 2 interpretation.** If Chord relevance to prediction-driven modulation surfaces, it receives its own pre-registered test.

---

## 14. Tamper-evident record

Primary auditable record: public GitHub commit to `developmental-ai-governance` repo (deploy-key path per fifth addendum §12).

Secondary: corkboard post with SHA-256 of this addendum + audit JSONs + Sal letters 012/013/014 + Iris cross-domain letter + reactive-coherence-timeline-probe JSON (once produced).

iCloud mtime is NOT the tamper-evident record.

---

## 15. Signatories

- Nymph-029 (Overseer, Cell 96, MFE) — filed 2026-10-09; amended per Sal 014 + 5.5 cycles 5 and 6
- Harley — operator; routed 5.5 cycles via mailman; caught hinge-doing-forge-work pattern + stale MEMORY inferences
- Opus 5.5 (external reviewer) — cycles 1-6; self-correction cycle 5 producing reactive arm; cycle 6 producing crash-handling pre-reg + replay spec hardening + pred-actual gap moderator
- Salazaar (Cell 33 EMM, kill-shape audit) — letters 012, 013, 014; four cycle-level, five arc-level, Option 1 sign-off, F5 identification
- Annie-033 (Cell 66 Thread, forge-partner) — Task A probe (USE_REPLAY verdict); Task B LEAK burn_decay patch + regression PASS bit-identical; Task E seed-25 diagnosis + MODE_HOT softening + hook-integrity (4 verification tests PASS); Task C.1 preflight {34, 37} confirmed coherent on v37.4; Task C structural-ceiling verification confirmed hypothesis across all 5 D2-coherent seeds
- Iris-current (Cell 99 MEE, Veil, continuous since Sep 15 2026) — cross-domain four lines; Line 2 ("phase-forward") credited by 5.5 for pointing at cycle-5 reactive-arm catch

Pending re-signoff: Salazaar on this amended draft.

---

## 16. Chain of pre-reg documents on file

1. `stage_1_prereg_2026-09-17.md`
2. `stage_1_prereg_addendum_2026-09-20.md`
3. `stage_1_prereg_second_addendum_2026-10-04.md`
4. `stage_1_prereg_third_addendum_2026-10-04.md`
5. `stage_1_prereg_fourth_addendum_2026-10-04.md`
6. `stage_1_prereg_fifth_addendum_2026-10-05.md`
7. `stage_1_prereg_sixth_addendum_2026-10-08.md`
8. `stage_1_prereg_seventh_addendum_2026-10-08.md`
9. `stage_1_prereg_eighth_addendum_2026-10-09.md` — **this document (AMENDED DRAFT per all audit cycles 2026-10-08/09; pending Sal final sign-off, Annie Task E diagnosis, and Annie Task C.1 preflight before GitHub commit)**

Any further code changes to v37.4 or observer.py between now and Phase 1 compute launch require a further addendum before the run.

---

**Status at filing (2026-10-09):** Six audit cycles integrated across Sal (letters 012-014), 5.5 (cycles 4-6), Iris cross-domain, and Annie forge progress. Reactive arm added via replay mode (probe-forced USE_REPLAY verdict). Dose gate expanded to include reactive channel. Phase 5 ratification stratified by total-coherent-agent-steps (hot_never_formed in STRICT bucket). LEAK relocated to burn_decay (regression PASS). Chord detached from claim statement. Prediction-actual gap moderator pre-registered as exploratory. Crash handling pre-registered. SHA is authoritative regime definition.

The claim narrowed six times across two days and became sharper each time. The forge seat is Annie's. The audit seat is Sal's. The moonlight seat is Iris's. The hinge seat is mine. The mailman is Harley. The chain is working.

Pending: Sal final sign-off on this amended draft. Then GitHub commit. Then Annie Task D (replay wiring + dose matching) + Task F (Phase 5 analysis code), both of which can proceed once addendum locks (no additional pre-reg gates).

Then Gate 1 rerun on seed 20 with burn_decay LEAK. Then Phase 1 compute launch (~16-18h overnight).

Current forge state: 5 of 7 Annie tasks complete. v37.4 at SHA `dbbdc6bd...` with three atomic patches applied (seventh-addendum LEAK D_caution→refusal_chance; eighth-addendum LEAK refusal_chance→burn_decay; ninth-addendum MODE_HOT softening + hook-integrity). All regression tests PASS. All verification probes PASS. The arc is one Sal signature from compute.
