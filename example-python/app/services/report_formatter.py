import logging
import re
from io import BytesIO
from html import escape

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
    """
    Định dạng lại các style TOC để:
    - Font: Times New Roman
    - Cỡ chữ: 13pt
    - Không thụt lề trái (0cm)
    """
    for depth in range(1, 10):  # Xử lý TOC 1 đến TOC 9
        style_name = f"TOC {depth}"
        try:
            style = doc.styles[style_name]
        except KeyError:
            continue

        # Xử lý Paragraph Format (pPr) - Indent
        try:
            p_pr = style._element.get_or_add_pPr()
            
            # Xóa tất cả các element indent cũ
            for child in list(p_pr):
                if child.tag.endswith("}ind") or child.tag.endswith("ind"):
                    p_pr.remove(child)
            
            # Tạo lại indent element với giá trị 0 (twips: 0 = 0cm)
            ind_elem = OxmlElement("w:ind")
            ind_elem.set(qn("w:left"), "0")
            ind_elem.set(qn("w:right"), "0")
            ind_elem.set(qn("w:firstLine"), "0")
            ind_elem.set(qn("w:hanging"), "0")
            p_pr.append(ind_elem)
            
            # Đặt alignment về Left
            jc_elem = p_pr.find(qn("w:jc"))
            if jc_elem is not None:
                p_pr.remove(jc_elem)
            jc_elem = OxmlElement("w:jc")
            jc_elem.set(qn("w:val"), "left")
            p_pr.append(jc_elem)
        except Exception as e:
            logging.warning(f"Không thể xử lý paragraph format cho {style_name}: {e}")

        # Xử lý Run Format (rPr) - Font
        try:
            # Lấy hoặc tạo rPr element
            r_pr = style._element.get_or_add_rPr()
            
            # Xóa font element cũ nếu có
            r_fonts_old = r_pr.find(qn("w:rFonts"))
            if r_fonts_old is not None:
                r_pr.remove(r_fonts_old)
            
            # Tạo lại rFonts với Times New Roman cho tất cả các loại font
            r_fonts = OxmlElement("w:rFonts")
            r_fonts.set(qn("w:ascii"), STANDARD_FONT)      # Font cho ASCII
            r_fonts.set(qn("w:hAnsi"), STANDARD_FONT)      # Font cho H-ANSI
            r_fonts.set(qn("w:eastAsia"), STANDARD_FONT)   # Font cho East Asia (Tiếng Việt)
            r_fonts.set(qn("w:cs"), STANDARD_FONT)         # Font cho Complex Scripts
            r_pr.append(r_fonts)
            
            # Xóa size element cũ nếu có
            sz_old = r_pr.find(qn("w:sz"))
            if sz_old is not None:
                r_pr.remove(sz_old)
            sz_old = r_pr.find(qn("w:szCs"))
            if sz_old is not None:
                r_pr.remove(sz_old)
            
            # Tạo lại size element (font size tính bằng half-points: 13pt = 26 half-points)
            sz_elem = OxmlElement("w:sz")
            sz_elem.set(qn("w:val"), "26")  # 13pt = 26 half-points
            r_pr.append(sz_elem)
            
            sz_cs_elem = OxmlElement("w:szCs")
            sz_cs_elem.set(qn("w:val"), "26")  # 13pt = 26 half-points
            r_pr.append(sz_cs_elem)
            
        except Exception as e:
            logging.warning(f"Không thể xử lý font cho {style_name}: {e}")
        
        # Cũng thiết lập qua API của python-docx để đảm bảo
        try:
            fmt = style.paragraph_format
            fmt.left_indent = Pt(0)
            fmt.first_line_indent = Pt(0)
            fmt.right_indent = Pt(0)
            fmt.alignment = WD_ALIGN_PARAGRAPH.LEFT
            
            font = style.font
            font.name = STANDARD_FONT
            font.size = TOC_FONT_SIZE
        except Exception as e:
            logging.warning(f"Không thể thiết lập style qua API cho {style_name}: {e}")


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
        # Xóa hết các old paragraphs nếu có và làm mới (tránh lỗi style cũ)
        while footer.paragraphs:
            p = footer.paragraphs[0]
            _remove_paragraph(p)
        para = footer.add_paragraph()
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # Đảm bảo paragraph này luôn đúng style
        para.style.font.name = STANDARD_FONT
        para.style.font.size = PAGE_NUMBER_FONT_SIZE

        run = para.add_run()
        fld = OxmlElement("w:fldSimple")
        fld.set(qn("w:instr"), instr)
        run._r.append(fld)
        _set_run_format(run, PAGE_NUMBER_FONT_SIZE, bold=False)
        run.font.name = STANDARD_FONT
        run.font.size = PAGE_NUMBER_FONT_SIZE

        # Ép lại mọi run trong đoạn này (dù thực tế chỉ một)
        for r in para.runs:
            try:
                r.font.name = STANDARD_FONT
                r.font.size = PAGE_NUMBER_FONT_SIZE
            except Exception:
                pass


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

    # Định dạng TOC styles TRƯỚC khi xử lý paragraphs để đảm bảo style đúng
    # (kể cả khi document đã có TOC sẵn)
    _copy_heading_style_to_toc(doc)

    for paragraph in list(doc.paragraphs):
        _standardize_paragraph(paragraph, options)

    if options.get("format_tables", True):
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in list(cell.paragraphs):
                        _standardize_paragraph(paragraph, options)

    _insert_table_of_contents(doc, options, anchor=_find_toc_anchor(doc))
    
    # Định dạng lại TOC styles SAU KHI chèn TOC để đảm bảo override mọi style mặc định
    _copy_heading_style_to_toc(doc)
    
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


def docx_to_html(doc: Document) -> str:
    """Convert Word document sang HTML để preview"""
    html_parts = ['<div class="docx-preview" style="font-family: \'Times New Roman\', serif; max-width: 210mm; margin: 0 auto; padding: 20mm 35mm 20mm 25mm; background: white; line-height: 1.3;">']
    
    for paragraph in doc.paragraphs:
        if not paragraph.text.strip():
            html_parts.append('<p style="margin: 0.5em 0;"><br></p>')
            continue
        
        style_name = paragraph.style.name if paragraph.style else ""
        is_heading = style_name.lower().startswith("heading") if style_name else False
        
        # Xác định tag và style
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
        
        # Xác định alignment
        alignment_map = {
            WD_ALIGN_PARAGRAPH.CENTER: "center",
            WD_ALIGN_PARAGRAPH.RIGHT: "right",
            WD_ALIGN_PARAGRAPH.JUSTIFY: "justify",
            WD_ALIGN_PARAGRAPH.LEFT: "left",
        }
        align = alignment_map.get(paragraph.alignment, "left")
        
        # Xây dựng style
        para_style = f"text-align: {align};"
        if is_heading:
            para_style += " font-weight: bold; margin: 12pt 0;"
            if level == 1:
                para_style += " font-size: 14pt;"
            else:
                para_style += " font-size: 13pt;"
        else:
            para_style += " font-size: 13pt; text-indent: 1cm; margin: 6pt 0;"
        
        # Xử lý runs (text formatting)
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
    
    # Xử lý tables
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
    
    # Wrap trong HTML đầy đủ với CSS
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
    """Convert Word document sang HTML stream"""
    html_content = docx_to_html(doc)
    html_bytes = html_content.encode('utf-8')
    stream = BytesIO(html_bytes)
    stream.seek(0)
    return stream

