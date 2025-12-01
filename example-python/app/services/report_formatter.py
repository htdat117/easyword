import logging
import re
from io import BytesIO
from html import escape

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.enum.style import WD_STYLE_TYPE # [MỚI] Quan trọng để tạo Style
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor, Cm # [MỚI] Dùng Cm để canh tab
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


def _detect_numbered_heading(text):
    """
    Phát hiện tiêu đề dựa trên số thứ tự.
    Ví dụ:
    - "1. Khái niệm" → (1, True)  # Heading 1
    - "1.1. Định nghĩa" → (2, True)  # Heading 2
    - "1.1.1. Chi tiết" → (3, True)  # Heading 3
    - "1.1.1.1. Mục nhỏ" → (4, True)  # Heading 4
    
    Returns: (level, is_heading) hoặc (None, False)
    """
    text = text.strip()
    if not text:
        return None, False
    
    # Pattern: bắt đầu bằng số, có thể có nhiều số cách nhau bởi dấu chấm
    # Ví dụ: "1. ", "1.1. ", "1.1.1. ", "1.1.1.1. "
    pattern = r'^(\d+(?:\.\d+)*)\.\s+(.+)$'
    match = re.match(pattern, text)
    
    if match:
        number_part = match.group(1)  # "1", "1.1", "1.1.1", etc.
        # Đếm số lượng số trong pattern (số chấm + 1)
        level = number_part.count('.') + 1
        # Giới hạn level từ 1 đến 6 (Word chỉ hỗ trợ Heading 1-6)
        level = min(max(level, 1), 6)
        return level, True
    
    return None, False


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


def _add_section_break(paragraph):
    """
    Thêm section break (next page) vào paragraph.
    Section break cho phép tách mục lục và nội dung, 
    và đánh số trang độc lập cho từng section.
    """
    try:
        p_pr = paragraph._p.get_or_add_pPr()
        
        # Xóa sectPr cũ nếu có (để tránh conflict)
        old_sect_pr = p_pr.find(qn("w:sectPr"))
        if old_sect_pr is not None:
            p_pr.remove(old_sect_pr)
        
        # Tạo sectPr element mới cho section break
        sect_pr = OxmlElement("w:sectPr")
        # Type "nextPage" tạo section break và bắt đầu trang mới
        sect_pr.set(qn("w:type"), "nextPage")
        
        # Copy các thuộc tính từ section hiện tại (margins, header, footer, etc.)
        current_section = paragraph._parent.sections[-1] if paragraph._parent.sections else None
        if current_section:
            try:
                # Copy margins
                sect_pr_margins = current_section._sectPr.find(qn("w:pgMar"))
                if sect_pr_margins is not None:
                    # Tạo lại margins element
                    new_margins = OxmlElement("w:pgMar")
                    for attr in ["top", "right", "bottom", "left", "header", "footer", "gutter"]:
                        val = sect_pr_margins.get(qn(f"w:{attr}"))
                        if val is not None:
                            new_margins.set(qn(f"w:{attr}"), val)
                    sect_pr.append(new_margins)
            except Exception:
                pass
        
        p_pr.append(sect_pr)
    except Exception as e:
        logging.warning(f"Không thể thêm section break: {e}")


