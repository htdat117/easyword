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

# Fix path
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))

# Import app modules
try:
    from docx import Document
    from app.services.report_formatter import format_uploaded_stream, docx_to_html
    from app.config import TEMP_DIR, CONVERTAPI_SECRET
except Exception as e:
    st.error(f"❌ Import Error: {e}")
    st.stop()

# ============================================================================
# CSS INJECTION
# ============================================================================
st.markdown('<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">', unsafe_allow_html=True)
st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">', unsafe_allow_html=True)

css = """
<style>
* { font-family: 'Inter', sans-serif; margin: 0; padding: 0; box-sizing: border-box; }
body { background-color: #F9FAFB; color: #1F2937; line-height: 1.6; }

/* Hide Streamlit defaults */
#MainMenu, footer, header[data-testid="stHeader"], .stDeployButton { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* Custom Header */
.custom-header { background-color: #FFFFFF; box-shadow: 0 1px 3px rgba(0,0,0,0.1); padding: 0 20px; }
.nav-wrapper { max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; height: 70px; }
.logo { font-size: 1.5rem; font-weight: 700; color: #2563EB; display: flex; align-items: center; gap: 10px; text-decoration: none; }
.auth-buttons a { text-decoration: none; font-weight: 500; }
.btn-login { color: #1F2937; margin-right: 15px; }
.btn-signup { background-color: #2563EB; color: #FFFFFF !important; padding: 8px 20px; border-radius: 6px; }

/* Apply gradient to entire Streamlit app background */
.stApp { background: linear-gradient(180deg, #FFFFFF 0%, #EFF6FF 50%, #FFFFFF 50%) !important; }

/* Hero Section */
.hero-full { background: transparent; padding: 60px 20px 30px; text-align: center; }
.hero-title { font-size: 2.8rem; color: #111827; margin-bottom: 16px; line-height: 1.2; font-weight: 700; }
.hero-desc { font-size: 1.1rem; color: #6B7280; margin-bottom: 30px; max-width: 600px; margin-left: auto; margin-right: auto; }

/* Tool Box - centered card */
.tool-box { background: #FFFFFF; border-radius: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); padding: 30px; max-width: 700px; margin: 0 auto; border: 1px solid #E5E7EB; }

/* Streamlit Tabs - match TEST.HTML */
[data-testid="stTabs"] [data-baseweb="tab-list"] { justify-content: center; gap: 0; border-bottom: none !important; background: transparent !important; }
[data-testid="stTabs"] button[data-baseweb="tab"] { background: transparent !important; border: none !important; border-bottom: 2px solid transparent !important; color: #6B7280 !important; font-weight: 600 !important; padding: 12px 24px !important; margin: 0 !important; border-radius: 0 !important; }
[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] { color: #2563EB !important; border-bottom: 2px solid #2563EB !important; }
[data-testid="stTabs"] button[data-baseweb="tab"]:hover { color: #2563EB !important; background: transparent !important; }
[data-testid="stTabs"] [data-baseweb="tab-highlight"], [data-testid="stTabs"] [data-baseweb="tab-border"] { display: none !important; }

/* File Uploader - match TEST.HTML upload-area */
[data-testid="stFileUploader"] { border: 2px dashed #D1D5DB !important; border-radius: 12px !important; padding: 50px 20px !important; background-color: #F9FAFB !important; text-align: center !important; transition: all 0.3s; }
[data-testid="stFileUploader"]:hover { border-color: #2563EB !important; background-color: #EFF6FF !important; }
[data-testid="stFileUploader"] > label { display: none !important; }
[data-testid="stFileUploader"] section { background: transparent !important; border: none !important; }
[data-testid="stFileUploader"] section > div { flex-direction: column !important; align-items: center !important; }
[data-testid="stFileUploader"] section > div::before { content: "\\f0ee"; font-family: "Font Awesome 6 Free"; font-weight: 900; font-size: 3rem; color: #2563EB; display: block; margin-bottom: 15px; }
[data-testid="stFileUploader"] section > div > span { font-size: 1.1rem !important; font-weight: 600 !important; color: #1F2937 !important; }
[data-testid="stFileUploader"] section small { color: #9CA3AF !important; font-size: 0.9rem !important; margin-top: 5px !important; }
[data-testid="stFileUploader"] button { background: #E5E7EB !important; color: #374151 !important; border: 1px solid #D1D5DB !important; padding: 8px 20px !important; border-radius: 8px !important; font-weight: 500 !important; margin-top: 15px !important; }
[data-testid="stFileUploader"] button:hover { background: #D1D5DB !important; }

/* Primary Button - match TEST.HTML btn-action */
div.stButton > button[kind="primary"], div.stButton > button { width: 100% !important; padding: 15px 20px !important; background-color: #2563EB !important; color: #FFFFFF !important; border: none !important; border-radius: 8px !important; font-size: 1rem !important; font-weight: 600 !important; margin-top: 20px !important; cursor: pointer !important; }
div.stButton > button:hover { background-color: #1D4ED8 !important; }

/* Expander */
[data-testid="stExpander"] { border: 1px solid #E5E7EB !important; border-radius: 8px !important; margin-top: 15px !important; background: #F9FAFB !important; }
[data-testid="stExpander"] summary { font-weight: 500 !important; }

/* Features Section */
.features-section { padding: 80px 20px; background-color: #FFFFFF; }
.features-container { max-width: 1200px; margin: 0 auto; }
.section-title { text-align: center; margin-bottom: 60px; }
.section-title h2 { font-size: 2.25rem; margin-bottom: 10px; font-weight: 700; color: #1F2937; }
.section-title p { color: #6B7280; }
.feature-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 30px; }
.feature-card { padding: 30px; border-radius: 12px; background: #F8FAFC; transition: all 0.3s; border: 1px solid transparent; }
.feature-card:hover { transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.05); border-color: #E2E8F0; background: #FFFFFF; }
.icon-box { width: 50px; height: 50px; border-radius: 10px; display: flex; align-items: center; justify-content: center; margin-bottom: 20px; font-size: 1.5rem; }
.bg-blue { background: #DBEAFE; color: #2563EB; }
.bg-green { background: #D1FAE5; color: #059669; }
.bg-purple { background: #EDE9FE; color: #7C3AED; }
.bg-orange { background: #FFEDD5; color: #EA580C; }
.bg-red { background: #FEE2E2; color: #DC2626; }
.bg-teal { background: #CCFBF1; color: #0D9488; }
.feature-card h3 { font-size: 1.25rem; margin-bottom: 10px; font-weight: 600; color: #1F2937; }
.feature-card p { color: #6B7280; font-size: 0.95rem; }

/* CTA Section */
.cta-section { padding: 80px 20px; background: linear-gradient(135deg, #2563EB 0%, #1E40AF 100%); color: #FFFFFF; text-align: center; }
.cta-section h2 { font-size: 2.5rem; margin-bottom: 20px; font-weight: 700; }
.cta-section p { font-size: 1.1rem; opacity: 0.9; margin-bottom: 20px; }
.btn-white { display: inline-block; background: #FFFFFF; color: #2563EB !important; padding: 15px 40px; border-radius: 8px; font-weight: 700; text-decoration: none; }
.btn-white:hover { transform: scale(1.05); }

/* Footer */
.custom-footer { background-color: #111827; color: #D1D5DB; padding: 60px 20px 20px; }
.footer-container { max-width: 1200px; margin: 0 auto; }
.footer-grid { display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; gap: 40px; margin-bottom: 40px; }
.footer-col h4 { color: #FFFFFF; margin-bottom: 20px; font-weight: 600; }
.footer-col a { color: #9CA3AF; text-decoration: none; display: block; margin-bottom: 10px; }
.footer-col a:hover { color: #FFFFFF; }
.copyright { text-align: center; border-top: 1px solid #374151; padding-top: 20px; font-size: 0.9rem; }

@media (max-width: 768px) {
    .hero-title { font-size: 2rem; }
    .feature-grid { grid-template-columns: 1fr; }
    .footer-grid { grid-template-columns: 1fr; text-align: center; }
}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
def collect_options():
    return {
        "clean_whitespace": st.session_state.get("opt_clean", True),
        "normalize_font": st.session_state.get("opt_font", True),
        "adjust_margins": st.session_state.get("opt_margins", True),
        "indent_spacing": True,
        "heading_detection": True,
        "format_tables": True,
        "insert_toc": st.session_state.get("opt_toc", True),
        "add_page_numbers": st.session_state.get("opt_page_numbers", True),
        "line_spacing": st.session_state.get("line_spacing", 1.3),
        "auto_numbered_heading": True,
    }

def convert_docx_to_pdf_cloud(docx_path, output_pdf_path):
    try:
        import requests
        if not CONVERTAPI_SECRET: return None
        url = f"https://v2.convertapi.com/convert/docx/to/pdf?Secret={CONVERTAPI_SECRET}&download=attachment"
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
    with open(pdf_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    html = f'''<!DOCTYPE html><html><head><script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script><style>body{{margin:0;background:#525659}}canvas{{display:block;margin:20px auto;box-shadow:0 4px 12px rgba(0,0,0,0.3)}}</style></head><body><div id="c"></div><script>pdfjsLib.GlobalWorkerOptions.workerSrc='https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';pdfjsLib.getDocument({{data:atob("{base64_pdf}")}}).promise.then(p=>{{for(let i=1;i<=p.numPages;i++)p.getPage(i).then(g=>{{let v=g.getViewport({{scale:1}}),c=document.createElement('canvas'),x=c.getContext('2d');c.height=v.height;c.width=v.width;document.getElementById('c').appendChild(c);g.render({{canvasContext:x,viewport:v}})}})}})</script></body></html>'''
    st.components.v1.html(html, height=800, scrolling=True)

def display_preview(doc):
    temp_docx = TEMP_DIR / f"preview_{uuid.uuid4()}.docx"
    temp_pdf = TEMP_DIR / f"preview_{uuid.uuid4()}.pdf"
    try:
        doc.save(str(temp_docx))
        if CONVERTAPI_SECRET:
            with st.spinner("🔄 Đang tạo PDF Preview..."):
                if convert_docx_to_pdf_cloud(temp_docx, temp_pdf) and temp_pdf.exists():
                    display_pdf_with_pdfjs(temp_pdf)
                    return
        html_content = docx_to_html(doc)
        st.components.v1.html(html_content, height=800, scrolling=True)
    except Exception as e:
        st.error(f"Lỗi Preview: {e}")
    finally:
        for f in [temp_docx, temp_pdf]:
            try: f.unlink() if f.exists() else None
            except: pass

def process_file(file_bytes, filename):
    try:
        stream, name = format_uploaded_stream(file_bytes, filename, collect_options())
        st.session_state["result_stream"] = stream
        st.session_state["result_name"] = name
        stream.seek(0)
        st.session_state["result_doc"] = Document(stream)
        return True
    except Exception as e:
        st.error(f"Lỗi: {e}")
        return False

# ============================================================================
# 1. HEADER
# ============================================================================
st.markdown('''
<header class="custom-header">
    <div class="nav-wrapper">
        <a href="#" class="logo"><i class="fa-solid fa-file-word"></i> EasyWord</a>
        <div class="auth-buttons">
            <a href="#" class="btn-login">Đăng nhập</a>
            <a href="#" class="btn-signup">Đăng ký ngay</a>
        </div>
    </div>
</header>
''', unsafe_allow_html=True)

# ============================================================================
# 2. HERO SECTION WITH TOOL BOX
# ============================================================================
st.markdown('''
<div class="hero-full">
    <h1 class="hero-title">Tạo Tài Liệu Word Chuyên Nghiệp<br>Trong Tích Tắc</h1>
    <p class="hero-desc">Upload file định dạng thô của bạn và để EasyWord xử lý mọi thứ với công nghệ AI tiên tiến. Tiết kiệm 90% thời gian định dạng.</p>
</div>
''', unsafe_allow_html=True)

# Tool Box with actual Streamlit widgets
st.markdown('<div style="max-width:700px;margin:-60px auto 40px;background:#fff;border-radius:16px;box-shadow:0 10px 25px rgba(0,0,0,0.05);padding:30px;border:1px solid #E5E7EB;position:relative;z-index:10;">', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["☁️ Upload File", "⚡ Test Nhanh"])

with tab1:
    uploaded_file = st.file_uploader(
        "Kéo thả hoặc chọn file Word (.docx)",
        type=["docx"],
        help="Giới hạn 200MB/file • Hỗ trợ DOCX",
        key="main_uploader"
    )
    
    if uploaded_file:
        st.success(f"✅ Đã chọn: **{uploaded_file.name}**")
    
    with st.expander("⚙️ Tùy chỉnh nâng cao"):
        c1, c2 = st.columns(2)
        with c1:
            st.checkbox("Xóa dòng trống", True, key="opt_clean")
            st.checkbox("Chuẩn hóa font", True, key="opt_font")
            st.checkbox("Chỉnh lề", True, key="opt_margins")
        with c2:
            st.checkbox("Tạo mục lục", True, key="opt_toc")
            st.checkbox("Đánh số trang", True, key="opt_page_numbers")
            st.number_input("Giãn dòng", 1.0, 2.0, 1.3, 0.1, key="line_spacing")
    
    if st.button("✨ Bắt đầu xử lý ngay", type="primary", key="btn_process", use_container_width=True):
        if uploaded_file:
            with st.spinner("Đang xử lý..."):
                if process_file(uploaded_file.read(), uploaded_file.name):
                    st.success("🎉 Thành công!")
                    st.rerun()
        else:
            st.warning("⚠️ Vui lòng chọn file!")

with tab2:
    st.info("💡 Dùng file mẫu để kiểm tra nhanh")
    if st.button("🚀 Chạy Test Ngay", type="primary", key="btn_test", use_container_width=True):
        test_path = Path("test.docx")
        if test_path.exists():
            with st.spinner("Đang xử lý..."):
                with open(test_path, "rb") as f:
                    if process_file(f.read(), "test_result.docx"):
                        st.success("🎉 Thành công!")
                        st.rerun()
        else:
            st.error("❌ Không tìm thấy test.docx")

st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# 3. RESULTS
# ============================================================================
if "result_stream" in st.session_state:
    st.markdown('<div style="max-width:900px;margin:0 auto 40px;padding:0 20px;">', unsafe_allow_html=True)
    st.markdown("### 📥 Kết quả xử lý")
    c1, c2 = st.columns([3, 1])
    with c1:
        st.info(f"File: **{st.session_state['result_name']}**")
    with c2:
        st.session_state["result_stream"].seek(0)
        st.download_button("⬇️ Tải xuống", st.session_state["result_stream"], st.session_state["result_name"], 
                          "application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)
    with st.expander("👁️ Xem trước", expanded=True):
        if "result_doc" in st.session_state:
            display_preview(st.session_state["result_doc"])
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# 4. FEATURES
# ============================================================================
st.markdown('''
<section class="features-section">
    <div class="features-container">
        <div class="section-title">
            <h2>EasyWord Làm Được Gì?</h2>
            <p>Khám phá các tính năng mạnh mẽ giúp công việc của bạn hiệu quả hơn</p>
        </div>
        <div class="feature-grid">
            <div class="feature-card">
                <div class="icon-box bg-blue"><i class="fa-solid fa-file-lines"></i></div>
                <h3>Tự Động Định Dạng</h3>
                <p>AI tự động nhận diện và áp dụng định dạng chuẩn (Heading, Paragraph, List) cho tài liệu.</p>
            </div>
            <div class="feature-card">
                <div class="icon-box bg-green"><i class="fa-solid fa-check-double"></i></div>
                <h3>Kiểm Tra Chính Tả</h3>
                <p>Phát hiện và sửa lỗi chính tả, ngữ pháp tự động với độ chính xác cao cho Tiếng Việt.</p>
            </div>
            <div class="feature-card">
                <div class="icon-box bg-purple"><i class="fa-solid fa-palette"></i></div>
                <h3>Template Đa Dạng</h3>
                <p>Hàng trăm mẫu tài liệu chuyên nghiệp cho mọi mục đích: Báo cáo, CV, Đơn từ.</p>
            </div>
            <div class="feature-card">
                <div class="icon-box bg-orange"><i class="fa-solid fa-sliders"></i></div>
                <h3>Tùy Chỉnh Linh Hoạt</h3>
                <p>Điều chỉnh font chữ, màu sắc, căn lề chỉ với vài cú click chuột.</p>
            </div>
            <div class="feature-card">
                <div class="icon-box bg-red"><i class="fa-solid fa-bolt"></i></div>
                <h3>Xử Lý Siêu Nhanh</h3>
                <p>Xử lý tài liệu trong vài giây dù file lớn hay phức tạp.</p>
            </div>
            <div class="feature-card">
                <div class="icon-box bg-teal"><i class="fa-solid fa-shield-halved"></i></div>
                <h3>Bảo Mật Tuyệt Đối</h3>
                <p>Mọi tài liệu được mã hóa end-to-end. File tự hủy sau 24h.</p>
            </div>
        </div>
    </div>
</section>
''', unsafe_allow_html=True)

# ============================================================================
# 5. CTA
# ============================================================================
st.markdown('''
<section class="cta-section">
    <h2>Sẵn Sàng Bắt Đầu?</h2>
    <p>Tham gia hàng nghìn người dùng đang tin dùng EasyWord mỗi ngày.</p>
    <a href="#" class="btn-white">Đăng Ký Miễn Phí Ngay</a>
</section>
''', unsafe_allow_html=True)

# ============================================================================
# 6. FOOTER
# ============================================================================
st.markdown('''
<footer class="custom-footer">
    <div class="footer-container">
        <div class="footer-grid">
            <div class="footer-col">
                <a href="#" class="logo" style="color:#fff;margin-bottom:20px;display:inline-block"><i class="fa-solid fa-file-word"></i> EasyWord</a>
                <p style="color:#9CA3AF;font-size:0.9rem">Giải pháp tạo tài liệu Word thông minh hàng đầu Việt Nam.</p>
            </div>
            <div class="footer-col">
                <h4>Sản phẩm</h4>
                <a href="#">Tính năng</a><a href="#">Bảng giá</a><a href="#">Templates</a><a href="#">API</a>
            </div>
            <div class="footer-col">
                <h4>Hỗ trợ</h4>
                <a href="#">Trung tâm trợ giúp</a><a href="#">Liên hệ</a><a href="#">Cộng đồng</a>
            </div>
            <div class="footer-col">
                <h4>Pháp lý</h4>
                <a href="#">Điều khoản</a><a href="#">Bảo mật</a><a href="#">Cookie Policy</a>
            </div>
        </div>
        <div class="copyright">© 2026 EasyWord. All rights reserved.</div>
    </div>
</footer>
''', unsafe_allow_html=True)
