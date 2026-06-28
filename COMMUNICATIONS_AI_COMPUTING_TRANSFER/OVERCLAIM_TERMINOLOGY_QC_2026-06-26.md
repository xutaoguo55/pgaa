# Overclaim and Terminology QC, 2026-06-26

Scope: PGAA Communications AI & Computing transfer manuscript, supplementary material, and submitted supplementary code archive.

## Main Corrections

- Replaced over-specific or overclaiming S2 language with `S2 histogram statistic` or `persistence-inspired histogram-shape statistic`.
- Stated that S2 is a ranking and diagnostic statistic, not a genome-wide discovery test.
- Replaced causal-style language in observational sections with marker-recovery and calibration-context language.
- Replaced `default ranking score` with `starting ranking score` or `starting distributional score`.
- Replaced `stress test` with `stress check` where the phrase could imply validation rather than a bounded external check.
- Removed software-comment overclaims in exploratory modules, including theorem-style statements, causal-effect wording, and innovation/first-to-combine claims.

## Remaining Intentional Boundary Language

- Negative statements such as `not causal`, `not clinical biomarker evidence`, and `not formal discovery` are retained where needed because they reduce, rather than increase, claim risk.
- TDA references remain in the bibliography because S2 uses one-dimensional topological-persistence ideas, but the manuscript and code no longer present S2 as a standard bottleneck-distance or persistence-landscape test.

## Verification

- Python syntax check passed for modified Python modules.
- R parse check passed for modified R files.
- High-risk positive overclaim scan returned no hits for `outperform`, `gold standard`, `causal inference`, `causal effect`, `clinical biomarker claim`, `validated inference`, `Theorem`, `Innovation`, `first to combine`, `valid Type I`, or `correct Type I`.
- `build_caic_docx.py`, `build_caic_pdf.py`, `build_caic_supplementary_pdf.py`, `build_caic_supplementary_zip.py`, and `build_caic_journal_upload_packet.py` were rerun.
- `verify_caic_transfer_ready.py`, `final_upload_strict_audit_2026_06_25.py`, and `deep_current_submission_audit_2026_06_25.py` passed after rebuild.
- Final journal-upload zip and supplementary-code zip passed `unzip -t`.
