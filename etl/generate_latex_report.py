"""Build PDF, Word and Markdown from the single maintained LaTeX report.

Prerequisites: pdflatex (MiKTeX), Pandoc, python-docx and pypdf.
Never overwrites the LaTeX source with an embedded historical template.
"""
from pathlib import Path
import re
import shutil
import subprocess

from docx import Document
from docx.shared import Mm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SOURCE = DOCS / "BDM_Project_Report.tex"
OUTPUT = ROOT / "output" / "pdf"


def run(command, cwd=DOCS):
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True,
                            encoding="utf-8", errors="replace")
    if result.returncode:
        raise RuntimeError(f"Command failed: {command}\n{result.stdout[-5000:]}\n{result.stderr[-2000:]}")
    if result.stderr.strip():
        print(result.stderr.strip())
    return result


def polish_word(path):
    document = Document(path)
    paragraphs = list(document.paragraphs)
    for index, paragraph in enumerate(paragraphs):
        if paragraph.text.strip() == "REPORTPAGEBREAK":
            if index + 1 < len(paragraphs):
                paragraphs[index + 1].paragraph_format.page_break_before = True
            paragraph._p.getparent().remove(paragraph._p)
    for section in document.sections:
        section.page_width, section.page_height = Mm(210), Mm(297)
        section.top_margin = section.bottom_margin = Mm(23)
        section.left_margin = section.right_margin = Mm(23)
    normal = document.styles["Normal"]
    normal.font.name = "Cambria"
    normal.font.size = Pt(11)
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.08
    for name, size in [("Heading 1", 17), ("Heading 2", 12), ("Heading 3", 11)]:
        style = document.styles[name]
        style.font.name = "Calibri"
        style.font.size = Pt(size)
        style.font.color.rgb = RGBColor.from_string("233448")
        style.paragraph_format.keep_with_next = True
    # Replace the LaTeX title-page conversion with a native Word cover.
    abstract = next(p for p in document.paragraphs if p.text.strip() == "Abstract")
    for paragraph in list(document.paragraphs):
        if paragraph._p is abstract._p:
            break
        paragraph._p.getparent().remove(paragraph._p)
    cover = [
        ("BIG DATA MANAGEMENT", 12, True, 30),
        ("RoadSafe GB", 32, True, 12),
        ("Spatial and Temporal Analysis\nof Road Collisions in Great Britain", 21, True, 16),
        ("An analysis of STATS19 records using\nMongoDB, Python, React and Power BI", 12, False, 30),
        ("A project report submitted for the course\nBig Data Management (Semester VII)", 13, False, 30),
        ("Submitted by", 11, False, 6),
        ("Nishant Harkut", 18, True, 6),
        ("Roll No.: 2023IMG-040", 13, False, 6),
        ("IMG (Integrated B.Tech + MBA)", 13, False, 42),
        ("ATAL BIHARI VAJPAYEE\nINDIAN INSTITUTE OF INFORMATION TECHNOLOGY\nAND MANAGEMENT GWALIOR", 12, True, 12),
        ("Gwalior, India\nOctober 2026", 11, False, 0),
    ]
    for text, size, bold, after in cover:
        paragraph = abstract.insert_paragraph_before()
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        paragraph.paragraph_format.space_after = Pt(after)
        run_text = paragraph.add_run(text)
        run_text.font.name = "Calibri"
        run_text.font.size = Pt(size)
        run_text.bold = bold
        run_text.font.color.rgb = RGBColor.from_string("233448")
    abstract.paragraph_format.page_break_before = True
    abstract.style = "TOC Heading"
    for run_text in abstract.runs:
        run_text.font.size = Pt(17)
        run_text.bold = True
    introduction = next(p for p in document.paragraphs if p.text.strip() in ("Introduction", "1 Introduction"))
    toc_title = introduction.insert_paragraph_before("Contents", "TOC Heading")
    for run_text in toc_title.runs:
        run_text.font.size = Pt(17)
        run_text.bold = True
    toc = introduction.insert_paragraph_before()
    field = OxmlElement("w:fldSimple")
    field.set(qn("w:instr"), 'TOC \\o "1-1" \\h \\z \\u')
    toc._p.append(field)
    introduction.paragraph_format.page_break_before = True
    for table in document.tables:
        table.autofit = True
        for row in table.rows:
            props = row._tr.get_or_add_trPr()
            props.append(OxmlElement("w:cantSplit"))
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    for run_text in paragraph.runs:
                        run_text.font.size = Pt(9)
        props = table.rows[0]._tr.get_or_add_trPr()
        props.append(OxmlElement("w:tblHeader"))
        for cell in table.rows[0].cells:
            shading = OxmlElement("w:shd")
            shading.set(qn("w:fill"), "EAF1F3")
            cell._tc.get_or_add_tcPr().append(shading)
    for section in document.sections:
        header = section.header.paragraphs[0]
        header.text = "RoadSafe GB | Big Data Management"
        footer = section.footer.paragraphs[0]
        footer.text = "Nishant Harkut | 2023IMG-040"
        footer.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        footer.add_run("   |   ")
        field = OxmlElement("w:fldSimple")
        field.set(qn("w:instr"), "PAGE")
        footer._p.append(field)
        for paragraph in (header, footer):
            for run_text in paragraph.runs:
                run_text.font.name = "Calibri"
                run_text.font.size = Pt(9)
        section.different_first_page_header_footer = True
    settings = document.settings.element
    update = OxmlElement("w:updateFields")
    update.set(qn("w:val"), "true")
    settings.append(update)
    document.core_properties.author = "Nishant Harkut"
    document.core_properties.title = "RoadSafe GB: Spatial and Temporal Analysis of Road Collisions"
    document.save(path)


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for required in ("pdflatex", "pandoc"):
        if not shutil.which(required):
            raise RuntimeError(f"Required executable not found: {required}")
    command = ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", SOURCE.name]
    for _ in range(3):
        run(command)
    log = SOURCE.with_suffix(".log").read_text(encoding="utf-8", errors="replace")
    problems = [line for line in log.splitlines() if "Overfull" in line or "undefined references" in line]
    if problems:
        print("Layout warnings requiring inspection:\n" + "\n".join(problems))
    reader = PdfReader(SOURCE.with_suffix(".pdf"))
    text = "\n".join(page.extract_text() for page in reader.pages)
    for expected in ("Nishant Harkut", "2023IMG-040", "Integrated B.Tech + MBA"):
        if expected not in text:
            raise RuntimeError(f"Missing cover detail: {expected}")
    for obsolete in ("Nishanth Harkut", "2023IMG-038", "Student 1", "anti-slop"):
        if obsolete in text:
            raise RuntimeError(f"Obsolete text remains: {obsolete}")
    # Pandoc cannot resolve the custom L column used by tabularx. Normalise
    # just the export copy so Word and Markdown receive real table cells.
    export_text = SOURCE.read_text(encoding="utf-8")
    export_text = re.sub(r"\\begin\{tabularx\}\{\\textwidth\}\{([^}]+)\}",
                         lambda match: r"\begin{tabular}{" + match.group(1).replace("L", "l") + "}",
                         export_text)
    export_text = export_text.replace(r"\end{tabularx}", r"\end{tabular}")
    export_text = export_text.replace(r"\begin{titlepage}", "").replace(r"\end{titlepage}", "")
    export_source = ROOT / "tmp" / "pdfs" / "report-export.tex"
    export_source.parent.mkdir(parents=True, exist_ok=True)
    export_source.write_text(export_text, encoding="utf-8")
    run(["pandoc", str(export_source), "--from=latex", "--to=gfm+tex_math_dollars", "--wrap=none",
         "-o", "BDM_Project_Report.md"])
    export_source.write_text(export_text.replace(r"\clearpage", "\n\nREPORTPAGEBREAK\n\n"),
                             encoding="utf-8")
    run(["pandoc", str(export_source), "--from=latex", "--to=docx",
         "--resource-path=.", "-o", "BDM_Project_Report.docx"])
    polish_word(SOURCE.with_suffix(".docx"))
    word = Document(SOURCE.with_suffix(".docx"))
    if len(word.tables) != 7 or len(word.inline_shapes) != 12:
        raise RuntimeError(f"Export mismatch: {len(word.tables)} tables, {len(word.inline_shapes)} images")
    shutil.copy2(SOURCE.with_suffix(".pdf"), OUTPUT / "BDM_Project_Report.pdf")
    print(f"Built {len(reader.pages)}-page PDF, editable DOCX and Markdown from {SOURCE}.")
    print(f"PDF: {OUTPUT / 'BDM_Project_Report.pdf'}")


if __name__ == "__main__":
    main()
