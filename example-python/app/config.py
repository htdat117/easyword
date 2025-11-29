from pathlib import Path

from docx.shared import Inches, Pt


PROJECT_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"

STANDARD_FONT = "Times New Roman"
BODY_FONT_SIZE = Pt(13)
HEADING_FONT_SIZE = Pt(14)
TOC_FONT_SIZE = Pt(13)
PAGE_NUMBER_FONT_SIZE = Pt(13)

LINE_SPACING = 1.3
PARAGRAPH_INDENT = Inches(0.39)

UEL_MARGINS = {
    "top": Inches(0.98),
    "bottom": Inches(0.98),
    "left": Inches(1.38),
    "right": Inches(0.79),
}

