#!/usr/bin/env python3
"""Robust CAIC PDF builder: md -> tex -> insert figures -> compile."""
import subprocess, sys, os, re

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Step 1: pandoc md -> tex
subprocess.run(["pandoc", "MANUSCRIPT_CAIC.md", "-o", "MANUSCRIPT_CAIC.tex",
                "--from", "markdown", "--standalone"], check=True)

with open("MANUSCRIPT_CAIC.tex") as f:
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
    r'\usepackage{needspace}',
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
    '1': ('figures_png/figure_caic_entry.png', "PGAA framework for distribution-aware single-cell perturbation ranking. a, Uniform shifts are captured by mean-based tests, whereas subset-confined responder states can show weak average shifts. b, PGAA residualizes cell-state and library-size effects, scores genes with PGAA-W for full-distribution shifts and PGAA-H for histogram-shape changes, calibrates rankings by within-cluster permutation and Storey's upper-tail diagnostic, and returns ranked response genes. PGAA-W is the primary starting score; PGAA-H is a secondary diagnostic and should be interpreted only when calibration is acceptable."),
    '2': ('figures_png/figure_adamson_benchmark.png', 'Independent validation on the Adamson 2016 UPR CRISPRi benchmark. a, Benchmark design and curated evaluation universe. b, Mean AUROC across five pre-specified UPR perturbations, with dots showing individual perturbations. c, Mean AUPRC compared with the random positive-rate baseline. d, Per-perturbation AUROC heatmap. Exact values for panel d are provided in Supplementary Table 2.'),
    '3': ('figures_png/figure_norman_main_caic.png', 'Norman 2019 CEBPE CRISPRa PGAA-H ranking as a narrow use-case example. a, PGAA-H histogram-shape diagnostic versus permutation p-value across genes, with known CEBPE targets highlighted. b, ELANE rank comparison across SCEPTRE, PGAA-W Wasserstein and PGAA-H histogram-shape ranking. The panel illustrates ranking evidence only, not FDR-controlled discovery or complete CEBPE program recovery.'),
    '4': ('figures_png/figure_3.png', 'Perturbation-specific calibration defines guardrails for PGAA-H histogram-shape ranking. a, Number of nominally significant genes and uncapped Storey upper-tail ratio across six Norman perturbations. b, CEBPE-target p-values across perturbation contexts. c, Leakage of CEBPE-target significance across non-CEBPE perturbations. PGAA-H denotes the histogram-shape diagnostic.'),
    '5': ('figures_png/figure_1.png', 'External marker-recovery stress checks across five observational single-cell datasets. a, Recovery of known marker sets compared with housekeeping negative controls in the top-100 Wasserstein ranking. b, Positive-to-negative enrichment ratios, with 1x as the random expectation and 2x as a practical enrichment threshold. c, CLL comparator analysis showing that Wasserstein produced coherent BCR-axis rankings but was not uniformly superior to all conventional ranking baselines. These analyses assess marker recovery rather than causal perturbation effects.'),
}
for num, (path, cap) in fig_map.items():
    placement = 'H'
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

# Keep main tables visually intact without hard page breaks. If the remaining
# page space is too small, LaTeX moves the table block naturally.
table_space = {
    'Table 1. Evidence levels across PGAA evaluations.': r'\Needspace{0.32\textheight}',
    'Table 2. Adamson 2016 UPR CRISPRi benchmark summary.': r'\Needspace{0.55\textheight}',
    'Table 3. Norman 2019 CEBPE ranking and calibration summary.': r'\Needspace{0.48\textheight}',
}
for caption, guard in table_space.items():
    tex = tex.replace(caption, guard + '\n\n' + caption)

# Step 5: Remove the in-text cross-reference marker. Supplementary figures and
# tables are built separately in SUPPLEMENTARY.pdf.
tex = tex.replace(r'\textbf{{[}Supplementary Table 1{]}}', '')

# Step 7: Write and compile
with open("MANUSCRIPT_CAIC.tex", "w") as f:
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
        ["Rscript", "-e", "tinytex::xelatex('MANUSCRIPT_CAIC.tex')"],
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
pdf_size = os.path.getsize("MANUSCRIPT_CAIC.pdf") / 1024
print("PDF: {:.0f} KB".format(pdf_size))
if pdf_size < 500:
    print("WARNING: PDF too small — figures may be missing")
else:
    print("SUCCESS — PDF ready")
