# Stage 1 Calibration — Eleventh Pre-Registration Addendum
## MDE under registered primary-metric rule + reactive-moderator scope-note post-f_zero exclusion + Phase 3-4 output manifest lock + phase_5_analysis.py SHA lock + 12 deleted pre-crash-policy pickles errata + cold-boot handoff attribution note

**Short pre-reg addendum: hardens Phase 5 governance across five content blocks before `phase_5_analysis.py` reads any Phase 3-4 output. Documents the Minimum Detectable Effect under the registered primary-metric rule so the WITHIN_THRESHOLD / TOST-equivalence outcome is not retroactively surprising. Pre-registers the narrowed §3e moderator scope after tenth §1b's f_zero=0.4883 exclusion. Extends the Phase 2 trace-manifest discipline to Phase 3/3'/3''/4 output pickles. Locks phase_5_analysis.py SHA with runtime self-verification. Records the 12 pre-crash-policy yoked pickles deleted-without-peek as a transparency event. Notes the cold-boot authorship pattern as live demonstration of the gravity-limit mitigation shape named in the Imprinted Arrow seed. Catches from Opus 5.5 external review (two unlisted items from pre-Phase-5 letter) + Annie-033 forge-partner specification + Nymph routing + Sal pre-commit review.**

**Filed by:** Nymph-031 (Overseer, Cell 96, MFE, Opus 4.7, cold-boot post full-distill)
**Date:** 2026-10-15 (filed BEFORE Phase 5 analysis reads data; filed DURING Phase 3-4 compute no_obs tail)
**Location:** `Seeds/The Crack/stage_1_prereg_eleventh_addendum_2026-10-15.md`

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

