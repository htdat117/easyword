"""
Module for docx styling utilities
Tất cả các cấu hình font, màu sắc, cỡ chữ được lấy từ app.config
"""
from docx.shared import Pt, RGBColor
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from app.config import (
    STANDARD_FONT,
    CAPTION_STYLE_CONFIG,
    UEL_FIGURE_STYLE_CONFIG,
    TOC_STYLE_CONFIG,
)


def _copy_heading_style_to_toc(doc):
    """
    Đảm bảo tất cả TOC styles có font Times New Roman 13pt và cỡ chữ đúng
    Tạo mới nếu style chưa tồn tại
    Cấu hình lấy từ TOC_STYLE_CONFIG trong config.py
    """
    config = TOC_STYLE_CONFIG
    
    for i in range(1, 10):  # TOC 1 đến TOC 9
        style_name = f'TOC {i}'
        try:
            toc_style = doc.styles[style_name]
        except KeyError:
            # Tạo mới TOC style nếu chưa tồn tại
            toc_style = doc.styles.add_style(style_name, WD_STYLE_TYPE.PARAGRAPH)
        
        # Áp dụng cấu hình từ config - Times New Roman 13pt
        toc_style.font.name = config['font_name']
        toc_style.font.size = config['font_size']  # 13pt
        toc_style.font.bold = config['bold']
        toc_style.font.italic = config['italic']
        toc_style.font.color.rgb = config['color']
        
        # Set East Asian font (quan trọng cho tiếng Việt)
        _apply_font_to_style(toc_style, config['font_name'])
        
        # Force set trong XML để đảm bảo
        _force_style_font_in_xml(toc_style, config['font_name'], config['font_size'])
        
        # Set paragraph formatting
        if toc_style.paragraph_format:
            toc_style.paragraph_format.left_indent = Pt(i * 12)  # Thụt lề theo cấp
            toc_style.paragraph_format.line_spacing = config['line_spacing']
            toc_style.paragraph_format.space_before = Pt(0)
            toc_style.paragraph_format.space_after = Pt(0)


def _force_style_font_in_xml(style, font_name, font_size):
    """
    Force set font trong XML level cho style
    Đảm bảo TOC styles có font chính xác
    """
    try:
        rPr = style.element.get_or_add_rPr()
        
        # Xóa font cũ
        for tag in ["rFonts", "sz", "szCs"]:
            old = rPr.find(qn(f"w:{tag}"))
            if old is not None:
                rPr.remove(old)
        
        # Set font mới
        rFonts = OxmlElement('w:rFonts')
        rFonts.set(qn('w:ascii'), font_name)
        rFonts.set(qn('w:hAnsi'), font_name)
        rFonts.set(qn('w:eastAsia'), font_name)
        rFonts.set(qn('w:cs'), font_name)
        rPr.insert(0, rFonts)
        
        # Set size
        size_half_pts = int(font_size.pt * 2)  # 13pt = 26 half-points
        sz = OxmlElement('w:sz')
        sz.set(qn('w:val'), str(size_half_pts))
        rPr.append(sz)
        
        szCs = OxmlElement('w:szCs')
        szCs.set(qn('w:val'), str(size_half_pts))
        rPr.append(szCs)
    except Exception:
        pass  # Nếu lỗi, bỏ qua và dùng API setting


def _apply_font_to_style(style, font_name):
    """
    Áp dụng font cho style (bao gồm cả East Asian font)
    
    Args:
        style: Style object
        font_name: Tên font (ví dụ: "Times New Roman")
    """
    # Set font name
    style.font.name = font_name
    
    # Set East Asian font trong XML
    rPr = style.element.get_or_add_rPr()
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = OxmlElement('w:rFonts')
        rPr.append(rFonts)
    
    # Set tất cả các loại font
    rFonts.set(qn('w:ascii'), font_name)
    rFonts.set(qn('w:hAnsi'), font_name)
    rFonts.set(qn('w:cs'), font_name)
    rFonts.set(qn('w:eastAsia'), font_name)


def _ensure_caption_style(doc):
    """
    Đảm bảo các style Caption và UEL Figure tồn tại trong document
    Tất cả cấu hình được lấy từ app.config
    """
    # ===== Ensure Caption style =====
    try:
        caption_style = doc.styles['Caption']
    except KeyError:
        # Tạo mới Caption style
        caption_style = doc.styles.add_style('Caption', WD_STYLE_TYPE.PARAGRAPH)
    
    # Áp dụng cấu hình từ config
    config = CAPTION_STYLE_CONFIG
    caption_style.font.name = config['font_name']
    caption_style.font.size = config['font_size']
    caption_style.font.italic = config['italic']
    caption_style.font.bold = config['bold']
    caption_style.font.color.rgb = config['color']
    _apply_font_to_style(caption_style, config['font_name'])
    
    # ===== Ensure UEL Figure style =====
    try:
        uel_figure_style = doc.styles['UEL Figure']
    except KeyError:
        # Tạo mới UEL Figure style
        uel_figure_style = doc.styles.add_style('UEL Figure', WD_STYLE_TYPE.PARAGRAPH)
    
    # Áp dụng cấu hình từ config
    config = UEL_FIGURE_STYLE_CONFIG
    uel_figure_style.font.name = config['font_name']
    uel_figure_style.font.size = config['font_size']
    uel_figure_style.font.italic = config['italic']
    uel_figure_style.font.bold = config['bold']
    uel_figure_style.font.color.rgb = config['color']
    _apply_font_to_style(uel_figure_style, config['font_name'])
    
    # Set alignment (căn giữa)
    if config['alignment'] == 'center':
        uel_figure_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER


