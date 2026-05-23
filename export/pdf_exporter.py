from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app_config import (
    APP_NAME,
    FOOTER_TEXT,
    HASSAN_AVATAR_PATH,
    POWERED_BY,
    STT_BANNER_PATH,
    SYNTHETIC_DISCLAIMER,
    TARGET_URL,
)
from core.models import DomainSpec, GenerationPlan

STT_RED = colors.HexColor("#E50914")
STT_DARK = colors.HexColor("#050508")
CYAN = colors.HexColor("#00A8C8")
LIME = colors.HexColor("#8FBF00")
VIOLET = colors.HexColor("#6D28D9")
TEXT = colors.HexColor("#111827")
MUTED = colors.HexColor("#4B5563")


def _styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="DBTitle", parent=styles["Title"], fontSize=22, leading=25, textColor=STT_DARK, spaceAfter=5, fontName="Helvetica-Bold"))
    styles.add(ParagraphStyle(name="DBPowered", parent=styles["Normal"], fontSize=10, leading=13, textColor=STT_RED, spaceAfter=8, fontName="Helvetica-Bold"))
    styles.add(ParagraphStyle(name="DBSubtitle", parent=styles["Normal"], fontSize=10, leading=14, textColor=MUTED, spaceAfter=10))
    styles.add(ParagraphStyle(name="DBHeading", parent=styles["Heading2"], fontSize=14, leading=17, textColor=STT_RED, spaceBefore=13, spaceAfter=7, fontName="Helvetica-Bold"))
    styles.add(ParagraphStyle(name="DBSmall", parent=styles["Normal"], fontSize=8, leading=10, textColor=colors.HexColor("#4B5563")))
    styles.add(ParagraphStyle(name="DBBrandSmall", parent=styles["Normal"], fontSize=8, leading=10, textColor=STT_DARK, fontName="Helvetica-Bold"))
    return styles


def _doc(path: Path):
    return SimpleDocTemplate(str(path), pagesize=A4, rightMargin=34, leftMargin=34, topMargin=32, bottomMargin=36)


def _safe_image(path: Path, width: float, height: float):
    if path.exists():
        img = Image(str(path), width=width, height=height)
        img.hAlign = "LEFT"
        return img
    return None


def _header(story, styles, title: str):
    logo = _safe_image(STT_BANNER_PATH, 2.55 * inch, 0.82 * inch)
    avatar = _safe_image(HASSAN_AVATAR_PATH, 0.82 * inch, 0.82 * inch)
    brand_lines = [
        Paragraph("STT SOLUTIONS AI & DATA LEARNING SYSTEMS", styles["DBBrandSmall"]),
        Paragraph(APP_NAME, styles["DBTitle"]),
        Paragraph(POWERED_BY, styles["DBPowered"]),
        Paragraph(f"Target web app URL: {TARGET_URL}", styles["DBSmall"]),
    ]
    brand_block = Table([[brand_lines]], colWidths=[3.25 * inch])
    brand_block.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
    header_row = [logo or "", brand_block, avatar or ""]
    header = Table([header_row], colWidths=[2.65 * inch, 3.35 * inch, 0.86 * inch])
    header.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LINEBELOW", (0, 0), (-1, 0), 1.4, STT_RED),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
    ]))
    story.append(header)
    story.append(Spacer(1, 0.13 * inch))
    story.append(Paragraph(title, styles["Heading1"]))
    story.append(Spacer(1, 0.10 * inch))


def _footer_note(story, styles):
    story.append(Spacer(1, 0.18 * inch))
    story.append(Paragraph(SYNTHETIC_DISCLAIMER, styles["DBSmall"]))
    story.append(Paragraph(FOOTER_TEXT, styles["DBSmall"]))


def _table(data, widths=None):
    table = Table(data, colWidths=widths, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), STT_DARK),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#CBD5E1")),
        ("LINEABOVE", (0, 0), (-1, 0), 2, STT_RED),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    return table


def create_all_pdfs(plan: GenerationPlan, domain: DomainSpec, output_dir: Path, dirt_report: Dict[str, List[str]]):
    create_data_dictionary_pdf(plan, domain, output_dir / "data_dictionary.pdf")
    create_cleaning_challenges_pdf(plan, domain, dirt_report, output_dir / "cleaning_challenges.pdf")
    create_suggested_dashboard_pdf(plan, domain, output_dir / "suggested_powerbi_dashboard.pdf")
    create_generation_summary_pdf(plan, domain, dirt_report, output_dir / "generation_summary.pdf")


