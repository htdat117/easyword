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
# CSS & ASSETS INJECTION
# ============================================================================
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
:root { --primary-color: #2563EB; --primary-dark: #1D4ED8; --secondary-color: #F3F4F6; --text-dark: #1F2937; --text-light: #6B7280; --white: #FFFFFF; --accent: #F59E0B; }
* { font-family: 'Inter', sans-serif; }
body { background-color: #F9FAFB; color: var(--text-dark); line-height: 1.6; }
#MainMenu, footer, header[data-testid="stHeader"], .stDeployButton { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }
.custom-header { background-color: var(--white); box-shadow: 0 1px 3px rgba(0,0,0,0.1); position: sticky; top: 0; z-index: 1000; padding: 0; }
.container { max-width: 1200px; margin: 0 auto; padding: 0 20px; }
.nav-wrapper { display: flex; justify-content: space-between; align-items: center; height: 70px; }
.logo { font-size: 1.5rem; font-weight: 700; color: var(--primary-color); display: flex; align-items: center; gap: 10px; text-decoration: none; }
.btn-login { color: var(--text-dark); margin-right: 15px; text-decoration: none; font-weight: 500; padding: 8px 16px; border-radius: 6px; }
.btn-signup { background-color: var(--primary-color); color: var(--white); text-decoration: none; padding: 8px 20px; border-radius: 6px; font-weight: 500; transition: background 0.3s; }
.btn-signup:hover { background: var(--primary-dark); color: white; }
.hero { text-align: center; padding: 80px 0 60px; background: linear-gradient(180deg, #FFFFFF 0%, #EFF6FF 100%); }
.hero-title { font-size: 3rem; color: #111827; margin-bottom: 16px; line-height: 1.2; font-weight: 700; }
.hero-desc { font-size: 1.125rem; color: var(--text-light); margin-bottom: 40px; max-width: 600px; margin-left: auto; margin-right: auto; }
.tool-box-wrapper { background: var(--white); border-radius: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); padding: 30px; max-width: 800px; margin: 0 auto; border: 1px solid #E5E7EB; }
[data-testid="stTabs"] { display: flex; justify-content: center; gap: 15px; margin-bottom: 20px; }
div[data-testid="stTabs"] button[data-testid="stTab"] { background-color: transparent; border: none; border-bottom: 2px solid transparent; color: #6B7280; font-weight: 600; padding: 10px 20px; height: auto; border-radius: 0; }
div[data-testid="stTabs"] button[data-testid="stTab"]:hover { color: #2563EB; }
div[data-testid="stTabs"] button[data-testid="stTab"][aria-selected="true"] { color: #2563EB; border-bottom: 2px solid #2563EB; }
[data-testid="stTabs"] > div:first-child { border-bottom: none !important; }
[data-testid="stFileUploader"] { border: 2px dashed #D1D5DB; border-radius: 12px; padding: 3rem 2rem; background-color: #F9FAFB; transition: all 0.3s; text-align: center; display: flex; flex-direction: column; align-items: center; justify-content: center; }
[data-testid="stFileUploader"]:hover { border-color: #2563EB; background-color: #EFF6FF; }
[data-testid="stFileUploader"]::before { content: "\\f0ee"; font-family: "Font Awesome 6 Free"; font-weight: 900; font-size: 3rem; color: #2563EB; margin-bottom: 15px; display: block; }
[data-testid="stFileUploader"]::after { content: "Kéo thả hoặc chọn file Word (.docx) \\A Giới hạn 200MB/file • Hỗ trợ DOCX"; white-space: pre-wrap; font-size: 1rem; font-weight: 600; color: #4B5563; margin-top: 10px; margin-bottom: 15px; display: block; }
[data-testid="stFileUploader"] section > div > span, [data-testid="stFileUploader"] small { display: none !important; }
[data-testid="stFileUploader"] button { display: inline-block; background: #E5E7EB; color: #374151; border: none; padding: 8px 16px; border-radius: 8px; font-size: 0.9rem; font-weight: 500; margin-top: 10px; }
div.stButton > button { display: block; width: 100%; padding: 15px; background-color: #2563EB; color: #FFFFFF; border: none; border-radius: 8px; font-size: 1rem; font-weight: 600; margin-top: 20px; cursor: pointer; box-shadow: none; }
div.stButton > button:hover { background-color: #1D4ED8; color: #FFFFFF; border-color: #1D4ED8; }
div.stButton > button:active { color: #FFFFFF; }
.features { padding: 80px 0; background-color: var(--white); }
.feature-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 30px; }
.feature-card { padding: 30px; border-radius: 12px; background: #F8FAFC; transition: transform 0.3s, box-shadow 0.3s; border: 1px solid transparent; }
.feature-card:hover { transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.05); border-color: #E2E8F0; background: var(--white); }
.icon-box { width: 50px; height: 50px; border-radius: 10px; display: flex; align-items: center; justify-content: center; margin-bottom: 20px; font-size: 1.5rem; }
.bg-blue { background: #DBEAFE; color: #2563EB; }
.bg-green { background: #D1FAE5; color: #059669; }
.bg-purple { background: #EDE9FE; color: #7C3AED; }
.bg-orange { background: #FFEDD5; color: #EA580C; }
.bg-red { background: #FEE2E2; color: #DC2626; }
.bg-teal { background: #CCFBF1; color: #0D9488; }
.feature-h3 { font-size: 1.25rem; margin-bottom: 10px; font-weight: 600; color: #1F2937; }
.feature-p { color: var(--text-light); font-size: 0.95rem; }
.cta-section { padding: 80px 0; background: linear-gradient(135deg, #2563EB 0%, #1E40AF 100%); color: var(--white); text-align: center; }
.btn-white { display: inline-block; background: var(--white); color: var(--primary-color) !important; padding: 15px 40px; border-radius: 8px; font-weight: 700; text-decoration: none; margin-top: 20px; transition: transform 0.2s; }
.btn-white:hover { transform: scale(1.05); }
.custom-footer { background-color: #111827; color: #D1D5DB; padding: 60px 0 20px; margin-top: -100px; }
.footer-grid { display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; gap: 40px; margin-bottom: 40px; }
.footer-col h4 { color: white; margin-bottom: 20px; font-weight: 600; }
.footer-col a { color: #9CA3AF; text-decoration: none; display: block; margin-bottom: 10px; }
.footer-col a:hover { color: white; }
@media (max-width: 768px) { .footer-grid { grid-template-columns: 1fr; text-align: center; } .hero-title { font-size: 2rem; } }
</style>
""", unsafe_allow_html=True)

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
    import base64
    with open(pdf_path, "rb") as pdf_file:
        base64_pdf = base64.b64encode(pdf_file.read()).decode('utf-8')
    
    pdfjs_html = f'''
<!DOCTYPE html><html><head>
<script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>
<style>body{{margin:0;background:#525659;}} canvas{{display:block;margin:20px auto;box-shadow:0 4px 12px rgba(0,0,0,0.3);}}</style>
</head><body><div id="pdf-container"></div>
<script>
    pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
    const pdfData = atob("{base64_pdf}");
    pdfjsLib.getDocument({{data: pdfData}}).promise.then(pdf => {{
        for (let i = 1; i <= pdf.numPages; i++) {{
            pdf.getPage(i).then(page => {{
                const scale = 1.0;
                const viewport = page.getViewport({{scale}});
                const canvas = document.createElement('canvas');
                const context = canvas.getContext('2d');
                canvas.height = viewport.height;
                canvas.width = viewport.width;
                document.getElementById('pdf-container').appendChild(canvas);
                page.render({{canvasContext: context, viewport: viewport}});
            }});
        }}
    }});
</script></body></html>'''
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

# ============================================================================
# APP LAYOUT
# ============================================================================

# 1. HEADER
st.markdown("""
<header class="custom-header">
<div class="container nav-wrapper">
<a href="#" class="logo">
<i class="fa-solid fa-file-word"></i> EasyWord
</a>
<div class="auth-buttons">
<a href="#" class="btn-login">Đăng nhập</a>
<a href="#" class="btn-signup">Đăng ký ngay</a>
</div>
</div>
</header>
""", unsafe_allow_html=True)

# 2. HERO
st.markdown("""
<section class="hero">
<div class="container">
<h1 class="hero-title">Tạo Tài Liệu Word Chuyên Nghiệp<br>Trong Tích Tắc</h1>
<p class="hero-desc">Upload file định dạng thô của bạn và để EasyWord xử lý mọi thứ với công nghệ AI tiên tiến. Tiết kiệm 90% thời gian định dạng.</p>
</div>
</section>
""", unsafe_allow_html=True)

# 3. TOOL BOX (Interactive)
st.markdown('<div class="container"><div class="tool-box-wrapper">', unsafe_allow_html=True)

# Tabs
tab1, tab2 = st.tabs(["☁️ Upload File", "⚡ Test Nhanh"])

with tab1:
    st.markdown('<div style="margin-top: 20px;"></div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload Word File", type=["docx"], label_visibility="collapsed")
    
    if uploaded_file:
        st.success(f"✅ Selected: {uploaded_file.name}")
        
    # Options inside expander to keep clean
    with st.expander("⚙️ Tùy chỉnh nâng cao"):
        col1, col2 = st.columns(2)
        with col1:
            st.checkbox("Xóa dòng trống", value=True, key="opt_clean")
            st.checkbox("Chuẩn hóa font", value=True, key="opt_font")
            st.checkbox("Chỉnh lề", value=True, key="opt_margins")
        with col2:
            st.checkbox("Tạo mục lục", value=True, key="opt_toc")
            st.checkbox("Đánh số trang", value=True, key="opt_page_numbers")
            st.number_input("Giãn dòng", 1.0, 2.0, 1.3, 0.1, key="line_spacing")

    if st.button("✨ Bắt đầu xử lý ngay", type="primary", key="btn_process_upload"):
        if uploaded_file:
            with st.spinner("Đang xử lý..."):
                try:
                    bytes_data = uploaded_file.read()
                    opts = collect_options()
                    stream, name = format_uploaded_stream(bytes_data, uploaded_file.name, opts)
                    st.session_state["result_stream"] = stream
                    st.session_state["result_name"] = name
                    stream.seek(0)
                    st.session_state["result_doc"] = Document(stream)
                    st.success("Xử lý thành công!")
                except Exception as e:
                    st.error(f"Lỗi: {e}")
        else:
            st.warning("Vui lòng upload file trước!")

with tab2:
    st.info("Sử dụng file mẫu để kiểm tra nhanh tính năng")
    if st.button("🚀 Chạy Test Ngay", key="btn_test_quick"):
        test_path = Path("test.docx")
        if test_path.exists():
             with st.spinner("Đang xử lý test..."):
                try:
                    with open(test_path, "rb") as f:
                        bytes_data = f.read()
                    opts = collect_options()
                    stream, name = format_uploaded_stream(bytes_data, "test_result.docx", opts)
                    st.session_state["result_stream"] = stream
                    st.session_state["result_name"] = name
                    stream.seek(0)
                    st.session_state["result_doc"] = Document(stream)
                    st.success("Test thành công!")
                except Exception as e:
                    st.error(f"Lỗi: {e}")
        else:
            st.error("Không tìm thấy file test.docx")

st.markdown('</div></div>', unsafe_allow_html=True) # End tool-box-wrapper

# 4. RESULTS (If any)
if "result_stream" in st.session_state:
    st.markdown('<div class="container" style="margin-top: 2rem;">', unsafe_allow_html=True)
    st.markdown("### 📥 Kết quả")
    col_d1, col_d2 = st.columns([3, 1])
    with col_d1:
        st.info(f"File sẵn sàng: **{st.session_state['result_name']}**")
    with col_d2:
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
    st.markdown('</div>', unsafe_allow_html=True)


# 5. FEATURES SECTION
st.markdown("""
<section class="features">
<div class="container">
<div style="text-align: center; margin-bottom: 60px;">
<h2 style="font-size: 2.25rem; margin-bottom: 10px; font-weight: 700; color: #1F2937;">EasyWord Làm Được Gì?</h2>
<p style="color: #6B7280;">Khám phá các tính năng mạnh mẽ giúp công việc của bạn hiệu quả hơn</p>
</div>
<div class="feature-grid">
<div class="feature-card">
<div class="icon-box bg-blue"><i class="fa-solid fa-file-lines"></i></div>
<div class="feature-h3">Tự Động Định Dạng</div>
<div class="feature-p">AI tự động nhận diện và áp dụng định dạng chuẩn (Heading, Paragraph, List) cho tài liệu ngay lập tức.</div>
</div>
<div class="feature-card">
<div class="icon-box bg-green"><i class="fa-solid fa-check-double"></i></div>
<div class="feature-h3">Kiểm Tra Chính Tả</div>
<div class="feature-p">Phát hiện và sửa lỗi chính tả, ngữ pháp tự động với độ chính xác cao dành cho Tiếng Việt.</div>
</div>
<div class="feature-card">
<div class="icon-box bg-purple"><i class="fa-solid fa-palette"></i></div>
<div class="feature-h3">Template Đa Dạng</div>
<div class="feature-p">Hàng trăm mẫu tài liệu chuyên nghiệp sẵn có cho mọi mục đích: Báo cáo, CV, Đơn từ, Hợp đồng.</div>
</div>
<div class="feature-card">
<div class="icon-box bg-orange"><i class="fa-solid fa-sliders"></i></div>
<div class="feature-h3">Tùy Chỉnh Linh Hoạt</div>
<div class="feature-p">Điều chỉnh mọi chi tiết theo ý muốn: font chữ, màu sắc, căn lề chỉ với vài cú click chuột.</div>
</div>
<div class="feature-card">
<div class="icon-box bg-red"><i class="fa-solid fa-bolt"></i></div>
<div class="feature-h3">Xử Lý Siêu Nhanh</div>
<div class="feature-p">Xử lý tài liệu trong vài giây dù file lớn hay phức tạp. Không còn chờ đợi.</div>
</div>
<div class="feature-card">
<div class="icon-box bg-teal"><i class="fa-solid fa-shield-halved"></i></div>
<div class="feature-h3">Bảo Mật Tuyệt Đối</div>
<div class="feature-p">Mọi tài liệu được mã hóa end-to-end, đảm bảo an toàn riêng tư. File tự hủy sau 24h.</div>
</div>
</div>
</div>
</section>
""", unsafe_allow_html=True)

# 6. CTA SECTION
st.markdown("""
<section class="cta-section">
<div class="container">
<h2 style="font-size: 2.5rem; margin-bottom: 20px; font-weight: 700;">Sẵn Sàng Bắt Đầu?</h2>
<p style="font-size: 1.1rem; opacity: 0.9;">Tham gia hàng nghìn người dùng đang tin dùng EasyWord mỗi ngày để tối ưu hóa công việc.</p>
<a href="#" class="btn-white">Đăng Ký Miễn Phí Ngay</a>
</div>
</section>
""", unsafe_allow_html=True)

# 7. FOOTER
st.markdown("""
<footer class="custom-footer">
<div class="container">
<div class="footer-grid">
<div class="footer-col">
<a href="#" class="logo" style="color: #fff; margin-bottom: 20px; display: inline-block;">
<i class="fa-solid fa-file-word"></i> EasyWord
</a>
<p style="font-size: 0.9rem; color: #9CA3AF;">Giải pháp tạo tài liệu Word thông minh và chuyên nghiệp hàng đầu Việt Nam.</p>
</div>
<div class="footer-col">
<h4>Sản phẩm</h4>
<a href="#">Tính năng</a>
<a href="#">Bảng giá</a>
<a href="#">Templates</a>
<a href="#">API</a>
</div>
<div class="footer-col">
<h4>Hỗ trợ</h4>
<a href="#">Trung tâm trợ giúp</a>
<a href="#">Liên hệ</a>
<a href="#">Cộng đồng</a>
</div>
<div class="footer-col">
<h4>Pháp lý</h4>
<a href="#">Điều khoản</a>
<a href="#">Bảo mật</a>
<a href="#">Cookie Policy</a>
</div>
</div>
<div style="text-align: center; border-top: 1px solid #374151; padding-top: 20px; font-size: 0.9rem; color: #9CA3AF;">
&copy; 2026 EasyWord. All rights reserved.
</div>
</div>
</footer>
""", unsafe_allow_html=True)
