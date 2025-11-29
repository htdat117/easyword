import logging
import re
from io import BytesIO

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor
from docx.text.paragraph import Paragraph

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


def _clean_leading_spaces(paragraph):
    try:
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
    try:
        for run in paragraph.runs:
            if not run.text:
                continue
            new_text = re.sub(r"[ \t\u00A0]{2,}", " ", run.text)
            if new_text != run.text:
                run.text = new_text
    except Exception:
        pass


def _remove_paragraph(paragraph):
    parent = paragraph._element.getparent()
    if parent is not None:
        parent.remove(paragraph._element)


def _looks_like_heading(text):
    text = text.strip()
    if not text or len(text) > 120:
        return False
    if text.endswith("."):
        return False
    return text.isupper()


def _document_has_toc(doc):
    for paragraph in doc.paragraphs:
        for run in paragraph.runs:
            for child in run._r:
                if child.tag.endswith("fldSimple"):
                    instr = child.get(qn("w:instr"))
                    if instr and "TOC" in instr:
                        return True
                if child.tag.endswith("instrText") and child.text and "TOC" in child.text:
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


def _copy_heading_style_to_toc(doc):
    # Đảm bảo các style TOC luôn được thiết lập đúng, bất kể có heading hay không
    for depth in range(1, 4):
        style_name = f"TOC {depth}"
        try:
            style = doc.styles[style_name]
        except KeyError:
            continue

        fmt = style.paragraph_format
        
        # Đặt mục lục không thụt lề, căn thẳng với lề trái - BẮT BUỘC về 0
        fmt.left_indent = None  # Xóa indent bằng cách đặt về None trước
        fmt.first_line_indent = None
        fmt.right_indent = None
        
        # Sau đó đặt về 0 một cách rõ ràng
        fmt.left_indent = Pt(0)
        fmt.first_line_indent = Pt(0)
        fmt.right_indent = Pt(0)
        
        # Đặt alignment về Left để đảm bảo căn trái
        fmt.alignment = WD_ALIGN_PARAGRAPH.LEFT
        
        # Xử lý trực tiếp XML để đảm bảo indent được xóa hoàn toàn
        try:
            p_pr = style._element.get_or_add_pPr()
            # Tìm và xóa element indent cũ (nếu có)
            for child in list(p_pr):
                if child.tag.endswith("ind"):
                    p_pr.remove(child)
            
            # Tạo lại indent element với giá trị 0 (tính bằng twips: 1cm = 567 twips)
            ind_elem = OxmlElement("w:ind")
            ind_elem.set(qn("w:left"), "0")  # 0 twips = 0cm
            ind_elem.set(qn("w:right"), "0")
            ind_elem.set(qn("w:firstLine"), "0")
            p_pr.append(ind_elem)
        except Exception:
            pass
        
        # Đặt font Times New Roman và cỡ chữ 13pt cho mục lục
        font = style.font
        font.name = STANDARD_FONT
        font.size = TOC_FONT_SIZE
        
        # Đảm bảo East Asia font cũng là Times New Roman
        try:
            r_pr = style._element.get_or_add_rPr()
            r_fonts = r_pr.rFonts
            if r_fonts is None:
                r_fonts = OxmlElement("w:rFonts")
                r_pr.append(r_fonts)
            r_fonts.set(qn("w:eastAsia"), STANDARD_FONT)
        except Exception:
            pass


