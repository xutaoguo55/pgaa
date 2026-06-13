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

# Step 3: Add packages (geometry, float, graphicx, fancyhdr for page numbers)
if r'\usepackage{graphicx}' not in tex:
    marker = r'\usepackage{longtable,booktabs,array}'
    extra = (r'\usepackage[margin=1in]{geometry}' + '\n'
             r'\usepackage{float}' + '\n' + r'\usepackage{graphicx}' + '\n'
             r'\usepackage{fancyhdr}' + '\n'
             r'\pagestyle{fancy}' + '\n'
             r'\fancyhf{}' + '\n'
             r'\fancyfoot[C]{\thepage}' + '\n'
             r'\renewcommand{\headrulewidth}{0pt}')
    tex = tex.replace(marker, extra + '\n' + marker)

# Step 4: Insert figures (use lambda to avoid \c escape in regex)
fig_map = {
    '1': ('figures_png/figure_cm_entry.png', 'PGAA as a clinically oriented single-cell perturbation mapping framework for heterogeneous disease-relevant transcriptional responses.'),
    '2': ('figures_png/figure_norman_main_cm.png', 'Norman 2019 CEBPE CRISPRa persistence ranking.'),
    '3': ('figures_png/figure_3.png', 'Calibration across six perturbations.'),
    '4': ('figures_png/figure_adamson_benchmark.png', 'Independent validation on Adamson 2016 UPR CRISPRi benchmark. Exact per-perturbation values for panel D are provided in Supplementary Table S5.'),
    '5': ('figures_png/figure_5.png', 'Simulation ablation.'),
}
for num, (path, cap) in fig_map.items():
    placement = 'htbp'
    width = '0.85\\textwidth'
    prefix = ''
    suffix = ''
    if num == '4':
        placement = 'p'
        width = '1.0\\textwidth'
        prefix = '\\clearpage\n'
        suffix = '\n\\clearpage'
    elif num in {'1', '2', '3', '5'}:
        width = '1.0\\textwidth'
    fig_code = prefix + '\\begin{figure}[' + placement + ']\n\\centering\n\\includegraphics[width=' + width + ']{' + path + '}\n\\caption{' + cap + '}\n\\end{figure}' + suffix
    pattern = r'\\textbf\{\{\[\}Figure ' + num + r'[^\}]*\{\]\}\}'
    tex = re.sub(pattern, lambda m, fc=fig_code: fc, tex, flags=re.DOTALL)

# Add clearpage before Discussion to flush all Results figures
tex = tex.replace(r'\subsection{4. Discussion}', r'\clearpage' + '\n' + r'\subsection{4. Discussion}')

# Add clearpage before availability sections.
tex = re.sub(r'\\subsection\{Data availability\}', r'\\clearpage\n\\subsection{Data availability}', tex)

# Step 5: Remove placeholder text. Supplementary figures and tables are built
# separately in SUPPLEMENTARY.pdf rather than inserted into the main manuscript.
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
    if "Emergency stop" in result.stdout or "Fatal" in result.stdout:
        print("LaTeX ERROR on pass {}".format(i+1))
        # Find error
        for line in result.stdout.split('\n'):
            if '!' in line or 'Error' in line:
                print("  " + line.strip()[:120])
    else:
        print("Pass {}: OK".format(i+1))

# Check PDF
pdf_size = os.path.getsize("MANUSCRIPT_CM.pdf") / 1024
print("PDF: {:.0f} KB".format(pdf_size))
if pdf_size < 500:
    print("WARNING: PDF too small — figures may be missing")
else:
    print("SUCCESS — PDF ready")