def _copy_heading_style_to_toc(doc):
    """
    Định dạng lại các style TOC để:
    - Font: Times New Roman, 13pt
    - Indent: 0cm tuyệt đối (xử lý cả XML để tránh Word override)
    - Tab stops: Thiết lập tab phải ở 16cm để số trang thẳng hàng
    """
    # Xử lý từ TOC 1 đến TOC 9
    for depth in range(1, 10):
        style_name = f"TOC {depth}"
        
        # [QUAN TRỌNG] Tạo Style nếu chưa tồn tại
        try:
            style = doc.styles[style_name]
        except KeyError:
            try:
                # Tạo style mới dạng Paragraph
                style = doc.styles.add_style(style_name, WD_STYLE_TYPE.PARAGRAPH)
                # Đặt base style là Normal để tránh kế thừa linh tinh
                style.base_style = doc.styles['Normal']
                style.hidden = False
                style.quick_style = True # Hiển thị trên thanh công cụ để dễ debug
            except Exception:
                continue

        # --- 1. Xử lý Indent và Spacing qua API (Cách chính thống) ---
        try:
            fmt = style.paragraph_format
            
            # Reset toàn bộ thụt lề về 0
            fmt.left_indent = Pt(0)
            fmt.right_indent = Pt(0)
            fmt.first_line_indent = Pt(0)
            
            # Spacing
            fmt.space_before = Pt(0)
            fmt.space_after = Pt(6)
            fmt.line_spacing = 1.5
            fmt.alignment = WD_ALIGN_PARAGRAPH.LEFT
            
            # [QUAN TRỌNG] Xóa Tab cũ và đặt Tab mới cho số trang
            # Word mặc định dùng tab hanging indent, ta cần xóa nó đi
            fmt.tab_stops.clear_all()
            # Thêm tab phải (Right align) tại vị trí ~16cm (gần lề phải trang A4)
            # Kèm theo leader dots (......)
            fmt.tab_stops.add_tab_stop(Cm(16), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
            
        except Exception as e:
            logging.warning(f"Lỗi API format {style_name}: {e}")

        # --- 2. Xử lý Can thiệp sâu vào XML (Cách mạnh tay) ---
        # Đây là bước chặn việc Word tự hồi phục định dạng mặc định (0.92cm)
        try:
            p_pr = style._element.get_or_add_pPr()
            
            # Xóa các thẻ indent cũ nếu còn sót
            for child in list(p_pr):
                if child.tag.endswith("ind") or child.tag.endswith("tabs"):
                    p_pr.remove(child)
            
            # Ép thẻ Indent XML về 0
            ind_elem = OxmlElement("w:ind")
            ind_elem.set(qn("w:left"), "0")
            ind_elem.set(qn("w:right"), "0")
            ind_elem.set(qn("w:firstLine"), "0")
            ind_elem.set(qn("w:hanging"), "0")
            p_pr.append(ind_elem)
            
            # (Tab stop đã được set ở trên qua API, thường là đủ, không cần set lại bằng XML ở đây trừ khi lỗi)

        except Exception as e:
            logging.warning(f"Lỗi XML format {style_name}: {e}")

        # --- 3. Xử lý Font chữ ---
        try:
            r_pr = style._element.get_or_add_rPr()
            
            # Xóa font cũ
            for tag in ["rFonts", "sz", "szCs", "b", "i"]:
                old = r_pr.find(qn(f"w:{tag}"))
                if old is not None:
                    r_pr.remove(old)
            
            # Set Font Times New Roman
            r_fonts = OxmlElement("w:rFonts")
            r_fonts.set(qn("w:ascii"), STANDARD_FONT)
            r_fonts.set(qn("w:hAnsi"), STANDARD_FONT)
            r_fonts.set(qn("w:eastAsia"), STANDARD_FONT)
            r_fonts.set(qn("w:cs"), STANDARD_FONT)
            r_pr.append(r_fonts)
            
            # Set Size 13pt (26 half-points)
            sz = OxmlElement("w:sz")
            sz.set(qn("w:val"), "26")
            r_pr.append(sz)
            
            sz_cs = OxmlElement("w:szCs")
            sz_cs.set(qn("w:val"), "26")
            r_pr.append(sz_cs)
            
        except Exception as e:
            logging.warning(f"Lỗi Font format {style_name}: {e}")


def _insert_table_of_contents(doc, options, anchor=None):
    if not options.get("insert_toc", True):
        return
    if _document_has_toc(doc):
        # Nếu đã có TOC, vẫn cần apply lại style để sửa lỗi thụt lề
        _copy_heading_style_to_toc(doc)
        return

    # Định nghĩa Style trước khi chèn
    _copy_heading_style_to_toc(doc)

    # Luôn chèn mục lục ở đầu document (trang đầu tiên)
    # Tìm paragraph đầu tiên của document để chèn trước nó
    first_paragraph = doc.paragraphs[0] if doc.paragraphs else None
    
    if first_paragraph is not None:
        # Chèn mục lục trước paragraph đầu tiên
        toc_heading = first_paragraph.insert_paragraph_before("MỤC LỤC")
    else:
        # Nếu document rỗng, thêm paragraph mới
        toc_heading = doc.add_paragraph("MỤC LỤC")

    toc_heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
    toc_heading.paragraph_format.space_after = Pt(6)
    for run in toc_heading.runs:
        _set_run_format(run, HEADING_FONT_SIZE, bold=True)

    # Chèn Field TOC
    toc_body = _insert_paragraph_after(toc_heading)
    
    # Đặt format cho chính đoạn chứa field (đề phòng)
    fmt_body = toc_body.paragraph_format
    fmt_body.left_indent = Pt(0)
    fmt_body.first_line_indent = Pt(0)
    fmt_body.right_indent = Pt(0)
    fmt_body.space_after = Pt(6)
    fmt_body.tab_stops.clear_all()
    fmt_body.tab_stops.add_tab_stop(Cm(16), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
    
    # Gọi lại hàm định nghĩa Style để chắc chắn nó được ghi đè cuối cùng
    _copy_heading_style_to_toc(doc)
    
    # Mã Field TOC: \h (hyperlink), \z (ẩn số trang nếu thiếu), \u (dùng outline level)
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

    # Tạo page break và section break sau mục lục
    page_break_para = _insert_paragraph_after(hint)
    page_break_para.add_run().add_break(WD_BREAK.PAGE)
    
    # Thêm section break (next page) để tách mục lục và nội dung
    # Section break cho phép đánh số trang độc lập
    _add_section_break(page_break_para)


def _apply_page_numbers(doc, options):
    if not options.get("add_page_numbers", True):
        return

    try:
        if "Footer" in doc.styles:
            footer_style = doc.styles["Footer"]
        else:
            footer_style = doc.styles["Normal"]
            
        footer_style.font.name = STANDARD_FONT
        footer_style.font.size = PAGE_NUMBER_FONT_SIZE
    except KeyError:
        pass

    instr = "PAGE"
    if options.get("page_number_style") == "roman":
        instr = "PAGE \\* ROMAN"

    sections = list(doc.sections)
    has_toc = _document_has_toc(doc) or (options.get("insert_toc", True) and len(sections) > 1)
    
    for idx, section in enumerate(sections):
        footer = section.footer
        while footer.paragraphs:
            p = footer.paragraphs[0]
            _remove_paragraph(p)
        
        # Nếu có TOC và đây là section đầu tiên (mục lục) - không đánh số trang
        if has_toc and idx == 0:
            # Để trống footer cho section đầu tiên (mục lục)
            continue
        
        # Các section khác (nội dung) - đánh số trang
        para = footer.add_paragraph()
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER

        para.style.font.name = STANDARD_FONT
        para.style.font.size = PAGE_NUMBER_FONT_SIZE

        run = para.add_run()
        fld = OxmlElement("w:fldSimple")
        fld.set(qn("w:instr"), instr)
        run._r.append(fld)
        _set_run_format(run, PAGE_NUMBER_FONT_SIZE, bold=False)
        run.font.name = STANDARD_FONT
        run.font.size = PAGE_NUMBER_FONT_SIZE
        
        for r in para.runs:
             try:
                r.font.name = STANDARD_FONT
                r.font.size = PAGE_NUMBER_FONT_SIZE
             except Exception:
                pass
        
        # Điều chỉnh page numbering: section đầu tiên có nội dung bắt đầu từ 1
        # (Nếu có TOC thì là section thứ 2, nếu không có TOC thì là section đầu tiên)
        target_section_idx = 1 if has_toc else 0
        if idx == target_section_idx:
            try:
                sect_pr = section._sectPr
                pg_num_type = sect_pr.find(qn("w:pgNumType"))
                if pg_num_type is None:
                    pg_num_type = OxmlElement("w:pgNumType")
                    sect_pr.append(pg_num_type)
                # Bắt đầu đánh số từ 1
                pg_num_type.set(qn("w:start"), "1")
            except Exception as e:
                logging.warning(f"Không thể đặt page numbering: {e}")


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
    heading_level = None
    style_name = paragraph.style.name if paragraph.style else ""
    
    if options.get("heading_detection", True):
        # Kiểm tra nếu đã có style heading (giữ nguyên nếu đã được set thủ công)
        if style_name.lower().startswith("heading"):
            is_heading = True
            # Lấy level từ style name (ví dụ: "Heading 1" → level 1)
            try:
                level_str = style_name.split()[-1]
                if level_str.isdigit():
                    heading_level = int(level_str)
            except Exception:
                heading_level = 1
        # Kiểm tra pattern số thứ tự (nếu chưa có style heading)
        elif options.get("auto_numbered_heading", True):
            detected_level, detected_heading = _detect_numbered_heading(normalized)
            if detected_heading:
                is_heading = True
                heading_level = detected_level
                try:
                    paragraph.style = f"Heading {heading_level}"
                except Exception:
                    pass
        # Kiểm tra heading theo pattern chữ hoa (fallback)
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
            # Chỉ Heading 1 mới bôi đậm, các heading khác (2, 3, 4...) để bình thường
            if is_heading:
                bold_flag = (heading_level == 1) if heading_level is not None else False
            else:
                # Không phải heading: giữ nguyên bold hiện tại
                bold_flag = bool(run.font.bold)
            italic_flag = bool(run.font.italic)
            _set_run_format(run, target_size, bold=bold_flag, italic=italic_flag)

    if options.get("indent_spacing", True):
        fmt = paragraph.paragraph_format
        # Lấy text sạch để kiểm tra điều kiện gạch đầu dòng và độ dài
        clean_text = paragraph.text.strip()

        if is_heading:
            fmt.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            fmt.space_before = Pt(0)  # Before: 0
            fmt.space_after = Pt(6)   # After: 6
            fmt.first_line_indent = Pt(0)
            fmt.left_indent = Pt(0)
            # Line spacing: 1.5 line
            fmt.line_spacing = 1.5
        else:
            # --- Cấu hình chung cho phần thân bài ---
            fmt.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            fmt.line_spacing = options.get("line_spacing", 1.3)
            fmt.space_before = Pt(0)
            fmt.space_after = Pt(6)

            # --- Logic xử lý thụt đầu dòng (First Line Indent) ---
            
            # 1. Nếu bắt đầu bằng gạch đầu dòng, dấu cộng, dấu sao hoặc chấm tròn
            if clean_text.startswith(("-", "+", "•", "*")):
                fmt.first_line_indent = Pt(0)
                fmt.left_indent = Pt(0) # Đảm bảo sát lề trái
            
            # 2. Nếu đoạn văn ngắn (dưới 50 ký tự) -> Coi là 1 dòng -> Không thụt đầu dòng
            # (Giả định đây là tiêu đề phụ hoặc chú thích ngắn)
            elif 0 < len(clean_text) < 50:
                fmt.first_line_indent = Pt(0)
                fmt.left_indent = Pt(0)
                
            # 3. Các trường hợp còn lại (Văn bản bình thường) -> Thụt đầu dòng
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

    _copy_heading_style_to_toc(doc)

    for paragraph in list(doc.paragraphs):
        _standardize_paragraph(paragraph, options)

    if options.get("format_tables", True):
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in list(cell.paragraphs):
                        _standardize_paragraph(paragraph, options)

    # Chèn mục lục ở đầu document (không cần anchor)
    _insert_table_of_contents(doc, options, anchor=None)
    
    # Apply lại lần cuối sau khi chèn TOC
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
    html_parts = ['<div class="docx-preview" style="font-family: \'Times New Roman\', serif; max-width: 210mm; margin: 0 auto; padding: 20mm 35mm 20mm 25mm; background: white; line-height: 1.3;">']
    
    for paragraph in doc.paragraphs:
        if not paragraph.text.strip():
            html_parts.append('<p style="margin: 0.5em 0;"><br></p>')
            continue
        
        style_name = paragraph.style.name if paragraph.style else ""
        is_heading = style_name.lower().startswith("heading") if style_name else False
        
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