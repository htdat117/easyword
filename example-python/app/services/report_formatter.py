import logging
import re
from io import BytesIO
from html import escape

from docx import Document 
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor, Cm
from docx.text.paragraph import Paragraph

# --- CHÚ Ý: Đảm bảo các biến này tồn tại trong app.config của bạn ---
# Nếu chạy test độc lập, hãy bỏ comment dòng dưới để định nghĩa biến tạm
# BODY_FONT_SIZE = Pt(13)
# HEADING_FONT_SIZE = Pt(14)
# PAGE_NUMBER_FONT_SIZE = Pt(10)
# PARAGRAPH_INDENT = Cm(1.27)
# STANDARD_FONT = "Times New Roman"
# TOC_FONT_SIZE = Pt(13)
# UEL_MARGINS = {"top": Cm(2), "bottom": Cm(2), "left": Cm(3), "right": Cm(2)}

from app.config import (
    BODY_FONT_SIZE,
    HEADING_FONT_SIZE,
    PAGE_NUMBER_FONT_SIZE,
    PARAGRAPH_INDENT,
    STANDARD_FONT,
    TOC_FONT_SIZE,
    UEL_MARGINS,
)
from app.utils.options import merge_options


def _ensure_east_asia_font(run):
    try:
        r_pr = run._element.get_or_add_rPr()
        r_fonts = r_pr.rFonts
        if r_fonts is None:
            r_fonts = OxmlElement("w:rFonts")
            r_pr.append(r_fonts)
        r_fonts.set(qn("w:eastAsia"), STANDARD_FONT)
    except Exception:
        pass


def _set_run_format(run, size, bold=False, color=None, italic=False):
    try:
        run.font.name = STANDARD_FONT
        run.font.size = size
        run.font.bold = bold
        run.font.italic = italic
        if color:
            run.font.color.rgb = color
        _ensure_east_asia_font(run)
    except Exception:
        pass


def _paragraph_has_image(paragraph):
    """
    Kiểm tra paragraph có chứa hình ảnh không (an toàn, không làm mất hình)
    """
    try:
        # Kiểm tra trong XML: w:drawing (hình ảnh hiện đại) hoặc w:pict (hình ảnh cũ/shape)
        has_drawing = paragraph._element.xpath('.//w:drawing')
        has_pict = paragraph._element.xpath('.//w:pict')
        return bool(has_drawing or has_pict)
    except Exception:
        return False


def _clean_leading_spaces(paragraph):
    """
    Xóa khoảng trắng đầu dòng - AN TOÀN: Chỉ xử lý text, không ảnh hưởng hình ảnh
    """
    try:
        if _paragraph_has_image(paragraph):
            return
        for run in paragraph.runs:
            if not run.text:
                continue
            cleaned = run.text.lstrip()
            run.text = cleaned
            if cleaned:
                break
    except Exception:
        pass


def _collapse_internal_spaces(paragraph):
    """
    Gộp khoảng trắng thừa - AN TOÀN: Chỉ xử lý text, không ảnh hưởng hình ảnh
    """
    try:
        if _paragraph_has_image(paragraph):
            return
        for run in paragraph.runs:
            if not run.text:
                continue
            new_text = re.sub(r"[ \t\u00A0]{2,}", " ", run.text)
            if new_text != run.text:
                run.text = new_text
    except Exception:
        pass


def _remove_paragraph(paragraph):
    try:
        parent = paragraph._element.getparent()
        if parent is not None:
            parent.remove(paragraph._element)
    except Exception:
        pass


def _looks_like_heading(text):
    text = text.strip()
    if not text or len(text) > 120:
        return False
    if text.endswith("."):
        return False
    return text.isupper()

def _detect_numbered_heading(text):
    text = text.strip()
    if not text:
        return None, False
    pattern = r'^(\d+(?:\.\d+)*)\.\s+(.+)$'
    match = re.match(pattern, text)
    if match:
        number_part = match.group(1)
        level = number_part.count('.') + 1
        level = min(max(level, 1), 6)
        return level, True
    return None, False

def _document_has_toc(doc):
    for paragraph in doc.paragraphs:
        for run in paragraph.runs:
            # Check simple field
            for child in run._element:
                if child.tag.endswith("fldSimple"):
                    instr = child.get(qn("w:instr"))
                    if instr and "TOC" in instr:
                        return True
            # Check complex field
            if "TOC" in run.text and "instrText" in [c.tag.split('}')[-1] for c in run._element.iter()]:
                 return True
    return False

def _find_toc_anchor(doc):
    for paragraph in doc.paragraphs:
        style_name = paragraph.style.name if paragraph.style else ""
        if style_name.lower().startswith("heading"):
            return paragraph
    return doc.paragraphs[0] if doc.paragraphs else None

def _insert_paragraph_after(paragraph, text=""):
    try:
        new_p = OxmlElement("w:p")
        paragraph._p.addnext(new_p)
        new_para = Paragraph(new_p, paragraph._parent)
        if text:
            new_para.add_run(text)
        return new_para
    except Exception:
        logging.warning("Không thể chèn đoạn văn sau vị trí yêu cầu.")
        return paragraph

