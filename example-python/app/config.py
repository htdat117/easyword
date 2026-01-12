import os
import tempfile
from pathlib import Path

from docx.shared import Inches, Pt, RGBColor, Cm


# ============================================================================
# ĐƯỜNG DẪN VÀ THƯ MỤC
# ============================================================================
PROJECT_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"
TEMP_DIR = Path(tempfile.gettempdir()) / "word_reports_preview"
TEMP_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================================
# CẤU HÌNH API - CONVERT PDF PREVIEW
# ============================================================================
# ConvertAPI Secret Key - Lấy miễn phí tại: https://www.convertapi.com/a/signup/free
# Đăng ký -> Vào Account -> API Tokens -> Copy Sandbox Token
CONVERTAPI_SECRET = "pzrYsSfAOsGUVt007DYajvlUsUW32QhE"  # <-- THAY BẰNG TOKEN CỦA BẠN


# ============================================================================
# CẤU HÌNH FONT CHỮ
# ============================================================================
# Font chữ chuẩn cho toàn bộ tài liệu
STANDARD_FONT = "Times New Roman"

# Font dự phòng (nếu Times New Roman không có)
FALLBACK_FONT = "Arial"


# ============================================================================
# CẤU HÌNH CỠ CHỮ
# ============================================================================
# Cỡ chữ nội dung văn bản
BODY_FONT_SIZE = Pt(13)

# Cỡ chữ tiêu đề (Heading 1, 2, 3...)
HEADING_FONT_SIZE = Pt(14)

# Cỡ chữ mục lục (Table of Contents)
TOC_FONT_SIZE = Pt(13)

# Cỡ chữ số trang
PAGE_NUMBER_FONT_SIZE = Pt(13)

# Cỡ chữ chú thích hình/bảng (Caption)
CAPTION_FONT_SIZE = Pt(10)

# Cỡ chữ đầu mục danh sách
LIST_FONT_SIZE = Pt(13)


# ============================================================================
# CẤU HÌNH MÀU SẮC
# ============================================================================
# Màu chữ mặc định (đen)
DEFAULT_TEXT_COLOR = RGBColor(0, 0, 0)

# Màu chữ tiêu đề
HEADING_COLOR = RGBColor(0, 0, 0)

# Màu chữ mục lục
TOC_COLOR = RGBColor(0, 0, 0)

# Màu chữ chú thích (caption)
CAPTION_COLOR = RGBColor(0, 0, 0)

# Màu chữ lỗi/cảnh báo (đỏ)
ERROR_COLOR = RGBColor(200, 0, 0)

# Màu chữ liên kết (xanh dương)
LINK_COLOR = RGBColor(0, 0, 255)


# ============================================================================
# CẤU HÌNH ĐỊNH DẠNG ĐOẠN VÀN
# ============================================================================
# Khoảng cách dòng
LINE_SPACING = 1.5

# Thụt lề đầu dòng
PARAGRAPH_INDENT = Cm(1.27)  # 1.27cm = 0.5 inch

# Khoảng cách trước đoạn
SPACE_BEFORE = Pt(0)

# Khoảng cách sau đoạn
SPACE_AFTER = Pt(0)


# ============================================================================
# CẤU HÌNH LỀ TRANG (MARGINS)
# ============================================================================
UEL_MARGINS = {
    "top": Cm(2),      # Lề trên: 2cm
    "bottom": Cm(2),   # Lề dưới: 2cm
    "left": Cm(3),     # Lề trái: 3cm
    "right": Cm(2),    # Lề phải: 2cm
}


# ============================================================================
# CẤU HÌNH STYLE
# ============================================================================
# Cấu hình style cho Caption
CAPTION_STYLE_CONFIG = {
    "font_name": STANDARD_FONT,
    "font_size": CAPTION_FONT_SIZE,
    "color": CAPTION_COLOR,
    "italic": True,
    "bold": False,
}

# Cấu hình style cho UEL Figure (chú thích hình)
UEL_FIGURE_STYLE_CONFIG = {
    "font_name": STANDARD_FONT,
    "font_size": BODY_FONT_SIZE,
    "color": CAPTION_COLOR,
    "italic": True,
    "bold": False,
    "alignment": "center",  # căn giữa
}

# Cấu hình style cho Heading 1
HEADING1_STYLE_CONFIG = {
    "font_name": STANDARD_FONT,
    "font_size": Pt(16),
    "color": HEADING_COLOR,
    "bold": True,
    "italic": False,
    "all_caps": False,
}

# Cấu hình style cho Heading 2
HEADING2_STYLE_CONFIG = {
    "font_name": STANDARD_FONT,
    "font_size": Pt(14),
    "color": HEADING_COLOR,
    "bold": True,
    "italic": False,
}

# Cấu hình style cho Heading 3
HEADING3_STYLE_CONFIG = {
    "font_name": STANDARD_FONT,
    "font_size": Pt(13),
    "color": HEADING_COLOR,
    "bold": True,
    "italic": False,
}

# Cấu hình style cho Mục lục (Table of Contents - TOC)
TOC_STYLE_CONFIG = {
    "font_name": STANDARD_FONT,
    "font_size": TOC_FONT_SIZE,
    "color": TOC_COLOR,
    "bold": False,
    "italic": False,
    "line_spacing": 1.5,
}

# Cấu hình tiêu đề "MỤC LỤC"
TOC_HEADING_CONFIG = {
    "font_name": STANDARD_FONT,
    "font_size": TOC_FONT_SIZE,
    "color": HEADING_COLOR,
    "bold": True,
    "italic": False,
    "alignment": "center",
}

# Cấu hình tiêu đề "DANH MỤC HÌNH ẢNH"
TOF_HEADING_CONFIG = {
    "font_name": STANDARD_FONT,
    "font_size": TOC_FONT_SIZE,
    "color": HEADING_COLOR,
    "bold": True,
    "italic": False,
    "alignment": "center",
}

