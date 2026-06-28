#!/usr/bin/env python3
"""Build the Communications AI & Computing manuscript as a Word document."""
from __future__ import annotations

from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
import xml.etree.ElementTree as ET

from docx import Document


ROOT = Path(__file__).resolve().parent
SRC = ROOT / "MANUSCRIPT_CAIC.md"
DOCX_SRC = ROOT / "MANUSCRIPT_CAIC.docx"
UPLOAD_DIR = ROOT / "FILES_TO_UPLOAD_COMMUNICATIONS_AI_COMPUTING"
DOCX_UPLOAD = UPLOAD_DIR / "MANUSCRIPT.docx"
TMP_MD = ROOT / ".MANUSCRIPT_CAIC_docx_input.md"
WORD_NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
    "ct": "http://schemas.openxmlformats.org/package/2006/content-types",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "pr": "http://schemas.openxmlformats.org/package/2006/relationships",
}

OOXML_NAMESPACES = {
    "": "http://schemas.openxmlformats.org/package/2006/content-types",
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "pic": "http://schemas.openxmlformats.org/drawingml/2006/picture",
    "mc": "http://schemas.openxmlformats.org/markup-compatibility/2006",
    "w14": "http://schemas.microsoft.com/office/word/2010/wordml",
    "w15": "http://schemas.microsoft.com/office/word/2012/wordml",
}
for prefix, uri in OOXML_NAMESPACES.items():
    ET.register_namespace(prefix, uri)

FIGURES = {
    "1": (
        "figures_png/figure_caic_entry.png",
        "PGAA framework for distribution-aware single-cell perturbation ranking. a, Uniform shifts are captured by mean-based tests, whereas subset-confined responder states can show weak average shifts. b, PGAA residualizes cell-state and library-size effects, scores genes with PGAA-W Wasserstein for full-distribution shifts and PGAA-H histogram-shape changes, calibrates rankings by within-cluster permutation and Storey's upper-tail diagnostic, and returns ranked response genes. The Wasserstein statistic is the primary starting score; PGAA-H is a secondary diagnostic and should be interpreted only when calibration is acceptable.",
    ),
    "2": (
        "figures_png/figure_adamson_benchmark.png",
        "Independent validation on the Adamson 2016 UPR CRISPRi benchmark. a, Benchmark design and curated evaluation universe. b, Mean AUROC across five pre-specified UPR perturbations, with dots showing individual perturbations. c, Mean AUPRC compared with the random positive-rate baseline. d, Per-perturbation AUROC heatmap. Exact values for panel d are provided in Supplementary Table 2.",
    ),
    "3": (
        "figures_png/figure_norman_main_caic.png",
        "Norman 2019 CEBPE CRISPRa PGAA-H ranking as a narrow use-case example. a, PGAA-H histogram-shape diagnostic versus permutation p-value across genes, with known CEBPE targets highlighted. b, ELANE rank comparison across SCEPTRE, PGAA-W Wasserstein and PGAA-H histogram-shape ranking. The panel illustrates ranking evidence only, not FDR-controlled discovery or complete CEBPE program recovery.",
    ),
    "4": (
        "figures_png/figure_3.png",
        "Perturbation-specific calibration defines guardrails for PGAA-H histogram-shape ranking. a, Number of nominally significant genes and uncapped Storey upper-tail ratio across six Norman perturbations. b, CEBPE-target p-values across perturbation contexts. c, Leakage of CEBPE-target significance across non-CEBPE perturbations. PGAA-H denotes the histogram-shape diagnostic.",
    ),
    "5": (
        "figures_png/figure_1.png",
        "External marker-recovery stress checks across five observational single-cell datasets. a, Recovery of known marker sets compared with housekeeping negative controls in the top-100 Wasserstein ranking. b, Positive-to-negative enrichment ratios, with 1x as the random expectation and 2x as a practical enrichment threshold. c, CLL comparator analysis showing that Wasserstein produced coherent BCR-axis rankings but was not uniformly superior to all conventional ranking baselines. These analyses assess marker recovery rather than causal perturbation effects.",
    ),
}