def _add_section_break(paragraph):
    """
    Thêm section break (ngắt trang với section mới) vào paragraph
    """
    try:
        # Lấy document từ paragraph
        doc = None
        try:
            # Thử lấy document từ part
            if hasattr(paragraph, 'part') and hasattr(paragraph.part, 'document'):
                doc = paragraph.part.document
            elif hasattr(paragraph, '_parent') and hasattr(paragraph._parent, 'part'):
                doc = paragraph._parent.part.document
        except Exception:
            pass
        
        p_pr = paragraph._p.get_or_add_pPr()
        old_sect_pr = p_pr.find(qn("w:sectPr"))
        if old_sect_pr is not None:
            p_pr.remove(old_sect_pr)
        
        sect_pr = OxmlElement("w:sectPr")
        
        # Thiết lập kiểu section break: nextPage (trang mới)
        pg_type = OxmlElement("w:type")
        pg_type.set(qn("w:val"), "nextPage")
        sect_pr.append(pg_type)
        
        # Copy margins từ section hiện tại nếu có
        if doc and hasattr(doc, 'sections') and len(doc.sections) > 0:
            try:
                current_section = doc.sections[-1]
                sect_pr_margins = current_section._sectPr.find(qn("w:pgMar"))
                if sect_pr_margins is not None:
                    new_margins = OxmlElement("w:pgMar")
                    for attr in ["top", "right", "bottom", "left", "header", "footer", "gutter"]:
                        val = sect_pr_margins.get(qn(f"w:{attr}"))
                        if val is not None:
                            new_margins.set(qn(f"w:{attr}"), val)
                    sect_pr.append(new_margins)
            except Exception as e:
                logging.debug(f"Không thể copy margins: {e}")
        
        p_pr.append(sect_pr)
        logging.info("Đã thêm section break thành công")
    except Exception as e:
        logging.warning(f"Không thể thêm section break: {e}")

# =========================================================================
# HÀM XỬ LÝ STYLE RIÊNG CHO HÌNH ẢNH (UEL Figure)
# =========================================================================
def _ensure_caption_style(doc):
    style_name = "UEL Figure"
    try:
        # Xóa style cũ nếu có để tạo mới hoàn toàn
        try:
            doc.styles[style_name].delete()
        except (KeyError, AttributeError):
            pass
        
        style = doc.styles.add_style(style_name, WD_STYLE_TYPE.PARAGRAPH)
        # KHÔNG base on Normal để tránh inherit Cambria
        style.base_style = None
        style.hidden = False
        style.quick_style = True
    except Exception:
        style = doc.styles[style_name]
    
    # Format paragraph
    p_fmt = style.paragraph_format
    p_fmt.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_fmt.space_before = Pt(6)
    p_fmt.space_after = Pt(12)
    p_fmt.first_line_indent = Pt(0)
    p_fmt.left_indent = Pt(0)
    p_fmt.right_indent = Pt(0)
    p_fmt.line_spacing = 1.5
    
    # Format font qua API
    font = style.font
    font.name = STANDARD_FONT
    font.size = TOC_FONT_SIZE  # 13pt
    font.italic = True
    font.bold = False
    
    # Force set font trong XML
    try:
        r_pr = style._element.get_or_add_rPr()
        
        # Xóa tất cả font properties cũ
        for child in list(r_pr):
            r_pr.remove(child)
        
        # Set font Times New Roman
        r_fonts = OxmlElement("w:rFonts")
        r_fonts.set(qn("w:ascii"), STANDARD_FONT)
        r_fonts.set(qn("w:hAnsi"), STANDARD_FONT)
        r_fonts.set(qn("w:eastAsia"), STANDARD_FONT)
        r_fonts.set(qn("w:cs"), STANDARD_FONT)
        r_pr.append(r_fonts)
        
        # Set size 13pt
        sz_half_pts = int(TOC_FONT_SIZE.pt * 2)
        sz = OxmlElement("w:sz")
        sz.set(qn("w:val"), str(sz_half_pts))
        r_pr.append(sz)
        sz_cs = OxmlElement("w:szCs")
        sz_cs.set(qn("w:val"), str(sz_half_pts))
        r_pr.append(sz_cs)
        
        # Set italic
        i_elem = OxmlElement("w:i")
        i_elem.set(qn("w:val"), "1")
        r_pr.append(i_elem)
        
        logging.info(f"Đã tạo style UEL Figure với font {STANDARD_FONT} {TOC_FONT_SIZE.pt}pt")
    except Exception as e:
        logging.warning(f"Lỗi khi set font cho UEL Figure style: {e}")

