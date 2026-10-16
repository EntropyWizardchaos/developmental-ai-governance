"""Independent re-verification of the Phase 3-4 output manifest.

Why this exists:
  phase_5_analysis.py's `verify_phase_3_4_manifest()` function reports
  `phase_3_4_manifest_verification: FAIL_WITH_LIST` in the Phase 5 output
  JSON. Investigation (2026-10-16, immediately post-Phase-5-run) traced the
  cause: a path-resolution bug in verify_phase_3_4_manifest. The manifest's
  per-pickle `path` field is RELATIVE TO CRACK_DIR (e.g.,
  "phase_1_output_2026-10-14/phase_1_seed_200_arm_yoked.pkl"), but the function
  joins it with the `output_dir` parameter (which IS phase_1_output_2026-10-14).
  Result: it looks for files at
  phase_1_output_2026-10-14/phase_1_output_2026-10-14/..., which don't exist.
  All 254 entries get flagged FILE_NOT_FOUND.

  The LOADER-side per-pickle SHA check (performed before each pickle.load in
  _verified_loader) uses a candidate-list resolution strategy that includes
  "phase_1_output_2026-10-14/<filename>" and hits the manifest key correctly.
  The analysis therefore ran against SHA-verified pickles — any mismatch would
  have raised RuntimeError and halted the analysis. The analysis completed, so
  all 254 pickles passed loader-side SHA verification. The top-level
  `phase_3_4_manifest_verification` field in the output JSON is misleading;
  the actual integrity-critical check (loader-side) was clean.

  This script is the external auditable re-verification. It is NOT a modification
  of phase_5_analysis.py (SHA b93fe5c2... remains locked). It resolves manifest
  paths against CRACK_DIR as the manifest intends.

Output:
  verify_phase_3_4_manifest_INDEPENDENT_2026-10-16.log (same directory)

Pre-reg references:
  - Eleventh addendum §3b (Phase 3-4 output manifest spec) at Commit 2 `2d6497d`
  - Phase 3-4 output manifest at Commit 3 `724942d`
  - Phase 5 analysis script at Commit 1 `481c90c` (SHA b93fe5c2...)
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys
import time

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

CRACK_DIR = pathlib.Path(r"C:\Users\14132\iCloudDrive\Seeds\The Crack")
MANIFEST = CRACK_DIR / "phase_3_4_output_manifest_2026-10-15.json"
LOG_PATH = CRACK_DIR / "verify_phase_3_4_manifest_INDEPENDENT_2026-10-16.log"


def _sha256_raw(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    lines: list[str] = []

    def log(s: str) -> None:
        print(s, flush=True)
        lines.append(s)

    log("=" * 72)
    log("Independent re-verification of Phase 3-4 output manifest")
    log(f"Manifest: {MANIFEST}")
    log(f"Resolution: paths relative to CRACK_DIR = {CRACK_DIR}")
    log(f"Started: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}")
    log("=" * 72)

    with open(MANIFEST, encoding="utf-8") as f:
        m = json.load(f)

    pickles = m.get("pickles", [])
    log(f"Total pickles in manifest: {len(pickles)}")
    log(f"Expected: 254 (40 yoked + 40 reactive + 40 matched + 134 no_obs)")

    pass_count = 0
    fail_count = 0
    missing_count = 0
    mismatches: list[tuple[str, str, str]] = []
    missing: list[str] = []

    for p in pickles:
        rel_path = p["path"]
        expected = p["sha256"]
        full_path = CRACK_DIR / rel_path
        if not full_path.exists():
            missing_count += 1
            missing.append(rel_path)
            continue
        observed = _sha256_raw(full_path)
        if observed == expected:
            pass_count += 1
        else:
            fail_count += 1
            mismatches.append((rel_path, expected, observed))

    log("")
    log("-" * 72)
    log("RESULTS")
    log("-" * 72)
    log(f"SHA match (clean):     {pass_count}")
    log(f"SHA mismatch (corrupt): {fail_count}")
    log(f"File missing:          {missing_count}")

    if mismatches:
        log("\nMISMATCHES:")
        for path, exp, obs in mismatches:
            log(f"  {path}")
            log(f"    expected: {exp}")
            log(f"    observed: {obs}")

    if missing:
        log("\nMISSING:")
        for path in missing:
            log(f"  {path}")

    log("")
    log("=" * 72)
    if pass_count == len(pickles) and fail_count == 0 and missing_count == 0:
        log("VERDICT: INTEGRITY CLEAN. All 254 manifest entries match on-disk SHA.")
        log("")
        log("Note: phase_5_analysis.py top-level verify_phase_3_4_manifest()")
        log("field FAIL_WITH_LIST was due to a path-resolution bug (joining")
        log("output_dir with CRACK-DIR-relative manifest paths). The loader-side")
        log("per-pickle SHA check used a candidate-list strategy and resolved")
        log("correctly, so the actual Phase 5 compute ran against SHA-verified")
        log("inputs. The top-level field is misleading; this independent script")
        log("establishes the correct result for the audit record.")
        ret = 0
    else:
        log(f"VERDICT: INTEGRITY FAIL. See mismatches/missing above.")
        ret = 1
    log("=" * 72)

    LOG_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nLog written to {LOG_PATH}", flush=True)
    return ret


if __name__ == "__main__":
    sys.exit(main())
