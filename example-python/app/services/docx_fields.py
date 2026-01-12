"""
Module for docx field utilities (page numbers, etc.)
Tất cả cấu hình font được lấy từ app.config
"""
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from app.config import PAGE_NUMBER_FONT_SIZE, STANDARD_FONT


def _add_page_number_field(run, instr_text):
    """
    Thêm field số trang vào run
    
    Args:
        run: Run object cần thêm field
        instr_text: Text instruction cho field (ví dụ: 'PAGE')
    """
    fldChar1 = OxmlElement('w:fldChar')
    fldChar1.set(qn('w:fldCharType'), 'begin')
    
    instrText = OxmlElement('w:instrText')
    instrText.set(qn('xml:space'), 'preserve')
    instrText.text = instr_text
    
    fldChar2 = OxmlElement('w:fldChar')
    fldChar2.set(qn('w:fldCharType'), 'end')
    
    r_element = run._element
    r_element.append(fldChar1)
    r_element.append(instrText)
    r_element.append(fldChar2)


def _add_page_number_field_simple(run):
    """
    Thêm field số trang đơn giản (PAGE)
    """
    _add_page_number_field(run, 'PAGE')


def _add_page_number_field_complex(run, instr_text='PAGE'):
    """
    Thêm field số trang phức tạp với instruction tùy chỉnh
    
    Args:
        run: Run object
        instr_text: Instruction tùy chỉnh cho field
    """
    _add_page_number_field(run, instr_text)


def format_page_number_run(run):
    """
    Format run cho hiển thị số trang
    Font và cỡ chữ được lấy từ config
    
    Args:
        run: Run object cần format
    """
    run.font.name = STANDARD_FONT
    run.font.size = PAGE_NUMBER_FONT_SIZE
    
    # Đảm bảo tất cả các loại font đều được set
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