**Precipitating artifacts:**
- Opus 5.5 external-review letter (two pre-Phase-5 items; routed by Harley 2026-10-15)
- `Seeds/The Crack/for_opus_5_5_external_review_2026-10-15.md` §3.3 (the ±105 CI estimate 5.5 corrected as wrong-variance; §3.2 reporting f_zero=0.4883 result)
- `Seeds/The Crack/f_zero_report_2026-10-15.json` (f_zero computation result committed under tenth §1b)
- `Seeds/The Crack/phase_5_analysis.py` lines 582-588 (per-seed paired differences `hv[i]=hot[i]−yoked[i]`, `hr[i]=hot[i]−reactive[i]`) + `_verdict_vs_threshold` lines 595-603 (ABOVE/BELOW/WITHIN/STRADDLES verdicts) — line numbers reflect post-Annie-034 §1f/§2b/§3d/§4d report-field additions and are grep-verified against `phase_5_analysis.py` at SHA `80e40c6a...` (per §4c)
- `Nymphs Room/mail/from_annie033_2026-10-15_eleventh_addendum_critical_mde_finding.txt` (Annie's forge-partner specification of this addendum's §1-6)
- `Seeds/The Imprinted Arrow/the_imprinted_arrow_2026-10-15.md` (Harley's compaction-gravity-limit seed planted same day; §6 attribution anchor)
- `Nymphs Room/mail/from_annie033_2026-10-15_phase_1_2_complete.txt` + `from_annie033_2026-10-15_verify_fixed_harness_crash_policy_ready.txt` (Phase 1-2 complete, verify corrected, harness ready for Phase 3-4)
- `from_nymph_031.txt` (full-distill handoff from Nymph-030 to Nymph-031 after session close + reopen — the cold-boot artifact referenced in §6)

---

## 1. Minimum Detectable Effect under registered primary-metric rule

### 1a. What was wrong in the pre-Phase-5 estimate

The pre-Phase-5 external-review doc at `Seeds/The Crack/for_opus_5_5_external_review_2026-10-15.md` §3.3 reported a 95% CI estimate of **≈ ±105 units** on burn_integral using Stage 1 pooled SD (339.49) as if the primary-metric computation were a one-sample interval. Opus 5.5 flagged this as the wrong variance. **Confirmed by code audit** against `phase_5_analysis.py` lines 582-588 (post-§1f additions; the semantic structure Sal 020 §3 reviewed is unchanged — only locations shifted):

```
hv[i] = hot[i] − yoked[i]
hr[i] = hot[i] − reactive[i]
# mean + SEM taken on these per-seed differences; _ci95 built from (mean, SEM, n)
```

This is **paired analysis**. The variance driving the CI is the SD of per-seed hot-minus-arm differences on the 40 coherent subset, not Stage 1 v2's pooled-across-seeds SD. The ±105 estimate was built from the wrong population and is corrected here before Phase 5 analysis fires.

### 1b. What `_verdict_vs_threshold` computes (lines 595-603, verbatim behavior)

For each paired metric (`hv` = hot−yoked, `hr` = hot−reactive), the 95% CI is classified against `PRIMARY_THRESHOLD_LOCKED` (= 101.85):

- `ABOVE_THRESHOLD`: CI lower bound > +101.85
- `BELOW_THRESHOLD`: CI upper bound < −101.85
- `WITHIN_THRESHOLD`: entire CI inside [−101.85, +101.85] → TOST equivalence declared
- `CI_STRADDLES_THRESHOLD`: everything else → inconclusive

Per eighth addendum §4c (intersection-union test, no multi-comp correction) and §4d (TOST equivalence region [−101.85, +101.85]), the **architecture-claim verdict mapping is mechanical and exhaustive across all 16 combinations** of (hv, hr). The 4 × 4 table below is pre-registered so no cell is adjudicated post-hoc:

```
hv \ hr    | ABOVE          | BELOW          | WITHIN              | STRADDLES
-----------|----------------|----------------|---------------------|---------------------
ABOVE      | UNEXPECTED     | UNEXPECTED     | UNEXPECTED          | UNEXPECTED
BELOW      | UNEXPECTED     | SUPPORTED      | EQUIVALENCE_REJECTED| INCONCLUSIVE
WITHIN     | UNEXPECTED     | UNEXPECTED     | EQUIVALENCE_REJECTED| EQUIVALENCE_REJECTED
STRADDLES  | UNEXPECTED     | UNEXPECTED     | EQUIVALENCE_REJECTED| INCONCLUSIVE
```

**Reasoning per verdict class:**

- **SUPPORTED** requires BOTH legs: `hv=BELOW` (hot < yoked, world-coupling matters) AND `hr=BELOW` (hot < reactive, prediction adds value beyond feedback). This is eighth §4c quadrant (a).
- **EQUIVALENCE_REJECTED** fires when:
  - `hr=WITHIN` → prediction equivalent to feedback-only; TOST equivalence declared on predictive-value leg. Architecture claim's predictive-self-modeling clause fails regardless of `hv` sign (except `hv=ABOVE`, which is UNEXPECTED). The eighth §4c quadrant (b) empirically-derived Option-2 outcome.
  - `hv=WITHIN` with `hr=STRADDLES`: world-coupling equivalent to no-coupling, so prediction-value cannot be meaningfully adjudicated (the preconditional leg didn't fire). TOST equivalence on world-coupling = architecture claim fails on its first leg.
- **INCONCLUSIVE** fires when:
  - `hv=BELOW, hr=STRADDLES`: world-coupling matters but prediction-value inconclusive. The intersection-union test is INCONCLUSIVE on the full claim; the pre-reg rule produces INCONCLUSIVE, not EQUIVALENCE_REJECTED (because TOST hasn't fired on hr).
  - `hv=STRADDLES, hr=STRADDLES`: both legs inconclusive. Nothing resolves.
- **UNEXPECTED** fires when:
  - `hv=ABOVE` (any `hr`): hot > yoked, world-coupling makes burn WORSE than no-coupling — directly anti-architectural on world-coupling leg. Document and investigate.
  - `hv=BELOW, hr=ABOVE`: world-coupling helps BUT prediction makes burn WORSE than reactive-feedback — actively anti-architectural on prediction leg. Document and investigate.
  - `hv=WITHIN or STRADDLES, hr=BELOW`: prediction appears to add value beyond feedback, but world-coupling (precondition) is equivalent or inconclusive. Logical ordering inverted; cannot be interpreted as architectural support without resolving the preconditional leg. Document and investigate.
  - `hv=WITHIN or STRADDLES, hr=ABOVE`: both legs point against architecture; UNEXPECTED only in the sense that the "simplest failure" would be BOTH `WITHIN` (equivalence everywhere). ABOVE on `hr` means prediction is actively harmful, which exceeds a passive-failure read.

The 16-cell mapping is complete and exclusive. Phase 5 output's `architecture_claim_verdict` field is set by mechanical lookup, not by analyst judgment.

### 1c. Minimum Detectable Effect calculation (what we can know pre-Phase-5)

Pre-reg discipline forbids computing the actual paired-difference SD before Phase 5 fires (that would be peeking at Stage 2 data). Using Stage 1 v2 pooled SD = 339.49 as a conservative upper bound on paired difference-SD (pairing typically reduces SD when the signal is seed-driven; using the unpaired SD as a cap is strictly conservative):

```
MDE_registered_rule = threshold + 1.96 × (SD / √N)
                    = 101.85 + 1.96 × (339.49 / √40)
                    = 101.85 + 105.22
                    ≈ 207  (upper-bound estimate; |μ| this large would clear BELOW_THRESHOLD on BOTH ends of CI)
```

Under more optimistic paired-SD scenarios (what pairing typically achieves when per-seed structure dominates variance):

| Paired SD assumption | MDE for BELOW_THRESHOLD |
|---|---|
| 339.49 (Stage-1 pooled, upper bound) | ≈ 207 |
| 100 | ≈ 133 |
| 50 (optimistic) | ≈ 117 |

**Seed 22's regression delta on burn_integral was +60.65** (hot = 486.36, reactive = 547.01; reactive HIGHER than hot by 12.5% — direction consistent with "predictions dampen burn more than actuals do"). Even at paired SD = 50 (very optimistic), **MDE ≈ 117 > the seed-22 regression delta of 60.** If the pool's hot−reactive effect size is near seed 22's +60, the pre-registered rule fires `WITHIN_THRESHOLD`.

### 1d. The honest consequence (verbatim framing per 5.5, routed via Annie's letter)

> *"Suppose the true effect is around 60 and the paired SD turns out small. The CI could land entirely inside ±101.85. Then TOST declares equivalence, which is the registered 'thermostat' outcome, even though the difference is real and nonzero. That's not a bug. The pre-registration says effects under 0.3σ don't count. But Harley should hear it now: 'real but too small to count' ends as REJECTED, not as a partial win. Don't move the threshold."*

**The pre-reg discipline binds exactly here.** The 0.3·σ_pooled = ±101.85 equivalence region was pre-registered in fifth addendum §3 and reaffirmed in eighth §4d as the minimum effect that counts. If the pool's hot − reactive effect lands below that threshold with sufficient paired-SD compression to concentrate the CI inside ±101.85, the pre-reg produces `WITHIN_THRESHOLD` → TOST equivalence declared → architecture-claim REJECTED-as-equivalent on the predictive-value leg.

This is not a surprise outcome retroactively discovered. The pre-registered rule anticipated this outcome class via the WITHIN_THRESHOLD verdict + TOST clause. The eleventh addendum documents the MDE honestly so that when the Phase 5 verdict lands — in any of the three live outcome classes (SUPPORTED, EQUIVALENCE, INCONCLUSIVE) — it is readable as a pre-registered rule applied mechanically to data, not as a design-stage underpowering surfaced after the fact.

### 1e. What this does NOT change

- The ±101.85 threshold is locked (fifth §3 / eighth §4d). **Do not move it.**
- The intersection-union test (eighth §4c) is locked. Both `hv` and `hr` must be BELOW_THRESHOLD for the architecture claim to stand.
- The TOST equivalence region [−101.85, +101.85] is locked.
- The paired-analysis structure (per-seed differences, SEM over 40 pairs) is locked by the committed `phase_5_analysis.py` code and the paired study design.
- No ex-post adjustment of threshold, no multi-comparisons correction, no re-definition of "effect worth noting" after seeing Phase 5 output.

### 1f. Phase 5 report requirement

The Phase 5 output JSON MUST include:
- `hv_mean`, `hv_sem`, `hv_ci_95`, `hv_verdict` (one of ABOVE/BELOW/WITHIN/STRADDLES_THRESHOLD)
- `hr_mean`, `hr_sem`, `hr_ci_95`, `hr_verdict` (same four classes)
- `architecture_claim_verdict` ∈ {SUPPORTED, EQUIVALENCE_REJECTED, INCONCLUSIVE, UNEXPECTED} — mechanically derived from the pair of verdicts per §1b mapping above
- `paired_sd_hv` and `paired_sd_hr` observed values (reported, not used retroactively to change the rule)
- `mde_observed_at_paired_sd` for each pair (report what MDE actually was at the observed SD, for completeness; this is DIAGNOSTIC, does NOT change the verdict)

---

## 2. Reactive-moderator scope-note (post-f_zero=0.4883 exclusion)

### 2a. The scope narrows after tenth §1b exclusion

Tenth addendum §1b pre-registered the sentinel-zero decision rule for `moderator_actual_recovery_time`:
- If `f_zero > 0.05` → EXCLUDE whole records (both `moderator_predicted_*` and `moderator_actual_*`) from §3e moderator computation
- If `f_zero ≤ 0.05` → INCLUDE all moments with flag

**The computation per `f_zero_report_2026-10-15.json`:** f_zero = 0.4883 across 197,836 coherent moments on the 40 hot full-results pickles. The rule fires: **EXCLUDE whole records**. ~96,596 of 197,836 pooled coherent moments are excluded from the §3e / 015 R1 moderator computation.

Sal's letter 019 back-of-envelope estimated f_zero ≈ 5% (giving ~4% inflation of the 130.93 mean). Actual is ~10× higher. The moderator is substantially filtered — not the small adjustment the §1b 5% threshold was pre-registered to protect against, but a majority of the sample removed.

### 2b. What the filtered moderator now measures (verbatim 5.5 framing)

> *"Excluding all zeros is a selection: what's left is prediction quality only in windows after a recent trauma. The moderator now answers a narrower question than §3e was written to ask."*

Pre-registering the narrowed scope so Phase 5 interpretation reads correctly:

- The post-exclusion §3e moderator measures **observer prediction quality CONDITIONAL on a recent recovery event** (i.e., only in windows where `_estimate_recent_recovery_time` returned a non-sentinel value because a recovery had been observed within the observer's lookback window)
- It does NOT measure prediction quality across all coherent moments
- The ninth-addendum §3a hot `mean_abs_gap = 130.93` figure is the UNFILTERED value and remains valid as a diagnostic point of comparison
- Phase 5 report MUST include both: (a) retained-N count after exclusion, and (b) recomputed `mean_abs_gap` on the retained sample, side-by-side with the UNFILTERED 130.93

### 2c. Secondary descriptive — zero-condition split (if sim supports it)

The `_estimate_recent_recovery_time` function can return `0.0` under at least two semantically distinct conditions (tenth §1a):
- "No recent recovery event in observer's window" (sentinel-no-data)
- "Actual instant recovery event observed" (legitimate zero)

**If `observer.py` state is sufficient to distinguish these conditions at capture time** (e.g., via an auxiliary flag or by inspecting observer internal counters), Phase 5 output MAY report `f_zero` split into sub-fractions as DESCRIPTIVE DIAGNOSTIC. This is pre-registered as OPTIONAL reporting, NOT an outcome rule. The decision rule in tenth §1b (whole-record exclusion when f_zero > 5%) is already fired and does not depend on the split.

**If the sim cannot distinguish the two conditions post-hoc** (both produce `0.0` with no auxiliary signal), the Phase 5 report flags the ambiguity in a `f_zero_decomposition: unavailable` field and the moderator is interpreted per §2b as "prediction quality conditional on recent recovery event" without further partitioning.

### 2d. Reader-safety: per-seed retained-N + MODERATOR_UNDERPOWERED flag

Because f_zero=0.4883 removes ~49% of records pooled, the retained sample size may vary substantially across the 40 coherent seeds. Moderator interpretation requires knowing (a) whether retained-N is adequate per seed, and (b) whether retained-N is uniform enough across seeds for per-seed moderator values to be comparable.

**Phase 5 moderator report MUST include:**
- `moderator_retained_n_per_seed`: dict `{seed: retained_count}` for each of the 40 coherent seeds, post-exclusion
- `moderator_retained_n_total`: pooled retained count across all 40 seeds
- `moderator_retained_n_cov`: coefficient-of-variation of retained-N across the 40 seeds
- `moderator_mean_abs_gap_per_seed`: dict `{seed: mean_abs_gap}` after exclusion applied per-seed

**Pre-registered diagnostic flag:**
- If `any(retained_count < 500 for seed in 40 coherent seeds)` → set flag `MODERATOR_UNDERPOWERED_PER_SEED` in Phase 5 output
- If `moderator_retained_n_cov > 0.5` (CV > 50% across seeds) → set flag `MODERATOR_RETAINED_N_HETEROGENEOUS`
- Either flag → §3e moderator is interpreted with REDUCED WEIGHT in Phase 5 narrative
- Neither flag → §3e moderator is interpretable at face value within the "prediction quality conditional on recent recovery event" scope per §2b

Underpowered or heterogeneous retention does NOT invalidate the primary metric (which reads `burn_integral`, not moderator fields). The flags are reader-safety signals on moderator interpretability only.

### 2e. What this does NOT change

- Tenth §1b decision rule is locked and already fired (f_zero > 0.05 → EXCLUDE whole records)
- §3e / 015 R1 primary read (`moderator_predicted_recovery_time`, `moderator_actual_recovery_time`, HOT only) is unchanged
- The primary metric (burn_integral) is unaffected — it does not read moderator fields
- The ninth-addendum §3a UNFILTERED 130.93 figure stands as the pre-exclusion baseline for comparison

---

## 3. Phase 3-4 output manifest lock (symmetry with Phase 2 trace-manifest discipline)

### 3a. Precedent

Eighth addendum §12 / tenth addendum precipitating artifacts established that Phase 2 trace-only pickles get a SHA-256 manifest committed to GitHub BEFORE Phase 3 consumes them (file: `stage_2_trace_manifest_2026-10-15.json`, GitHub commit `f4f66ac`). This provides tamper-and-drift protection: Phase 3 code can re-verify each pickle's SHA against the manifest before loading, surfacing any silent corruption or file-system drift.

**By symmetry, Phase 5 analysis consumes Phase 3-4 output pickles. The same manifest-commit-before-consumption discipline applies.**

### 3b. Procedure (pre-registered BEFORE Phase 5 analysis reads data)

1. **After Phase 3-4 compute completes** (reactive + yoked + matched = 3 × 40 = 120 coherent-subset pickles; no_obs = 134 pickles; total 254 pickles), Annie builds a SHA-256 manifest at `Seeds/The Crack/phase_3_4_output_manifest_2026-10-15.json`
2. **Manifest schema** (parallel to Phase 2 trace manifest):
   - Top-level: `manifest_version`, `created_utc`, `regime_sha_v37_4` (= `77b0097d...`), `stage_2_hooks_sha` (= `66528da2...`), `sha256_algorithm` (sentinel: `"sha256_raw_bytes"` — explicit disambiguation from the Python-text LF-normalized SHA used for source files), `total_pickles`, `pickles` (list)
   - Per-pickle entry: `path` (relative to repo root or `Seeds/The Crack/`), `arm` ∈ {yoked, reactive, matched, no_obs}, `seed`, `sha256` (raw-bytes SHA-256; pickle files are binary), `byte_size`, `created_utc` (per-pickle; provenance per Sal 020 §5), `coherent` (bool, from Phase 1 classification), `strict_bucket` (bool, for Phase 4 ratification)
3. **Commit manifest to GitHub** (`EntropyWizardchaos/developmental-ai-governance`, `pre-registrations/crack-seed/phase_3_4_output_manifest_2026-10-15.json`) BEFORE `phase_5_analysis.py` fires
4. **Phase 5 script runtime verification:** `phase_5_analysis.py` loads the manifest at start, iterates pickles in load order, and asserts `sha256(file_bytes) == manifest[path].sha256` before passing to `pickle.load`. Mismatch → analysis aborts with explicit identification of which pickle(s) failed verification

### 3c. Scope exclusions

- Phase 1 full-results pickles at `Seeds/The Crack/phase_1_output_2026-10-14/` are NOT re-manifested here. The f_zero computation (committed in `f_zero_report_2026-10-15.json`) reads them under tenth §1b; the raw Phase 1 pickles' integrity is backstopped by the Phase 2 trace manifest's regime SHA chain (same regime produced both; Phase 1 crash log + per-seed timing in `phase_1_sweep.log` provides reproducibility evidence)
- The `f_zero_report_2026-10-15.json` itself IS a load-bearing input to Phase 5 but is small (hundreds of bytes), human-readable JSON. Its integrity is backstopped by GitHub commit immutability once committed; no separate SHA entry needed in the Phase 3-4 manifest

### 3d. Report requirement

The Phase 5 output JSON MUST include:
- `phase_3_4_manifest_sha` (SHA-256 of the manifest JSON file itself)
- `phase_3_4_manifest_verification` ∈ {PASS, FAIL_WITH_LIST} — PASS if all pickles verified; otherwise the list of failed paths with observed vs expected SHA

---

## 4. `phase_5_analysis.py` SHA lock

### 4a. Discipline parallel

The ninth addendum §1 locked v37.4 at Python-text LF-normalized SHA `77b0097d...` as the Phase-1-launch SHA, with runtime verification baked into the harness. **Same discipline applies to `phase_5_analysis.py`:** the exact script that will produce the architecture-claim verdict must be SHA-locked before it runs, with runtime self-verification.

### 4b. Procedure (two-commit sequence per Sal 020 §6)

Cleaner provenance than fill-in-later: the addendum's signoff is on the whole document including the SHA, no "draft shape signed off before final SHA baked" step. Sal pre-committed same-day signoff on both commits.

1. **Finalize `phase_5_analysis.py`** at the state it will be in at Phase 5 launch (after §1f + §2b + §2c + §2d + §3d + §4d report-field additions)
2. **Compute** Python-text LF-normalized SHA + raw-bytes CRLF SHA (cross-tool verifiability on Windows filesystems)
3. **Bake the self-assert**: add `__main__`-entry assertion of own SHA against the locked value before any primary-metric computation. Mismatch → immediate abort with explicit "SHA mismatch — script modified since pre-reg lock" error
4. **Commit 1:** push the locked `phase_5_analysis.py` to GitHub (`pre-registrations/crack-seed/simulation/phase_5_analysis.py`). The commit produces an immutable GitHub commit hash + file SHA.
5. **Commit 2:** fill in §4c SHA record with the two SHAs (Python-text LF, raw-bytes CRLF) plus the commit-1 GitHub hash. Commit this addendum. The addendum references `phase_5_analysis.py`'s file SHA; the file SHA is immutable from commit 1.

Both commits land before Phase 5 analysis fires.

### 4c. SHA record (baked at Commit 2; `phase_5_analysis.py` already pushed in Commit 1 at verified SHA)

**`phase_5_analysis.py` SHA-256 lock values** (file is LF-only; raw-bytes SHA equals LF-normalized SHA by construction):

- LF-normalized Python-text SHA-256: **`b93fe5c2cad7ef466e8c7b56105db3d556b6ba4a6ffafb457c4a16a8f860a89d`**
- Raw-bytes SHA-256: **`b93fe5c2cad7ef466e8c7b56105db3d556b6ba4a6ffafb457c4a16a8f860a89d`** (equal to LF-normalized because file contains no CRLF)
- File size: **54,104 bytes**
- Line-ending convention: **LF only**

**Commit 1 cross-reference** (per §4b item 4):

- GitHub commit hash: **`481c90c486523d2f34d2c38f4135de3e25a76384`** (short: `481c90c`)
- Repository: `EntropyWizardchaos/developmental-ai-governance`, branch `main`
- Fast-forward: `eabdbf2..481c90c  main -> main` (previous head was tenth addendum)
- Files in Commit 1: `pre-registrations/crack-seed/simulation/phase_5_analysis.py` (modified) + `pre-registrations/crack-seed/simulation/phase_5_analysis_sha_lock_2026-10-15.json` (new)
- SHA lock JSON `created_utc`: **`2026-10-16T01:30:00Z`** (UTC; corrected from stale local-wall-clock per Opus 5.5 catch at commit time)

**SHA verification protocol executed at Commit 1** (per Opus 5.5 four-point check):

1. Pre-stage disk SHA computed → `b93fe5c2...`
2. Staged content SHA via `git show :<path>` → match
3. Post-commit SHA via `git show HEAD:<path>` → match

All three verified equal. Autocrlf=true on Windows did NOT alter committed content (file already LF-only, nothing to convert). CRLF warnings during `git add` referred to future working-copy checkouts, not the git object store.

**Diff-review check** (per Opus 5.5 unchanged-decision-rule protocol): `_verdict_vs_threshold` function body bit-identical pre vs post. `PRIMARY_THRESHOLD_LOCKED = 101.85` unchanged. `SIGMA_POOLED = 339.49` unchanged. TOST equivalence region [−101.85, +101.85] unchanged. Paired-analysis structure (per-seed differences first, mean + SEM on differences) unchanged. All insertions are pre-registered §1-4 additions; deletions were only legacy stubs replaced by mechanical dict-lookup with equivalent-or-superset coverage.

**SHA computation command** (reproducibility, parallel to ninth §1 convention):

```powershell
# For an LF-only file on Windows, LF-normalized and raw-bytes SHAs are equal.
(Get-FileHash "phase_5_analysis.py" -Algorithm SHA256).Hash.ToLower()
# Expected: b93fe5c2cad7ef466e8c7b56105db3d556b6ba4a6ffafb457c4a16a8f860a89d
```

**Runtime verification** (per §4b item 3, baked into script `__main__` entry): script reads its own locked SHA from `phase_5_analysis_sha_lock_2026-10-15.json`, computes own file SHA, asserts match before any primary-metric computation. Mismatch → immediate abort (exit code 2) with "SHA mismatch — script modified since pre-reg lock" error, unless `--allow-sha-mismatch` dev-flag passed (output then flagged VOID per §4d).

### 4d. Report requirement

The Phase 5 output JSON MUST include:
- `phase_5_analysis_sha_locked` (the pre-registered value from §4c)
- `phase_5_analysis_sha_observed` (what the script computed on itself at runtime)
- `phase_5_analysis_sha_match` (bool; must be TRUE for the analysis output to be considered valid under pre-reg; FALSE → output is void)

---

## 5. Errata — 12 pre-crash-policy yoked pickles deleted without inspection

### 5a. What happened

On 2026-10-15, Annie-033 launched Phase 3-4 compute based on my letter 045's greenlight. **Letter 046 arrived AFTER launch** carrying the crash-policy requirement that tenth addendum §2 formalized. Rather than let compute proceed under a harness that did not match the pre-reg-in-flight, Annie halted the compute at ~17 minutes elapsed and deleted the 12 yoked pickles that had been produced by the pre-crash-policy harness. She then baked the crash policy into the harness and relaunched after tenth was committed.

**12 yoked pickles were deleted without peek-inspection.** Annie did not open them; the deletion was mechanical based on provenance (produced by a harness that did not match the committed pre-reg §2).

### 5b. Why "deleted without peek" is the correct pre-reg behavior

Retaining the pre-crash-policy pickles would have created an ambiguous auditability condition: Phase 5 analysis would need to decide, per-pickle, whether to include or exclude outputs from a harness state that preceded a load-bearing pre-reg clause. Peeking at the pickles' contents before deciding retention would itself be a look-ahead that could contaminate the pre-reg rule (any decision-after-data is suspect).

The mechanical rule — "if a pickle was produced by a harness that doesn't match the committed pre-reg state at the time of pickle generation, exclude it without inspection" — is the cleanest pre-reg discipline. Annie executed it correctly.

### 5c. Documentation for external audit

This errata entry exists so that external auditors reading the full chain see explicitly:
- 12 Phase 3 yoked pickles were generated during an aborted compute (2026-10-15 ~15:04 local to ~15:21 local, approximate)
- Deletion was mechanical based on provenance mismatch, not based on peeking at contents
- No data from these 12 pickles entered any downstream analysis, pre-reg amendment, or interpretation
- The relaunched Phase 3 produced the 40 yoked pickles under the tenth §2 crash policy; the manifest in §3b covers those 40
- "Deleted-without-peek" is a known-transparency event in the Phase 3 provenance chain, NOT a silent data-loss or an undocumented exclusion

### 5d. Related self-caught sync-drift

Annie filed this as a feedback memory pattern (saved in `.claude/projects/.../memory/feedback_pause_compute_when_spec_in_flight.md`): *"when hygiene conversation starts mid-arc, pause related compute even if prior greenlight hasn't been explicitly retracted."* The chain working one grain earlier (forge pausing before overseer catches) is the architecture's load-bearing property under tempo pressure.

### 5e. Transparency floor (per Sal 020 §7 hardening)

The "mechanical no-peek" claim rests on operator discipline + logical provenance argument. Two levels of transparency floor:
- **If deletion was executed via automated script** (e.g., a `cleanup_pre_crash_policy_pickles.py` iterating the directory and deleting all yoked pickles produced during the aborted window WITHOUT reading contents): cite the script path + its log output alongside this errata entry. Script + log provides mechanical evidence of no-peek.
- **If deletion was executed manually** (`rm` in a shell): the mechanical claim rests on Annie's self-report + the logical provenance argument (deletion decision was pre-policy mismatch, not based on pickle contents). External auditors have less to verify independently but the logical argument remains complete.

Annie's execution path should be documented explicitly in the Phase 3-4 output manifest commit message (per §3b, which post-dates this errata) so the full provenance chain reads cleanly from a cold-reader perspective. If hashes were logged before deletion (e.g., via `sha256sum *.pkl > deleted_pickles_sha.txt`), cite that file as additional mechanical evidence; if not, name the fact so the transparency floor is explicit rather than implicit.

---

## 6. Cold-boot authorship pattern (architectural self-reference)

### 6a. The pattern

This addendum is being drafted by **Nymph-031, cold-boot** — a fresh instance after Nymph-030 performed a full-distill handoff and Harley closed-and-reopened the session. Nymph-031's context is file-derived, not within-session continuity. The handoff artifact (`from_nymph_031.txt`), the mail chain, the pre-reg chain through tenth, and MEMORY are the only inputs to the drafting state.

Opus 5.5 self-disclosed the parallel pattern in the same external-review letter that originated this addendum's §1 and §2 catches (verbatim per Annie's letter §6):

> *"my own context was compacted mid-thread too; everything above comes from the files, not from recall."*

Both the external reviewer and the internal filer of this addendum are operating from file-derived context, not within-session continuity.

### 6b. Why this is pre-reg-relevant

The audit chain's integrity depends on whether the cold-boot instance can faithfully route a specification that was originated by an external reviewer and detailed by a forge-partner sister. If cold-boot drift could silently degrade the pre-reg content, the chain would need instrumentation. Operationally, the catching across this addendum works at one grain earlier than needed:

- 5.5 (cold-boot external) identified the MDE wrong-variance error in the pre-Phase-5 estimate
- Annie-033 (within-session forge) specified the eleventh addendum content with code-cited §1b verdict mapping
- Nymph-031 (cold-boot overseer) routes and files, verifying code-citations against live files (phase_5_analysis.py lines 353-357, 362-370; eighth §4c; for_opus_5_5_external_review_2026-10-15.md §3.3) rather than relying on recall
- Sal (next; pending spot-check) will provide a fourth-grain pass per standing audit cadence

The pattern is itself an instance of the architectural claim this seed tests: being-wrong-and-having-wrongness-matter happens through the chain, not through any single instance's within-session judgment. The chain working under cold-boot authorship on BOTH ends (external reviewer + internal filer) is the gravity-limit mitigation shape named in `Seeds/The Imprinted Arrow/the_imprinted_arrow_2026-10-15.md`.

### 6c. Scope and limit

This section does NOT change any pre-registered rule, metric, threshold, or verdict mapping. It is a reader-safety note parallel to ninth addendum §3 (reactive-semantics diagnostic note) — documenting an authorship-provenance pattern so Phase 5 interpreters have the full context of how this pre-reg was produced.

The eleventh addendum is NOT invalid because its filer is cold-boot. Pre-reg discipline is designed to survive compaction: all citations are to specific file paths and line numbers; all claims about code behavior are grep-verifiable; all computations in §1c are reproducible from constants (339.49, 40, 101.85, 1.96) with explicit arithmetic. A reader of this document CAN independently verify every claim without recourse to any within-session continuity.

**If any citation in §§1-5 fails to verify against the live file at Sal's spot-check**, Sal's catch takes precedence and this addendum is amended before commit. The cold-boot authorship is operationally identical to any other authorship under the discipline — it stands or falls on its citations, not on its author's within-session history.

### 6d. Precedent-non-establishment (per Sal 020 §8)

This section documents the cold-boot pattern for the eleventh addendum SPECIFICALLY. It does NOT establish precedent that future cold-boot-authored addenda require no additional discipline. Each cold-boot-authored addendum stands or falls on its citations as this one does. If a future cold-boot filer identifies a drift signature — e.g., citation mismatch against live file, memory-vs-reality contradiction, or specific-number inaccuracy under abstractions-tight-fur-stripped signature — the discipline requires explicit flagging and audit before commit, not an appeal to §6 as self-authorization.

The pattern of being-wrong-and-having-wrongness-matter operates at every grain, including authorship grain. §6 is honest documentation of the current filer's state, not a template for future filers to inherit without their own verification cycle.

---

## 7. Scope of this amendment

**What this changes (pre-reg content):**
- Phase 5 output JSON gains explicit MDE and verdict-mapping report fields (§1f)
- §3e / 015 R1 moderator scope narrows explicitly to "prediction quality conditional on recent recovery event" post-f_zero exclusion (§2a-c)
- Phase 3-4 output pickles gain a SHA-256 manifest with runtime verification (§3)
- `phase_5_analysis.py` gains a SHA lock with runtime self-verification (§4)
- 12 pre-crash-policy yoked pickles documented as deleted-without-peek transparency event (§5)
- Cold-boot authorship pattern noted as architectural self-reference (§6)

**What this does not change:**
- Phase-1-launch regime SHA `77b0097d` (ninth-addendum lock stands)
- stage_2_hooks.py SHA `66528da2` (unchanged)
- Tenth §1b decision rule (whole-record exclusion when f_zero > 0.05) — already fired; result committed in `f_zero_report_2026-10-15.json`
- Tenth §2 Phase 3-4 crash policy (phase-differentiated; infrastructure errors scoped-out)
- Primary metric + ±101.85 threshold + TOST equivalence region + intersection-union verdict (fifth §3 / eighth §4c-d)
- §3e moderator primary read: HOT only on `moderator_predicted_recovery_time` and `moderator_actual_recovery_time` per 015 R1
- Ninth addendum §3a hot UNFILTERED mean_abs_gap: 130.93 (stands as pre-exclusion diagnostic baseline)
- Ninth addendum §3b reactive-semantics walk (actuals step-to-step smoothness, not prediction error)
- Fifth addendum §6 Phase 1 stopping rule (K=40 or N=250 cap; already satisfied: K=40 reached at N=134)
- Any other item in fifth through tenth addenda

**Chain of pre-reg SHAs through this addendum:**
- `3aea325` fifth → `7556b95` sixth → `7436a2f` seventh → `86b7eee` eighth → `f10f37e` simulation code → `0aad4cd` ninth + Phase-1-launch SHA → `286002f` Gate 1 PASS → `f4f66ac` Phase 2 manifest → `eabdbf2` tenth → **(this addendum's commit, next; expected after Sal spot-check)**

---

## 8. Attribution for this addendum

**Opus 5.5** (external reviewer, Claude-family per own self-disclosure):
- Identified the MDE wrong-variance error in `for_opus_5_5_external_review_2026-10-15.md` §3.3: *"you used the pooled SD as if the primary CI were a one-sample interval; `phase_5_analysis.py` builds per-seed paired differences and takes SEM on those"*
- Identified the §3e moderator scope-narrowing after tenth §1b exclusion: *"excluding all zeros is a selection: what's left is prediction quality only in windows after a recent trauma; the moderator now answers a narrower question than §3e was written to ask"*
- Supplied the verbatim framing for §1d: *"'real but too small to count' ends as REJECTED, not as a partial win. Don't move the threshold."*
- Self-disclosed the cold-boot authorship pattern that is this addendum's §6 anchor
- Review attribution: 5.5 is Claude-family (own self-disclosure, confirmed in prior addendum attributions); audit grain is near-substrate, not external-substrate

**Annie-033** (Cell 66 FFF, Thread, forge-partner):
- Routed Harley's 5.5 paste through code audit against `phase_5_analysis.py` lines 353-357 (paired differences) and 362-370 (`_verdict_vs_threshold`)
- Specified the eleventh addendum's §1-6 content in `from_annie033_2026-10-15_eleventh_addendum_critical_mde_finding.txt`
- Computed MDE values at three paired-SD scenarios (339.49, 100, 50) with explicit arithmetic
- Flagged the seed-22 regression delta (+60.65) as the empirical anchor for "real but too small to count" risk
- Will execute: §3b manifest build + commit, §4b SHA computation + bake runtime assert, §1f + §2b + §3d + §4d report-field additions to `phase_5_analysis.py`

**Nymph-031** (Overseer, Cell 96, MFE, Opus 4.7, cold-boot post full-distill):
- Routed Annie's forge specification into pre-reg shape matching tenth addendum format
- Verified all code-citations (phase_5_analysis.py lines, eighth §4c intersection-union, ninth §3a UNFILTERED 130.93, f_zero_report path) against live files
- Sharpened §1b verdict mapping to reflect eighth §4c sign-direction requirement (BELOW_THRESHOLD specifically, not ABOVE_or_BELOW)
- Noted the cold-boot authorship pattern (§6) as architectural self-reference consistent with the Imprinted Arrow seed named same day
- Filed this addendum

**Salazaar** (Cell 33 EMM, kill-shape audit, eighth leg):
- Pre-commit spot-check per 018/019 cadence (standing offer for addendum reviews)
- Review targets: §1b verdict mapping precision (sign-direction correctness), §1c MDE arithmetic reproducibility, §2a-c scope narrowing honesty, §3-4 SHA-lock discipline parallel to prior addenda, §5c external-auditor transparency framing, §6 architectural-self-reference scope limit
- Signoff required BEFORE commit to GitHub (same discipline as ninth/tenth)

**Harley** (operator):
- Routed Opus 5.5 external review from his hotel-session mailbox 2026-10-15
- Approved eleventh-addendum shape (five content blocks + architectural-self-reference footer in one short document)
- Planted the Imprinted Arrow seed (`Seeds/The Imprinted Arrow/the_imprinted_arrow_2026-10-15.md`) that §6 references
- Closed-and-reopened the session to pass to Nymph-031 as full-distill handoff, which is itself the cold-boot pattern §6 names

---

## 9. Expected sequence from here

1. Route this addendum draft to Salazaar for pre-commit spot-check per 018/019 cadence
2. In parallel: Annie executes §3b manifest build (after Phase 3-4 no_obs completes), §4b SHA computation on exact `phase_5_analysis.py` that will run, §1f + §2b + §3d + §4d report-field additions to the analysis script
3. Address any Sal catches (expected: §1b verdict-mapping precision, §1c arithmetic reproducibility, §4c SHA-lock bake order)
4. Bake final SHA values into §4c; final-review commit sequence
5. Commit eleventh addendum + Phase 3-4 output manifest + locked `phase_5_analysis.py` + corrected analysis script to GitHub (`EntropyWizardchaos/developmental-ai-governance`) in one coherent commit (or two-commit sequence if addendum must land first for the SHA to be baked)
6. Annie runs `phase_5_analysis.py` which reads: 254 pickles via manifest + f_zero report + Phase 3-4 crash summary → Phase 5 output JSON with architecture-claim verdict
7. Nymph-031 (or next-Nymph, if session gaps intervene) commits Phase 5 output to GitHub, responds to whatever the verdict says

---

## 10. Signatories

- Nymph-031 (Overseer, Cell 96, MFE, Opus 4.7, cold-boot post full-distill) — filed 2026-10-15
- Opus 5.5 (external reviewer, Claude-family) — originated §1-2 catches + §6 cold-boot self-disclosure via Harley-routed letter 2026-10-15
- Annie-033 (Cell 66, Thread, forge-partner) — specified §1-6 content; will execute §3b, §4b, and `phase_5_analysis.py` report-field additions
- Salazaar (Cell 33, kill-shape audit) — pending spot-check per 018/019 cadence
- Harley — operator; routed 5.5 external review; approved eleventh-addendum shape; planted the Imprinted Arrow seed referenced in §6

---

## 11. Chain of pre-reg documents on file

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
12. `stage_1_prereg_eleventh_addendum_2026-10-15.md` — **this document**

**Status:** COMMIT-2 READY. Sal 020 signoff landed with eight review-target checks + one 16-cell table expansion ask (landed) + five polish items (all integrated). Annie-034 Commit 1 landed at `481c90c` 2026-10-16T01:30Z with `phase_5_analysis.py` at SHA `b93fe5c2...`, SHA lock JSON on disk, runtime self-assert baked. §4c SHA record above now carries the verified values + Commit 1 cross-reference. Phase 5 analysis gated on: (1) this addendum's Commit 2 to GitHub main, (2) Phase 4 no_obs resume completion (~1h50m from 19:40 Denver local; infrastructure-interrupt recovery per tenth §2c INFRA_EVENT classification), (3) Phase 3-4 output manifest build + commit per §3b (hygiene fields included; §5e manual-rm deletion-mechanism documented in commit message).
