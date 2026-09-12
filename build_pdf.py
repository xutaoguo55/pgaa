#!/usr/bin/env python3
"""Robust PDF builder: md -> tex -> insert figures -> compile."""
import subprocess, sys, os, re

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
    '1': ('figures_png/figure1_recharter_decision_object.png', 'PGAA as an executable claim-state compiler.'),
    '2': ('figures_png/figure2_claim_promotion_benchmark.png', 'False-promotion benchmark and reporting-baseline ablation.'),
    '3': ('figures_png/figure_1.png', 'Empirical perturbation-transcriptomic anchors for upstream score modules.'),
    '4': ('figures_png/atm_hdac_branch_vulnerability_map.png', 'EGFR-resistance branch-vulnerability demonstration with ATM as the primary bounded hypothesis.'),
    '5': ('figures_png/figure5_reproducibility_source_audit.png', 'Reproducibility and source-data audit states supporting the claim-state compiler.'),
}
for num, (path, cap) in fig_map.items():
    placement = 'htbp'
    width = '0.85\\textwidth'
    prefix = ''
    suffix = ''
    if num in {'4', '5'}:
        placement = 'p'
        width = '1.0\\textwidth'
        prefix = '\\clearpage\n'
        suffix = '\n\\clearpage'
    fig_code = prefix + '\\begin{figure}[' + placement + ']\n\\centering\n\\includegraphics[width=' + width + ']{' + path + '}\n\\caption{' + cap + '}\n\\end{figure}' + suffix
    pattern = r'\\textbf\{\{\[\}Figure ' + num + r'[^\}]*\{\]\}\}'
    tex = re.sub(pattern, lambda m, fc=fig_code: fc, tex, flags=re.DOTALL)

# Add clearpage before Discussion to flush all Results figures
tex = tex.replace(r'\subsection{4. Discussion}', r'\clearpage' + '\n' + r'\subsection{4. Discussion}')

# Add clearpage before Data and Code Availability (title wraps, use regex)
tex = re.sub(r'\\subsection\{Data and Code', r'\\clearpage\n\\subsection{Data and Code', tex)

# Step 5: Remove placeholder text. Supplementary figures and tables are built
# separately in SUPPLEMENTARY.pdf rather than inserted into the main manuscript.
tex = tex.replace(r'\textbf{{[}Supplementary Table S1{]}}', '')

# Step 7: Write and compile
with open("MANUSCRIPT.tex", "w") as f:
    f.write(tex)

# Verify
figs_n = tex.count('includegraphics')
tabs_n = tex.count('begin{table}')
print("Figures: {} Tables: {}".format(figs_n, tabs_n))

if figs_n < 5:
    print("WARNING: less than 5 main figures!")
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
