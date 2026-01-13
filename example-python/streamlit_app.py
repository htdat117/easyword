import streamlit as st
import uuid
from pathlib import Path
import logging
import sys
import base64
import os

# ============================================================================
# CẤU HÌNH STREAMLIT
# ============================================================================
st.set_page_config(
    page_title="EasyWord - Tạo Tài Liệu Word Chuyên Nghiệp",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Fix path to ensure 'app' module can be imported
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))

# Import app modules
try:
    from docx import Document
    from app.services.report_formatter import (
        format_uploaded_stream,
        docx_to_html,
    )
    from app.config import TEMP_DIR, CONVERTAPI_SECRET
except Exception as e:
    st.error(f"❌ Import Error: {e}")
    st.code(f"Sys Path: {sys.path}")
    st.stop()


# ============================================================================
# CSS INJECTION - Using separate components to avoid Markdown parsing issues
# ============================================================================

# External fonts and icons
st.markdown('<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">', unsafe_allow_html=True)
st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">', unsafe_allow_html=True)

# CSS styles - using f-string to avoid markdown parsing issues
css_styles = """
<style>
* { font-family: 'Inter', sans-serif; }
body { background-color: #F9FAFB; color: #1F2937; line-height: 1.6; }
#MainMenu, footer, header[data-testid="stHeader"], .stDeployButton { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }
.custom-header { background-color: #FFFFFF; box-shadow: 0 1px 3px rgba(0,0,0,0.1); position: sticky; top: 0; z-index: 1000; padding: 0; }
.container { max-width: 1200px; margin: 0 auto; padding: 0 20px; }
.nav-wrapper { display: flex; justify-content: space-between; align-items: center; height: 70px; }
.logo { font-size: 1.5rem; font-weight: 700; color: #2563EB; display: flex; align-items: center; gap: 10px; text-decoration: none; }
.btn-login { color: #1F2937; margin-right: 15px; text-decoration: none; font-weight: 500; padding: 8px 16px; border-radius: 6px; }
.btn-signup { background-color: #2563EB; color: #FFFFFF; text-decoration: none; padding: 8px 20px; border-radius: 6px; font-weight: 500; }
.hero-section { text-align: center; padding: 60px 20px 80px; background: linear-gradient(180deg, #FFFFFF 0%, #EFF6FF 100%); }
.hero-title { font-size: 2.5rem; color: #111827; margin-bottom: 16px; line-height: 1.2; font-weight: 700; }
.hero-desc { font-size: 1rem; color: #6B7280; margin-bottom: 30px; max-width: 600px; margin-left: auto; margin-right: auto; }
.tool-box-container { max-width: 800px; margin: 0 auto; background: #FFFFFF; border-radius: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); padding: 30px; border: 1px solid #E5E7EB; }
[data-testid="stTabs"] { margin-bottom: 20px; }
[data-testid="stTabs"] [data-baseweb="tab-list"] { gap: 10px; justify-content: center; border-bottom: none !important; background: transparent; }
[data-testid="stTabs"] button[data-baseweb="tab"] { background: transparent !important; border: none !important; border-bottom: 2px solid transparent !important; border-radius: 0 !important; color: #6B7280 !important; font-weight: 600 !important; padding: 10px 20px !important; }
[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] { color: #2563EB !important; border-bottom-color: #2563EB !important; }
[data-testid="stTabs"] button[data-baseweb="tab"]:hover { color: #2563EB !important; }
[data-testid="stTabs"] [data-baseweb="tab-highlight"], [data-testid="stTabs"] [data-baseweb="tab-border"] { display: none !important; }
[data-testid="stFileUploader"] { border: 2px dashed #D1D5DB !important; border-radius: 12px !important; padding: 40px 20px !important; background-color: #F9FAFB !important; text-align: center !important; }
[data-testid="stFileUploader"]:hover { border-color: #2563EB !important; background-color: #EFF6FF !important; }
[data-testid="stFileUploader"] section { padding: 0 !important; background: transparent !important; }
[data-testid="stFileUploader"] section > div { display: flex !important; flex-direction: column !important; align-items: center !important; }
[data-testid="stFileUploader"] section small { color: #9CA3AF !important; margin-top: 10px !important; }
[data-testid="stFileUploader"] button { background: #E5E7EB !important; color: #374151 !important; border: 1px solid #D1D5DB !important; padding: 8px 20px !important; border-radius: 8px !important; font-weight: 500 !important; margin-top: 15px !important; }
[data-testid="stFileUploader"] button:hover { background: #D1D5DB !important; }
div.stButton > button[kind="primary"], div.stButton > button[data-testid="baseButton-primary"] { width: 100% !important; padding: 15px !important; background-color: #2563EB !important; color: #FFFFFF !important; border: none !important; border-radius: 8px !important; font-size: 1rem !important; font-weight: 600 !important; margin-top: 20px !important; }
div.stButton > button[kind="primary"]:hover, div.stButton > button[data-testid="baseButton-primary"]:hover { background-color: #1D4ED8 !important; }
.features { padding: 80px 20px; background-color: #FFFFFF; }
.feature-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 30px; max-width: 1200px; margin: 0 auto; }
.feature-card { padding: 25px; border-radius: 12px; background: #F8FAFC; border: 1px solid transparent; }
.feature-card:hover { transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.05); border-color: #E2E8F0; background: #FFFFFF; }
.icon-box { width: 50px; height: 50px; border-radius: 10px; display: flex; align-items: center; justify-content: center; margin-bottom: 15px; font-size: 1.5rem; }
.bg-blue { background: #DBEAFE; color: #2563EB; }
.bg-green { background: #D1FAE5; color: #059669; }
.bg-purple { background: #EDE9FE; color: #7C3AED; }
.bg-orange { background: #FFEDD5; color: #EA580C; }
.bg-red { background: #FEE2E2; color: #DC2626; }
.bg-teal { background: #CCFBF1; color: #0D9488; }
.feature-h3 { font-size: 1.1rem; margin-bottom: 8px; font-weight: 600; color: #1F2937; }
.feature-p { color: #6B7280; font-size: 0.9rem; }
.cta-section { padding: 80px 20px; background: linear-gradient(135deg, #2563EB 0%, #1E40AF 100%); color: #FFFFFF; text-align: center; }
.btn-white { display: inline-block; background: #FFFFFF; color: #2563EB !important; padding: 15px 40px; border-radius: 8px; font-weight: 700; text-decoration: none; margin-top: 20px; }
.custom-footer { background-color: #111827; color: #D1D5DB; padding: 60px 20px 20px; }
.footer-grid { display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; gap: 40px; max-width: 1200px; margin: 0 auto 40px; }
.footer-col h4 { color: white; margin-bottom: 20px; font-weight: 600; }
.footer-col a { color: #9CA3AF; text-decoration: none; display: block; margin-bottom: 10px; }
[data-testid="stExpander"] { border: 1px solid #E5E7EB !important; border-radius: 8px !important; margin-top: 15px !important; }
</style>
"""
st.markdown(css_styles, unsafe_allow_html=True)