def create_data_dictionary_pdf(plan: GenerationPlan, domain: DomainSpec, path: Path):
    styles = _styles(); story = []
    _header(story, styles, "Data Dictionary")
    story.append(Paragraph(f"Dataset type: {domain.name}", styles["DBSubtitle"]))
    data = [["Column", "Type", "Definition", "Dirty Data Selected"]]
    for col in plan.columns:
        dirt = ", ".join(col.dirt_types) if col.dirt_types else "None"
        data.append([col.final_name, col.data_type, col.definition, dirt])
    story.append(_table(data, [1.35*inch, 0.75*inch, 2.75*inch, 2.1*inch]))
    _footer_note(story, styles)
    _doc(path).build(story)


def create_cleaning_challenges_pdf(plan: GenerationPlan, domain: DomainSpec, dirt_report: Dict[str, List[str]], path: Path):
    styles = _styles(); story = []
    _header(story, styles, "Cleaning Challenges")
    story.append(Paragraph("This STT Solutions learning document explains the intentional data quality problems included for Power Query and Power BI cleaning practice.", styles["DBSubtitle"]))
    data = [["Column / Scope", "Injected or Selected Challenge"]]
    if dirt_report:
        for col, issues in dirt_report.items():
            data.append([col, ", ".join(sorted(set(issues)))])
    else:
        data.append(["Dataset", "No dirty data was selected."])
    story.append(_table(data, [2.0*inch, 4.85*inch]))
    story.append(Paragraph("Recommended Cleaning Workflow", styles["DBHeading"]))
    workflow = "Start by profiling columns, trimming text, cleaning non-printing characters, standardizing categories, replacing placeholder codes, fixing date formats, checking numeric ranges, and removing or investigating duplicates."
    story.append(Paragraph(workflow, styles["Normal"]))
    _footer_note(story, styles)
    _doc(path).build(story)


def create_suggested_dashboard_pdf(plan: GenerationPlan, domain: DomainSpec, path: Path):
    styles = _styles(); story = []
    _header(story, styles, "Suggested Power BI Dashboard")
    story.append(Paragraph(f"Learning objective: {plan.learning_objective}", styles["DBSubtitle"]))
    story.append(Paragraph("Recommended Visuals and Analysis Questions", styles["DBHeading"]))
    for item in domain.dashboard_guidance:
        story.append(Paragraph(f"• {item}", styles["Normal"]))
    story.append(Spacer(1, 0.12*inch))
    story.append(Paragraph("Recommended page structure: data quality overview, executive KPI summary, trend analysis, categorical breakdown, and drill-through detail table.", styles["Normal"]))
    _footer_note(story, styles)
    _doc(path).build(story)


def create_generation_summary_pdf(plan: GenerationPlan, domain: DomainSpec, dirt_report: Dict[str, List[str]], path: Path):
    styles = _styles(); story = []
    _header(story, styles, "Generation Summary")
    data = [
        ["Field", "Value"],
        ["Product", APP_NAME],
        ["Institutional Engine", "STT Solutions"],
        ["Powered by", POWERED_BY],
        ["Dataset Type", domain.name],
        ["Learning Objective", plan.learning_objective],
        ["Rows", f"{plan.rows:,}"],
        ["Columns", str(plan.column_count)],
        ["Dirty Data Intensity", plan.dirt_intensity],
        ["Random Seed", str(plan.random_seed)],
    ]
    story.append(_table(data, [2.1*inch, 4.75*inch]))
    story.append(Paragraph("Contextual Questions", styles["DBHeading"]))
    q_data = [["Question", "Answer"]]
    for q, ans in plan.question_answers.items():
        q_data.append([q, "Yes" if ans else "No"])
    story.append(_table(q_data, [5.55*inch, 1.0*inch]))
    story.append(Paragraph("Package Contents", styles["DBHeading"]))
    story.append(Paragraph("The package contains CSV dataset files and PDF documentation only. No Markdown, JSON, Excel, Parquet, SQLite, or database files are generated.", styles["Normal"]))
    _footer_note(story, styles)
    _doc(path).build(story)
