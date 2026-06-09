#!/usr/bin/env python3
"""Robust PDF builder: md → tex → insert figures+tables → compile."""
import subprocess, sys, os, re, pandas as pd

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Step 1: pandoc md → tex
subprocess.run(["pandoc", "MANUSCRIPT.md", "-o", "MANUSCRIPT.tex",
                "--from", "markdown", "--standalone"], check=True)

with open("MANUSCRIPT.tex") as f:
    tex = f.read()

# Step 2: Fix Unicode math
tex = tex.replace('π̂₀', r'$\hat{\pi}_0$')
tex = tex.replace('H₀', r'$H_0$')
tex = tex.replace('≥', r'$\ge$')

# Step 3: Add packages (float, graphicx, fancyhdr for page numbers)
if r'\usepackage{graphicx}' not in tex:
    marker = r'\usepackage{longtable,booktabs,array}'
    extra = (r'\usepackage{float}' + '\n' + r'\usepackage{graphicx}' + '\n'
             r'\usepackage{fancyhdr}' + '\n'
             r'\pagestyle{fancy}' + '\n'
             r'\fancyhf{}' + '\n'
             r'\fancyfoot[C]{\thepage}' + '\n'
             r'\renewcommand{\headrulewidth}{0pt}')
    tex = tex.replace(marker, extra + '\n' + marker)

# Step 4: Insert figures (use lambda to avoid \c escape in regex)
fig_map = {
    '1': ('figures_png/figure_1.png', 'Multi-dataset Wasserstein validation.'),
    '2': ('figures_png/figure_2.png', 'Norman 2019 CEBPE CRISPRa.'),
    '3': ('figures_png/figure_3.png', 'Calibration across six perturbations.'),
    '4': ('figures_png/figure_4.png', 'CLL 20k: Wasserstein and persistence.'),
    '5': ('figures_png/figure_adamson_benchmark.png', 'Independent validation on Adamson 2016 UPR CRISPRi benchmark.'),
    '6': ('figures_png/figure_5.png', 'Simulation ablation.'),
}
for num, (path, cap) in fig_map.items():
    fig_code = '\\begin{figure}[htbp]\n\\centering\n\\includegraphics[width=0.85\\textwidth]{' + path + '}\n\\caption{' + cap + '}\n\\end{figure}'
    pattern = r'\\textbf\{\{\[\}Figure ' + num + r'[^\}]*\{\]\}\}'
    tex = re.sub(pattern, lambda m, fc=fig_code: fc, tex, flags=re.DOTALL)

# Add clearpage before Discussion to flush all Results figures
tex = tex.replace(r'\subsection{4. Discussion}', r'\clearpage' + '\n' + r'\subsection{4. Discussion}')

# Add clearpage before Data and Code Availability (title wraps, use regex)
tex = re.sub(r'\\subsection\{Data and Code', r'\\clearpage\n\\subsection{Data and Code', tex)

# Step 5: Insert ELANE histogram after Figure 2
elane_code = r'\begin{figure}[H]\centering\includegraphics[width=0.95\textwidth]{figures_png/figure_elane_histogram.png}\caption{ELANE expression distribution in Norman 2019 CEBPE CRISPRa.}\end{figure}'
pos = tex.find('figure_2.png')
if pos > 0:
    end = tex.find(r'\end{figure}', pos)
    tex = tex[:end + len(r'\end{figure}')] + '\n' + elane_code + '\n' + tex[end + len(r'\end{figure}'):]

# Step 6: Build supplementary tables
def esc(s):
    return str(s).replace('_', r'\_').replace('%', r'\%').replace('&', r'\&')

tbl_text = ""

# Table S1
df = pd.read_csv("scripts/sensitivity_s2_bins.csv")
rows = []
for _, r in df.iterrows():
    rows.append('%d & %d & %.3f & %d & %.2f & %s \\\\' % (
        int(r["n_bins"]), int(r["elane_rank"]), float(r["elane_p"]),
        int(r["n_sig"]), float(r["pi0"]), r["known_hits"]))
hdr1 = r'\begin{table}[H]\centering\caption{Supplementary Table S1: Persistence test hyperparameter sensitivity (n\_perms=200).}' + '\n'
hdr1 += r'\begin{tabular}{|c|c|c|c|c|c|}\hline n\_bins & ELANE rank & p & n\_sig & pi0 & Hits \\\hline' + '\n'
tbl_text += hdr1 + '\n'.join(rows) + '\n' + r'\hline\end{tabular}\end{table}' + '\n\n'

