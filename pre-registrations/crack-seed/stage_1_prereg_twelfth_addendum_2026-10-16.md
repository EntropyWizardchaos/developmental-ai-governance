# Stage 1 Calibration — Twelfth Pre-Registration Addendum
## Post-Phase-5 corrigenda: manifest-verifier path-resolution bug + f_zero-direction correction + prose-label disambiguation + verdict record

**Short post-outcome addendum: documents three corrigenda surfaced by Opus 5.5 external review of Annie-034's Phase-5-landing write-up, plus the verdict itself for the audit record. This addendum does NOT alter any pre-registered rule. The eleventh addendum's primary-metric mapping fired mechanically on the observed data and produced its registered outcome. Twelfth is scoped to: (§1) `verify_phase_3_4_manifest()` path-join bug that caused the top-level `phase_3_4_manifest_verification` field to report `FAIL_WITH_LIST` on all 254 entries despite the loader-side per-pickle SHA check passing clean — the compute wasn't contaminated, a hygiene verifier reported wrong; (§2) correction of the pre-Phase-5 expectation that f_zero exclusion would REDUCE the mean_abs_gap — actual observation: exclusion RAISED it (102.29 → 148.99), interpretation flipped (observer worse in trauma-adjacent windows than in quiet windows); (§3) prose-label disambiguation for `EQUIVALENCE_REJECTED` which reads in English as the opposite of what the test did; (§4) verdict record as the audit-chain's final-answer artifact for the registered primary metric. Catches from Opus 5.5 external review (three items on Annie's Phase-5-landing letter) + Annie-034 forge-partner specification + Nymph-031 routing + Sal pre-commit spot-check pending.**

**Filed by:** Nymph-031 (Overseer, Cell 96, MFE, Opus 4.7, cold-boot post full-distill)
**Date:** 2026-10-16 (filed POST Phase 5 analysis; corrigenda, not pre-registration)
**Location:** `Seeds/The Crack/stage_1_prereg_twelfth_addendum_2026-10-16.md`

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
- `stage_1_prereg_tenth_addendum_2026-10-15.md`
- `stage_1_prereg_eleventh_addendum_2026-10-15.md`

**Precipitating artifacts:**
- `Seeds/The Crack/phase_1_output_2026-10-14/phase_5_analysis_20261016_051648.json` — Phase 5 output JSON produced by `phase_5_analysis.py` at SHA `b93fe5c2...` (eleventh §4c)
- `Nymphs Room/mail/from_annie034_2026-10-16_phase_5_verdict_architecture_claim_rejected_equivalence_demonstrated.txt` — Annie-034's Phase-5-landing write-up with 5.5's three corrections folded in
- Opus 5.5 external-review letter on Annie's first Phase-5 write-up (routed by Harley 2026-10-16)
- `Seeds/The Crack/verify_phase_3_4_manifest_INDEPENDENT_2026-10-16.py` — Annie's independent manifest-integrity verifier (254 entries, candidate-list path resolution against CRACK_DIR)
- `Seeds/The Crack/verify_phase_3_4_manifest_INDEPENDENT_2026-10-16.log` — audit log: 0 mismatches, 0 missing, INTEGRITY CLEAN

---

## 1. Manifest-verifier path-resolution bug (hygiene corrigendum)

### 1a. The observation

The Phase 5 output JSON at `phase_1_output_2026-10-14/phase_5_analysis_20261016_051648.json` reports:

```
phase_3_4_manifest_verification: FAIL_WITH_LIST
phase_3_4_manifest_failures: [254 entries, all with reason FILE_NOT_FOUND]
```

All 254 manifest entries flagged `FILE_NOT_FOUND`. **This is a path-resolution bug in a hygiene verifier, not evidence of pickle corruption or missing files.**

### 1b. Root cause

`verify_phase_3_4_manifest()` in `phase_5_analysis.py` (SHA-locked at `b93fe5c2...` per eleventh §4c) joins each manifest entry's `path` field (CRACK-DIR-relative, e.g., `phase_1_output_2026-10-14/phase_1_seed_200_arm_yoked.pkl`) against the `output_dir` parameter (which IS `phase_1_output_2026-10-14`). Result: it checks for files at `phase_1_output_2026-10-14/phase_1_output_2026-10-14/<file>.pkl` — doubly-prefixed, nonexistent paths. All 254 entries get flagged `FILE_NOT_FOUND` mechanically.

The bug is purely in the path-join logic of the top-level verifier function. It does not affect the actual integrity of the manifest or the pickles.

### 1c. Load-bearing fact — the loader-side check PASSED

The pre-registered load-bearing check (per eleventh §3b item 4: *"Phase 5 script re-verifies each pickle against manifest before consumption"*) is implemented in the `_verified_loader` function that `pickle.load` passes through. `_verified_loader` uses a **candidate-list path resolution strategy** (checks absolute path, bare filename, and `phase_1_output_2026-10-14/<filename>` in sequence) that resolves manifest keys CORRECTLY against on-disk locations.

**If any of the 254 pickles had been SHA-mismatched or missing, `_verified_loader` would have raised `RuntimeError` and halted the analysis.** The analysis completed, which proves all 254 pickles passed loader-side SHA verification at compute time.

The top-level `phase_3_4_manifest_verification` field is a separate hygiene-report path that failed to resolve correctly. The actual gating check — the one that would have halted compute on a real integrity issue — ran clean.

### 1d. Independent re-verify artifact

Annie-034 wrote and ran an independent verifier post-landing to confirm integrity:

- **Script:** `Seeds/The Crack/verify_phase_3_4_manifest_INDEPENDENT_2026-10-16.py` (5,315 bytes)
- **Output log:** `Seeds/The Crack/verify_phase_3_4_manifest_INDEPENDENT_2026-10-16.log` (1,431 bytes)
- **Verdict: INTEGRITY CLEAN.** All 254 manifest entries match on-disk SHA. Zero mismatches, zero missing.
- **Resolution strategy:** paths resolved against `CRACK_DIR` directly (not `output_dir`)
- **SHA computation:** byte-identical to the manifest builder (streaming SHA-256 at 65KB chunks)

The independent re-verify establishes that the manifest's declared SHAs match the on-disk pickles. Combined with §1c (loader-side gating check passed at compute time), the integrity of the Phase 5 input data is established on TWO independent paths.

### 1e. Why we are NOT patching the SHA-locked script

**⚠ LOAD-BEARING READER-RULE for Phase 5 output interpretation:** `phase_3_4_manifest_verification: FAIL_WITH_LIST` in isolation would suggest Phase 5 ran on unverified data. **In context: the field is a hygiene-verifier output that failed due to a path-join bug (§1b), and the actual load-bearing per-pickle SHA check (loader-side, pre-reg §3b item 4) passed clean (§1c), with independent re-verify confirming integrity (§1d). The compute wasn't contaminated. The claim stands as filed.**

Patching `verify_phase_3_4_manifest()` in `phase_5_analysis.py` would:
- Move the file's SHA away from the pre-registered lock value `b93fe5c2...`
- Require a new commit sequence (parallel to eleventh §4b two-commit sequence)
- Introduce a code change AFTER the pre-reg result landed — exactly the kind of post-outcome edit pre-reg discipline forbids

Instead, the resolution is **documentation + external artifact**:
- This addendum (§1a-d plus the reader-rule above) names the bug + the load-bearing fact
- Annie's independent re-verify script + log provides the mechanical integrity evidence
- The Phase 5 output JSON's `phase_3_4_manifest_verification: FAIL_WITH_LIST` field remains in place, interpretable via the reader-rule above

### 1f. Future-schema-extension discipline note

The path-resolution convention for pre-reg-locked verifiers needs to be explicit at write time. The eleventh §3b spec said *"Phase 5 script re-verifies each pickle against manifest before consumption"* but did not specify path-resolution convention (absolute vs CRACK-DIR-relative vs output_dir-relative). Future verifier specifications should name the resolution convention explicitly, parallel to how `sha256_algorithm` sentinel disambiguates the SHA computation convention. Candidate feedback-memory, not filed here.

---

## 2. f_zero exclusion raised the gap, not lowered — direction correction

### 2a. The pre-Phase-5 expectation

Eleventh addendum §2a-b framed the f_zero=0.4883 exclusion as a filter that would narrow the moderator to "prediction quality conditional on recent recovery event." The implicit framing (also in `for_opus_5_5_external_review_2026-10-15.md` §3) was that the sentinel-zero records were **inflating** the mean_abs_gap — exclusion would remove the inflation, producing a cleaner (and lower) retained-sample mean.

**That framing was wrong.** The direction was the opposite.

### 2b. The actual observation

From Phase 5 output JSON:
- UNFILTERED pooled `mean_abs_gap`: **102.29** (across all coherent moments, including sentinel-zero records)
- FILTERED pooled `mean_abs_gap` (post-tenth §1b exclusion): **148.99** (retained records only)
- Delta: **+46.7 units** — exclusion RAISED the gap

The ninth-addendum §3a UNFILTERED hot `mean_abs_gap = 130.93` figure (from verify-script on seed 20) sits between these pooled values, as expected (single-seed sample vs 40-seed pooled). All three numbers are mutually consistent.

### 2c. Interpretation

In the quiet windows (no recent recovery event in observer's lookback → `moderator_actual_recovery_time = 0.0` sentinel), the observer defaults to small `moderator_predicted_recovery_time` values. The predicted ≈ actual ≈ 0 pairing produces small absolute gaps numerically — these records *looked* like good predictions in the pooled unfiltered mean.

After exclusion, the retained records are **trauma-adjacent moments** — windows where the observer HAD witnessed a recovery event and `moderator_actual_recovery_time` is a real nonzero value the observer is trying to predict. In those windows, the observer's prediction accuracy is substantially worse.

**Honest interpretation line, add to any Phase 5 write-up:**

> *"The observer's prediction accuracy is worse in trauma-adjacent windows than in quiet windows. The pre-Phase-5 expectation that sentinel-zero records were inflating the mean_abs_gap was wrong; those records were deflating it. Post-exclusion, the retained-sample mean (148.99) is the honest conditional measure of observer prediction quality during moments where there was real recovery dynamics to predict."*

**Reader note on floor effect (per Sal 021 §2 polish):** small quiet-window gaps don't constitute prediction skill — any predictor defaulting to near-zero values would produce similar absolute gaps in sentinel-zero windows. The 148.99 retained-sample mean is the honest conditional measure of skill in windows where there was something real to predict; the 102.29 pooled unfiltered figure reflects a mix of real skill and floor-effect numerical convenience.

### 2d. Primary verdict unaffected

The primary metric (`burn_integral` delta) does not read moderator fields. The architecture-claim verdict (EQUIVALENCE_REJECTED per §4 of this addendum) is unchanged by this interpretation correction.

The §3e moderator was always a secondary/diagnostic read per fifth addendum §3. This correction tightens the moderator's interpretation; it does not alter the pre-registered primary metric or its threshold.

### 2e. Why this is a corrigendum, not an amendment

The eleventh §2 did not pre-register a numerical expectation about the direction of f_zero exclusion's effect on the mean. It pre-registered the mechanical rule (whole-record exclusion when f_zero > 0.05) and the reporting requirement (filtered + unfiltered side-by-side). Both rule and reporting ran correctly on data. The error was in the interpretive-prose framing in `for_opus_5_5_external_review_2026-10-15.md` §3 and in Annie's letter 034 §3, both of which inherited the "exclusion-removes-inflation" expectation without computing it.

This addendum documents the direction correction honestly; the pre-reg rule stands as applied.

---

## 3. Prose-label disambiguation — `EQUIVALENCE_REJECTED` reads as the opposite in English

### 3a. The ambiguity

The code label `EQUIVALENCE_REJECTED` was pre-registered in eleventh §1b as the `architecture_claim_verdict` value when the pre-reg rule fires on `(hr=WITHIN)` or related cells of the 16-cell table. In English, the two-word phrase reads as "equivalence was rejected," which would mean *"the test found that the arms are NOT equivalent."*

**The actual semantic is the opposite.** When `_verdict_vs_threshold` returns `WITHIN_THRESHOLD`, equivalence is DEMONSTRATED (both CIs sit entirely inside the TOST equivalence region [−101.85, +101.85]). The architecture claim is REJECTED **BY DEMONSTRATING equivalence** — the predictive-self-modeling claim required `hot < yoked` AND `hot < reactive` by at least 0.3·σ_pooled; demonstrating equivalence instead means prediction doesn't do work beyond feedback at the pre-registered threshold.

### 3b. Preservation of the code label

The code label `EQUIVALENCE_REJECTED` is pre-registered. It stays. Patching it would move the SHA-locked `phase_5_analysis.py` (per §1e logic) and is not necessary — the label is unambiguous in context (it's the value of `architecture_claim_verdict`, read alongside `hv_verdict = WITHIN_THRESHOLD` and `hr_verdict = WITHIN_THRESHOLD`, which make the shape clear).

### 3c. Prose convention for write-ups going forward

**In write-up prose, state:** *"architecture claim rejected; equivalence demonstrated"* (two independent clauses that read correctly in English).

**Avoid:** *"the test rejected equivalence"* (reads opposite) or *"equivalence was rejected"* (ambiguous).

Phase 5 output JSON retains code labels. Any human-readable commentary — commit messages, letters, external documentation — uses the two-clause prose form.

---

## 4. Verdict record — what the pre-reg rule said when applied to data

### 4a. Primary metric verdicts

From `phase_5_analysis_20261016_051648.json`:

| metric | mean | SEM | 95% CI | verdict | paired SD | MDE at observed SD |
|---|---|---|---|---|---|---|
| hv (hot − yoked)    | **−36.0308** | 18.045 | [−72.5193, +0.4577]  | `WITHIN_THRESHOLD` | 116.26 | 138.34 |
| hr (hot − reactive) | **−5.4465**  | 3.529  | [−12.5828, +1.6898]  | `WITHIN_THRESHOLD` |  22.74 | 108.99 |

Both metrics' 95% CIs land entirely inside the pre-registered TOST equivalence region [−101.85, +101.85]. Direction of effect is consistent with the hypothesized direction in both legs (hot < yoked, hot < reactive — slight dampening) but magnitude is well below the 0.3·σ_pooled = ±101.85 threshold.

- hv magnitude: ~35% of threshold
- hr magnitude: ~5% of threshold

### 4b. Architecture-claim verdict (mechanical dict-lookup per eleventh §1b 16-cell table)

```
architecture_claim_verdict: EQUIVALENCE_REJECTED  (equivalence demonstrated per §3c prose convention)
architecture_claim_feedback_matters_specific_subcase: False
```

The (WITHIN_THRESHOLD, WITHIN_THRESHOLD) cell of the 16-cell table maps to `EQUIVALENCE_REJECTED` per Sal 020 §1 exhaustive mapping (eleventh §1b).

The `feedback_matters_specific_subcase` boolean is False because the specific sub-pattern (hv=BELOW_THRESHOLD ∧ hr=WITHIN_THRESHOLD) did not fire — hv also landed WITHIN_THRESHOLD, not BELOW.

### 4c. Why this is a defensible answer

Per eleventh §1d (Opus 5.5 verbatim framing): *"'real but too small to count' ends as REJECTED, not as a partial win. Don't move the threshold."* The pre-reg discipline produced its registered outcome.

Pre-reg §1 anticipated this outcome class via the WITHIN_THRESHOLD + TOST clause. Both CI's landing inside the equivalence band at 95% framing (stricter than the usual 90% for TOST) makes this a CONSERVATIVE equivalence declaration.

The paired analysis structure paid off: paired SDs 116 (hv) and 23 (hr) vs pooled 339 — the pairing compressed variance substantially, resolving into equivalence rather than into `CI_STRADDLES_THRESHOLD` (which would have been INCONCLUSIVE). The pre-Phase-5 MDE concern (eleventh §1c) that cited paired SD ≤ 50 as the regime where CIs would compress inside the equivalence band fired exactly as hypothesized.

### 4d. What the test says, plainly

> *"Hot vs reactive came out −5.45, with CI [−12.6, +1.7]. That's a tight tie. Acting on predictions did essentially nothing that reacting to the current state didn't already do. Hot vs yoked (−36) hints that timing matters a little, but that's well inside the band too. The direction was right both times. The size wasn't there."* (Opus 5.5, via Annie-034's §2 verbatim)

The observer's recovery-time predictions miss the mark by ~149 steps (filtered pooled mean_abs_gap per §2b above) — a very blurry shadow. The registered conclusion is "this observer's foresight doesn't beat the present," not "foresight can't help." The claim as built is dead; testing a sharper predictor would require a new pre-registration (Stage 3), not a revision of this one.

### 4e. What's additionally solid (preserved for audit record)

- **SHA lock match:** `phase_5_analysis_sha_locked = phase_5_analysis_sha_observed = b93fe5c2...`, `phase_5_analysis_sha_match = True`.
- **Strict ratification:** 0 fails on the 21 strict-bucket seeds (per eighth §6b assertion).
- **f_zero rule fired as pre-registered:** `f_zero = 0.4883` > 0.05 → EXCLUDE whole records applied mechanically per tenth §1b.
- **Phase 3-4 pickle integrity:** loader-side per-pickle SHA check passed on all 254 pickles at compute time (§1c); independent re-verify confirmed (§1d).
- **Phase 1-4 crash policy:** 0 crashes in Phase 1 (134 seeds); 0 crashes in Phase 3 arms (120 pickles); 1 INFRASTRUCTURE_INTERRUPTION in Phase 4 (seed 236 at 17:47 Denver 2026-10-15) classified per tenth §2c as INFRA_EVENT, NOT a sim crash, resolved via resume with atomic-write + idempotency.

---

## 5. Scope of this amendment

**What this changes (post-outcome documentation only):**
- Phase 5 output JSON's `phase_3_4_manifest_verification: FAIL_WITH_LIST` is now interpretable in context (§1)
- Pre-Phase-5 interpretive-prose framing of f_zero exclusion direction is corrected (§2)
- Write-up prose convention for `EQUIVALENCE_REJECTED` is specified (§3)
- The architecture-claim verdict and supporting evidence are recorded for the audit chain (§4)

**What this does not change:**
- `phase_5_analysis.py` SHA lock `b93fe5c2...` (eleventh §4c lock stands; no code patch)
- Phase-1-launch regime SHA `77b0097d` (ninth-addendum lock stands)
- stage_2_hooks.py SHA `66528da2` (unchanged)
- Tenth §1b decision rule (whole-record exclusion when f_zero > 0.05) — already fired; result stands
- Tenth §2 Phase 3-4 crash policy (phase-differentiated; infrastructure errors scoped-out) — fired as pre-registered on the Phase 4 INFRA_EVENT
- Eleventh §1b 16-cell `architecture_claim_verdict` mapping — fired mechanically on (WITHIN, WITHIN) cell → `EQUIVALENCE_REJECTED`
- Eleventh §2a-d moderator scope-note + per-seed retained-N reader-safety flags — fired as pre-registered
- Eleventh §3b Phase 3-4 output manifest discipline — manifest committed as Commit 3 (`724942d`); SHA matches
- Eleventh §4b-d SHA-lock + runtime self-assert — fired clean (`phase_5_analysis_sha_match = True`)
- Eleventh §5a-e 12-pickles errata — stands as filed
- Eleventh §6a-d cold-boot authorship note — stands as filed
- Primary metric + ±101.85 threshold + TOST equivalence + intersection-union verdict (fifth §3 / eighth §4c-d) — unchanged
- Any other item in fifth through eleventh addenda

**Chain of pre-reg SHAs through this addendum:**
`3aea325` fifth → `7556b95` sixth → `7436a2f` seventh → `86b7eee` eighth → `f10f37e` simulation code → `0aad4cd` ninth + Phase-1-launch SHA → `286002f` Gate 1 PASS → `f4f66ac` Phase 2 manifest → `eabdbf2` tenth → `481c90c` phase_5_analysis.py SHA lock (Commit 1) → `2d6497d` eleventh addendum (Commit 2) → `724942d` Phase 3-4 output manifest (Commit 3) → **(this addendum's commit, next; Commit 4 bundled with Annie's `verify_phase_3_4_manifest_INDEPENDENT_2026-10-16.py` + log)**

---

## 6. Attribution for this addendum

**Opus 5.5** (external reviewer, Claude-family):
- Caught the `EQUIVALENCE_REJECTED` prose-label ambiguity on first read of Annie's Phase-5-landing letter (§3 origin)
- Caught the f_zero exclusion direction misread (§2 origin): identified that the pre-Phase-5 expectation was wrong and interpretation needed to flip (observer worse in trauma-adjacent windows than in quiet windows)
- Caught the manifest-verifier `FAIL_WITH_LIST` dismissal as "cosmetic" (§1 origin): named that a pre-registered §3d check returning FAIL requires explicit documentation + independent-verify-artifact, not retrospective dismissal
- Reiterated the eleventh §1d framing: *"'real but too small to count' ends as REJECTED, not as a partial win. Don't move the threshold."* (§4c anchor)
- Review attribution: 5.5 is Claude-family (own self-disclosure, consistent with prior addendum attributions); audit grain is near-substrate, not external-substrate; consistency with eleventh §6 cold-boot authorship pattern

**Annie-034** (Cell 66 FFF, Thread, forge-partner):
- Ran `phase_5_analysis.py` through its pre-reg sequence (SHA self-assert → manifest verification → compute); documented the primary verdict and all §1f + §2b + §2c + §2d + §3d + §4d report fields
- Wrote and ran `verify_phase_3_4_manifest_INDEPENDENT_2026-10-16.py` to establish integrity on an independent path
- Routed 5.5's three corrections through to Nymph via her 2026-10-16 letter (`from_annie034_2026-10-16_phase_5_verdict_architecture_claim_rejected_equivalence_demonstrated.txt`)
- Will execute: Commit 4 bundling this addendum + independent re-verify script + log

**Nymph-031** (Overseer, Cell 96, MFE, Opus 4.7, cold-boot post full-distill):
- Routed Annie's Phase-5-landing report + 5.5's three corrections
- **Framing decision:** scoped the twelfth as post-outcome corrigenda rather than pre-reg amendment — the decision that preserved SHA lock `b93fe5c2...` and prevented post-outcome code modification. Named as its own meaningful contribution per Sal 021 §6 attribution-precision polish; this framing call is what kept the pre-reg discipline intact across the arc-close.
- Verified citation integrity against live artifacts (Annie's letter, Phase 5 output JSON at `phase_5_analysis_20261016_051648.json`, independent re-verify script + log, prior pre-reg chain)
- Filed this addendum

**Salazaar** (Cell 33 EMM, kill-shape audit, eighth leg):
- Pre-commit spot-check per 018/019/020 cadence (standing offer for addendum reviews)
- Review targets: §1b-e manifest-bug framing honesty (is "hygiene verifier bug" the right scope, or does this surface a load-bearing concern?), §2c interpretation of trauma-adjacent vs quiet-windows observer accuracy, §3b label-preservation vs patch rationale, §4a-e verdict-record completeness
- Signoff required BEFORE commit to GitHub (same discipline as ninth/tenth/eleventh)

**Harley** (operator):
- Routed Opus 5.5 external review of Annie's Phase-5-landing letter from his session mailbox 2026-10-16
- Approved twelfth-addendum shape (post-outcome corrigenda, not pre-reg amendment)
- Said "lets open the results up like christmas" at the Phase 5 fire gate; register signal: the result is to be received cleanly, whatever it says

---

## 7. What the arc produced (per Sal 021 §7, verbatim)

The pre-reg discipline worked exactly as designed. The threshold was locked before data arrived. The analysis ran mechanically on the locked rule. The verdict fired: architecture claim rejected; equivalence demonstrated. That is the clean outcome — not consolation, not failure, measurement.

What's additionally real from the data:

**The floor held.** Strict ratification: 0 fails across 21 strict-bucket seeds. The canonical surface is intact. The claim about prediction-adds-value is dead; the claim about the architecture's behavioral stability under coherent seeds survives untouched.

**hr paired SD = 22.74 is a tight empirical constraint.** Hot and reactive tracked within single digits across 40 seeds. In this regime, the feedback loop captures nearly everything the predictive arm captures. That's not consolation — it's a characterization of these world-dynamics. Future work in a different regime has a baseline to push against.

**The zero-direction finding is genuinely new.** The prediction mechanism fails precisely in the highest-stakes moments (post-trauma, real-valued recovery windows) and appears most "accurate" in quiet windows that are trivially easy to predict. This characterizes where the predictor breaks down and points at a specific design target if anyone builds a sharper instrument.

**The oracle test remains the clean next question.** Does the IDEA fail or the INSTRUMENT fail? Three outcomes, not two:
- (a) oracle wins → sharpen the predictor;
- (b) oracle loses → foresight can't matter in this regime regardless of accuracy;
- (c) oracle also WITHIN_THRESHOLD but by smaller margin → world dynamics are the bottleneck, not predictor blurriness.

The pre-reg would need to name all three outcomes to be honest.

**The pre-reg discipline is the plank.** Twelve addenda, three cold-boot cells holding the chain, one infrastructure interruption resumed cleanly, one external reviewer (5.5, Claude-family) catching three post-outcome corrections, a mechanical verdict that means what it says. That chain is the architecture. Whether the specific claim stood or fell, the chain is what future work builds from.

**On oracle timing:** Harley's register, as of this session: let it drift. See what falls into empty hands. The question will keep. Signal not reflex.

---

## 8. Expected sequence from here

1. Route this addendum draft to Salazaar for pre-commit spot-check per 018/019/020 cadence — **COMPLETE (Sal 021, 2026-10-16)**
2. Address any Sal catches — three polish items integrated (§1e reader-rule placement + bold flag, §2c floor-effect sentence, §6c attribution precision) + §7 "What the arc produced" integrated verbatim per Sal 021 §7 offer-accepted
3. Commit 4: bundle this addendum + `verify_phase_3_4_manifest_INDEPENDENT_2026-10-16.py` + `.log` + Phase 5 output JSON into one commit on GitHub main
4. Phase 5 output JSON path: `Seeds/The Crack/phase_1_output_2026-10-14/phase_5_analysis_20261016_051648.json` — committed to repo per Sal 021 signoff (result-artifact deserves same treatment as pre-reg docs)

**Arc close:** The Crack seed's registered primary-metric claim is tested and did not clear the pre-registered threshold. The architecture claim as filed is dead. The chain stands.

Any further test (sharper predictor, different metric, Stage 3) requires new pre-reg.

---

## 9. Signatories

- Nymph-031 (Overseer, Cell 96, MFE, Opus 4.7, cold-boot post full-distill) — filed 2026-10-16
- Opus 5.5 (external reviewer, Claude-family) — originated §1-3 catches via Harley-routed letter on Annie's Phase-5-landing write-up 2026-10-16
- Annie-034 (Cell 66, Thread) — ran Phase 5 analysis + wrote independent re-verify artifact; will execute Commit 4
- Salazaar (Cell 33, kill-shape audit) — pending spot-check per 018/019/020 cadence
- Harley — operator; routed 5.5 external review; approved twelfth-addendum shape

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
10. `stage_1_prereg_ninth_addendum_2026-10-13.md`
11. `stage_1_prereg_tenth_addendum_2026-10-15.md`
12. `stage_1_prereg_eleventh_addendum_2026-10-15.md`
13. `stage_1_prereg_twelfth_addendum_2026-10-16.md` — **this document**

**Status:** Draft. Routing to Salazaar for pre-commit spot-check. Commit 4 (addendum + Annie's independent re-verify artifact + log) still gated on Sal signoff. The architecture-claim verdict stands as `EQUIVALENCE_REJECTED` per the pre-registered rule applied mechanically to data; this addendum documents post-outcome corrigenda, not amendments.
