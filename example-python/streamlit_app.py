import streamlit as st
import tempfile
import uuid
from pathlib import Path
from io import BytesIO
import logging

from docx import Document
from app.services.report_formatter import (
    format_uploaded_stream,
    generate_template_stream,
    docx_to_html,
)
from app.config import TEMP_DIR

# ============================================================================
# CẤU HÌNH STREAMLIT
# ============================================================================
st.set_page_config(
    page_title="Chuẩn Hóa Báo Cáo Word",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Thiết lập logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# ============================================================================
# CSS TÙY CHỈNH
# ============================================================================
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        font-size: 1rem;
        font-weight: 600;
        border-radius: 8px;
        transition: transform 0.2s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
    }
    .upload-section {
        background: #f9fafb;
        padding: 1.5rem;
        border-radius: 12px;
        border: 2px dashed #cbd5f5;
        margin: 1rem 0;
    }
    .success-message {
        padding: 1rem;
        background: #d1fae5;
        border-left: 4px solid #10b981;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .error-message {
        padding: 1rem;
        background: #fee2e2;
        border-left: 4px solid #ef4444;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .info-box {
        background: #f0f5ff;
        border-left: 4px solid #667eea;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    h1 {
        color: #2b2d42;
        text-align: center;
    }
    h2 {
        color: #4a4e69;
        margin-top: 2rem;
    }
    h3 {
        color: #667eea;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 1rem 2rem;
        background-color: #f5f6fb;
        border-radius: 8px 8px 0 0;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# HÀM PHỤ TRỢ
# ============================================================================
def collect_options():
    """Thu thập các tùy chọn định dạng từ sidebar"""
    return {
        "clean_whitespace": st.session_state.get("opt_clean", True),
        "normalize_font": st.session_state.get("opt_font", True),
        "adjust_margins": st.session_state.get("opt_margins", True),
        "indent_spacing": st.session_state.get("opt_spacing", True),
        "heading_detection": st.session_state.get("opt_heading", True),
        "format_tables": st.session_state.get("opt_tables", True),
        "insert_toc": st.session_state.get("opt_toc", True),
        "add_page_numbers": st.session_state.get("opt_page_numbers", True),
        "page_number_style": st.session_state.get("opt_page_style", "arabic"),
        "line_spacing": st.session_state.get("line_spacing", 1.3),
        "auto_numbered_heading": True,
    }

def save_uploaded_file(uploaded_file):
    """Lưu file được upload vào thư mục tạm"""
    try:
        file_id = str(uuid.uuid4())
        file_path = TEMP_DIR / f"{file_id}_{uploaded_file.name}"
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return file_path
    except Exception as e:
        st.error(f"Lỗi lưu file: {e}")
        return None

def display_preview(doc: Document):
    """Hiển thị preview của document dưới dạng HTML"""
    try:
        html_content = docx_to_html(doc)
        st.components.v1.html(html_content, height=800, scrolling=True)
    except Exception as e:
        st.error(f"Không thể hiển thị preview: {e}")

# ============================================================================
# SIDEBAR - TÙY CHỌN ĐỊNH DẠNG
# ============================================================================
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/microsoft-word-2019.png", width=80)
    st.title("⚙️ Tùy Chọn Định Dạng")
    
    st.markdown("### 📋 Các tùy chọn UEL")
    st.markdown('<div class="info-box">Áp dụng cho cả việc tạo mẫu mới và chuẩn hóa file tải lên.</div>', unsafe_allow_html=True)
    
    st.checkbox(
        "🧹 Xóa dòng trống & dấu cách thừa",
        value=True,
        key="opt_clean",
        help="Loại bỏ khoảng trắng thừa và dòng trống không cần thiết"
    )
    
    st.checkbox(
        "🔤 Áp dụng font Times New Roman 13pt / 14pt",
        value=True,
        key="opt_font",
        help="Chuẩn hóa font chữ theo quy định UEL"
    )
    
    st.checkbox(
        "📏 Thiết lập lề chuẩn UEL",
        value=True,
        key="opt_margins",
        help="Trái 3cm, Phải 2cm, Trên/Dưới 2cm"
    )
    
    st.checkbox(
        "↔️ Thụt đầu dòng 1.27cm và giãn dòng",
        value=True,
        key="opt_spacing",
        help="Thụt đầu dòng và điều chỉnh khoảng cách dòng"
    )
    
    st.number_input(
        "📐 Giãn dòng (Line Spacing)",
        min_value=1.0,
        max_value=3.0,
        value=1.3,
        step=0.1,
        key="line_spacing",
        help="Khoảng cách giữa các dòng văn bản"
    )
    
    st.checkbox(
        "🎯 Nhận diện & chuẩn hóa tiêu đề",
        value=True,
        key="opt_heading",
        help="Tự động nhận diện và định dạng tiêu đề"
    )
    
    st.checkbox(
        "📊 Chuẩn hóa định dạng trong bảng",
        value=True,
        key="opt_tables",
        help="Áp dụng định dạng cho nội dung trong bảng"
    )
    
    st.checkbox(
        "📑 Chèn mục lục tự động",
        value=True,
        key="opt_toc",
        help="Tạo mục lục và danh mục hình ảnh tự động"
    )
    
    st.checkbox(
        "🔢 Đánh số trang ở giữa chân trang",
        value=True,
        key="opt_page_numbers",
        help="Thêm số trang tự động"
    )
    
    st.selectbox(
        "Kiểu số trang:",
        options=["arabic", "roman"],
        format_func=lambda x: "Số Ả Rập (1,2,3...)" if x == "arabic" else "Số La Mã (i, ii, iii...)",
        key="opt_page_style"
    )
    
    st.markdown("---")
    st.markdown("### 📚 Hướng dẫn")
    with st.expander("💡 Cách sử dụng"):
        st.markdown("""
        **Tạo báo cáo mới:**
        1. Chuyển sang tab "Tạo Báo Cáo Mới"
        2. Điền thông tin sinh viên và báo cáo
        3. Nhấn "Tạo File Word"
        
        **Chuẩn hóa file có sẵn:**
        1. Chuyển sang tab "Chuẩn Hóa File"
        2. Tải lên file .docx
        3. Nhấn "Chuẩn Hóa File"
        4. Xem trước và tải về
        
        **Lưu ý:** Mục lục được tạo thủ công với font Times New Roman 13pt. Số trang là ước tính.
        """)

# ============================================================================
# MAIN APP
# ============================================================================
st.title("📄 Chuẩn Hóa Báo Cáo Word")
st.markdown("### Công cụ chuẩn hóa báo cáo theo định dạng UEL")

# Tạo tabs
tab1, tab2 = st.tabs(["📝 Tạo Báo Cáo Mới", "📂 Chuẩn Hóa File Có Sẵn"])

# ============================================================================
# TAB 1: TẠO BÁO CÁO MỚI
# ============================================================================
with tab1:
    st.markdown("### Tạo file Word mới theo mẫu chuẩn UEL")
    st.markdown('<div class="info-box">Nhập thông tin để tạo file Word theo mẫu chuẩn với đầy đủ cấu trúc báo cáo.</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        student_name = st.text_input(
            "👤 Họ và tên sinh viên",
            placeholder="Nguyễn Văn A",
            help="Họ tên đầy đủ của sinh viên"
        )
        
        student_id = st.text_input(
            "🎓 Mã số sinh viên (MSSV)",
            placeholder="K2140xxxx",
            help="Mã số sinh viên"
        )
        
        class_name = st.text_input(
            "🏫 Lớp/Khoa",
            placeholder="Công nghệ thông tin K45",
            help="Tên lớp hoặc khoa"
        )
    
    with col2:
        report_title = st.text_input(
            "📋 Tiêu đề báo cáo",
            placeholder="BÁO CÁO MÔN...",
            help="Tiêu đề chính của báo cáo"
        )
        
        year = st.text_input(
            "📅 Năm học",
            placeholder="2024-2025",
            help="Năm học thực hiện báo cáo"
        )
        
        advisor = st.text_input(
            "👨‍🏫 Giảng viên hướng dẫn",
            placeholder="GVHD: ................................",
            help="Tên giảng viên hướng dẫn"
        )
    
    location = st.text_input(
        "📍 Địa điểm",
        value="TP. Hồ Chí Minh",
        help="Địa điểm thực hiện báo cáo"
    )
    
    st.markdown("#### 📝 Nội dung bổ sung")
    
    col3, col4 = st.columns(2)
    
    with col3:
        intro = st.text_area(
            "Phần mở đầu",
            placeholder="Trình bày lý do chọn đề tài, mục tiêu, phạm vi và phương pháp nghiên cứu...",
            height=150,
            help="Nội dung phần mở đầu"
        )
        
        content = st.text_area(
            "Nội dung chính",
            placeholder="Nêu hiện trạng thu thập được, số liệu minh họa và phân tích...",
            height=150,
            help="Nội dung chương 2"
        )
    
    with col4:
        solution = st.text_area(
            "Giải pháp/Kiến nghị",
            placeholder="Đề xuất giải pháp, kiến nghị chính sách và điều kiện thực hiện...",
            height=150,
            help="Nội dung chương 3"
        )
        
        conclusion = st.text_area(
            "Kết luận",
            placeholder="Tóm tắt kết quả đạt được và hướng nghiên cứu tiếp theo...",
            height=150,
            help="Phần kết luận"
        )
    
    references = st.text_area(
        "Tài liệu tham khảo",
        placeholder="APA (2019). Publication Manual of the American Psychological Association (7th ed.). APA Publishing.",
        height=100,
        help="Danh sách tài liệu tham khảo theo chuẩn APA"
    )
    
    st.markdown("---")
    
    if st.button("🚀 Tạo File Word", type="primary", use_container_width=True):
        if not student_name or not report_title:
            st.error("⚠️ Vui lòng nhập ít nhất Họ tên và Tiêu đề báo cáo!")
        else:
            with st.spinner("Đang tạo file Word..."):
                try:
                    # Chuẩn bị payload
                    payload = {
                        "studentName": student_name,
                        "studentId": student_id,
                        "className": class_name,
                        "reportTitle": report_title,
                        "year": year,
                        "advisor": advisor,
                        "location": location,
                        "intro": intro,
                        "content": content,
                        "solution": solution,
                        "conclusion": conclusion,
                        "references": references,
                        "options": collect_options()
                    }
                    
                    # Tạo file
                    stream, filename = generate_template_stream(payload)
                    
                    # Hiển thị thông báo thành công
                    st.markdown('<div class="success-message">✅ Đã tạo file báo cáo thành công!</div>', unsafe_allow_html=True)
                    
                    # Nút tải về
                    st.download_button(
                        label="⬇️ Tải File Về Máy",
                        data=stream,
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True
                    )
                    
                    st.success("💡 **Lưu ý:** Mục lục đã được tạo thủ công với font Times New Roman 13pt. Số trang là ước tính, vui lòng kiểm tra và chỉnh sửa nếu cần.")
                    
                except Exception as e:
                    logging.error(f"Lỗi tạo báo cáo: {e}")
                    st.markdown(f'<div class="error-message">❌ Lỗi: {str(e)}</div>', unsafe_allow_html=True)

# ============================================================================
# TAB 2: CHUẨN HÓA FILE CÓ SẴN
# ============================================================================
with tab2:
    st.markdown("### Tải lên file Word để chuẩn hóa")
    st.markdown('<div class="info-box">Tải lên file .docx chưa đúng format để hệ thống tự động chuẩn hóa theo tiêu chuẩn UEL.</div>', unsafe_allow_html=True)
    
    # ==================== QUICK TEST SECTION ====================
    st.markdown("---")
    st.markdown("### ⚡ Test Nhanh")
    
    # Đường dẫn file test mặc định
    TEST_FILE_PATH = Path(r"E:\Personal Project\test.docx")
    
    col_test1, col_test2 = st.columns([3, 1])
    
    with col_test1:
        test_file_path = st.text_input(
            "📁 Đường dẫn file test",
            value=str(TEST_FILE_PATH),
            help="Nhập đường dẫn đến file Word cần test"
        )
    
    with col_test2:
        st.markdown("<br>", unsafe_allow_html=True)
        quick_test_btn = st.button("🚀 Test Ngay!", type="primary", use_container_width=True, key="quick_test")
    
    if quick_test_btn:
        test_path = Path(test_file_path)
        if test_path.exists():
            with st.spinner(f"Đang xử lý {test_path.name}..."):
                try:
                    # Đọc file từ đường dẫn
                    with open(test_path, "rb") as f:
                        file_bytes = f.read()
                    
                    # Chuẩn hóa
                    options = collect_options()
                    stream, filename = format_uploaded_stream(
                        file_bytes,
                        test_path.name,
                        options
                    )
                    
                    # Lưu vào session state
                    st.session_state["formatted_stream"] = stream
                    st.session_state["formatted_filename"] = filename
                    
                    # Tạo document để preview
                    stream.seek(0)
                    doc = Document(stream)
                    st.session_state["formatted_doc"] = doc
                    
                    st.markdown('<div class="success-message">✅ Test thành công! File đã được chuẩn hóa.</div>', unsafe_allow_html=True)
                    st.balloons()
                    
                except Exception as e:
                    logging.error(f"Lỗi test: {e}")
                    import traceback
                    st.markdown(f'<div class="error-message">❌ Lỗi: {str(e)}</div>', unsafe_allow_html=True)
                    with st.expander("Chi tiết lỗi"):
                        st.code(traceback.format_exc())
        else:
            st.error(f"❌ File không tồn tại: {test_file_path}")
    
    st.markdown("---")
    st.markdown("### 📂 Upload File Thủ Công")
    
    # Upload file
    uploaded_file = st.file_uploader(
        "📎 Chọn file Word (.docx)",
        type=["docx"],
        help="Chọn file Word cần chuẩn hóa"
    )
    
    if uploaded_file is not None:
        st.success(f"✅ Đã chọn file: **{uploaded_file.name}**")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("🔄 Chuẩn Hóa File", type="primary", use_container_width=True):
                with st.spinner("Đang xử lý file..."):
                    try:
                        # Đọc file
                        file_bytes = uploaded_file.read()
                        
                        # Chuẩn hóa
                        options = collect_options()
                        stream, filename = format_uploaded_stream(
                            file_bytes,
                            uploaded_file.name,
                            options
                        )
                        
                        # Lưu vào session state
                        st.session_state["formatted_stream"] = stream
                        st.session_state["formatted_filename"] = filename
                        
                        # Tạo document để preview
                        stream.seek(0)
                        doc = Document(stream)
                        st.session_state["formatted_doc"] = doc
                        
                        st.markdown('<div class="success-message">✅ Đã chuẩn hóa file thành công!</div>', unsafe_allow_html=True)
                        st.balloons()
                        
                    except Exception as e:
                        logging.error(f"Lỗi chuẩn hóa: {e}")
                        st.markdown(f'<div class="error-message">❌ Lỗi: {str(e)}</div>', unsafe_allow_html=True)
        
        with col2:
            # Nút reset
            if st.button("🔄 Reset", use_container_width=True):
                if "formatted_stream" in st.session_state:
                    del st.session_state["formatted_stream"]
                if "formatted_filename" in st.session_state:
                    del st.session_state["formatted_filename"]
                if "formatted_doc" in st.session_state:
                    del st.session_state["formatted_doc"]
                st.rerun()
    
    # Hiển thị kết quả
    if "formatted_stream" in st.session_state and "formatted_filename" in st.session_state:
        st.markdown("---")
        st.markdown("### 📥 File đã chuẩn hóa")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.info(f"**File:** {st.session_state['formatted_filename']}")
        
        with col2:
            # Nút tải về
            st.session_state["formatted_stream"].seek(0)
            st.download_button(
                label="⬇️ Tải File Về",
                data=st.session_state["formatted_stream"],
                file_name=st.session_state["formatted_filename"],
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
        
        st.markdown("---")
        
        # Preview
        st.markdown("### 👁️ Xem Trước File")
        
        if "formatted_doc" in st.session_state:
            with st.expander("📄 Hiển thị nội dung", expanded=True):
                display_preview(st.session_state["formatted_doc"])
        
        st.success("💡 **Lưu ý:** Mục lục đã được tạo thủ công với font Times New Roman 13pt. Số trang là ước tính, vui lòng kiểm tra và chỉnh sửa nếu cần.")

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #718096; padding: 2rem 0;">
    <p>📄 <strong>Công cụ Chuẩn Hóa Báo Cáo Word</strong></p>
    <p>Phát triển cho Trường Đại học Kinh tế - Luật (UEL)</p>
    <p style="font-size: 0.875rem;">Sử dụng công cụ này để đảm bảo báo cáo của bạn đạt chuẩn định dạng UEL</p>
</div>
""", unsafe_allow_html=True)

