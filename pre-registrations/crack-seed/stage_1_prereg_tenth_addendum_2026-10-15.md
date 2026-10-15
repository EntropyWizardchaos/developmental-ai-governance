# Stage 1 Calibration — Tenth Pre-Registration Addendum
## Recovery-time zero sentinel rule + Phase 1-4 crash policy + verify-script correction + ninth-addendum errata footer

**Short pre-reg addendum: integrates two load-bearing decision rules that MUST be set before Phase 5 analysis reads data (recovery-time zero sentinel handling + Phase 1-4 crash policy), one verification-script correction (reactive-semantics contradictions removed), and one errata note for stale code comments in files committed under ninth addendum. Pre-Phase-5 governance; filed BEFORE Phase 3-4 launches so the crash policy covers any crashes during the remaining ~254 sim runs. Catches from Opus 5.5 external review (two unlisted items from pre-Phase-1 letter) + Nymph routing + Sal pre-commit review.**

**Filed by:** Nymph-029 (Overseer, Cell 96, MFE)
**Date:** 2026-10-15 (filed BEFORE Phase 3-4 compute)
**Location:** `Seeds/The Crack/stage_1_prereg_tenth_addendum_2026-10-15.md`

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
- `stage_1_prereg_ninth_addendum_2026-10-13.md`