def _insert_table_of_contents(doc, options, anchor=None):
    if not options.get("insert_toc", True):
        return
    if _document_has_toc(doc):
        return

    _copy_heading_style_to_toc(doc)

    target = anchor or _find_toc_anchor(doc)
    if target is not None:
        toc_heading = target.insert_paragraph_before("MỤC LỤC")
    else:
        toc_heading = doc.add_paragraph("MỤC LỤC")

    toc_heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
    toc_heading.paragraph_format.space_after = Pt(6)
    for run in toc_heading.runs:
        _set_run_format(run, HEADING_FONT_SIZE, bold=True)

    toc_body = _insert_paragraph_after(toc_heading)
    # Đảm bảo paragraph chứa TOC field không có indent
    fmt_body = toc_body.paragraph_format
    fmt_body.left_indent = Pt(0)
    fmt_body.first_line_indent = Pt(0)
    fmt_body.right_indent = Pt(0)
    fmt_body.space_after = Pt(6)
    
    # Đảm bảo style TOC được thiết lập lại một lần nữa sau khi đã có paragraph
    _copy_heading_style_to_toc(doc)
    
    fld = OxmlElement("w:fldSimple")
    fld.set(qn("w:instr"), 'TOC \\o "1-3" \\h \\z \\u')
    toc_body.add_run()._r.append(fld)

    hint = _insert_paragraph_after(
        toc_body,
        "(* Nhấn Ctrl + A rồi F9 trong Word để cập nhật mục lục *)",
    )
    hint.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in hint.runs:
        _set_run_format(run, Pt(11), italic=True, color=RGBColor(200, 0, 0))

    page_break_para = _insert_paragraph_after(hint)
    page_break_para.add_run().add_break(WD_BREAK.PAGE)


def _apply_page_numbers(doc, options):
    if not options.get("add_page_numbers", True):
        return

    try:
        footer_style = doc.styles["Footer"]
        footer_style.font.name = STANDARD_FONT
        footer_style.font.size = PAGE_NUMBER_FONT_SIZE
    except KeyError:
        pass

    instr = "PAGE"
    if options.get("page_number_style") == "roman":
        instr = "PAGE \\* ROMAN"

    for section in doc.sections:
        footer = section.footer
        if footer.paragraphs:
            para = footer.paragraphs[0]
            para.text = ""
        else:
            para = footer.add_paragraph()
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER

        run = para.add_run()
        fld = OxmlElement("w:fldSimple")
        fld.set(qn("w:instr"), instr)
        run._r.append(fld)
        _set_run_format(run, PAGE_NUMBER_FONT_SIZE, bold=False)


def _standardize_paragraph(paragraph, options):
    text = paragraph.text
    if options.get("clean_whitespace", True):
        _clean_leading_spaces(paragraph)
        _collapse_internal_spaces(paragraph)
        text = paragraph.text

    normalized = (text or "").strip()
    if not normalized:
        _remove_paragraph(paragraph)
        return

    is_heading = False
    style_name = paragraph.style.name if paragraph.style else ""
    if options.get("heading_detection", True):
        if style_name.lower().startswith("heading"):
            is_heading = True
        elif _looks_like_heading(normalized):
            is_heading = True
            try:
                paragraph.style = "Heading 1"
            except Exception:
                pass

    if options.get("normalize_font", True):
        target_size = HEADING_FONT_SIZE if is_heading else BODY_FONT_SIZE
        for run in paragraph.runs:
            bold_flag = is_heading or bool(run.font.bold)
            italic_flag = bool(run.font.italic)
            _set_run_format(run, target_size, bold=bold_flag, italic=italic_flag)

    if options.get("indent_spacing", True):
        fmt = paragraph.paragraph_format
        if is_heading:
            fmt.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            fmt.space_before = Pt(12)
            fmt.space_after = Pt(12)
            fmt.first_line_indent = Pt(0)
        else:
            fmt.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            fmt.first_line_indent = PARAGRAPH_INDENT
            fmt.line_spacing = options.get("line_spacing", 1.3)
            fmt.space_before = Pt(0)
            fmt.space_after = Pt(6)


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

    for paragraph in list(doc.paragraphs):
        _standardize_paragraph(paragraph, options)

    if options.get("format_tables", True):
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in list(cell.paragraphs):
                        _standardize_paragraph(paragraph, options)

    _insert_table_of_contents(doc, options, anchor=_find_toc_anchor(doc))
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