# ============================================================================
# HELPER FUNCTIONS
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
        "line_spacing": st.session_state.get("line_spacing", 1.3),
        "auto_numbered_heading": True,
    }

def convert_docx_to_pdf_cloud(docx_path, output_pdf_path):
    try:
        import requests
        api_secret = CONVERTAPI_SECRET
        if not api_secret: return None
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

def display_pdf_with_pdfjs(pdf_path):
    with open(pdf_path, "rb") as pdf_file:
        base64_pdf = base64.b64encode(pdf_file.read()).decode('utf-8')
    pdfjs_html = f'''<!DOCTYPE html><html><head><script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script><style>body{{margin:0;background:#525659}}canvas{{display:block;margin:20px auto;box-shadow:0 4px 12px rgba(0,0,0,0.3)}}</style></head><body><div id="pdf-container"></div><script>pdfjsLib.GlobalWorkerOptions.workerSrc='https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';const pdfData=atob("{base64_pdf}");pdfjsLib.getDocument({{data:pdfData}}).promise.then(pdf=>{{for(let i=1;i<=pdf.numPages;i++){{pdf.getPage(i).then(page=>{{const scale=1.0;const viewport=page.getViewport({{scale}});const canvas=document.createElement('canvas');const context=canvas.getContext('2d');canvas.height=viewport.height;canvas.width=viewport.width;document.getElementById('pdf-container').appendChild(canvas);page.render({{canvasContext:context,viewport:viewport}})}})}}}})</script></body></html>'''
    st.components.v1.html(pdfjs_html, height=800, scrolling=True)

