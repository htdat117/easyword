import streamlit as st
import uuid
from pathlib import Path
import logging
import sys
import base64

# ============================================================================
# PAGE CONFIG
# ============================================================================
st.set_page_config(
    page_title="EasyWord - Tạo Tài Liệu Word Chuyên Nghiệp",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed",
)

logging.basicConfig(level=logging.INFO)

current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))

try:
    from docx import Document
    from app.services.report_formatter import format_uploaded_stream, docx_to_html
    from app.config import TEMP_DIR, CONVERTAPI_SECRET
except Exception as e:
    st.error(f"❌ Import Error: {e}")
    st.stop()

# ============================================================================
# CSS - EXACT MATCH WITH TEST.HTML
# ============================================================================
st.markdown('<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">', unsafe_allow_html=True)
st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">', unsafe_allow_html=True)

css = """
<style>
:root {
    --primary-color: #2563EB;
    --primary-dark: #1D4ED8;
    --secondary-color: #F3F4F6;
    --text-dark: #1F2937;
    --text-light: #6B7280;
    --white: #FFFFFF;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: 'Inter', sans-serif;
}

body {
    background-color: #F9FAFB;
    color: var(--text-dark);
    line-height: 1.6;
}

/* Hide Streamlit defaults */
#MainMenu, footer, header[data-testid="stHeader"], .stDeployButton { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* Header */
.site-header {
    background-color: var(--white);
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    position: sticky;
    top: 0;
    z-index: 1000;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}

.nav-wrapper {
    display: flex;
    justify-content: space-between;
    align-items: center;
    height: 70px;
}

.logo {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--primary-color);
    display: flex;
    align-items: center;
    gap: 10px;
    text-decoration: none;
}

.auth-buttons .btn {
    padding: 8px 20px;
    border-radius: 6px;
    font-weight: 500;
    text-decoration: none;
    transition: all 0.3s ease;
}

.btn-login {
    color: var(--text-dark);
    margin-right: 10px;
}

.btn-signup {
    background-color: var(--primary-color);
    color: var(--white) !important;
}

.btn-signup:hover {
    background-color: var(--primary-dark);
}

/* Hero Section */
.hero {
    text-align: center;
    padding: 80px 0 60px;
    background: linear-gradient(180deg, #FFFFFF 0%, #EFF6FF 100%);
}

.hero h1 {
    font-size: 3rem;
    color: #111827;
    margin-bottom: 16px;
    line-height: 1.2;
    font-weight: 700;
}

.hero p {
    font-size: 1.125rem;
    color: var(--text-light);
    margin-bottom: 40px;
    max-width: 600px;
    margin-left: auto;
    margin-right: auto;
}

/* Tool Box */
.tool-box {
    background: var(--white);
    border-radius: 16px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
    padding: 30px;
    max-width: 800px;
    margin: 0 auto;
    border: 1px solid #E5E7EB;
}

/* Streamlit Tabs Override */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    display: flex;
    gap: 15px;
    justify-content: center;
    border-bottom: none !important;
    background: transparent !important;
}

[data-testid="stTabs"] button[data-baseweb="tab"] {
    padding: 10px 20px !important;
    border: none !important;
    background: transparent !important;
    font-weight: 600 !important;
    color: var(--text-light) !important;
    cursor: pointer !important;
    border-bottom: 2px solid transparent !important;
    border-radius: 0 !important;
    margin: 0 !important;
}

[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] {
    color: var(--primary-color) !important;
    border-bottom-color: var(--primary-color) !important;
}

[data-testid="stTabs"] button[data-baseweb="tab"]:hover {
    color: var(--primary-color) !important;
    background: transparent !important;
}

[data-testid="stTabs"] [data-baseweb="tab-highlight"],
[data-testid="stTabs"] [data-baseweb="tab-border"] {
    display: none !important;
}

/* File Uploader Override - Match .upload-area from TEST.HTML */
[data-testid="stFileUploader"] {
    border: 2px dashed #D1D5DB !important;
    border-radius: 12px !important;
    padding: 50px 20px !important;
    text-align: center !important;
    cursor: pointer !important;
    transition: all 0.3s !important;
    background-color: #F9FAFB !important;
}

[data-testid="stFileUploader"]:hover {
    border-color: var(--primary-color) !important;
    background-color: #EFF6FF !important;
}

/* Hide the label */
[data-testid="stFileUploader"] > label { display: none !important; }

/* Style the section container */
[data-testid="stFileUploader"] section {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
}

/* Hide default Streamlit uploader content completely */
[data-testid="stFileUploader"] section [data-testid="stFileUploaderDropzone"] {
    border: none !important;
    background: transparent !important;
    padding: 0 !important;
}

/* Hide the default SVG icon */
[data-testid="stFileUploader"] section svg {
    display: none !important;
}

/* Hide default "Drag and drop" text */
[data-testid="stFileUploader"] section [data-testid="stFileUploaderDropzoneInstructions"] > div > span {
    display: none !important;
}

/* Center everything in the uploader */
[data-testid="stFileUploader"] section > div {
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
}

/* Custom Icon using Font Awesome */
[data-testid="stFileUploader"] section [data-testid="stFileUploaderDropzoneInstructions"]::before {
    content: "\\f0ee";
    font-family: "Font Awesome 6 Free";
    font-weight: 900;
    font-size: 3rem;
    color: var(--primary-color);
    display: block;
    margin-bottom: 15px;
}

/* Custom Title Text */
[data-testid="stFileUploader"] section [data-testid="stFileUploaderDropzoneInstructions"]::after {
    content: "Kéo thả hoặc chọn file Word (.docx)";
    font-size: 1.1rem;
    font-weight: 600;
    color: #111827;
    display: block;
    margin-bottom: 5px;
}

/* Style the small text */
[data-testid="stFileUploader"] section small {
    font-size: 0.9rem !important;
    color: #9CA3AF !important;
    margin-top: 5px !important;
    display: block !important;
}

/* Browse Files Button - centered */
[data-testid="stFileUploader"] button {
    background: #E5E7EB !important;
    color: #374151 !important;
    margin: 15px auto 0 auto !important;
    font-size: 0.9rem !important;
    padding: 8px 16px !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 500 !important;
    display: block !important;
}

[data-testid="stFileUploader"] button:hover {
    background: #D1D5DB !important;
}

/* Action Button - Match .btn-action */
div.stButton > button[kind="primary"],
div.stButton > button {
    display: block !important;
    width: 100% !important;
    padding: 15px !important;
    background-color: var(--primary-color) !important;
    color: var(--white) !important;
    border: none !important;
    border-radius: 8px !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    margin-top: 20px !important;
    cursor: pointer !important;
    transition: background 0.3s !important;
}

div.stButton > button:hover {
    background-color: var(--primary-dark) !important;
}

/* Features Section */
.features {
    padding: 80px 0;
    background-color: var(--white);
}

.section-title {
    text-align: center;
    margin-bottom: 60px;
}

.section-title h2 {
    font-size: 2.25rem;
    margin-bottom: 10px;
    font-weight: 700;
    color: #1F2937;
}

.section-title p {
    color: var(--text-light);
}

.feature-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 30px;
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}

.feature-card {
    padding: 30px;
    border-radius: 12px;
    background: #F8FAFC;
    transition: transform 0.3s, box-shadow 0.3s;
    border: 1px solid transparent;
}

.feature-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.05);
    border-color: #E2E8F0;
    background: var(--white);
}

.icon-box {
    width: 50px;
    height: 50px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 20px;
    font-size: 1.5rem;
}

.bg-blue { background: #DBEAFE; color: #2563EB; }
.bg-green { background: #D1FAE5; color: #059669; }
.bg-purple { background: #EDE9FE; color: #7C3AED; }
.bg-orange { background: #FFEDD5; color: #EA580C; }
.bg-red { background: #FEE2E2; color: #DC2626; }
.bg-teal { background: #CCFBF1; color: #0D9488; }

.feature-card h3 {
    font-size: 1.25rem;
    margin-bottom: 10px;
    font-weight: 600;
}

.feature-card p {
    color: var(--text-light);
    font-size: 0.95rem;
}

/* CTA Section */
.cta-section {
    padding: 80px 0;
    background: linear-gradient(135deg, #2563EB 0%, #1E40AF 100%);
    color: var(--white);
    text-align: center;
}

.cta-content h2 {
    font-size: 2.5rem;
    margin-bottom: 20px;
    font-weight: 700;
}

.cta-content p {
    font-size: 1.1rem;
    margin-bottom: 20px;
    opacity: 0.9;
}

.btn-white {
    display: inline-block;
    background: var(--white);
    color: var(--primary-color) !important;
    padding: 15px 40px;
    border-radius: 8px;
    font-weight: 700;
    text-decoration: none;
    transition: transform 0.2s;
}

.btn-white:hover {
    transform: scale(1.05);
}

/* Footer */
.site-footer {
    background-color: #111827;
    color: #D1D5DB;
    padding: 60px 0 20px;
}

.footer-grid {
    display: grid;
    grid-template-columns: 2fr 1fr 1fr 1fr;
    gap: 40px;
    margin-bottom: 40px;
}

.footer-col h4 {
    color: var(--white);
    margin-bottom: 20px;
    font-size: 1.1rem;
    font-weight: 600;
}

.footer-col ul {
    list-style: none;
}

.footer-col ul li {
    margin-bottom: 10px;
}

.footer-col ul li a {
    color: #9CA3AF;
    text-decoration: none;
    transition: color 0.3s;
}

.footer-col ul li a:hover {
    color: var(--white);
}

.copyright {
    text-align: center;
    border-top: 1px solid #374151;
    padding-top: 20px;
    font-size: 0.9rem;
}

/* Expander Override */
[data-testid="stExpander"] {
    border: 1px solid #E5E7EB !important;
    border-radius: 8px !important;
    margin-top: 15px !important;
    background: #F9FAFB !important;
}

/* Responsive */
@media (max-width: 768px) {
    .hero h1 { font-size: 2rem; }
    .footer-grid { grid-template-columns: 1fr; text-align: center; }
    .nav-wrapper { flex-direction: column; height: auto; padding: 15px 0; }
    .logo { margin-bottom: 15px; }
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
# LAYOUT - EXACT MATCH WITH TEST.HTML
# ============================================================================

# 1. HEADER
st.markdown('''
<header class="site-header">
    <div class="container nav-wrapper">
        <a href="#" class="logo">
            <i class="fa-solid fa-file-word"></i> EasyWord
        </a>
        <div class="auth-buttons">
            <a href="#" class="btn btn-login">Đăng nhập</a>
            <a href="#" class="btn btn-signup">Đăng ký ngay</a>
        </div>
    </div>
</header>
''', unsafe_allow_html=True)

# 2. HERO SECTION - tool-box is INSIDE hero
st.markdown('''
<section class="hero">
    <div class="container">
        <h1>Tạo Tài Liệu Word Chuyên Nghiệp<br>Trong Tích Tắc</h1>
        <p>Upload file định dạng thô của bạn và để EasyWord xử lý mọi thứ với công nghệ AI tiên tiến. Tiết kiệm 90% thời gian định dạng.</p>
    </div>
</section>
''', unsafe_allow_html=True)

# 3. TOOL BOX - Positioned to overlap hero
st.markdown('<div class="container"><div class="tool-box" style="margin-top: -30px; position: relative; z-index: 10;">', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["☁️ Upload File", "⚡ Test Nhanh"])

with tab1:
    uploaded_file = st.file_uploader(
        "Kéo thả hoặc chọn file Word (.docx)",
        type=["docx"],
        help="Giới hạn 200MB/file • Hỗ trợ DOCX",
        key="main_uploader"
    )
    
    # Inject JavaScript to customize uploader appearance
    st.components.v1.html("""
    <script>
    (function() {
        function customizeUploader() {
            const doc = window.parent.document;
            
            // Target the main dropzone input container and force column layout
            const dropzoneInputs = doc.querySelectorAll('[data-testid="stFileUploaderDropzoneInput"]');
            dropzoneInputs.forEach(input => {
                input.style.display = 'flex';
                input.style.flexDirection = 'column';
                input.style.alignItems = 'center';
                input.style.justifyContent = 'center';
                input.style.width = '100%';
                input.style.gap = '10px';
            });
            
            // Style the dropzone container
            const dropzones = doc.querySelectorAll('[data-testid="stFileUploaderDropzone"]');
            dropzones.forEach(dz => {
                dz.style.border = '2px dashed #D1D5DB';
                dz.style.borderRadius = '12px';
                dz.style.padding = '50px 20px';
                dz.style.backgroundColor = '#F9FAFB';
                dz.style.textAlign = 'center';
                dz.style.display = 'flex';
                dz.style.flexDirection = 'column';
                dz.style.alignItems = 'center';
                
                // Find all direct children and center them
                Array.from(dz.children).forEach(child => {
                    child.style.display = 'flex';
                    child.style.flexDirection = 'column';
                    child.style.alignItems = 'center';
                    child.style.width = '100%';
                });
            });
            
            // Hide default SVG icons
            const uploaders = doc.querySelectorAll('[data-testid="stFileUploader"]');
            uploaders.forEach(uploader => {
                const svgs = uploader.querySelectorAll('svg');
                svgs.forEach(svg => svg.style.display = 'none');
                
                // Replace text and add icon
                const spans = uploader.querySelectorAll('span');
                spans.forEach(span => {
                    if (span.textContent.includes('Drag and drop') || span.textContent.includes('drag and drop')) {
                        span.textContent = 'Kéo thả hoặc chọn file Word (.docx)';
                        span.style.cssText = 'font-size:1.1rem;font-weight:600;color:#111827;display:block;text-align:center;margin-bottom:8px;';
                        
                        // Add custom icon
                        if (!uploader.querySelector('.custom-upload-icon')) {
                            const iconDiv = document.createElement('div');
                            iconDiv.className = 'custom-upload-icon';
                            iconDiv.innerHTML = '<i class="fa-solid fa-cloud-arrow-up" style="font-size:3rem;color:#2563EB;margin-bottom:15px;"></i>';
                            iconDiv.style.textAlign = 'center';
                            iconDiv.style.width = '100%';
                            span.parentElement.insertBefore(iconDiv, span);
                        }
                    }
                });
                
                // Center all buttons
                const btns = uploader.querySelectorAll('button');
                btns.forEach(btn => {
                    btn.style.cssText = 'margin:15px auto 0 auto !important;display:block !important;';
                });
            });
            
            // Center tabs
            const tabLists = doc.querySelectorAll('[data-baseweb="tab-list"]');
            tabLists.forEach(tl => {
                tl.style.justifyContent = 'center';
                tl.style.gap = '15px';
            });
        }
        
        setTimeout(customizeUploader, 500);
        setTimeout(customizeUploader, 1500);
        setTimeout(customizeUploader, 3000);
        
        const observer = new MutationObserver(customizeUploader);
        observer.observe(window.parent.document.body, { childList: true, subtree: true });
    })();
    </script>
    """, height=0)
    
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
    st.info("💡 Dùng file mẫu có sẵn để kiểm tra nhanh tính năng")
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

st.markdown('</div></div>', unsafe_allow_html=True)

# 4. RESULTS
if "result_stream" in st.session_state:
    st.markdown('<div class="container" style="margin-top: 40px;">', unsafe_allow_html=True)
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

# 5. FEATURES SECTION
st.markdown('''
<section class="features">
    <div class="section-title">
        <h2>EasyWord Làm Được Gì?</h2>
        <p>Khám phá các tính năng mạnh mẽ giúp công việc của bạn hiệu quả hơn</p>
    </div>
    <div class="feature-grid">
        <div class="feature-card">
            <div class="icon-box bg-blue"><i class="fa-solid fa-file-lines"></i></div>
            <h3>Tự Động Định Dạng</h3>
            <p>AI tự động nhận diện và áp dụng định dạng chuẩn (Heading, Paragraph, List) cho tài liệu của bạn ngay lập tức.</p>
        </div>
        <div class="feature-card">
            <div class="icon-box bg-green"><i class="fa-solid fa-check-double"></i></div>
            <h3>Kiểm Tra Chính Tả</h3>
            <p>Phát hiện và sửa lỗi chính tả, ngữ pháp tự động với độ chính xác cao dành cho Tiếng Việt.</p>
        </div>
        <div class="feature-card">
            <div class="icon-box bg-purple"><i class="fa-solid fa-palette"></i></div>
            <h3>Template Đa Dạng</h3>
            <p>Hàng trăm mẫu tài liệu chuyên nghiệp sẵn có cho mọi mục đích: Báo cáo, CV, Đơn từ, Hợp đồng.</p>
        </div>
        <div class="feature-card">
            <div class="icon-box bg-orange"><i class="fa-solid fa-sliders"></i></div>
            <h3>Tùy Chỉnh Linh Hoạt</h3>
            <p>Điều chỉnh mọi chi tiết theo ý muốn: font chữ, màu sắc, căn lề chỉ với vài cú click chuột.</p>
        </div>
        <div class="feature-card">
            <div class="icon-box bg-red"><i class="fa-solid fa-bolt"></i></div>
            <h3>Xử Lý Siêu Nhanh</h3>
            <p>Xử lý tài liệu trong vài giây dù file lớn hay phức tạp. Không còn chờ đợi.</p>
        </div>
        <div class="feature-card">
            <div class="icon-box bg-teal"><i class="fa-solid fa-shield-halved"></i></div>
            <h3>Bảo Mật Tuyệt Đối</h3>
            <p>Mọi tài liệu được mã hóa end-to-end, đảm bảo an toàn riêng tư. File tự hủy sau 24h.</p>
        </div>
    </div>
</section>
''', unsafe_allow_html=True)

# 6. CTA SECTION
st.markdown('''
<section class="cta-section">
    <div class="container cta-content">
        <h2>Sẵn Sàng Bắt Đầu?</h2>
        <p>Tham gia hàng nghìn người dùng đang tin dùng EasyWord mỗi ngày để tối ưu hóa công việc.</p>
        <a href="#" class="btn-white">Đăng Ký Miễn Phí Ngay</a>
    </div>
</section>
''', unsafe_allow_html=True)

# 7. FOOTER
st.markdown('''
<footer class="site-footer">
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
                <ul>
                    <li><a href="#">Tính năng</a></li>
                    <li><a href="#">Bảng giá</a></li>
                    <li><a href="#">Templates</a></li>
                    <li><a href="#">API</a></li>
                </ul>
            </div>
            <div class="footer-col">
                <h4>Hỗ trợ</h4>
                <ul>
                    <li><a href="#">Trung tâm trợ giúp</a></li>
                    <li><a href="#">Liên hệ</a></li>
                    <li><a href="#">Cộng đồng</a></li>
                </ul>
            </div>
            <div class="footer-col">
                <h4>Pháp lý</h4>
                <ul>
                    <li><a href="#">Điều khoản</a></li>
                    <li><a href="#">Bảo mật</a></li>
                    <li><a href="#">Cookie Policy</a></li>
                </ul>
            </div>
        </div>
        <div class="copyright">
            © 2026 EasyWord. All rights reserved.
        </div>
    </div>
</footer>
''', unsafe_allow_html=True)
