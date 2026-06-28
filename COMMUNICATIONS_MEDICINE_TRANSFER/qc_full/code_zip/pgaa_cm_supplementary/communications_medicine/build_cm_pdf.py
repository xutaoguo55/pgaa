#!/usr/bin/env python3
"""Robust PDF builder: md -> tex -> insert figures -> compile."""
import subprocess, sys, os, re

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Step 1: pandoc md → tex
subprocess.run(["pandoc", "MANUSCRIPT_CM.md", "-o", "MANUSCRIPT_CM.tex",
                "--from", "markdown", "--standalone"], check=True)

with open("MANUSCRIPT_CM.tex") as f:
    tex = f.read()

# Step 2: Fix Unicode math
tex = tex.replace('π̂₀', r'$\hat{\pi}_0$')
tex = tex.replace('H₀', r'$H_0$')
tex = tex.replace('≥', r'$\ge$')

# Step 3: Add packages (geometry, float, graphicx, fancyhdr, lineno).
# Insert before \begin{document}; relying on a longtable package anchor is
# fragile because the main manuscript may contain no formal tables.
required_preamble = '\n'.join([
    r'\usepackage[margin=1in]{geometry}',
    r'\usepackage{float}',
    r'\usepackage{graphicx}',
    r'\usepackage{lineno}',
    r'\usepackage{fancyhdr}',
    r'\pagestyle{fancy}',
    r'\fancyhf{}',
    r'\fancyfoot[C]{\thepage}',
    r'\renewcommand{\headrulewidth}{0pt}',
    r'\setlength\linenumbersep{8pt}',
    r'\renewcommand\linenumberfont{\normalfont\tiny\sffamily}',
    r'\linenumbers',
])
if r'\usepackage{graphicx}' not in tex:
    tex = tex.replace(r'\begin{document}', required_preamble + '\n\n' + r'\begin{document}')

# Step 4: Insert figures (use lambda to avoid \c escape in regex)
fig_map = {
    '1': ('figures_png/figure_cm_entry.png', 'PGAA as a clinically oriented single-cell perturbation mapping framework for heterogeneous disease-relevant transcriptional responses.'),
    '2': ('figures_png/figure_1.png', 'Disease-state marker recovery across five observational single-cell datasets. (A) Recovery of known disease-relevant marker sets compared with housekeeping negative controls in the top-100 Wasserstein ranking. (B) Positive-to-negative enrichment ratios, with 1x as the random expectation and 2x as a practical enrichment threshold. (C) CLL comparator analysis showing that Wasserstein produced coherent BCR-axis rankings but was not uniformly superior to all conventional ranking baselines. These analyses assess marker recovery rather than causal perturbation effects.'),
    '3': ('figures_png/figure_adamson_benchmark.png', 'Independent validation on the Adamson 2016 UPR CRISPRi benchmark. (A) Benchmark design and curated evaluation universe. (B) Mean AUROC across five pre-specified UPR perturbations, with dots showing individual perturbations. (C) Mean AUPRC compared with the random positive-rate baseline. (D) Per-perturbation AUROC heatmap. Exact values for panel D are provided in Supplementary Table S5.'),
    '4': ('figures_png/figure_norman_main_cm.png', 'Norman 2019 CEBPE CRISPRa persistence ranking as a narrow use-case example. (A) S2 persistence statistic versus permutation p-value across genes, with known CEBPE targets highlighted. (B) ELANE rank comparison across SCEPTRE, PGAA S1 Wasserstein and PGAA S2 persistence. The panel illustrates ranking evidence only, not FDR-controlled discovery or complete CEBPE program recovery.'),
    '5': ('figures_png/figure_3.png', 'Perturbation-specific calibration defines guardrails for persistence-based ranking. (A) Number of nominally significant genes and Storey pi0-hat across six Norman perturbations. (B) CEBPE-target p-values across perturbation contexts. (C) Leakage of CEBPE-target significance across non-CEBPE perturbations.'),
}
for num, (path, cap) in fig_map.items():
    placement = 'htbp'
    width = '0.85\\textwidth'
    prefix = ''
    suffix = ''
    if num == '3':
        width = '0.92\\textwidth'
    elif num in {'1', '2', '5'}:
        width = '1.0\\textwidth'
    fig_code = prefix + '\\begin{figure}[' + placement + ']\n\\centering\n\\includegraphics[width=' + width + ']{' + path + '}\n\\caption{' + cap + '}\n\\end{figure}' + suffix
    pattern = r'\\textbf\{\{\[\}Figure ' + num + r'[^\}]*\{\]\}\}'
    tex = re.sub(pattern, lambda m, fc=fig_code: fc, tex, flags=re.DOTALL)

# Add clearpage before Discussion to flush all Results figures.
tex = tex.replace(r'\subsection{3. Discussion}', r'\clearpage' + '\n' + r'\subsection{3. Discussion}')

# Add clearpage before availability sections.
tex = re.sub(r'\\subsection\{Data availability\}', r'\\clearpage\n\\subsection{Data availability}', tex)

# Step 5: Remove the in-text cross-reference marker. Supplementary figures and
# tables are built separately in SUPPLEMENTARY.pdf.
tex = tex.replace(r'\textbf{{[}Supplementary Table S1{]}}', '')

# Step 7: Write and compile
with open("MANUSCRIPT_CM.tex", "w") as f:
    f.write(tex)

# Verify
figs_n = tex.count('includegraphics')
tabs_n = tex.count('begin{table}')
print("Figures: {} Tables: {}".format(figs_n, tabs_n))

if figs_n != 5:
    print("WARNING: expected exactly 5 main figures!")
    sys.exit(1)

# Step 9: Compile with xelatex (twice for TOC)
for i in range(2):
    result = subprocess.run(
        ["Rscript", "-e", "tinytex::xelatex('MANUSCRIPT_CM.tex')"],
        capture_output=True, text=True
    )
    combined_log = result.stdout + "\n" + result.stderr
    if result.returncode != 0 or "Emergency stop" in combined_log or "Fatal" in combined_log or "Undefined control sequence" in combined_log:
        print("LaTeX ERROR on pass {}".format(i+1))
        # Find error
        for line in combined_log.split('\n'):
            if '!' in line or 'Error' in line:
                print("  " + line.strip()[:120])
        sys.exit(1)
    else:
        print("Pass {}: OK".format(i+1))

# Check PDF
pdf_size = os.path.getsize("MANUSCRIPT_CM.pdf") / 1024
print("PDF: {:.0f} KB".format(pdf_size))
if pdf_size < 500:
    print("WARNING: PDF too small — figures may be missing")
else:
    print("SUCCESS — PDF ready")