def display_preview(doc: Document):
    temp_docx = TEMP_DIR / f"preview_{uuid.uuid4()}.docx"
    temp_pdf = TEMP_DIR / f"preview_{uuid.uuid4()}.pdf"
    try:
        doc.save(str(temp_docx))
        if CONVERTAPI_SECRET:
            with st.spinner("🔄 Đang tạo PDF Preview..."):
                result_pdf = convert_docx_to_pdf_cloud(temp_docx, temp_pdf)
                if result_pdf and Path(result_pdf).exists():
                    display_pdf_with_pdfjs(temp_pdf)
                    return
        st.info("📄 Hiển thị HTML Preview")
        html_content = docx_to_html(doc)
        st.components.v1.html(html_content, height=800, scrolling=True)
    except Exception as e:
        st.error(f"Lỗi Preview: {e}")
    finally:
        try:
            if temp_docx.exists(): temp_docx.unlink()
            if temp_pdf.exists(): temp_pdf.unlink()
        except: pass

def process_file(file_bytes, filename):
    try:
        opts = collect_options()
        stream, name = format_uploaded_stream(file_bytes, filename, opts)
        st.session_state["result_stream"] = stream
        st.session_state["result_name"] = name
        stream.seek(0)
        st.session_state["result_doc"] = Document(stream)
        return True
    except Exception as e:
        st.error(f"Lỗi xử lý: {e}")
        return False

# ============================================================================
# APP LAYOUT
# ============================================================================

# 1. HEADER
st.markdown('''<header class="custom-header"><div class="container nav-wrapper"><a href="#" class="logo"><i class="fa-solid fa-file-word"></i> EasyWord</a><div class="auth-buttons"><a href="#" class="btn-login">Đăng nhập</a><a href="#" class="btn-signup">Đăng ký ngay</a></div></div></header>''', unsafe_allow_html=True)

# 2. HERO SECTION
st.markdown('''<section class="hero-section"><div class="container"><h1 class="hero-title">Tạo Tài Liệu Word Chuyên Nghiệp<br>Trong Tích Tắc</h1><p class="hero-desc">Upload file định dạng thô của bạn và để EasyWord xử lý mọi thứ với công nghệ AI tiên tiến. Tiết kiệm 90% thời gian định dạng.</p></div></section>''', unsafe_allow_html=True)

# 3. TOOL BOX
st.markdown('<div class="tool-box-container">', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["☁️ Upload File", "⚡ Test Nhanh"])