def figure_block(number: str) -> str:
    path, caption = FIGURES[number]
    if not (ROOT / path).exists():
        raise FileNotFoundError(path)
    return f"\n\n![Figure {number}. {caption}]({path})\n\n"


def prepare_markdown(text: str) -> str:
    for number in FIGURES:
        text = re.sub(rf"\*\*\[Figure {number}\]\*\*", figure_block(number), text)
    text = re.sub(r"\\textsuperscript\{([^}]*)\}", r"^\1^", text)
    text = text.replace(r"\*", "*")
    text = text.replace("π̂₀", "pi0-hat")
    text = text.replace("H₀", "H0")
    return text


def force_docx_submission_styles(docx_path: Path) -> None:
    """Apply OOXML fixes after Pandoc's DOCX export."""
    with tempfile.TemporaryDirectory(prefix="caic_docx_") as tmp:
        tmpdir = Path(tmp)
        with zipfile.ZipFile(docx_path) as zin:
            zin.extractall(tmpdir)

        styles_path = tmpdir / "word" / "styles.xml"
        tree = ET.parse(styles_path)
        root = tree.getroot()

        style_specs = {
            "Normal": {"size": "22", "bold": False, "before": "0", "after": "120"},
            "BodyText": {"size": "22", "bold": False, "before": "0", "after": "120"},
            "FirstParagraph": {"size": "22", "bold": False, "before": "0", "after": "120"},
            "Compact": {"size": "20", "bold": False, "before": "0", "after": "60"},
            "ImageCaption": {"size": "19", "bold": False, "before": "80", "after": "160"},
            "Caption": {"size": "19", "bold": False, "before": "80", "after": "160"},
            "Heading1": {"size": "32", "bold": True, "before": "160", "after": "120"},
            "Heading2": {"size": "26", "bold": True, "before": "200", "after": "80"},
            "Heading3": {"size": "23", "bold": True, "before": "160", "after": "60"},
            "Heading4": {"size": "22", "bold": True, "before": "120", "after": "40"},
            "Heading5": {"size": "22", "bold": True, "before": "120", "after": "40"},
            "Title": {"size": "32", "bold": True, "before": "120", "after": "120"},
        }

        def child(parent: ET.Element, tag: str) -> ET.Element:
            found = parent.find(tag, WORD_NS)
            if found is None:
                found = ET.SubElement(parent, f"{{{WORD_NS['w']}}}{tag.split(':')[-1]}")
            return found

        for style_id, spec in style_specs.items():
            style = root.find(f".//w:style[@w:styleId='{style_id}']", WORD_NS)
            if style is None:
                continue
            ppr = child(style, "w:pPr")
            spacing = child(ppr, "w:spacing")
            spacing.set(f"{{{WORD_NS['w']}}}before", spec["before"])
            spacing.set(f"{{{WORD_NS['w']}}}after", spec["after"])
            spacing.set(f"{{{WORD_NS['w']}}}line", "276")
            spacing.set(f"{{{WORD_NS['w']}}}lineRule", "auto")

            rpr = child(style, "w:rPr")
            color = child(rpr, "w:color")
            color.attrib.clear()
            color.set(f"{{{WORD_NS['w']}}}val", "000000")
            size = child(rpr, "w:sz")
            size.set(f"{{{WORD_NS['w']}}}val", spec["size"])
            size_cs = child(rpr, "w:szCs")
            size_cs.set(f"{{{WORD_NS['w']}}}val", spec["size"])
            fonts = child(rpr, "w:rFonts")
            fonts.set(f"{{{WORD_NS['w']}}}ascii", "Times New Roman")
            fonts.set(f"{{{WORD_NS['w']}}}hAnsi", "Times New Roman")
            fonts.set(f"{{{WORD_NS['w']}}}cs", "Times New Roman")
            bold = rpr.find("w:b", WORD_NS)
            bold_cs = rpr.find("w:bCs", WORD_NS)
            if spec["bold"]:
                if bold is None:
                    ET.SubElement(rpr, f"{{{WORD_NS['w']}}}b")
                if bold_cs is None:
                    ET.SubElement(rpr, f"{{{WORD_NS['w']}}}bCs")
            else:
                if bold is not None:
                    rpr.remove(bold)
                if bold_cs is not None:
                    rpr.remove(bold_cs)

        for style_id in ["Heading1Char", "Heading2Char", "Heading3Char", "Heading4Char", "Heading5Char"]:
            style = root.find(f".//w:style[@w:styleId='{style_id}']", WORD_NS)
            if style is None:
                continue
            rpr = child(style, "w:rPr")
            color = child(rpr, "w:color")
            color.attrib.clear()
            color.set(f"{{{WORD_NS['w']}}}val", "000000")

        tree.write(styles_path, encoding="UTF-8", xml_declaration=True)

        content_types_path = tmpdir / "[Content_Types].xml"
        ct_tree = ET.parse(content_types_path)
        ct_root = ct_tree.getroot()
        has_png = any(
            elem.tag == f"{{{WORD_NS['ct']}}}Default"
            and elem.attrib.get("Extension") == "png"
            for elem in ct_root
        )
        if not has_png:
            ET.SubElement(
                ct_root,
                f"{{{WORD_NS['ct']}}}Default",
                {"Extension": "png", "ContentType": "image/png"},
            )
        for elem in list(ct_root):
            if elem.attrib.get("PartName") == "/word/comments.xml":
                ct_root.remove(elem)
        ct_tree.write(content_types_path, encoding="UTF-8", xml_declaration=True)

        comments_path = tmpdir / "word" / "comments.xml"
        comments_path.unlink(missing_ok=True)
        rels_path = tmpdir / "word" / "_rels" / "document.xml.rels"
        rels_tree = ET.parse(rels_path)
        rels_root = rels_tree.getroot()
        for elem in list(rels_root):
            if elem.attrib.get("Type") == "http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments":
                rels_root.remove(elem)
        rels_tree.write(rels_path, encoding="UTF-8", xml_declaration=True)

        document_path = tmpdir / "word" / "document.xml"
        doc_tree = ET.parse(document_path)
        doc_root = doc_tree.getroot()

        def qn(tag: str) -> str:
            prefix, name = tag.split(":")
            return f"{{{WORD_NS[prefix]}}}{name}"

        def ensure(parent: ET.Element, tag: str) -> ET.Element:
            found = parent.find(tag, WORD_NS)
            if found is None:
                found = ET.SubElement(parent, qn(tag))
            return found

        def set_border(parent: ET.Element, name: str, value: str = "single", size: str = "8") -> None:
            border = parent.find(f"w:{name}", WORD_NS)
            if border is None:
                border = ET.SubElement(parent, qn(f"w:{name}"))
            border.attrib.clear()
            border.set(qn("w:val"), value)
            if value != "nil":
                border.set(qn("w:sz"), size)
                border.set(qn("w:space"), "0")
                border.set(qn("w:color"), "000000")

        def set_run_size(para: ET.Element, size: str) -> None:
            for run in para.findall("w:r", WORD_NS):
                rpr = ensure(run, "w:rPr")
                sz = ensure(rpr, "w:sz")
                sz.set(qn("w:val"), size)
                sz_cs = ensure(rpr, "w:szCs")
                sz_cs.set(qn("w:val"), size)

        def apply_three_line_tables(root_element: ET.Element) -> None:
            for table_idx, tbl in enumerate(root_element.findall(".//w:tbl", WORD_NS), start=1):
                tbl_pr = ensure(tbl, "w:tblPr")
                tbl_w = ensure(tbl_pr, "w:tblW")
                tbl_w.set(qn("w:w"), "5000")
                tbl_w.set(qn("w:type"), "pct")

                tbl_borders = ensure(tbl_pr, "w:tblBorders")
                set_border(tbl_borders, "top")
                set_border(tbl_borders, "bottom")
                for edge in ["left", "right", "insideH", "insideV"]:
                    set_border(tbl_borders, edge, "nil")

                rows = tbl.findall("w:tr", WORD_NS)
                compact_long_table = table_idx == 4
                for row_idx, row in enumerate(rows):
                    tr_pr = row.find("w:trPr", WORD_NS)
                    if tr_pr is None:
                        tr_pr = ET.Element(qn("w:trPr"))
                        row.insert(0, tr_pr)
                    if tr_pr.find("w:cantSplit", WORD_NS) is None:
                        tr_pr.insert(0, ET.Element(qn("w:cantSplit")))
                    for cell in row.findall("w:tc", WORD_NS):
                        tc_pr = ensure(cell, "w:tcPr")
                        old_borders = tc_pr.find("w:tcBorders", WORD_NS)
                        if old_borders is not None:
                            tc_pr.remove(old_borders)
                        if row_idx == 0:
                            cell_borders = ET.SubElement(tc_pr, qn("w:tcBorders"))
                            set_border(cell_borders, "bottom")
                        for para in cell.findall(".//w:p", WORD_NS):
                            ppr = ensure(para, "w:pPr")
                            spacing = ensure(ppr, "w:spacing")
                            spacing.set(qn("w:before"), "0")
                            spacing.set(qn("w:after"), "20" if compact_long_table else "40")
                            spacing.set(qn("w:line"), "210" if compact_long_table else "240")
                            spacing.set(qn("w:lineRule"), "auto")
                            if compact_long_table:
                                set_run_size(para, "17")

        def paragraph_text(para: ET.Element) -> str:
            return "".join(
                node.text or ""
                for node in para.findall(".//w:t", WORD_NS)
            )

        def insert_after_pstyle(ppr: ET.Element, element: ET.Element) -> None:
            children = list(ppr)
            insert_at = 0
            for idx, child in enumerate(children):
                if child.tag == qn("w:pStyle"):
                    insert_at = idx + 1
            ppr.insert(insert_at, element)

        def add_keep_next(para: ET.Element) -> None:
            ppr = ensure(para, "w:pPr")
            if ppr.find("w:keepNext", WORD_NS) is None:
                keep_next = ET.Element(qn("w:keepNext"))
                insert_after_pstyle(ppr, keep_next)

        def apply_word_pagination(root_element: ET.Element) -> None:
            for para in root_element.findall(".//w:p", WORD_NS):
                text = paragraph_text(para).strip()
                if text.startswith(("Table 1.", "Table 2.", "Table 3.")):
                    add_keep_next(para)

        apply_three_line_tables(doc_root)
        apply_word_pagination(doc_root)
        for parent in doc_root.iter():
            for child in list(parent):
                if child.tag == f"{{{WORD_NS['m']}}}sty":
                    parent.remove(child)
        doc_tree.write(document_path, encoding="UTF-8", xml_declaration=True)

        fixed = docx_path.with_suffix(".fixed.docx")
        with zipfile.ZipFile(fixed, "w", compression=zipfile.ZIP_DEFLATED) as zout:
            for path in sorted(tmpdir.rglob("*")):
                if path.is_file():
                    zout.write(path, path.relative_to(tmpdir))
        fixed.replace(docx_path)


def normalize_docx_for_word_processors(docx_path: Path) -> None:
    """Re-save through python-docx to normalize repacked OOXML relationships."""
    tmp = docx_path.with_suffix(".normalized.docx")
    Document(str(docx_path)).save(str(tmp))
    tmp.replace(docx_path)


def main() -> int:
    prepared = prepare_markdown(SRC.read_text(encoding="utf-8"))
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

    force_docx_submission_styles(DOCX_SRC)
    normalize_docx_for_word_processors(DOCX_SRC)
    UPLOAD_DIR.mkdir(exist_ok=True)
    shutil.copy2(DOCX_SRC, DOCX_UPLOAD)
    print(f"Wrote {DOCX_SRC}")
    print(f"Wrote {DOCX_UPLOAD}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
