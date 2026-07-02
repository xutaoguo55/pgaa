#!/usr/bin/env python3
"""Build the Communications AI & Computing supplementary PDF."""
from __future__ import annotations

import os
import subprocess
import sys


ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)


def run(cmd: list[str]) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True)
    output = result.stdout + result.stderr
    if result.returncode != 0:
        print(output)
        raise SystemExit(result.returncode)
    return output


def main() -> None:
    run([
        "pandoc",
        "SUPPLEMENTARY_CAIC.md",
        "-o",
        "SUPPLEMENTARY_CAIC.tex",
        "--from",
        "markdown",
        "--standalone",
    ])

    for _ in range(2):
        output = run(["Rscript", "-e", "tinytex::xelatex('SUPPLEMENTARY_CAIC.tex')"])
        if any(token in output for token in ["Emergency stop", "Fatal", "Undefined control sequence"]):
            print(output)
            raise SystemExit(1)

    text = run(["pdftotext", "SUPPLEMENTARY_CAIC.pdf", "-"])
    tables = []
    figures = []
    for line in text.splitlines():
        if line.startswith("Supplementary Table "):
            tables.append(line.split()[2].rstrip("."))
        elif line.startswith("Supplementary Figure "):
            figures.append(line.split()[2].rstrip("."))

    print(f"Supplementary figures: {', '.join(figures)}")
    print(f"Supplementary tables: {', '.join(tables)}")
    if tables != ["1", "2", "3", "4", "5", "6", "7"]:
        print("Unexpected supplementary table sequence")
        raise SystemExit(1)
    if figures != ["1", "2", "3", "4", "5", "6", "7"]:
        print("Unexpected supplementary figure sequence")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
