import streamlit as st
import uuid
from pathlib import Path
import logging
from docx import Document
from app.services.report_formatter import (
    format_uploaded_stream,
    docx_to_html,
)
from app.config import TEMP_DIR, CONVERTAPI_SECRET

# ============================================================================
# CẤU HÌNH STREAMLIT
# ============================================================================
st.set_page_config(
    page_title="EasyReport - Chuẩn Hóa Báo Cáo",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="collapsed",
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# ============================================================================
# CSS - BENTO STYLE (Fixed colors)
# ============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,1,0');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .material-symbols-rounded {
        font-family: 'Material Symbols Rounded';
        font-weight: normal;
        font-style: normal;
        font-size: 28px;
        display: inline-block;
        line-height: 1;
        text-transform: none;
        letter-spacing: normal;
        word-wrap: normal;
        white-space: nowrap;
        direction: ltr;
        font-variation-settings: 'FILL' 1;
    }
    
    /* Main container */
    .block-container {
        padding-top: 2rem !important;
        max-width: 1200px !important;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 8px;
        border-radius: 16px;
        margin-bottom: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 12px 24px;
        background: transparent;
        border-radius: 12px;
        color: rgba(255,255,255,0.7) !important;
        font-weight: 600;
        border: none;
    }
    
    .stTabs [aria-selected="true"] {
        background: white !important;
        color: #6366f1 !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* Bento Cards */
    .bento-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 20px;
        margin: 2rem 0;
    }
    
    .bento-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 20px;
        padding: 1.5rem;
        transition: all 0.3s ease;
    }
    
    .bento-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 24px rgba(0,0,0,0.08);
    }
    
    .card-icon {
        width: 52px;
        height: 52px;
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 1rem;
    }
    
    .card-icon .material-symbols-rounded {
        font-size: 28px;
    }
    
    .icon-purple .material-symbols-rounded { color: #8b5cf6; }
    .icon-blue .material-symbols-rounded { color: #3b82f6; }
    .icon-orange .material-symbols-rounded { color: #f97316; }
    .icon-pink .material-symbols-rounded { color: #ec4899; }
    
    .icon-purple { background: #ede9fe; }
    .icon-blue { background: #dbeafe; }
    .icon-orange { background: #ffedd5; }
    .icon-pink { background: #fce7f3; }
    
    .card-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0.5rem;
    }
    
    .card-desc {
        font-size: 0.9rem;
        color: #64748b;
        line-height: 1.5;
    }
    
    /* Hero Section */
    .hero-container {
        text-align: center;
        padding: 3rem 1rem;
        background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);
        border-radius: 24px;
        margin-bottom: 2rem;
    }
    
    .hero-title {
        font-size: 2.5rem;
        font-weight: 800;
        color: #1e293b;
        margin-bottom: 1rem;
        line-height: 1.2;
    }
    
    .hero-subtitle {
        font-size: 1.1rem;
        color: #64748b;
        max-width: 600px;
        margin: 0 auto;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(99, 102, 241, 0.4);
    }
    
    /* Tool Container */
    .tool-section {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 1.5rem;
    }
    
    /* Info boxes */
    .info-box {
        background: #eff6ff;
        border-left: 4px solid #3b82f6;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        color: #1e40af;
    }
    
    .success-box {
        background: #dcfce7;
        border-left: 4px solid #22c55e;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        color: #166534;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        color: #94a3b8;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# HÀM PHỤ TRỢ
# ============================================================================
def collect_options():
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

def convert_docx_to_pdf_cloud(docx_path, output_pdf_path):
    try:
        import requests
        api_secret = CONVERTAPI_SECRET
        if not api_secret:
            return None
        url = f"https://v2.convertapi.com/convert/docx/to/pdf?Secret={api_secret}&download=attachment"
        with open(docx_path, 'rb') as f:
            files = {'File': ('document.docx', f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
            response = requests.post(url, files=files, timeout=60)
            if response.status_code == 200:
                with open(output_pdf_path, 'wb') as pdf_out:
                    pdf_out.write(response.content)
                return output_pdf_path
    except Exception as e:
        logging.warning(f"ConvertAPI failed: {e}")
    return None

def display_pdf_in_iframe(pdf_path):
    import base64
    with open(pdf_path, "rb") as pdf_file:
        base64_pdf = base64.b64encode(pdf_file.read()).decode('utf-8')
        st.markdown(f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="700px" style="border:none;border-radius:12px;"></iframe>', unsafe_allow_html=True)

def display_preview(doc: Document):
    temp_docx = TEMP_DIR / f"preview_{uuid.uuid4()}.docx"
    temp_pdf = TEMP_DIR / f"preview_{uuid.uuid4()}.pdf"
    try:
        doc.save(str(temp_docx))
        if CONVERTAPI_SECRET:
            with st.spinner("🔄 Đang tạo PDF Preview..."):
                result_pdf = convert_docx_to_pdf_cloud(temp_docx, temp_pdf)
                if result_pdf and result_pdf.exists():
                    st.success("✅ PDF Preview sẵn sàng!")
                    display_pdf_in_iframe(temp_pdf)
                    return
        st.info("📄 Hiển thị HTML Preview")
        html_content = docx_to_html(doc)
        st.components.v1.html(html_content, height=700, scrolling=True)
    except Exception as e:
        st.error(f"Lỗi: {e}")
    finally:
        try:
            if temp_docx.exists(): temp_docx.unlink()
            if temp_pdf.exists(): temp_pdf.unlink()
        except: pass

# ============================================================================
# HEADER
# ============================================================================
st.markdown("# ✨ EasyReport")
st.markdown("*Công cụ chuẩn hóa báo cáo Word chuyên nghiệp*")

# ============================================================================
# TABS: Tổng Quan & Trải Nghiệm
# ============================================================================
tab1, tab2 = st.tabs(["🏠 Tổng Quan", "🚀 Trải Nghiệm"])

# ============================================================================
# TAB 1: TỔNG QUAN (Landing Page)
# ============================================================================
with tab1:
    # Hero Section
    st.markdown("""
    <div class="hero-container">
        <h1 class="hero-title">Biến báo cáo của bạn<br>trở nên hoàn hảo</h1>
        <p class="hero-subtitle">Tự động chuẩn hóa định dạng văn bản theo quy chuẩn. Tiết kiệm 90% thời gian chỉnh sửa thủ công.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Bento Grid
    st.markdown("""
    <div class="bento-grid">
        <div class="bento-card">
            <div class="card-icon icon-purple"><span class="material-symbols-rounded">text_format</span></div>
            <div class="card-title">Chuẩn Hóa Font</div>
            <p class="card-desc">Tự động chuyển đổi về font Times New Roman 13/14pt theo đúng quy định.</p>
        </div>
        <div class="bento-card">
            <div class="card-icon icon-blue"><span class="material-symbols-rounded">toc</span></div>
            <div class="card-title">Mục Lục Tự Động</div>
            <p class="card-desc">Tạo mục lục có số trang và danh mục hình ảnh chỉ với một click.</p>
        </div>
        <div class="bento-card">
            <div class="card-icon icon-orange"><span class="material-symbols-rounded">format_align_justify</span></div>
            <div class="card-title">Căn Lề Chuẩn</div>
            <p class="card-desc">Lề trái 3cm, phải 2cm, trên/dưới 2cm và giãn dòng 1.3 theo quy chuẩn.</p>
        </div>
        <div class="bento-card">
            <div class="card-icon icon-pink"><span class="material-symbols-rounded">bolt</span></div>
            <div class="card-title">Xử Lý Nhanh</div>
            <p class="card-desc">Upload file và nhận kết quả ngay lập tức với preview PDF trực quan.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📖 Hướng dẫn sử dụng")
    st.markdown("""
    1. Chuyển sang tab **🚀 Trải Nghiệm**
    2. Upload file Word (.docx) hoặc dùng Quick Test
    3. Tùy chỉnh các options (nếu cần)
    4. Nhấn **Chuẩn Hóa** và tải file kết quả về
    """)
    
    st.markdown('<div class="footer">© 2026 EasyReport. Made with ❤️</div>', unsafe_allow_html=True)

# ============================================================================
# TAB 2: TRẢI NGHIỆM (Tool Page)
# ============================================================================
with tab2:
    # Options Section (Collapsible)
    with st.expander("⚙️ Tùy chỉnh định dạng", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.checkbox("🧹 Xóa dòng trống thừa", value=True, key="opt_clean")
            st.checkbox("🔤 Chuẩn hóa font chữ", value=True, key="opt_font")
            st.checkbox("📏 Thiết lập lề chuẩn", value=True, key="opt_margins")
        with col2:
            st.checkbox("↔️ Thụt đầu dòng & giãn dòng", value=True, key="opt_spacing")
            st.checkbox("🎯 Nhận diện tiêu đề", value=True, key="opt_heading")
            st.checkbox("📊 Format bảng biểu", value=True, key="opt_tables")
        with col3:
            st.checkbox("📑 Tạo mục lục", value=True, key="opt_toc")
            st.checkbox("🔢 Đánh số trang", value=True, key="opt_page_numbers")
            st.number_input("Giãn dòng", value=1.3, step=0.1, key="line_spacing")
    
    st.markdown("---")
    
    # ==================== QUICK TEST SECTION ====================
    st.markdown("### ⚡ Test Nhanh")
    TEST_FILE_PATH = Path(r"E:\Personal Project\test.docx")
    
    col_test1, col_test2 = st.columns([3, 1])
    with col_test1:
        test_file_path = st.text_input("📁 Đường dẫn file test", value=str(TEST_FILE_PATH))
    with col_test2:
        st.markdown("<br>", unsafe_allow_html=True)
        quick_test_btn = st.button("🚀 Test Ngay!", type="primary", use_container_width=True)
    
    if quick_test_btn:
        test_path = Path(test_file_path)
        if test_path.exists():
            with st.spinner(f"Đang xử lý {test_path.name}..."):
                try:
                    with open(test_path, "rb") as f:
                        file_bytes = f.read()
                    options = collect_options()
                    stream, filename = format_uploaded_stream(file_bytes, test_path.name, options)
                    st.session_state["formatted_stream"] = stream
                    st.session_state["formatted_filename"] = filename
                    stream.seek(0)
                    st.session_state["formatted_doc"] = Document(stream)
                    st.success("✅ Test thành công!")
                    st.balloons()
                except Exception as e:
                    st.error(f"❌ Lỗi: {e}")
        else:
            st.error(f"❌ File không tồn tại: {test_file_path}")
    
    st.markdown("---")
    
    # ==================== UPLOAD SECTION ====================
    st.markdown("### 📂 Upload File")
    uploaded_file = st.file_uploader("Kéo thả hoặc chọn file Word (.docx)", type=["docx"])
    
    if uploaded_file:
        st.success(f"✅ Đã chọn: **{uploaded_file.name}**")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✨ CHUẨN HÓA", type="primary", use_container_width=True):
                with st.spinner("Đang xử lý..."):
                    try:
                        file_bytes = uploaded_file.read()
                        options = collect_options()
                        stream, filename = format_uploaded_stream(file_bytes, uploaded_file.name, options)
                        st.session_state["formatted_stream"] = stream
                        st.session_state["formatted_filename"] = filename
                        stream.seek(0)
                        st.session_state["formatted_doc"] = Document(stream)
                        st.success("✅ Chuẩn hóa thành công!")
                        st.balloons()
                    except Exception as e:
                        st.error(f"❌ Lỗi: {e}")
        
        with col2:
            if st.button("🔄 Reset", use_container_width=True):
                for key in ["formatted_stream", "formatted_filename", "formatted_doc"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
    
    # ==================== RESULTS SECTION ====================
    if "formatted_stream" in st.session_state:
        st.markdown("---")
        st.markdown("### 📥 Kết quả")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.info(f"**File:** {st.session_state['formatted_filename']}")
        with col2:
            st.session_state["formatted_stream"].seek(0)
            st.download_button(
                "⬇️ Tải File Về",
                st.session_state["formatted_stream"],
                file_name=st.session_state["formatted_filename"],
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
        
        st.markdown("---")
        st.markdown("### 👁️ Xem Trước")
        with st.expander("📄 Mở Preview", expanded=True):
            if "formatted_doc" in st.session_state:
                display_preview(st.session_state["formatted_doc"])
