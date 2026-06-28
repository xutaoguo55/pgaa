#!/usr/bin/env python3
"""Build the Communications Medicine manuscript as a Word document."""
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "MANUSCRIPT_CM.md"
DOCX_SRC = ROOT / "MANUSCRIPT_CM.docx"
UPLOAD_DIR = ROOT / "FILES_TO_UPLOAD_COMMUNICATIONS_MEDICINE"
DOCX_UPLOAD = UPLOAD_DIR / "MANUSCRIPT.docx"
TMP_MD = ROOT / ".MANUSCRIPT_CM_docx_input.md"

FIGURES = {
    "1": (
        "figures_png/figure_cm_entry.png",
        "PGAA as a clinically oriented single-cell perturbation mapping framework for heterogeneous disease-relevant transcriptional responses.",
    ),
    "2": (
        "figures_png/figure_1.png",
        "Disease-state marker recovery across five observational single-cell datasets. a, Recovery of known disease-relevant marker sets compared with housekeeping negative controls in the top-100 Wasserstein ranking. b, Positive-to-negative enrichment ratios, with 1x as the random expectation and 2x as a practical enrichment threshold. c, CLL comparator analysis showing that Wasserstein produced coherent BCR-axis rankings but was not uniformly superior to all conventional ranking baselines. These analyses assess marker recovery rather than causal perturbation effects.",
    ),
    "3": (
        "figures_png/figure_adamson_benchmark.png",
        "Independent validation on the Adamson 2016 UPR CRISPRi benchmark. a, Benchmark design and curated evaluation universe. b, Mean AUROC across five pre-specified UPR perturbations, with dots showing individual perturbations. c, Mean AUPRC compared with the random positive-rate baseline. d, Per-perturbation AUROC heatmap. Exact values for panel d are provided in Supplementary Table S5.",
    ),
    "4": (
        "figures_png/figure_norman_main_cm.png",
        "Norman 2019 CEBPE CRISPRa persistence ranking as a narrow use-case example. a, S2 persistence statistic versus permutation p-value across genes, with known CEBPE targets highlighted. b, ELANE rank comparison across SCEPTRE, PGAA S1 Wasserstein and PGAA S2 persistence. The panel illustrates ranking evidence only, not FDR-controlled discovery or complete CEBPE program recovery.",
    ),
    "5": (
        "figures_png/figure_3.png",
        "Perturbation-specific calibration defines guardrails for persistence-based ranking. a, Number of nominally significant genes and Storey pi0-hat across six Norman perturbations. b, CEBPE-target p-values across perturbation contexts. c, Leakage of CEBPE-target significance across non-CEBPE perturbations. S2 denotes the persistence statistic.",
    ),
}


def figure_block(number: str) -> str:
    path, caption = FIGURES[number]
    if not (ROOT / path).exists():
        raise FileNotFoundError(path)
    return f"\n\n![Figure {number}. {caption}]({path})\n\n"


def prepare_markdown(text: str) -> str:
    for number in FIGURES:
        text = re.sub(
            rf"\*\*\[Figure {number}\]\*\*",
            figure_block(number),
            text,
        )
    text = re.sub(r"\\textsuperscript\{([^}]*)\}", r"^\1^", text)
    text = text.replace(r"\*", "*")
    text = text.replace("π̂₀", "pi0-hat")
    text = text.replace("H₀", "H0")
    return text


def main() -> int:
    text = SRC.read_text(encoding="utf-8")
    prepared = prepare_markdown(text)
    TMP_MD.write_text(prepared, encoding="utf-8")
    try:
        subprocess.run(
            [
                "pandoc",
                str(TMP_MD),
                "-o",
                str(DOCX_SRC),
                "--from",
                "markdown",
                "--resource-path",
                str(ROOT),
                "--standalone",
            ],
            check=True,
            cwd=ROOT,
        )
    finally:
        TMP_MD.unlink(missing_ok=True)

    UPLOAD_DIR.mkdir(exist_ok=True)
    shutil.copy2(DOCX_SRC, DOCX_UPLOAD)
    print(f"Wrote {DOCX_SRC}")
    print(f"Wrote {DOCX_UPLOAD}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