with tab1:
    uploaded_file = st.file_uploader(
        "Kéo thả hoặc chọn file Word (.docx)",
        type=["docx"],
        help="Giới hạn 200MB/file • Hỗ trợ DOCX"
    )
    
    if uploaded_file:
        st.success(f"✅ Đã chọn: **{uploaded_file.name}**")
    
    with st.expander("⚙️ Tùy chỉnh nâng cao", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.checkbox("Xóa dòng trống", value=True, key="opt_clean")
            st.checkbox("Chuẩn hóa font", value=True, key="opt_font")
            st.checkbox("Chỉnh lề", value=True, key="opt_margins")
        with col2:
            st.checkbox("Tạo mục lục", value=True, key="opt_toc")
            st.checkbox("Đánh số trang", value=True, key="opt_page_numbers")
            st.number_input("Giãn dòng", 1.0, 2.0, 1.3, 0.1, key="line_spacing")
    
    if st.button("✨ Bắt đầu xử lý ngay", type="primary", key="btn_upload_process", use_container_width=True):
        if uploaded_file:
            with st.spinner("Đang xử lý tài liệu..."):
                if process_file(uploaded_file.read(), uploaded_file.name):
                    st.success("🎉 Xử lý thành công!")
                    st.rerun()
        else:
            st.warning("⚠️ Vui lòng chọn file trước khi xử lý!")

with tab2:
    st.info("💡 Sử dụng file mẫu có sẵn để kiểm tra nhanh tính năng của EasyWord")
    
    if st.button("🚀 Chạy Test Ngay", type="primary", key="btn_test", use_container_width=True):
        test_path = Path("test.docx")
        if test_path.exists():
            with st.spinner("Đang xử lý file test..."):
                with open(test_path, "rb") as f:
                    if process_file(f.read(), "test_result.docx"):
                        st.success("🎉 Test thành công!")
                        st.rerun()
        else:
            st.error("❌ Không tìm thấy file test.docx trong thư mục gốc")

st.markdown('</div>', unsafe_allow_html=True)

# 4. RESULTS
if "result_stream" in st.session_state:
    st.markdown("---")
    st.markdown("### 📥 Kết quả xử lý")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info(f"File sẵn sàng tải: **{st.session_state['result_name']}**")
    with col2:
        st.session_state["result_stream"].seek(0)
        st.download_button(
            "⬇️ Tải xuống",
            st.session_state["result_stream"],
            file_name=st.session_state["result_name"],
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True
        )
    
    with st.expander("👁️ Xem trước tài liệu", expanded=True):
        if "result_doc" in st.session_state:
            display_preview(st.session_state["result_doc"])

# 5. FEATURES SECTION
st.markdown('''<section class="features"><div style="text-align:center;margin-bottom:50px"><h2 style="font-size:2rem;font-weight:700;color:#1F2937;margin-bottom:10px">EasyWord Làm Được Gì?</h2><p style="color:#6B7280">Khám phá các tính năng mạnh mẽ giúp công việc của bạn hiệu quả hơn</p></div><div class="feature-grid"><div class="feature-card"><div class="icon-box bg-blue"><i class="fa-solid fa-file-lines"></i></div><div class="feature-h3">Tự Động Định Dạng</div><div class="feature-p">AI tự động nhận diện và áp dụng định dạng chuẩn cho tài liệu ngay lập tức.</div></div><div class="feature-card"><div class="icon-box bg-green"><i class="fa-solid fa-check-double"></i></div><div class="feature-h3">Kiểm Tra Chính Tả</div><div class="feature-p">Phát hiện và sửa lỗi chính tả, ngữ pháp tự động với độ chính xác cao.</div></div><div class="feature-card"><div class="icon-box bg-purple"><i class="fa-solid fa-palette"></i></div><div class="feature-h3">Template Đa Dạng</div><div class="feature-p">Hàng trăm mẫu tài liệu chuyên nghiệp sẵn có cho mọi mục đích.</div></div><div class="feature-card"><div class="icon-box bg-orange"><i class="fa-solid fa-sliders"></i></div><div class="feature-h3">Tùy Chỉnh Linh Hoạt</div><div class="feature-p">Điều chỉnh mọi chi tiết theo ý muốn chỉ với vài cú click chuột.</div></div><div class="feature-card"><div class="icon-box bg-red"><i class="fa-solid fa-bolt"></i></div><div class="feature-h3">Xử Lý Siêu Nhanh</div><div class="feature-p">Xử lý tài liệu trong vài giây dù file lớn hay phức tạp.</div></div><div class="feature-card"><div class="icon-box bg-teal"><i class="fa-solid fa-shield-halved"></i></div><div class="feature-h3">Bảo Mật Tuyệt Đối</div><div class="feature-p">Mọi tài liệu được mã hóa end-to-end, đảm bảo an toàn riêng tư.</div></div></div></section>''', unsafe_allow_html=True)

# 6. CTA SECTION
st.markdown('''<section class="cta-section"><h2 style="font-size:2rem;font-weight:700;margin-bottom:15px">Sẵn Sàng Bắt Đầu?</h2><p style="opacity:0.9">Tham gia hàng nghìn người dùng đang tin dùng EasyWord mỗi ngày.</p><a href="#" class="btn-white">Đăng Ký Miễn Phí Ngay</a></section>''', unsafe_allow_html=True)

# 7. FOOTER
st.markdown('''<footer class="custom-footer"><div class="footer-grid"><div class="footer-col"><a href="#" class="logo" style="color:#fff;margin-bottom:20px;display:inline-block"><i class="fa-solid fa-file-word"></i> EasyWord</a><p style="font-size:0.9rem;color:#9CA3AF">Giải pháp tạo tài liệu Word thông minh và chuyên nghiệp hàng đầu Việt Nam.</p></div><div class="footer-col"><h4>Sản phẩm</h4><a href="#">Tính năng</a><a href="#">Bảng giá</a><a href="#">Templates</a><a href="#">API</a></div><div class="footer-col"><h4>Hỗ trợ</h4><a href="#">Trung tâm trợ giúp</a><a href="#">Liên hệ</a><a href="#">Cộng đồng</a></div><div class="footer-col"><h4>Pháp lý</h4><a href="#">Điều khoản</a><a href="#">Bảo mật</a><a href="#">Cookie Policy</a></div></div><div style="text-align:center;border-top:1px solid #374151;padding-top:20px;font-size:0.9rem;color:#9CA3AF;max-width:1200px;margin:0 auto">© 2026 EasyWord. All rights reserved.</div></footer>''', unsafe_allow_html=True)
