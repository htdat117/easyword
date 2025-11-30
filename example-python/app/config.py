import os
import tempfile
from pathlib import Path

from docx.shared import Inches, Pt


PROJECT_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"
TEMP_DIR = Path(tempfile.gettempdir()) / "word_reports_preview"
TEMP_DIR.mkdir(parents=True, exist_ok=True)

STANDARD_FONT = "Times New Roman"
BODY_FONT_SIZE = Pt(13)
HEADING_FONT_SIZE = Pt(14)
TOC_FONT_SIZE = Pt(13)
PAGE_NUMBER_FONT_SIZE = Pt(13)

LINE_SPACING = 1.5
PARAGRAPH_INDENT = Inches(0.39)

UEL_MARGINS = {
    "top": Inches(0.98),
    "bottom": Inches(0.98),
    "left": Inches(1.38),
    "right": Inches(0.79),
}