# Table S2
df = pd.read_csv("scripts/table_sceptre_vs_pgaa.csv")
rows = []
for _, r in df.iterrows():
    m = esc(str(r["method"])[:30])
    rows.append('%s & %d & %.3f & %d & %.3f \\\\' % (m, int(r["elane_rank"]), float(r["elane_p"]), int(r["n_sig"]), float(r["auroc"])))
hdr2 = r'\begin{table}[H]\centering\caption{Supplementary Table S2: SCEPTRE vs PGAA on Norman 2019 CEBPE.}' + '\n'
hdr2 += r'\begin{tabular}{|l|c|c|c|c|}\hline Method & ELANE rank & p & n\_sig & AUROC \\\hline' + '\n'
tbl_text += hdr2 + '\n'.join(rows) + '\n' + r'\hline\end{tabular}\end{table}' + '\n\n'

# Table S5
df = pd.read_csv("scripts/adamson2016_full_results.csv")
rows = []
for _, r in df.iterrows():
    tgt = esc(str(r["target"])[:18])
    rows.append('%s & %.3f & %.3f & %.3f & %.3f & %.3f \\\\' % (tgt, float(r["auroc_s1"]), float(r["auroc_s2"]), float(r["auroc_wilcox"]), float(r["auroc_ttest"]), float(r["auroc_mast"])))
hdr9 = r'\begin{table}[H]\centering\caption{Supplementary Table S5: Adamson 2016 UPR CRISPRi benchmark (random AUPRC = 0.0065).}' + '\n'
hdr9 += r'\begin{tabular}{|l|c|c|c|c|c|}\hline Target & S1 & S2 & Wilcoxon & t-test & MAST \\\hline' + '\n'
tbl_text += hdr9 + '\n'.join(rows) + '\n' + r'\hline\end{tabular}\end{table}' + '\n\n'

# QQ plot
qq_code = r'\begin{figure}[H]\centering\includegraphics[width=0.8\textwidth]{figures_png/figure_s2_calibration_qq.png}\vspace{0.3cm}\par\textbf{Supplementary Figure S1: Calibration QQ plot and p-value histogram.}\end{figure}'
# BHLHE40 supplementary
bhlhe40_code = r'\begin{figure}[H]\centering\includegraphics[width=0.95\textwidth]{figures_png/figure_s2_bhlhe40.png}\vspace{0.3cm}\par\textbf{Supplementary Figure S2: Adamson 2016 BHLHE40 perturbation details.}\end{figure}'
# PGAA workflow supplementary schematic
workflow_code = r'\begin{figure}[H]\centering\includegraphics[width=0.95\textwidth]{figures_png/figure_pgaa_workflow.png}\vspace{0.3cm}\par\textbf{Supplementary Figure S3: PGAA distribution-aware Perturb-seq testing workflow.}\end{figure}'

# Step 7: Insert tables + supplementary figures before References (with clearpage to separate from main text)
refs_pos = tex.find(r'\subsection{References}')
if refs_pos > 0:
    tex = tex[:refs_pos] + r'\clearpage' + '\n' + tbl_text + qq_code + '\n' + bhlhe40_code + '\n' + workflow_code + '\n' + tex[refs_pos:]

# Remove placeholder text
tex = tex.replace(r'\textbf{{[}Supplementary Table S1{]}}', '')

# Step 8: Write and compile
with open("MANUSCRIPT.tex", "w") as f:
    f.write(tex)

# Verify
figs_n = tex.count('includegraphics')
tabs_n = tex.count('begin{table}')
print("Figures: {} Tables: {}".format(figs_n, tabs_n))

if figs_n < 10:
    print("WARNING: less than 10 figures!")
    sys.exit(1)

# Step 9: Compile with xelatex (twice for TOC)
for i in range(2):
    result = subprocess.run(
        ["Rscript", "-e", "tinytex::xelatex('MANUSCRIPT.tex')"],
        capture_output=True, text=True
    )
    if "Emergency stop" in result.stdout or "Fatal" in result.stdout:
        print("LaTeX ERROR on pass {}".format(i+1))
        # Find error
        for line in result.stdout.split('\n'):
            if '!' in line or 'Error' in line:
                print("  " + line.strip()[:120])
    else:
        print("Pass {}: OK".format(i+1))

# Check PDF
pdf_size = os.path.getsize("MANUSCRIPT.pdf") / 1024
print("PDF: {:.0f} KB".format(pdf_size))
if pdf_size < 500:
    print("WARNING: PDF too small — figures may be missing")
else:
    print("SUCCESS — PDF ready")