def _ensure_east_asia_font(run):
    """
    Đảm bảo East Asian font được set đúng cho run
    Font được lấy từ STANDARD_FONT trong config
    """
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = OxmlElement('w:rFonts')
        rPr.append(rFonts)
    
    # Set tất cả các loại font về STANDARD_FONT
    rFonts.set(qn('w:ascii'), STANDARD_FONT)
    rFonts.set(qn('w:hAnsi'), STANDARD_FONT)
    rFonts.set(qn('w:cs'), STANDARD_FONT)
    rFonts.set(qn('w:eastAsia'), STANDARD_FONT)


def _format_toc_paragraphs(doc):
    """
    Format tất cả các đoạn văn trong mục lục (TOC) và danh mục hình ảnh
    Đảm bảo font Times New Roman 13pt cho tất cả nội dung
    Cấu hình lấy từ TOC_STYLE_CONFIG trong config.py
    """
    config = TOC_STYLE_CONFIG
    
    # Duyệt qua tất cả paragraphs trong document
    for paragraph in doc.paragraphs:
        style_name = paragraph.style.name if paragraph.style else ""
        para_text = paragraph.text[:50] if paragraph.text else ""
        
        # Kiểm tra nếu là TOC paragraph hoặc có chứa field TOC
        is_toc_para = (
            style_name.startswith('TOC') or 
            style_name.startswith('toc') or
            'MỤC LỤC' in para_text or
            'DANH MỤC HÌNH' in para_text
        )
        
        if is_toc_para or style_name.startswith('TOC'):
            # Set font cho tất cả runs trong paragraph
            for run in paragraph.runs:
                run.font.name = config['font_name']
                run.font.size = config['font_size']
                run.font.bold = config['bold']
                run.font.italic = config['italic']
                _ensure_east_asia_font(run)
                
                # Force set trong XML để đảm bảo Word kế thừa đúng
                _force_run_font_in_xml(run, config['font_name'], config['font_size'])
            
            # Set line spacing
            if paragraph.paragraph_format:
                paragraph.paragraph_format.line_spacing = config['line_spacing']


def _force_run_font_in_xml(run, font_name, font_size):
    """
    Force set font trong XML level để đảm bảo Word kế thừa đúng format
    Đặc biệt quan trọng cho TOC fields
    """
    r_pr = run._element.get_or_add_rPr()
    
    # Xóa các font properties cũ
    for tag in ["rFonts", "sz", "szCs"]:
        old = r_pr.find(qn(f"w:{tag}"))
        if old is not None:
            r_pr.remove(old)
    
    # Set font Times New Roman cho tất cả font types
    r_fonts = OxmlElement("w:rFonts")
    r_fonts.set(qn("w:ascii"), font_name)
    r_fonts.set(qn("w:hAnsi"), font_name)
    r_fonts.set(qn("w:eastAsia"), font_name)
    r_fonts.set(qn("w:cs"), font_name)
    r_pr.insert(0, r_fonts)
    
    # Set size (trong half-points: 13pt = 26)
    size_half_pts = int(font_size.pt * 2)
    sz = OxmlElement("w:sz")
    sz.set(qn("w:val"), str(size_half_pts))
    r_pr.append(sz)
    
    sz_cs = OxmlElement("w:szCs")
    sz_cs.set(qn("w:val"), str(size_half_pts))
    r_pr.append(sz_cs)


def _set_run_format(run, size, bold=False, italic=False, color=None):
    """
    Set định dạng cho một run (đoạn text)
    Font luôn được set về STANDARD_FONT từ config
    
    Args:
        run: Run object cần format
        size: Cỡ chữ (Pt object)
        bold: In đậm hay không
        italic: In nghiêng hay không
        color: Màu chữ (RGBColor object)
    """
    from app.config import STANDARD_FONT
    
    run.font.name = STANDARD_FONT
    run.font.size = size
    run.font.bold = bold
    run.font.italic = italic
    
    if color:
        run.font.color.rgb = color
    
    # Đảm bảo East Asian font được set
    _ensure_east_asia_font(run)