def _copy_heading_style_to_toc(doc):
    for depth in range(1, 10):
        style_name = f"TOC {depth}"
        try:
            try:
                doc.styles[style_name].delete()
            except (KeyError, AttributeError):
                pass
            
            style = doc.styles.add_style(style_name, WD_STYLE_TYPE.PARAGRAPH)
            # KHÔNG base_style từ Normal để tránh inherit font Cambria
            # style.base_style = doc.styles['Normal']
            style.base_style = None
            style.hidden = False
            style.quick_style = True
            
            fmt = style.paragraph_format
            fmt.left_indent = Pt(0)
            fmt.right_indent = Pt(0)
            fmt.first_line_indent = Pt(0)
            fmt.space_before = Pt(0)
            fmt.space_after = Pt(6)
            fmt.line_spacing = 1.5
            fmt.alignment = WD_ALIGN_PARAGRAPH.LEFT
            fmt.tab_stops.clear_all()
            fmt.tab_stops.add_tab_stop(Cm(16), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
            
            p_pr = style._element.get_or_add_pPr()
            for child in list(p_pr):
                if child.tag.endswith("ind") or child.tag.endswith("tabs"):
                    p_pr.remove(child)
            ind_elem = OxmlElement("w:ind")
            ind_elem.set(qn("w:left"), "0")
            ind_elem.set(qn("w:right"), "0")
            ind_elem.set(qn("w:firstLine"), "0")
            ind_elem.set(qn("w:hanging"), "0")
            p_pr.append(ind_elem)
            
            style.font.name = STANDARD_FONT
            style.font.size = TOC_FONT_SIZE
            style.font.bold = False
            style.font.italic = False
            
            r_pr = style._element.get_or_add_rPr()
            for child in list(r_pr):
                r_pr.remove(child)
            
            r_fonts = OxmlElement("w:rFonts")
            r_fonts.set(qn("w:ascii"), STANDARD_FONT)
            r_fonts.set(qn("w:hAnsi"), STANDARD_FONT)
            r_fonts.set(qn("w:eastAsia"), STANDARD_FONT)
            r_fonts.set(qn("w:cs"), STANDARD_FONT)
            r_pr.append(r_fonts)
            
            toc_size_half_pts = int(TOC_FONT_SIZE.pt * 2)
            sz = OxmlElement("w:sz")
            sz.set(qn("w:val"), str(toc_size_half_pts))
            r_pr.append(sz)
            sz_cs = OxmlElement("w:szCs")
            sz_cs.set(qn("w:val"), str(toc_size_half_pts))
            r_pr.append(sz_cs)
            
            b_elem = OxmlElement("w:b")
            b_elem.set(qn("w:val"), "0")
            r_pr.append(b_elem)
            
        except Exception as e:
            logging.warning(f"Lỗi tạo/style TOC {style_name}: {e}")
            continue

# =========================================================================
# HÀM XỬ LÝ NHẬN DIỆN VÀ ĐÁNH SỐ CAPTION AN TOÀN
# =========================================================================
def _force_caption_font(run):
    """Force set font Times New Roman 13pt cho caption run"""
    # Set qua API
    run.font.name = STANDARD_FONT
    run.font.size = TOC_FONT_SIZE
    run.font.bold = False
    run.font.italic = True
    _ensure_east_asia_font(run)
    
    # Force set trong XML
    r_pr = run._element.get_or_add_rPr()
    
    # Xóa font cũ
    for child in list(r_pr):
        tag_name = child.tag.split('}')[-1] if '}' in child.tag else child.tag
        if tag_name in ["rFonts", "sz", "szCs"]:
            r_pr.remove(child)
    
    # Set font Times New Roman
    r_fonts = OxmlElement("w:rFonts")
    r_fonts.set(qn("w:ascii"), STANDARD_FONT)
    r_fonts.set(qn("w:hAnsi"), STANDARD_FONT)
    r_fonts.set(qn("w:eastAsia"), STANDARD_FONT)
    r_fonts.set(qn("w:cs"), STANDARD_FONT)
    r_pr.insert(0, r_fonts)
    
    # Set size 13pt
    sz_half_pts = int(TOC_FONT_SIZE.pt * 2)
    sz = OxmlElement("w:sz")
    sz.set(qn("w:val"), str(sz_half_pts))
    r_pr.append(sz)
    sz_cs = OxmlElement("w:szCs")
    sz_cs.set(qn("w:val"), str(sz_half_pts))
    r_pr.append(sz_cs)

def _process_captions(doc):
    _ensure_caption_style(doc)
    figure_count = 0
    pattern = re.compile(r'^(Hình|Sơ đồ|Bảng|Biểu đồ)[\s\d\.]*[:\.]?\s+(.+)$', re.IGNORECASE)
    for paragraph in doc.paragraphs:
        has_image = _paragraph_has_image(paragraph)
        text = paragraph.text.strip()
        if not text: continue
        match = pattern.match(text)
        if match:
            figure_count += 1
            prefix = "Hình" 
            content = match.group(2).strip()
            new_text = f"{prefix} {figure_count}: {content}"
            paragraph.style = "UEL Figure"
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            if has_image:
                text_replaced = False
                for run in paragraph.runs:
                    if run.text.strip():
                        if not text_replaced:
                            run.text = new_text
                            _force_caption_font(run)
                            text_replaced = True
                        else:
                            run.text = ""
            else:
                paragraph.text = "" 
                run = paragraph.add_run(new_text)
                _force_caption_font(run)
    
    if figure_count > 0:
        logging.info(f"Đã xử lý {figure_count} captions với font {STANDARD_FONT} {TOC_FONT_SIZE.pt}pt")

# =========================================================================
# HÀM FORMAT LẠI TẤT CẢ CÁC PARAGRAPH TOC
# =========================================================================
def _format_toc_paragraphs(doc):
    """
    Format lại tất cả các paragraph TOC để đảm bảo font Times New Roman 13pt
    FORCE OVERRIDE mọi font setting từ Normal style
    """
    toc_count = 0
    for paragraph in doc.paragraphs:
        style_name = paragraph.style.name if paragraph.style else ""
        text = paragraph.text.strip()
        
        # Kiểm tra xem có phải paragraph TOC không
        if style_name.startswith("TOC") or "MỤC LỤC" in text or "DANH MỤC" in text:
            toc_count += 1
            
            # Format paragraph
            try:
                fmt = paragraph.paragraph_format
                if style_name.startswith("TOC"):
                    fmt.line_spacing = 1.5
                    fmt.space_before = Pt(0)
                    fmt.space_after = Pt(6)
            except Exception:
                pass
            
            # Format tất cả runs trong paragraph
            for run in paragraph.runs:
                try:
                    # Force set font trong XML TRƯỚC - QUAN TRỌNG!
                    r_pr = run._element.get_or_add_rPr()
                    
                    # XÓA HOÀN TOÀN tất cả font properties cũ
                    for child in list(r_pr):
                        tag_name = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                        if tag_name in ["rFonts", "sz", "szCs", "rStyle"]:
                            r_pr.remove(child)
                    
                    # Set font Times New Roman - FORCE OVERRIDE
                    r_fonts = OxmlElement("w:rFonts")
                    r_fonts.set(qn("w:ascii"), STANDARD_FONT)
                    r_fonts.set(qn("w:hAnsi"), STANDARD_FONT)
                    r_fonts.set(qn("w:eastAsia"), STANDARD_FONT)
                    r_fonts.set(qn("w:cs"), STANDARD_FONT)
                    r_pr.insert(0, r_fonts)  # Insert ở đầu để đảm bảo priority
                    
                    # Set size 13pt
                    toc_size_half_pts = int(TOC_FONT_SIZE.pt * 2)
                    sz = OxmlElement("w:sz")
                    sz.set(qn("w:val"), str(toc_size_half_pts))
                    r_pr.append(sz)
                    sz_cs = OxmlElement("w:szCs")
                    sz_cs.set(qn("w:val"), str(toc_size_half_pts))
                    r_pr.append(sz_cs)
                    
                    # Set qua API sau (để đồng bộ)
                    run.font.name = STANDARD_FONT
                    run.font.size = TOC_FONT_SIZE
                    run.font.bold = False if style_name.startswith("TOC") else run.font.bold
                    _ensure_east_asia_font(run)
                    
                except Exception as e:
                    logging.warning(f"Lỗi format run trong TOC paragraph: {e}")
    
    if toc_count > 0:
        logging.info(f"Đã FORCE format {toc_count} paragraphs TOC với Times New Roman 13pt")

# =========================================================================
# HÀM CHÈN TOC (MỤC LỤC) VÀ TOF (DANH MỤC HÌNH)
# =========================================================================
def _insert_table_of_contents(doc, options, anchor=None):
    if not options.get("insert_toc", True):
        return
    _copy_heading_style_to_toc(doc)
    _ensure_caption_style(doc) 
    
    first_paragraph = doc.paragraphs[0] if doc.paragraphs else None
    if first_paragraph is not None:
        toc_heading = first_paragraph.insert_paragraph_before("MỤC LỤC")
    else:
        toc_heading = doc.add_paragraph("MỤC LỤC")
    
    toc_heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
    toc_heading.paragraph_format.space_after = Pt(6)
    for run in toc_heading.runs:
        _set_run_format(run, TOC_FONT_SIZE, bold=True)
    
    toc_body = _insert_paragraph_after(toc_heading)
    fmt_body = toc_body.paragraph_format
    fmt_body.tab_stops.clear_all()
    fmt_body.tab_stops.add_tab_stop(Cm(16), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
    fmt_body.line_spacing = 1.5
    fmt_body.space_before = Pt(0)
    fmt_body.space_after = Pt(0)
    
    # Tạo run với format font trước khi chèn field
    run = toc_body.add_run()
    
    # Force set font trong XML TRƯỚC khi chèn field
    r_pr = run._element.get_or_add_rPr()
    
    # Xóa font cũ
    for tag in ["rFonts", "sz", "szCs"]:
        old = r_pr.find(qn(f"w:{tag}"))
        if old is not None:
            r_pr.remove(old)
    
    # Set font Times New Roman
    r_fonts = OxmlElement("w:rFonts")
    r_fonts.set(qn("w:ascii"), STANDARD_FONT)
    r_fonts.set(qn("w:hAnsi"), STANDARD_FONT)
    r_fonts.set(qn("w:eastAsia"), STANDARD_FONT)
    r_fonts.set(qn("w:cs"), STANDARD_FONT)
    r_pr.append(r_fonts)
    
    # Set size 13pt
    toc_size_half_pts = int(TOC_FONT_SIZE.pt * 2)
    sz = OxmlElement("w:sz")
    sz.set(qn("w:val"), str(toc_size_half_pts))
    r_pr.append(sz)
    sz_cs = OxmlElement("w:szCs")
    sz_cs.set(qn("w:val"), str(toc_size_half_pts))
    r_pr.append(sz_cs)
    
    # Set qua API cũng
    run.font.name = STANDARD_FONT
    run.font.size = TOC_FONT_SIZE
    _ensure_east_asia_font(run)
    
    logging.info(f"Đang tạo TOC với font = {STANDARD_FONT}, size = {TOC_FONT_SIZE.pt}pt")
    
    fld = OxmlElement("w:fldSimple")
    fld.set(qn("w:instr"), 'TOC \\o "1-3" \\h \\z \\u')
    run._r.append(fld)
    
    current_para = toc_body
    toc_page_break = _insert_paragraph_after(current_para)
    toc_page_break.add_run().add_break(WD_BREAK.PAGE)
    current_para = toc_page_break
    
    tof_heading = _insert_paragraph_after(current_para, "DANH MỤC HÌNH ẢNH")
    tof_heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
    tof_heading.paragraph_format.space_before = Pt(18)
    tof_heading.paragraph_format.space_after = Pt(6)
    for run in tof_heading.runs:
        _set_run_format(run, TOC_FONT_SIZE, bold=True)
    
    tof_body = _insert_paragraph_after(tof_heading)
    fmt_tof = tof_body.paragraph_format
    fmt_tof.tab_stops.clear_all()
    fmt_tof.tab_stops.add_tab_stop(Cm(16), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
    fmt_tof.line_spacing = 1.5
    fmt_tof.space_before = Pt(0)
    fmt_tof.space_after = Pt(0)
    
    # Tạo run với format font trước khi chèn field
    run_tof = tof_body.add_run()
    
    # Force set font trong XML TRƯỚC khi chèn field
    r_pr_tof = run_tof._element.get_or_add_rPr()
    
    # Xóa font cũ
    for tag in ["rFonts", "sz", "szCs"]:
        old = r_pr_tof.find(qn(f"w:{tag}"))
        if old is not None:
            r_pr_tof.remove(old)
    
    # Set font Times New Roman
    r_fonts_tof = OxmlElement("w:rFonts")
    r_fonts_tof.set(qn("w:ascii"), STANDARD_FONT)
    r_fonts_tof.set(qn("w:hAnsi"), STANDARD_FONT)
    r_fonts_tof.set(qn("w:eastAsia"), STANDARD_FONT)
    r_fonts_tof.set(qn("w:cs"), STANDARD_FONT)
    r_pr_tof.append(r_fonts_tof)
    
    # Set size 13pt
    toc_size_half_pts = int(TOC_FONT_SIZE.pt * 2)
    sz_tof = OxmlElement("w:sz")
    sz_tof.set(qn("w:val"), str(toc_size_half_pts))
    r_pr_tof.append(sz_tof)
    sz_cs_tof = OxmlElement("w:szCs")
    sz_cs_tof.set(qn("w:val"), str(toc_size_half_pts))
    r_pr_tof.append(sz_cs_tof)
    
    # Set qua API cũng
    run_tof.font.name = STANDARD_FONT
    run_tof.font.size = TOC_FONT_SIZE
    _ensure_east_asia_font(run_tof)
    
    tof_fld = OxmlElement("w:fldSimple")
    tof_fld.set(qn("w:instr"), 'TOC \\h \\z \\t "UEL Figure,1"')
    run_tof._r.append(tof_fld)
    
    current_para = tof_body
    hint = _insert_paragraph_after(
        current_para,
        "(* Nhấn Ctrl + A rồi F9 trong Word (chọn Update Entire Table) để cập nhật cả 2 mục lục *)",
    )
    hint.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in hint.runs:
        _set_run_format(run, TOC_FONT_SIZE, italic=True, color=RGBColor(200, 0, 0))
    
    page_break_para = _insert_paragraph_after(hint)
    page_break_para.add_run().add_break(WD_BREAK.PAGE)
    
    # Tạo section break để ngắt việc đánh số trang
    _add_section_break(page_break_para)

# =========================================================================
# [SỬA QUAN TRỌNG] HÀM TẠO FIELD PAGE NUMBER BẰNG COMPLEX FIELD
# =========================================================================
def _create_element(name):
    return OxmlElement(name)

def _create_attribute(element, name, value):
    element.set(qn(name), value)

def _add_page_number_field_simple(run, instr="PAGE"):
    """
    Chèn field code trang bằng w:fldSimple (Simple Field)
    Cách này đơn giản và đáng tin cậy hơn cho số trang.
    """
    # Xóa text mặc định của run
    run.text = ""
    
    # Lưu lại rPr (format properties) nếu có
    r_pr = run._element.find(qn('w:rPr'))
    
    # Xóa tất cả các element hiện có trong run
    for child in list(run._element):
        run._element.remove(child)
    
    # Khôi phục rPr nếu có để giữ format
    if r_pr is not None:
        run._element.append(r_pr)
    
    # Tạo Simple Field với text node bên trong
    fld = OxmlElement('w:fldSimple')
    fld.set(qn('w:instr'), instr)
    
    # Thêm text node vào trong field để hiển thị placeholder
    t = OxmlElement('w:t')
    t.text = "1"  # Placeholder - Word sẽ update thành số trang thực
    fld.append(t)
    
    run._element.append(fld)

def _add_page_number_field(run, instr="PAGE"):
    """
    Chèn field code trang bằng w:fldChar (Complex Field)
    Cách này đảm bảo field nằm TRONG run và nhận định dạng font của run.
    Theo chuẩn Office Open XML, rPr PHẢI đứng đầu tiên trong run.
    """
    # Xóa text mặc định của run nếu có
    run.text = ""
    
    # Lưu lại rPr để đảm bảo format font không bị mất
    r_pr = run._element.find(qn('w:rPr'))
    
    # Xóa tất cả các element
    for child in list(run._element):
        run._element.remove(child)
    
    # Thêm lại rPr vào đầu tiên nếu có (theo chuẩn Office Open XML)
    if r_pr is not None:
        run._element.insert(0, r_pr)
    
    # 1. Start Complex Field
    fld_char_begin = OxmlElement('w:fldChar')
    fld_char_begin.set(qn('w:fldCharType'), 'begin')
    run._element.append(fld_char_begin)

    # 2. Instruction Text
    instr_text = OxmlElement('w:instrText')
    instr_text.set(qn('xml:space'), 'preserve')
    instr_text.text = instr
    run._element.append(instr_text)

    # 3. Separate Field (chia tách lệnh và kết quả hiển thị)
    fld_char_separate = OxmlElement('w:fldChar')
    fld_char_separate.set(qn('w:fldCharType'), 'separate')
    run._element.append(fld_char_separate)

    # 4. Display Text (Placeholder) - hiển thị số "1" cho đến khi Word update field
    t = OxmlElement('w:t')
    t.text = "1"
    run._element.append(t)

    # 5. End Complex Field
    fld_char_end = OxmlElement('w:fldChar')
    fld_char_end.set(qn('w:fldCharType'), 'end')
    run._element.append(fld_char_end)

def _apply_page_numbers(doc, options):
    if not options.get("add_page_numbers", True):
        logging.info("add_page_numbers=False, bỏ qua đánh số trang")
        return
    
    # Xác định kiểu đánh số
    instr_main = "PAGE"
    instr_toc = "PAGE \\* ROMAN" if options.get("page_number_style") == "roman" else "PAGE"
    
    # Kiểm tra xem có Mục lục không để xác định Section bắt đầu đánh số 1
    has_toc = _document_has_toc(doc) or options.get("insert_toc", True)
    logging.info(f"Số sections trong document: {len(doc.sections)}, has_toc: {has_toc}")
    
    # Nếu có TOC VÀ có nhiều hơn 1 section, nội dung chính ở Section 1 (bắt đầu đánh số từ 1)
    # Nếu chỉ có 1 section, bắt đầu đánh số từ section đó
    target_section_idx = 1 if (has_toc and len(doc.sections) > 1) else 0
    logging.info(f"Target section để bắt đầu đánh số từ 1: {target_section_idx}")
    
    for idx, section in enumerate(doc.sections):
        logging.info(f"Đang xử lý section {idx}/{len(doc.sections)-1}")
        
        # --- XỬ LÝ FOOTER ---
        # Đảm bảo footer tồn tại - truy cập footer để khởi tạo nếu chưa có
        try:
            footer = section.footer
            logging.info(f"Section {idx}: Đã truy cập footer, số paragraphs hiện tại: {len(footer.paragraphs)}")
        except Exception as e:
            logging.error(f"Không thể truy cập footer của section {idx}: {e}")
            continue
        
        # Ngắt kết nối với section trước (quan trọng để restart numbering)
        try:
            section.footer.is_linked_to_previous = False
            logging.info(f"Section {idx}: Đã ngắt kết nối footer với section trước")
        except AttributeError as e:
            logging.warning(f"Section {idx}: Không thể ngắt kết nối footer: {e}")
            pass
        
        # Xóa các đoạn văn cũ trong footer
        old_para_count = len(footer.paragraphs)
        while footer.paragraphs:
            _remove_paragraph(footer.paragraphs[0])
        logging.info(f"Section {idx}: Đã xóa {old_para_count} paragraphs cũ trong footer")
        
        # Nếu là trang bìa (idx=0, có mục lục VÀ có nhiều hơn 1 section) thì KHÔNG đánh số
        # Nếu chỉ có 1 section thì vẫn phải đánh số dù có TOC
        if has_toc and idx == 0 and len(doc.sections) > 1:
            logging.info(f"Section {idx}: Bỏ qua (trang bìa)")
            continue
        
        # Tạo đoạn văn mới chứa số trang
        para = footer.add_paragraph()
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        para_format = para.paragraph_format
        para_format.space_before = Pt(0)
        para_format.space_after = Pt(0)
        
        # Chọn kiểu số (La mã cho TOC, Số thường cho nội dung nếu cần tách biệt, ở đây dùng chung)
        # Nếu muốn TOC dùng La Mã, bạn có thể chỉnh logic tại đây. 
        # Ví dụ: nếu idx < target_section_idx dùng instr_toc
        current_instr = instr_main
        
        # Sử dụng Complex Field thay vì Simple Field vì đáng tin cậy hơn
        # Tạo run để chứa field
        run = para.add_run("")
        
        # Format font cho run TRƯỚC khi chèn field để field thừa hưởng format này
        try:
            # Format font thông qua API
            run.font.name = STANDARD_FONT
            run.font.size = PAGE_NUMBER_FONT_SIZE
            _ensure_east_asia_font(run)
            
            logging.info(f"Section {idx}: Đang set font = {STANDARD_FONT}, size = {PAGE_NUMBER_FONT_SIZE.pt}pt")
            
            # Force set font trong XML để đảm bảo field thừa hưởng
            r_pr = run._element.get_or_add_rPr()
            
            # Xóa các font properties cũ
            for tag in ["rFonts", "sz", "szCs"]:
                old = r_pr.find(qn(f"w:{tag}"))
                if old is not None:
                    r_pr.remove(old)
            
            # Set mới font properties
            r_fonts = OxmlElement("w:rFonts")
            r_fonts.set(qn("w:ascii"), STANDARD_FONT)
            r_fonts.set(qn("w:hAnsi"), STANDARD_FONT)
            r_fonts.set(qn("w:eastAsia"), STANDARD_FONT)
            r_fonts.set(qn("w:cs"), STANDARD_FONT)
            r_pr.append(r_fonts)
            
            page_size_half_pts = int(PAGE_NUMBER_FONT_SIZE.pt * 2)
            logging.info(f"Section {idx}: Font size trong XML = {page_size_half_pts} half-points ({page_size_half_pts/2}pt)")
            
            sz = OxmlElement("w:sz")
            sz.set(qn("w:val"), str(page_size_half_pts))
            r_pr.append(sz)
            sz_cs = OxmlElement("w:szCs")
            sz_cs.set(qn("w:val"), str(page_size_half_pts))
            r_pr.append(sz_cs)
        except Exception as e:
            logging.error(f"Lỗi format font cho số trang: {e}")
        
        # Chèn Complex Field - đáng tin cậy hơn Simple Field
        _add_page_number_field(run, current_instr)
        
        logging.info(f"Đã thêm field số trang vào footer section {idx}")

        # --- XỬ LÝ SỐ TRANG BẮT ĐẦU (RESTART NUMBERING) ---
        # Chỉ reset về 1 tại section đầu tiên của phần Nội dung
        if idx == target_section_idx:
            try:
                sect_pr = section._sectPr
                pg_num_type = sect_pr.find(qn("w:pgNumType"))
                if pg_num_type is None:
                    pg_num_type = OxmlElement("w:pgNumType")
                    sect_pr.append(pg_num_type)
                
                # Bắt buộc bắt đầu từ 1
                pg_num_type.set(qn("w:start"), "1")
                pg_num_type.set(qn("w:fmt"), "decimal")
            except Exception as e:
                logging.warning(f"Lỗi đặt start page number: {e}")

# =========================================================================
# CÁC HÀM XỬ LÝ CHÍNH
# =========================================================================
def _standardize_paragraph(paragraph, options):
    style_name = paragraph.style.name if paragraph.style else ""
    if style_name in ["UEL Figure", "Caption"] or style_name.startswith("TOC"):
        return
    
    has_image = _paragraph_has_image(paragraph)
    text = paragraph.text
    
    if options.get("clean_whitespace", True) and not has_image:
        _clean_leading_spaces(paragraph)
        _collapse_internal_spaces(paragraph)
        text = paragraph.text
        
    normalized = (text or "").strip()
    
    if not normalized and not has_image:
        _remove_paragraph(paragraph)
        return
        
    if has_image and not normalized:
        if options.get("normalize_font", True):
            for run in paragraph.runs:
                if run.text:
                    _set_run_format(run, BODY_FONT_SIZE, bold=False, italic=False)
        return
    
    is_heading = False
    heading_level = None
    
    if options.get("heading_detection", True):
        if style_name.lower().startswith("heading"):
            is_heading = True
            try:
                level_str = style_name.split()[-1]
                if level_str.isdigit():
                    heading_level = int(level_str)
            except Exception:
                heading_level = 1
        elif options.get("auto_numbered_heading", True):
            detected_level, detected_heading = _detect_numbered_heading(normalized)
            if detected_heading:
                is_heading = True
                heading_level = detected_level
                try:
                    paragraph.style = f"Heading {heading_level}"
                except Exception:
                    pass
        elif _looks_like_heading(normalized):
            is_heading = True
            heading_level = 1
            try:
                paragraph.style = "Heading 1"
            except Exception:
                pass
                
    if options.get("normalize_font", True):
        target_size = HEADING_FONT_SIZE if is_heading else BODY_FONT_SIZE
        for run in paragraph.runs:
            try:
                run_has_image = (run._element.xpath('.//w:drawing') or
                                run._element.xpath('.//w:pict'))
                if run_has_image:
                    continue 
            except Exception:
                pass
            
            if is_heading:
                bold_flag = (heading_level == 1) if heading_level is not None else False
            else:
                bold_flag = bool(run.font.bold)
            italic_flag = bool(run.font.italic)
            _set_run_format(run, target_size, bold=bold_flag, italic=italic_flag)
            
    if options.get("indent_spacing", True):
        fmt = paragraph.paragraph_format
        clean_text = paragraph.text.strip()
        if is_heading:
            fmt.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            fmt.space_before = Pt(0)
            fmt.space_after = Pt(6)
            fmt.first_line_indent = Pt(0)
            fmt.left_indent = Pt(0)
            fmt.line_spacing = 1.5
        else:
            fmt.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            fmt.line_spacing = options.get("line_spacing", 1.3)
            fmt.space_before = Pt(0)
            fmt.space_after = Pt(6)
            if clean_text.startswith(("-", "+", "•", "*")):
                fmt.first_line_indent = Pt(0)
                fmt.left_indent = Pt(0)
            elif 0 < len(clean_text) < 50:
                fmt.first_line_indent = Pt(0)
                fmt.left_indent = Pt(0)
            else:
                fmt.first_line_indent = PARAGRAPH_INDENT
                fmt.left_indent = Pt(0)

def apply_standard_formatting(doc: Document, options=None):
    options = merge_options(options)
    
    if options.get("adjust_margins", True):
        try:
            for section in doc.sections:
                section.top_margin = UEL_MARGINS["top"]
                section.bottom_margin = UEL_MARGINS["bottom"]
                section.left_margin = UEL_MARGINS["left"]
                section.right_margin = UEL_MARGINS["right"]
        except Exception:
            logging.warning("Không thể áp dụng lề cho tài liệu.")
            
    _process_captions(doc)
    _copy_heading_style_to_toc(doc)
    
    for paragraph in list(doc.paragraphs):
        _standardize_paragraph(paragraph, options)
        
    if options.get("format_tables", True):
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in list(cell.paragraphs):
                        _standardize_paragraph(paragraph, options)
                        
    _insert_table_of_contents(doc, options, anchor=None)
    _copy_heading_style_to_toc(doc)
    _format_toc_paragraphs(doc)
    
    # GỌI HÀM ĐÁNH SỐ TRANG SAU CÙNG
    _apply_page_numbers(doc, options)
    
    return doc

def _add_center_line(doc, text, size=HEADING_FONT_SIZE, bold=True):
    para = doc.add_paragraph()
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _set_run_format(para.add_run(text), size, bold=bold)
    return para

def create_template_report(payload, options=None):
    student = payload.get("studentName", "Nguyễn Văn A")
    student_id = payload.get("studentId", "K2140xxxx")
    clazz = payload.get("className", "Khoa Kinh tế đối ngoại")
    title = payload.get("reportTitle", "BÁO CÁO / TIỂU LUẬN")
    year = payload.get("year", "2024-2025")
    advisor = payload.get("advisor", "GVHD: ................................")
    location = payload.get("location", "TP. Hồ Chí Minh")
    
    doc = Document()
    _add_center_line(doc, "ĐẠI HỌC QUỐC GIA TP. HỒ CHÍ MINH", Pt(14), bold=True)
    _add_center_line(doc, "TRƯỜNG ĐẠI HỌC KINH TẾ - LUẬT", Pt(14), bold=True)
    doc.add_paragraph()
    _add_center_line(doc, title.upper(), Pt(20), bold=True)
    doc.add_paragraph()
    
    info = doc.add_paragraph()
    info.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _set_run_format(
        info.add_run(
            f"Sinh viên thực hiện: {student}\n"
            f"MSSV: {student_id}\n"
            f"Lớp/Khoa: {clazz}\n"
            f"{advisor}\n"
            f"Năm học: {year}"
        ),
        BODY_FONT_SIZE,
    )
    doc.add_paragraph()
    _add_center_line(doc, f"{location}, {year}", BODY_FONT_SIZE, bold=False)
    doc.add_page_break()
    
    doc.add_heading("LỜI CAM ĐOAN", level=1)
    doc.add_paragraph("Tôi cam đoan báo cáo này do tôi thực hiện, các số liệu và trích dẫn đều được ghi rõ nguồn gốc.")
    doc.add_heading("LỜI CẢM ƠN", level=1)
    doc.add_paragraph("Tập thể tác giả xin chân thành cảm ơn các thầy cô Trường Đại học Kinh tế - Luật đã hỗ trợ trong suốt quá trình thực hiện đề tài.")
    doc.add_heading("DANH MỤC TỪ VIẾT TẮT", level=1)
    doc.add_paragraph("UEL: Trường Đại học Kinh tế - Luật\nSV: Sinh viên\nGVHD: Giảng viên hướng dẫn")
    doc.add_heading("MỞ ĐẦU", level=1)
    doc.add_paragraph(payload.get("intro", "Trình bày lý do chọn đề tài, mục tiêu, phạm vi và phương pháp nghiên cứu."))
    doc.add_heading("CHƯƠNG 1. CƠ SỞ LÝ LUẬN", level=1)
    doc.add_paragraph("Mô tả cơ sở lý thuyết, tổng quan nghiên cứu.")
    doc.add_heading("CHƯƠNG 2. THỰC TRẠNG VẤN ĐỀ", level=1)
    doc.add_paragraph(payload.get("content", "Nêu hiện trạng thu thập được, số liệu minh họa và phân tích."))
    doc.add_paragraph("Hình: Biểu đồ tăng trưởng kinh tế")
    doc.add_heading("CHƯƠNG 3. GIẢI PHÁP KIẾN NGHỊ", level=1)
    doc.add_paragraph(payload.get("solution", "Đề xuất giải pháp, kiến nghị chính sách và điều kiện thực hiện."))
    doc.add_heading("KẾT LUẬN", level=1)
    doc.add_paragraph(payload.get("conclusion", "Tóm tắt kết quả đạt được và hướng nghiên cứu tiếp theo."))
    doc.add_heading("TÀI LIỆU THAM KHẢO", level=1)
    doc.add_paragraph(payload.get("references", "APA (2019). Publication Manual of the American Psychological Association (7th ed.). APA Publishing."))
    doc.add_heading("PHỤ LỤC", level=1)
    doc.add_paragraph("Đính kèm bảng biểu, hình ảnh, phiếu khảo sát (nếu có).")
    
    return apply_standard_formatting(doc, options)

def build_report_stream(doc: Document, download_name: str):
    output_stream = BytesIO()
    doc.save(output_stream)
    output_stream.seek(0)
    return output_stream, download_name

def generate_template_stream(payload):
    options = merge_options(payload.get("options"))
    doc = create_template_report(payload, options)
    return build_report_stream(doc, "bao-cao-uel.docx")

def format_uploaded_stream(file_bytes, filename, options_payload):
    options = merge_options(options_payload)
    doc = Document(BytesIO(file_bytes))
    apply_standard_formatting(doc, options)
    safe_name = f"formatted-{filename}"
    return build_report_stream(doc, safe_name)

def docx_to_html(doc: Document) -> str:
    html_parts = ['<div class="docx-preview" style="font-family: \'Times New Roman\', serif; max-width: 210mm; margin: 0 auto; padding: 20mm 35mm 20mm 25mm; background: white; line-height: 1.3;">']
    for paragraph in doc.paragraphs:
        if not paragraph.text.strip():
            html_parts.append('<p style="margin: 0.5em 0;"><br></p>')
            continue
        style_name = paragraph.style.name if paragraph.style else ""
        is_heading = style_name.lower().startswith("heading") if style_name else False
        is_caption = (style_name == "UEL Figure" or style_name == "Caption")
        
        if is_heading:
            level = 1
            if "heading" in style_name.lower():
                try:
                    level = int(style_name.split()[-1]) if style_name.split()[-1].isdigit() else 1
                except:
                    level = 1
            level = min(max(level, 1), 6)
            tag = f"h{level}"
        else:
            tag = "p"
            
        alignment_map = {
            WD_ALIGN_PARAGRAPH.CENTER: "center",
            WD_ALIGN_PARAGRAPH.RIGHT: "right",
            WD_ALIGN_PARAGRAPH.JUSTIFY: "justify",
            WD_ALIGN_PARAGRAPH.LEFT: "left",
        }
        align = alignment_map.get(paragraph.alignment, "left")
        para_style = f"text-align: {align};"
        
        if is_heading:
            para_style += " font-weight: bold; margin: 12pt 0;"
            if level == 1:
                para_style += " font-size: 14pt;"
            else:
                para_style += " font-size: 13pt;"
        elif is_caption:
            para_style += " font-style: italic; margin: 6pt 0; font-size: 13pt;"
        else:
            para_style += " font-size: 13pt; text-indent: 1cm; margin: 6pt 0;"
            
        html_parts.append(f'<{tag} style="{para_style}">')
        if paragraph.runs:
            for run in paragraph.runs:
                run_text = escape(run.text)
                if not run_text:
                    continue
                run_style = ""
                if run.bold:
                    run_style += "font-weight: bold; "
                if run.italic:
                    run_style += "font-style: italic; "
                if run.underline:
                    run_style += "text-decoration: underline; "
                if run_style:
                    html_parts.append(f'<span style="{run_style}">{run_text}</span>')
                else:
                    html_parts.append(run_text)
        else:
            html_parts.append(escape(paragraph.text))
        html_parts.append(f'</{tag}>')
        
    for table in doc.tables:
        html_parts.append('<table style="width: 100%; border-collapse: collapse; margin: 12pt 0; font-size: 13pt;">')
        for row in table.rows:
            html_parts.append('<tr>')
            for cell in row.cells:
                cell_text = escape(cell.text.strip().replace('\n', '<br>'))
                html_parts.append(f'<td style="border: 1px solid #ddd; padding: 8px;">{cell_text}</td>')
            html_parts.append('</tr>')
        html_parts.append('</table>')
    html_parts.append('</div>')
    
    full_html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Xem trước</title>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
            font-family: 'Times New Roman', serif;
        }}
        .docx-preview {{
            background: white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            min-height: 297mm;
            box-sizing: border-box;
        }}
        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            .docx-preview {{
                box-shadow: none;
            }}
        }}
    </style>
</head>
<body>
    {''.join(html_parts)}
</body>
</html>"""
    return full_html

def docx_to_html_stream(doc: Document) -> BytesIO:
    html_content = docx_to_html(doc)
    html_bytes = html_content.encode('utf-8')
    stream = BytesIO(html_bytes)
    stream.seek(0)
    return stream