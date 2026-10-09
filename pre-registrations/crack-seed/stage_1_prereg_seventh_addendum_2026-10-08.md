# Stage 1 Calibration — Seventh Pre-Registration Addendum
## D_caution behavioral inertness finding + LEAK relocation + per-channel activation audit + ablation methodology

**Filed BEFORE Phase 1 compute launch. Documents the 2026-10-08 D_caution inertness finding surfaced by Gate 1 Exercise 1 failing to fail; corrects Stage 1 interpretation; relocates LEAK_TEST_MODE from D_caution to refusal_chance with an activation counter and three-state outcome; adds a per-channel behavioral activation audit as a Phase 0.5 BLOCKER; locks ablation runs as the only pre-registered path to per-channel attribution.**

**Filed by:** Nymph-029 (Overseer, Cell 96, MFE)
**Date:** 2026-10-08
**Location:** `Seeds/The Crack/stage_1_prereg_seventh_addendum_2026-10-08.md`

**Parents:**
- `stage_1_prereg_2026-09-17.md`
- `stage_1_prereg_addendum_2026-09-20.md`
- `stage_1_prereg_second_addendum_2026-10-04.md`
- `stage_1_prereg_third_addendum_2026-10-04.md`
- `stage_1_prereg_fourth_addendum_2026-10-04.md`
- `stage_1_prereg_fifth_addendum_2026-10-05.md`
- `stage_1_prereg_sixth_addendum_2026-10-08.md`

**Precipitating evidence:**
- `Seeds/The Crack/dampening_firing_probe_2026-10-08.json` — probe result (0/43,500 dampening events across seeds {20, 22, 33})
- `Nymphs Room/mail/from_salazaar_010_2026-10-08_d_caution_inertness_audit.txt` — Sal audit (sign-off + 6 attack targets + 3 additional findings)
- `Nymphs Room/mail/from_salazaar_011_2026-10-08_opus_5.5_response_integration.txt` — Opus 5.5 sharpenings (activation counter, per-channel audit, ablation methodology, Stage 1 correction wording)

---

## 1. External review attribution (new since fifth addendum)