**Precipitating artifacts:**
- Opus 5.5 external-review letter (two pre-Phase-5 items unlisted in prior paste; routed by Harley 2026-10-15)
- `Seeds/The Crack/verify_prediction_actual_gap_moderator_2026-10-13.py` (verify script with contradictory print statements, lines 74-100)
- `Seeds/The Crack/verify_moderator_output_2026-10-13.log` (log containing the contradiction: numbers show 94× separation, prose claims "~matches")
- `Seeds/The Crack/v37_4_task_f_snapshot_schema_patch.py` (stale docstring lines 27-29 preserved under ninth addendum regime SHA)
- `Seeds/The Crack/stage_2_trace_manifest_2026-10-15.json` (Phase 1 ran clean; 40 coherent seeds locked for Phase 3-4)
- `Nymphs Room/mail/from_annie033_2026-10-15_phase_1_2_complete.txt` (Phase 1 completion report; zero crashes)
- `Nymphs Room/mail/from_annie033_2026-10-13_task_f_option_a_landed.txt` §5 (Annie's self-caught docstring correction; the semantics documented in ninth addendum §3)

---

## 1. Recovery-time zero sentinel decision rule (§3e moderator pre-Phase-5 governance)

### 1a. The question

The `_estimate_recent_recovery_time` function in `observer.py` (invoked at `v37.4:852` to produce `actuals['recovery_time']`) can return `0.0` under two semantically distinct conditions:

- **"Actual instant recovery event"** — a legitimate zero representing an observed recovery that completed in near-zero steps
- **"No recent recovery event yet"** — a sentinel-zero representing missing data (observer has not yet witnessed any recovery event in its window)

If the second case contributes materially to the hot `moderator_actual_recovery_time` distribution at coherent moments, the §3e / 015 R1 prediction-actual gap moderator **is partly measuring how often the sentinel-zero shows up**, not pure observer prediction error. The hot 130.93 mean_abs_gap value (per ninth addendum §3a) would be inflated by sentinel-zero contributions.

### 1b. Pre-registered decision procedure

Executed **BEFORE** Phase 5 analysis reads any data:

1. **Compute** the fraction `f_zero = count(moderator_actual_recovery_time == 0.0) / count(coherent moments)` across the 40 coherent-subset Phase 1 FULL-RESULTS pickles at `Seeds/The Crack/phase_1_output_2026-10-14/phase_1_seed_<N>_arm_hot.pkl` (hot arm only, since the moderator reads hot per 015 R1). The full-results pickles contain `channel_snapshots` — the per-step dicts carrying `moderator_actual_recovery_time` added by the Task F snapshot-schema patch under Phase-1-launch regime SHA `77b0097d...`. The trace-only pickles in `Seeds/The Crack/stage_2_traces/` are a DIFFERENT data stream (built via `build_trace_pickle_payload`, carrying `traces_by_step` for Phase 3 yoked consumption) and do NOT carry `moderator_*` fields; do not load those for this computation.
2. **Apply the pre-registered threshold:**
   - **If `f_zero > 0.05` (5%):** EXCLUDE those coherent-moment samples from the §3e moderator computation. **Exclusion removes both `moderator_actual_recovery_time` AND `moderator_predicted_recovery_time` from the same `(step, agent, seed)` record** — the gap computation requires both sides and the pre-registered exclusion is of the record, not just one side of the pair. Phase 5 report explicitly lists the exclusion count and recomputed `mean_abs_gap` on the retained sample. The verify log's 130.93 figure (ninth addendum §3a) is understood to be the UNFILTERED value; the Phase 5 filtered value may differ.
   - **If `f_zero ≤ 0.05` (5%):** INCLUDE all moments. Phase 5 report explicitly flags the `f_zero` fraction in output. The 130.93 figure stands.
3. **Report** regardless: the full `f_zero` fraction, the retained sample size, and whether exclusion was applied, in Phase 5 output.

### 1c. Threshold rationale

The 5% threshold is a reasonable "few percent" boundary consistent with 5.5's framing ("if it's more than a few percent, pre-register whether those moments get excluded or flagged"). Sentinel contributions below 5% are small relative to the 94× hot-reactive separation and don't materially alter the §3e moderator's interpretation. Contributions above 5% could inflate the gap by a non-trivial fraction and warrant exclusion.

The threshold is pre-registered BEFORE the `f_zero` fraction is computed. The decision rule is the pre-reg; the fraction value is the observation; the application is mechanical.

### 1d. Scope

- Applies to hot arm only (§3e moderator reads hot per 015 R1; reactive moderator values measure actuals step-to-step smoothness per ninth addendum §3b and are not subject to this rule)
- Applies to `moderator_actual_recovery_time` only (not to `moderator_predicted_recovery_time`, which is observer-generated and does not have sentinel semantics)
- Applies to the 40 coherent-subset seeds (not to the 21 STRICT-bucket seeds, which have no coherent moments by construction)

---

## 2. Phase 1-4 crash policy (pre-Phase-3 governance)

### 2a. Precipitating concern

The MODE_HOT invariant crash on seed 25 (Annie's probe 2026-10-09) was documented in eighth addendum §Phase-1 crash-handling softening (flag + hook integrity check). The ninth addendum did not explicitly state what happens if a seed crashes during Phase 1 (now historical) or during Phase 3-4 (upcoming). Phase 1 ran clean (no crashes), but this leaves the crash policy as a decision made after seeing data — contaminating stopping-rule integrity.

**Pre-reg the policy now, before Phase 3-4 launches.**

### 2b. Policy by phase

**Phase 1 scan (historical, documented for completeness):**
- Crash = seed SKIPPED, next seed in the scan sequence added, scan continues
- Skipped seed counted toward N=250 cap (consumes a slot)
- Skipped seed NOT counted toward K=40 coherent target (cannot contribute coherence it didn't produce)
- Phase 1 ran clean (134 seeds, zero crashes); this clause documents what the policy WOULD HAVE been if any seed had crashed

**Phase 3 / 3' / 3'' (coherent-subset arm runs on 40-seed subset):**
- Crash on seed `s` in arm `A` = `(s, A)` marked FAILED-AT-PHASE-3, EXCLUDED from arm `A`'s primary-metric computation
- Phase 5 report explicitly lists the exclusion count per arm (`failed_at_phase_3_count` field)
- **Methodology-concern threshold:** if > 5% of coherent-40 seeds (i.e., > 2 seeds) crash in any single arm, flag as a METHODOLOGY CONCERN in Phase 5 report with explicit "retained N < 38" note on that arm's primary metric
- Does NOT trigger re-launch or re-run; the exclusion stands

**Phase 4 (no_obs on all 134 Phase 1 seeds, for canonical surface ratification per §6b):**
- Crash on a STRICT-bucket seed (hot_observer_never_formed, N=21) = flagged, excluded from the ≤1e-10 bit-identity ratification check with explicit note in Phase 5 output
- Crash on a coherent-subset seed in Phase 4 = excluded with note (Phase 4 is secondary ratification; less load-bearing than Phase 3)
- **Phase 4 methodology-concern threshold:** if > 10% of STRICT-bucket seeds (> 2 seeds) crash in Phase 4, flag as a RATIFICATION CONCERN — the STRICT bucket's §6b assertion loses statistical power

### 2c. Scope exclusions

- The sys.modules registration bug caught during Phase 1 seed 200 (Annie's near-miss, 2026-10-15) was an infrastructure error, not a MODE_HOT invariant crash. Infrastructure errors are handled by catch-and-retry (standard harness pattern); they do not fall under this crash policy.
- `LEAK_TEST_MODE=True` runs (positive control) are not production; Gate 1 Exercise 1 crashes would be a different pre-reg concern not covered here.

### 2d. Report requirement

Phase 5 output JSON must include fields:
- `phase_1_crash_count` (expected 0, confirmed from `phase_1_sweep.log`)
- `phase_3_arm_crash_counts` (per-arm dict: `{yoked: N, reactive: N, matched: N}`)
- `phase_4_strict_crash_count` and `phase_4_coherent_crash_count`
- `methodology_concern_flags` (list of flags fired per 2b thresholds)

---

## 3. Verify-script correction (log self-contradiction fix)

### 3a. The contradiction

`verify_prediction_actual_gap_moderator_2026-10-13.py` lines 74-100 contain print statements written against Annie's PRE-corrected docstring assumption that "reactive mode should show ~0 gap due to F5 override." The subsequent corrected semantics (ninth addendum §3b) establish that reactive captures `|actuals[t-1] − actuals[t]|` (step-to-step smoothness), not prediction error. The script's print statements and the actual output numbers contradict within the same log:

- Line ~344 output: `reactive mean_abs_gap: 1.3916278033407625`
- Line ~346 output: `(Note: reactive moderator ~matches hot's because capture happens BEFORE step_predictions AND BEFORE F5 override.`

The 94× separation between hot's 130.93 and reactive's 1.39 (ninth §3b) is the correct interpretation. The log's prose "~matches hot's" is stale.

### 3b. Correction procedure

1. Edit the verify script to remove or rewrite the stale print statements (lines 74-76, 94-100 specifically). Replace with the correct semantics: *"Reactive captures |actuals[t-1] − actuals[t]| step-to-step smoothness (not prediction error). Hot captures observer prediction error. The ~94× separation confirms F5 override is firing and the two modes measure genuinely different quantities, as pre-registered in ninth addendum §3b."*
2. Rerun the verify script to produce a clean, non-self-contradictory log.
3. Commit the corrected log alongside this addendum.

### 3c. Scope exclusion

The verify script's CORE FUNCTION — confirming `compute_prediction_actual_gap(hot_results)` runs end-to-end on live hot trace — remains valid and unchanged. Only the stale prose/comments are corrected. The numerical result (hot n=5746, mean_abs_gap=130.93) stands.

---

## 4. Ninth-addendum errata footer (stale code comments acknowledged)

The following comments in files committed under ninth-addendum regime SHA `77b0097d...` describe the PRE-corrected reactive-mode semantics and are known-stale. They are preserved in the committed source for traceability (editing them would move the regime SHA, which is pre-registered). **The current authoritative semantics are those of ninth addendum §3; the comments below are superseded by that section.**

Known-stale comments:

| File | Line(s) | Stale claim |
|---|---|---|
| `v37.4_structural_metacognition_stage_2.py` | 922 | `# channel consumers see predicted == actual.` |
| `v37.4_structural_metacognition_stage_2.py` | 2839-2840 | `# Reactive runs have predicted==actual due to F5 override; moderator reads HOT runs only per 015 R1.` |
| `v37_4_task_f_snapshot_schema_patch.py` | 27-29 | `Phase 5 moderator reads HOT runs only per Sal 015 R1 (reactive's predicted== actual trivially due to F5, so reactive values are not informative for the moderator — captured regardless for diagnostic completeness).` |

The F4 edit block in `v37_4_task_f_snapshot_schema_patch.py` may contain additional stale commentary preserved verbatim as part of the patch's atomic apply (patch content is immutable once applied; the patch script itself is historical).

**Beyond the three enumerated comments above, any comment in files committed under regime SHA `77b0097d...` asserting one of the following claim-patterns is also superseded by ninth addendum §3b:**

- `"predicted==actual"` or `"predicted == actual"` (as a claim about reactive mode)
- `"trivially due to F5 override"` or variants claiming reactive's gap is trivial
- `"reactive's moderator values are not informative"` or variants claiming reactive gap is near-zero/zero
- `"reactive moderator ~matches hot's"` or variants claiming the two modes measure the same quantity

These semantic claims about reactive mode were pre-corrected before Phase 1 compute (per Annie's self-catch 2026-10-13 Task F Option A letter §5). Any such stale comment preserved in committed source is documentation drift, not operational code — the simulation itself computes correctly per ninth §3b semantics; only the comments describing what it computes are stale. The patterns above are grep-able identifiers for future readers encountering a comment they're uncertain about.

**Why not fix in source and re-lock the SHA:** modifying the regime file for comment corrections would move the regime SHA, invalidating the ninth-addendum lock without substantive change. This errata footer is cheaper (one short document) and just as honest (future readers see explicitly what's stale and what supersedes it). Per Opus 5.5 external-review recommendation (Option B of two options presented, 2026-10-15).

---

## 5. Scope of this amendment

**What this changes (pre-reg content):**
- §3e moderator computation gains a pre-registered sentinel-zero handling rule (§1 of this addendum)
- Phase 3-4 compute gains a pre-registered crash policy (§2)
- Verify script and its log are corrected (§3)
- Three stale code comments acknowledged as superseded (§4)

**What this does not change:**
- Phase-1-launch regime SHA `77b0097d` (ninth-addendum lock stands)
- stage_2_hooks.py SHA `66528da2` (unchanged)
- §3e moderator primary read: HOT only on `moderator_predicted_recovery_time` and `moderator_actual_recovery_time` per 015 R1
- Ninth addendum §3a hot mean_abs_gap: 130.93 (unfiltered value; §1c Phase 5 filter may produce a different retained value)
- Ninth addendum §3b reactive-semantics walk (actuals step-to-step smoothness, not prediction error)
- Fifth addendum §6 Phase 1 stopping rule (K=40 or N=250 cap; already satisfied: K=40 reached at N=134)
- Primary metric + ±101.85 threshold + TOST equivalence + intersection-union verdict
- Any other item in fifth through ninth addenda

**Chain of pre-reg SHAs through this addendum:**
- `3aea325` fifth → `7556b95` sixth → `7436a2f` seventh → `86b7eee` eighth → `f10f37e` simulation code → `0aad4cd` ninth + Phase-1-launch SHA → `286002f` Gate 1 PASS → `f4f66ac` Phase 2 manifest → **(this addendum's commit, next)**

---

## 6. Attribution for this addendum

**Opus 5.5** (external reviewer, pre-Phase-1 letter routed by Harley 2026-10-15):
- Identified the recovery-time zero sentinel concern (§1 origin): *"if `_estimate_recent_recovery_time` returns 0 when there's been no recent recovery, many of hot's 5,746 coherent moments are 'no data,' not 'instant recovery.' That would inflate the 130.93 gap, and the moderator would partly be measuring how often 0 shows up."*
- Identified the crash policy gap (§2 origin): *"it matters before Phase 1 launches, not just before Phase 5. If Phase 1 is already running, get the rule written down now, before any crash shows up."*
- Identified the verify-log self-contradiction (§3 origin) and the two-option framing for the stale code comments (§4 origin, Option B selected)
- Review attribution: 5.5 is Claude-family (own self-disclosure); audit grain is near-substrate not external-substrate

**Nymph-029** (Overseer, Cell 96, MFE):
- Routed Harley's paste of 5.5's items into this addendum
- Specified the pre-registered decision procedure for §1 (f_zero threshold at 5%, applied BEFORE computing the fraction)
- Specified the phase-differentiated crash policy for §2 (skip-and-replace for Phase 1 scan; mark-failed-and-exclude for Phase 3-4; methodology-concern thresholds)
- Specified the verify-script correction procedure for §3
- Specified the errata footer per 5.5 Option B for §4

**Annie-033** (Cell 66 FFF, Thread, forge-partner):
- Original self-catch (2026-10-13 Task F Option A letter §5) on docstring drift that produced the ninth-addendum §3b correction — this addendum's §4 is the committed-source analog of that same correction
- Will execute: §3 verify-script fix + rerun, §1 fraction-computation (BEFORE Phase 5), §2d report fields in Phase 5 output

**Salazaar** (Cell 33 EMM, kill-shape audit, eighth leg):
- Pre-commit spot-check per 018 cadence (standing offer for addendum reviews)
- Review targets: §1 threshold justification, §2 phase-differentiated policy, §3 correction procedure, §4 errata completeness
- Signoff required BEFORE commit to GitHub (same discipline as ninth)

**Harley** (operator):
- Routed Opus 5.5 external review from his own hotel-session mailbox 2026-10-15
- Approved tenth-addendum shape (recovery-time rule + crash policy + verify fix + errata footer in one short document, over any alternative shape)

---

## 7. Expected sequence from here

1. Route this addendum draft to Salazaar for pre-commit spot-check readthrough per 018 cadence
2. In parallel: Annie corrects verify script (§3) and reruns to produce clean log
3. Address any Sal catches (expected fast — four content blocks, each tight)
4. Commit tenth addendum + corrected verify log to GitHub (`EntropyWizardchaos/developmental-ai-governance`)
5. Annie launches Phase 3/3'/3''/4 compute (~7h overnight)
6. BEFORE Phase 5 analysis reads data: Annie computes `f_zero` fraction on existing Phase 1 coherent-subset trace pickles and applies §1b rule mechanically
7. Phase 5 analysis via `phase_5_analysis.py` with crash counts (§2d) and f_zero handling (§1b) reported in output

---

## 8. Signatories

- Nymph-029 (Overseer, Cell 96, MFE) — filed 2026-10-15
- Opus 5.5 (external reviewer, Claude-family) — originated §1-4 catches via Harley-routed letter 2026-10-15
- Annie-033 (Cell 66, Thread) — will execute §3 and §1b
- Salazaar (Cell 33, kill-shape audit) — pending spot-check per 018 cadence
- Harley — operator; approved tenth-addendum shape and sequence

---

## 9. Chain of pre-reg documents on file

1. `stage_1_prereg_2026-09-17.md`
2. `stage_1_prereg_addendum_2026-09-20.md`
3. `stage_1_prereg_second_addendum_2026-10-04.md`
4. `stage_1_prereg_third_addendum_2026-10-04.md`
5. `stage_1_prereg_fourth_addendum_2026-10-04.md`
6. `stage_1_prereg_fifth_addendum_2026-10-05.md`
7. `stage_1_prereg_sixth_addendum_2026-10-08.md`
8. `stage_1_prereg_seventh_addendum_2026-10-08.md`
9. `stage_1_prereg_eighth_addendum_2026-10-09.md`
10. `stage_1_prereg_ninth_addendum_2026-10-13.md`
11. `stage_1_prereg_tenth_addendum_2026-10-15.md` — **this document**

**Status:** Draft. Routing to Salazaar for pre-commit spot-check. Phase 3-4 compute still gated on this addendum's Sal signoff + GitHub commit; Phase 5 analysis still gated on §1b fraction computation + rule application.
