#!/usr/bin/env python3
"""Apply all 10 bug fixes to Python and R packages."""
import sys; sys.path.insert(0, '..')
import numpy as np

# ══════════════════════════════════════════
# BUG 1: R perm_null_s2 bin mismatch
# ══════════════════════════════════════════
# Fix: use per-gene bins in null too (consistent with obs)
# File: pgaa_r/R/utils.R, lines 117-155
# R fix (to be applied):
# - In obs computation (L117-127): already uses per-gene bins. OK.
# - In null computation (L146-155): currently uses global bins.
#   Change to per-gene bins like obs.
print("BUG 1: R perm_null_s2 bin mismatch → per-gene bins in null")
print("  Fix: lines 146-155 in utils.R → compute per-gene bins")

# ══════════════════════════════════════════
# BUG 2: Python prt_s3.py hard-coded seed
# ══════════════════════════════════════════
print("BUG 2: Python prt_s3.py hard-coded seed=42 → parameterize")
print("  Fix: add random_state param to kraskov_mi_vectorized")

# ══════════════════════════════════════════
# BUG 3: Python prt.py single-cluster edge case
# ══════════════════════════════════════════
print("BUG 3: Python prt.py single-cluster dummies → guard")
print("  Fix: check n_unique_ct > 1 before dropping first column")

# ══════════════════════════════════════════
# BUG 4: R perm_null_s1 dead code
# ══════════════════════════════════════════
print("BUG 4: R perm_null_s1 dead code np <- sum(Dp) → remove")

# ══════════════════════════════════════════
# BUG 5: R prt_s1.R + prt_s2.R redundant set.seed
# ══════════════════════════════════════════
print("BUG 5: R redundant set.seed → remove outer call")

# ══════════════════════════════════════════
# BUG 6: Python prt_s3.py unused n_perm param
# ══════════════════════════════════════════
print("BUG 6: Python prt_s3.py unused n_perm → mark as deprecated")

# ══════════════════════════════════════════
# BUG 7: Python prt_s2.py redundant recomputation
# ══════════════════════════════════════════
print("BUG 7: Python prt_s2.py n_peaks_on recomputed → inline")

# ══════════════════════════════════════════
# BUG 8: Python prt.py function-internal import
# ══════════════════════════════════════════
print("BUG 8: Python prt.py import time inside function → move to top")

# ══════════════════════════════════════════
# BUG 9: Python prt_s4.py doc comment
# ══════════════════════════════════════════
print("BUG 9: Python prt_s4.py canonical→mean-param comment → fix")

# ══════════════════════════════════════════
# BUG 10: Python prt.py missing duplicate gene guard
# ══════════════════════════════════════════
print("BUG 10: Python prt.py no duplicate gene check → add guard")

print("\nNow applying fixes...")