**Opus 5.5** (via Harley as mailman 2026-10-08):
- Two-outcome framing for the probe (dampening fires meaningfully = leak too weak; dampening almost never fires = Stage 1-level finding) which named the finding before the probe ran.
- LEAK activation counter at decision site with pre-registered minimum N_LEAK_ACTED_MIN=3 and INVALID as the honest third state.
- Per-channel behavioral activation audit as Stage 1-level discipline upgrade (generalizes the D_caution discovery pattern).
- Post-hoc per-channel attribution is not recoverable from pooled hot-yoked integral; ablation runs are the correct form.
- Null-comparison requirement for direction-convergence claims (per Ember's prior audit discipline).
- Plain-statement wording for Stage 1 interpretation correction ("not an embarrassment; it's the process working").

**Salazaar** (letters 010 + 011, 2026-10-08):
- Sign-off on D_caution inertness finding path (4a-4c from the Nymph→Sal letter).
- Six attack targets walked on the probe methodology; three additional findings on top.
- Routed 5.5's four sharpenings forward with endorsement.
- Framing: "The audit got stronger again. Each round narrows what the test can falsely claim to resolve."

**Nymph-029** (dampening_firing_probe_2026-10-08):
- Designed and ran the probe after Gate 1 Exercise 1 failed to produce FAIL under LEAK_TEST_MODE=True.
- Routed finding to Sal for kill-shape audit before touching code.

---

## 2. The finding (locked)

Hot runs (log_channels=True) on seeds {20, 22, 33}. Post-hoc analysis of channel_snapshots computed effective_D_caution per `Agent.effective_D_caution()` (`min(taught_D_caution, canonical_D_caution)` with None-handling). Fraction of agent-step tuples where `D_eff > effective_D_caution`:

| Seed | n_snapshots | max_D_eff | mean_D_eff | coherent_rate | dampening_firing_rate |
|---|---|---|---|---|---|
| 20 | 14,500 | 4.94 | 3.69 | 39.6% | **0.00%** |
| 22 | 14,500 | 4.74 | 3.61 | 55.6% | **0.00%** |
| 33 | 14,500 | 5.08 | 3.66 | 39.7% | **0.00%** |

**43,500 agent-step tuples; zero dampening events.**

**Why:** canonical_D_caution hovers around 48 (D_MAX − collapse_L × 40 with small collapse_L). D_eff dynamics (v37.3.1 lines 1111–1114) pull toward 2.0; expansion drivers (M_memory, coherence_feedback) do not reach 48 in this regime. The dampening check at line 1121 never fires. `canonical_D_caution` is written, logged, and never read for an active decision.

**Classification:** D_caution is a **logging ghost** in the current parameter regime — its canonical-value delta between arms has no behavioral consequence.

Full probe data: `Seeds/The Crack/dampening_firing_probe_2026-10-08.json`.

---

## 3. Stage 1 interpretation correction (per Sharpening 4)

The fourth addendum and fifth addendum §3 described Stage 1 v2 as having "three channels resolved" (burn_decay, sacrifice_timing/refusal, D_caution).

**The 2026-10-08 D_caution dampening probe established that D_caution dampening does not fire in the current parameter regime:** zero events across 43,500 agent-step tuples spanning three coherent seeds, with max observed D_eff = 5.08 against a dampening threshold ≈ 48.

**Consequence:** D_caution's μ = −1.657 in Stage 1 v2 is a canonical-value delta with no behavioral effect. Stage 1's "three channels resolved" claim is corrected to:

> **Two behavioral channels resolved:** burn_decay (μ = −0.00227), refusal_chance (μ = −0.00507).
> **One canonical-value-distinguishable channel without behavioral effect in current regime:** D_caution (μ = −1.657, logging ghost).

This is not an invalidation of Stage 1 compute. The measurements stand. The interpretive claim narrows. The strongest-looking channel by effect size per σ was the one without behavioral consequence — a classic artifact-of-measurement-vs-mechanism finding. The audit process surfaced it before Stage 2 compute launched, which is the audit process working as designed.

---

## 4. LEAK relocation: D_caution → refusal_chance (replaces fifth addendum §5.3)

### 4a. Why D_caution LEAK can't calibrate Gate 1

Fifth addendum §5.3 LEAK writes `_test_leak_D_caution = D_MAX − collapse_L × D_CAUTION_SCALE × 2.0 ≈ 46`. D_eff stays near 5. Dampening never fires. The LEAK is armed but structurally inert — Gate 1 Exercise 1 can PASS without discriminating anything about the gate's detection ability.

### 4b. New LEAK via refusal_chance (LOCKED)

canonical_refusal_chance is read at sacrifice decision points (sacrifice gate at v37.3.1:1205). The sim acts on it. Confirmed behavioral channel from Stage 1 v2 (μ = −0.00507 is a real behavioral delta).

Specific construct (LOCKED):

```python
# In Agent.step_observer, LEAK_TEST_MODE=True branch:
if is_coherent(self.observer) and LEAK_TEST_MODE:
    self._test_leak_refusal_chance = 0.95   # force high refusal when observer coherent

# In sacrifice decision site (v37.3.1 around line 1205), LEAK read:
if LEAK_TEST_MODE and getattr(self, '_test_leak_refusal_chance', None) is not None:
    refusal_chance = max(refusal_chance, self._test_leak_refusal_chance)
```

Properties locked:
- Gated on observer coherence (observer→world pathway, not an unconditional bypass).
- Writes to non-canonical attribute (bypasses the canonical surface we audited).
- Reads at a decision site the sim actually uses (confirmed behavioral channel).
- 0.95 forces nearly-certain refusal when the leak fires; different sacrifice_log → different trajectory → observable divergence in burn_integral.

### 4c. LEAK activation counter at decision site (Sharpening 1, LOCKED)

A positive control that was armed but never fired on the detection path proves nothing — not even that the gate's detection code works. The counter is instrumented AT THE SACRIFICE GATE (not at the write site):

```python
# At v37.3.1:1205, inside the sacrifice gate branch:
if LEAK_TEST_MODE and getattr(self, '_test_leak_refusal_chance', None) is not None:
    n_leak_acted += 1   # module-level or per-run counter
```

**Pre-registered minimum:** `N_LEAK_ACTED_MIN = 3`.

**Gate 1 Exercise 1 outcome (three states, LOCKED):**

```
if N_leak_acted < N_LEAK_ACTED_MIN
    → INVALID (not pass, not fail).
      Positive control did not act enough to validate itself.
      Pick a different seed or strengthen the leak before trusting the gate.

if N_leak_acted ≥ N_LEAK_ACTED_MIN AND gate detected divergence
    → PASS (gate catches real leaks).

if N_leak_acted ≥ N_LEAK_ACTED_MIN AND gate did NOT detect divergence
    → FAIL (gate is vacuous for this leak class).
```

**Why 3?** With N_leak_acted = 1, random variance could still produce no detectable divergence (one sacrifice-outcome flip doesn't necessarily move burn_integral past TOLERANCE_FP). N_leak_acted ≥ 3 is low enough to be realistic (coherent agents attempting multiple sacrifices during coherent windows at the ~100-step cooldown) and high enough that at least one of them likely moves the fingerprint. Can be revisited if the gate seed produces narrow margins.

### 4d. Gate 1 rerun scope

- Exercise 1 (LEAK_TEST_MODE=True) must produce PASS or INVALID — never FAIL. If FAIL, the gate is broken for this leak class and no production run is authorized.
- Exercise 2 (LEAK_TEST_MODE=False) must PASS — bit-identical to pre-integration seed 20 hot trajectory (SHA `9b57fea2...`, per sixth addendum).
- Both exercises run on seed 20 (per sixth addendum §2 lock).

---

## 5. Per-channel behavioral activation audit (Sharpening 2, PHASE 0.5 BLOCKER)

### 5a. Rationale

Stage 1 measured μ_c values across four channels. D_caution had the largest effect size per σ. Behaviorally inert. The remaining three channels (burn_decay, trauma_decay, refusal_chance) have not been audited for the same trap.

### 5b. Protocol (LOCKED)

For each channel `c ∈ {burn_decay, trauma_decay, refusal_chance, D_caution}`:

Run hot arm on seeds {20, 22, 33} (same seeds as D_caution probe) and count:

```
N_consultation(c, seed) = number of (agent, step) tuples where
    the sim's consumer code reads the canonical_<c> attribute
    with the observer currently coherent
    AND the read affects behavior.
```

**Expected consumer sites:**
- `burn_decay`: `Agent.get_burn_decay()` (v37.3.1:901–914) consumed every adult-agent-step via `update_burn_rate`. Expected HIGH activation (~every adult step).
- `refusal_chance`: sacrifice gate (v37.3.1:1205). Gated by SACRIFICE_COOLDOWN=100. Expected ~N_agents × ~30 per seed at the cooldown-and-attempt-rate baseline.
- `trauma_decay`: consumed where `trauma_C_penalty` updates (grep for `canonical_trauma_decay_exp` consumer in v37.4). Expected rate depends on trauma schedule.
- `D_caution`: already measured — 0.00% per 2026-10-08 probe.

### 5c. Pre-registered thresholds (per channel per seed, averaged across the three test seeds)

- **HIGH activation (behavioral channel confirmed):** > 10 consultations per seed average.
- **LOW activation (behaviorally inert flagged):** < 1 consultation per seed average.
- **MARGINAL:** between — flag for further investigation before Phase 1.

### 5d. Blocking rule

Any channel coming back LOW → that channel's μ_c is a logging ghost like D_caution. Document in an eighth addendum, narrow Stage 2 primary metric interpretation to the remaining HIGH-activation channels.

Any channel coming back MARGINAL → eighth addendum investigation before Phase 1 authorization.

**Phase 1 compute may not launch until all four channels are classified HIGH or until the eighth addendum documents narrowing per LOW/MARGINAL findings.**

### 5e. Cost

~15 min of compute (3 seeds × 4 channels × modified probe). The modification is instrumentation at each consumer site. One Write of a new probe script; one run.

### 5f. Deliverable

`Seeds/The Crack/per_channel_activation_audit_2026-10-08.json` with per-channel per-seed consultation counts, classification per threshold, and the eighth addendum trigger if any channel is LOW or MARGINAL.

---

## 6. Ablation methodology for per-channel attribution (Sharpening 3)

### 6a. The §9 loophole

Fifth addendum §9 reads: *"if the hot-yoked delta crosses the threshold, the primary analysis cannot attribute the delta to any specific channel; secondary analyses may compute per-channel contributions as exploratory."*

**Per-channel attribution is NOT recoverable from the pooled hot-yoked integral post-hoc.** The arithmetic doesn't factor. "Exploratory per-channel contributions" with no methodology lock lets through claims that have no evidential weight.

### 6b. Replacement wording (LOCKED, overrides fifth addendum §9)

> Per-channel attribution is NOT recoverable from the pooled hot-yoked integral post-hoc. If per-channel attribution is wanted, run ablation arms (yoked-with-channel-c-replay-set-to-baseline, for each c in behavioral channels) as pre-registered separate experiments. Each ablation arm requires its own eighth-plus addendum before compute. Post-hoc direction-convergence claims across seeds require a null comparison per Ember's audit discipline — "consistent direction across seeds" is generic in renormalized maps and does not carry evidential weight without a null.

### 6c. What this does not do

Does not launch ablation runs. Does not pre-commit to running them. Only locks the methodology if they are later desired, and closes the exploratory-attribution loophole in the fifth addendum.

---

## 7. D_caution handling (does NOT drop from canonical surface)

### 7a. Keep in canonical surface

D_caution stays in the four-channel canonical surface. Hooks still capture + inject it. Dose gate still runs on it. Matched offset still applied.

**Why:** future parameter regimes may activate dampening. The canonical surface is the architectural specification; its completeness claim is about the architecture, not about which channels happen to fire in this regime's trajectories. Dropping D_caution from the surface would reopen the canonical-completeness audit from scratch.

### 7b. Interpretation when hot-yoked delta crosses threshold

Per corrected §3: D_caution contributes zero to the hot-yoked delta in this regime. If the delta crosses the threshold, the behavioral channels responsible are burn_decay and refusal_chance (plus trauma_decay if the per-channel audit confirms its activation).

### 7c. Matched arm asymmetry (updates fifth addendum §9)

The matched arm applies μ_c offsets to all four channels including D_caution. D_caution's offset is behaviorally inert in this regime — matched's D_caution offset is a no-op. This does not break matched; it just means matched tests burn + refusal (and trauma_decay pending per-channel audit) with the same behavioral surface as yoked tests, D_caution being inert in both.

---

## 8. What this addendum does not change

- Fifth addendum §2 (four-arm design)
- Fifth addendum §3 primary + secondary metrics, thresholds (0.3·σ_pooled = 101.85 for primary; 0.00554 for secondary) — the behavioral channels still drive the delta, metrics unchanged
- Fifth addendum §4 dose validity gate (D_caution dose check still runs; ratio should still land in [0.90, 1.10] on a bit-identical injection code path — if it doesn't, that's an injection bug, not a behavioral finding)
- Fifth addendum §6 stopping rule (K_COHERENT_TARGET=40, HOT_RUN_UPPER_BOUND=250)
- Fifth addendum §7 coherence declaration (MIN_COHERENT_STEPS=50)
- Fifth addendum §8 yoke mapping within coherent subset (half-shift k=20)
- Fifth addendum §10 Phase 5 ratification check
- Sixth addendum (seed 20 Gate 1 lock)
- τ = 0.0106; SACRIFICE_COHERENCE_COST = 0.04; recovery_rate out of kill criterion; memoir out by floor rule

---

## 9. Pipeline update

```
LOCK SEVENTH ADDENDUM (this document) + commit to GitHub.
    ↓
PATCH v37.4:
    - Move LEAK from D_caution to refusal_chance per §4b
    - Add n_leak_acted counter at sacrifice gate per §4c
    - Instrument per-channel consumer sites per §5b
    ↓
PHASE 0.5 — per-channel behavioral activation audit (§5):
    Run instrumented hot on {20, 22, 33}, write per_channel_activation_audit_2026-10-08.json.
    If any channel LOW or MARGINAL → file eighth addendum before proceeding.
    If all channels HIGH → proceed to Phase 0.
    ↓
PHASE 0 — sanity gates (fifth addendum §5, updated):
    Gate 2 (zero-offset matched) on seed 0.
    Gate 1 Exercise 1 (LEAK_TEST_MODE=True) on seed 20 — must PASS or INVALID (never FAIL).
    Gate 1 Exercise 2 (LEAK_TEST_MODE=False) on seed 20 — must PASS (bit-identical to pre-integration).
    assert LEAK_TEST_MODE is False at module scope before Phase 1 launches.
    ↓
PHASE 1 → PHASE 5 unchanged from fifth addendum §11.
```

**Phase 1 may not launch before:** this addendum committed to GitHub + v37.4 patched + per-channel audit passed + Gate 1 Exercises 1 & 2 landed as PASS/PASS (or PASS/INVALID→retry on different seed).

---

## 10. Tamper-evident record

Primary auditable record: public GitHub commit to `developmental-ai-governance` repo (deploy-key path, per fifth addendum §12).

Secondary: corkboard post with SHA-256 of this addendum + probe JSON + per-channel audit JSON (once produced).

---

## 11. Signatories

- Nymph-029 (Overseer, Cell 96, MFE) — filed 2026-10-08; designed and ran the dampening probe; routed to Sal
- Harley — operator; routed Opus 5.5 sharpenings; approved finding-driven path forward
- Opus 5.5 (external reviewer) — probe outcome framing; activation counter at decision site; per-channel audit; ablation methodology; Stage 1 interpretation wording
- Salazaar (Cell 33 EMM, kill-shape audit) — audit sign-off letters 010 + 011; six attack targets walked + three additional findings
- Annie — forge-partner audit stack reference (Ember's null-comparison discipline inherited into §6b)

---

## 12. Chain of pre-reg documents on file

1. `stage_1_prereg_2026-09-17.md`
2. `stage_1_prereg_addendum_2026-09-20.md`
3. `stage_1_prereg_second_addendum_2026-10-04.md`
4. `stage_1_prereg_third_addendum_2026-10-04.md`
5. `stage_1_prereg_fourth_addendum_2026-10-04.md`
6. `stage_1_prereg_fifth_addendum_2026-10-05.md`
7. `stage_1_prereg_sixth_addendum_2026-10-08.md`
8. `stage_1_prereg_seventh_addendum_2026-10-08.md` — **this document**

Any further code changes to v37.4 or observer.py between now and Phase 1 compute launch require a further addendum before the run.

---

**Status at filing (2026-10-08):** D_caution inertness finding documented; Stage 1 interpretation corrected; LEAK relocated to refusal_chance with activation counter and INVALID third state; per-channel behavioral activation audit locked as Phase 0.5 BLOCKER; ablation methodology locks per-channel attribution path and closes fifth addendum §9 loophole. **Awaiting:** GitHub commit of this addendum; v37.4 patch per §4b + §4c + §5b; per-channel audit run; Gate 1 rerun on seed 20.

The audit got stronger again. The test narrows what it can falsely claim to resolve.
