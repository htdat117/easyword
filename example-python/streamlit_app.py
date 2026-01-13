import streamlit as st
import uuid
from pathlib import Path
import logging
import sys
import base64
import os

# ============================================================================
# 1. CẤU HÌNH & SETUP (GIỮ NGUYÊN LOGIC)
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

# Mock imports để code chạy được độc lập (nếu bạn chưa có module app)
# Nếu bạn chạy trên môi trường thật, hãy bỏ comment phần import thật
try:
    from docx import Document
    # from app.services.report_formatter import format_uploaded_stream, docx_to_html
    # from app.config import TEMP_DIR, CONVERTAPI_SECRET
    
    # --- MOCK CHO DEMO (Xóa phần này khi chạy thật) ---
    TEMP_DIR = Path("temp")
    TEMP_DIR.mkdir(exist_ok=True)
    CONVERTAPI_SECRET = None # Điền secret nếu có
    
    def format_uploaded_stream(bytes_data, name, opts):
        # Giả lập xử lý
        import io
        return io.BytesIO(bytes_data), f"processed_{name}"
        
    def docx_to_html(doc):
        return "<h3>Bản xem trước tài liệu (Demo Mode)</h3><p>Nội dung đã được xử lý...</p>"
    # --------------------------------------------------

except Exception as e:
    st.error(f"❌ Import Error: {e}")
    st.stop()

# ============================================================================
# 2. CSS & GIAO DIỆN (ĐÃ TỐI ƯU HÓA THEO HTML MỚI)
# ============================================================================
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
    /* --- Global Variables --- */
    :root {
        --primary-color: #2563EB;
        --primary-dark: #1D4ED8;
        --secondary-color: #F3F4F6;
        --text-dark: #1F2937;
        --text-light: #6B7280;
        --white: #FFFFFF;
    }

    /* --- Reset Streamlit Defaults --- */
    body { font-family: 'Inter', sans-serif; background-color: #F9FAFB; color: var(--text-dark); }
    .stApp { background-color: #F9FAFB; }
    
    /* Ẩn header mặc định, footer và menu của Streamlit */
    header[data-testid="stHeader"], footer, #MainMenu { display: none !important; }
    .block-container { padding-top: 0 !important; padding-left: 0 !important; padding-right: 0 !important; max-width: 100% !important; }

    /* --- Custom Header --- */
    .custom-header {
        background-color: var(--white);
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        padding: 15px 20px;
        position: sticky;
        top: 0;
        z-index: 999;
    }
    .nav-wrapper { max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; }
    .logo-area { font-size: 1.5rem; font-weight: 700; color: var(--primary-color); text-decoration: none; display: flex; gap: 10px; align-items: center; }
    .auth-btn { text-decoration: none; padding: 8px 20px; border-radius: 6px; font-weight: 500; font-size: 0.9rem; }
    .btn-login { color: var(--text-dark); margin-right: 10px; }
    .btn-signup { background-color: var(--primary-color); color: white !important; transition: 0.3s; }
    .btn-signup:hover { background-color: var(--primary-dark); }

    /* --- Hero Section --- */
    .hero {
        text-align: center;
        padding: 80px 20px 40px;
        background: linear-gradient(180deg, #FFFFFF 0%, #EFF6FF 100%);
    }
    .hero h1 { font-size: 3rem; color: #111827; margin-bottom: 16px; font-weight: 800; line-height: 1.2; }
    .hero p { font-size: 1.125rem; color: var(--text-light); margin-bottom: 40px; max-width: 600px; margin: 0 auto 40px auto; }

    /* --- Tool Box Container (Streamlit Injection Area) --- */
    .tool-container {
        max-width: 800px;
        margin: 0 auto;
        background: var(--white);
        border-radius: 16px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        border: 1px solid #E5E7EB;
        padding: 30px;
        position: relative;
        z-index: 10;
    }

    /* --- Customizing Streamlit Widgets to match Design --- */
    
    /* 1. Tabs */
    .stTabs [data-baseweb="tab-list"] { justify-content: center; gap: 20px; border-bottom: none; margin-bottom: 20px; }
    .stTabs [data-baseweb="tab"] { background: transparent; border: none; padding: 10px 20px; color: #6B7280; font-weight: 600; }
    .stTabs [data-baseweb="tab"]:hover { color: var(--primary-color); }
    .stTabs [aria-selected="true"] { color: var(--primary-color) !important; border-bottom: 2px solid var(--primary-color) !important; background: transparent !important; }

    /* 2. File Uploader - Making it look like the dashed box */
    [data-testid="stFileUploader"] { padding: 0; }
    [data-testid="stFileUploader"] section { 
        padding: 40px 20px; 
        background-color: #F9FAFB; 
        border: 2px dashed #D1D5DB; 
        border-radius: 12px; 
        text-align: center;
        transition: all 0.3s;
    }
    [data-testid="stFileUploader"] section:hover { border-color: var(--primary-color); background-color: #EFF6FF; }
    /* Icon giả lập bằng CSS before */
    [data-testid="stFileUploader"] section::before {
        font-family: "Font Awesome 6 Free"; font-weight: 900; content: "\\f0ee"; 
        font-size: 3rem; color: var(--primary-color); display: block; margin-bottom: 15px;
    }

    /* 3. Button - Primary Action */
    .stButton > button {
        width: 100%;
        background-color: var(--primary-color);
        color: white;
        font-weight: 600;
        padding: 15px 0;
        border-radius: 8px;
        border: none;
        margin-top: 10px;
        font-size: 1rem;
        transition: 0.3s;
    }
    .stButton > button:hover { background-color: var(--primary-dark); color: white; border: none; }
    .stButton > button:active { background-color: var(--primary-dark); color: white; }

    /* 4. Expander (Options) */
    .streamlit-expanderHeader { font-weight: 500; color: var(--text-dark); background: white; }

    /* --- Features Section --- */
    .features-sec { padding: 80px 20px; background-color: var(--white); }
    .sec-title { text-align: center; margin-bottom: 60px; }
    .sec-title h2 { font-size: 2.25rem; color: #111827; margin-bottom: 10px; font-weight: 700; }
    .grid-container { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 30px; max-width: 1200px; margin: 0 auto; }
    .f-card { padding: 30px; border-radius: 12px; background: #F8FAFC; border: 1px solid transparent; transition: 0.3s; }
    .f-card:hover { transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.05); background: white; border-color: #E2E8F0; }
    .icon-box { width: 50px; height: 50px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; margin-bottom: 20px; }
    
    /* Icon Colors */
    .bg-blue { background: #DBEAFE; color: #2563EB; }
    .bg-green { background: #D1FAE5; color: #059669; }
    .bg-purple { background: #EDE9FE; color: #7C3AED; }
    .bg-orange { background: #FFEDD5; color: #EA580C; }
    .bg-red { background: #FEE2E2; color: #DC2626; }
    .bg-teal { background: #CCFBF1; color: #0D9488; }

    /* --- CTA & Footer --- */
    .cta-sec { padding: 80px 20px; background: linear-gradient(135deg, #2563EB 0%, #1E40AF 100%); text-align: center; color: white; }
    .btn-cta-white { display: inline-block; background: white; color: var(--primary-color); padding: 15px 40px; border-radius: 8px; font-weight: 700; text-decoration: none; margin-top: 20px; }
    
    .main-footer { background-color: #111827; color: #D1D5DB; padding: 60px 20px 20px; }
    .footer-grid { display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; gap: 40px; max-width: 1200px; margin: 0 auto 40px; }
    .f-col h4 { color: white; margin-bottom: 20px; }
    .f-col a { color: #9CA3AF; text-decoration: none; display: block; margin-bottom: 10px; }
    .f-col a:hover { color: white; }

    /* Mobile */
    @media (max-width: 768px) {
        .hero h1 { font-size: 2rem; }
        .footer-grid { grid-template-columns: 1fr; text-align: center; }
        .nav-wrapper { flex-direction: column; gap: 10px; }
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# 3. UI RENDERING & LOGIC
# ============================================================================

# --- HEADER ---
st.markdown("""
<div class="custom-header">
    <div class="nav-wrapper">
        <a href="#" class="logo-area"><i class="fa-solid fa-file-word"></i> EasyWord</a>
        <div class="auth-btns">
            <a href="#" class="auth-btn btn-login">Đăng nhập</a>
            <a href="#" class="auth-btn btn-signup">Đăng ký ngay</a>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- HERO SECTION ---
st.markdown("""
<div class="hero">
    <h1>Tạo Tài Liệu Word Chuyên Nghiệp<br>Trong Tích Tắc</h1>
    <p>Upload file định dạng thô của bạn và để EasyWord xử lý mọi thứ với công nghệ AI tiên tiến. Tiết kiệm 90% thời gian định dạng.</p>
</div>
""", unsafe_allow_html=True)

# --- HELPER LOGIC ---
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

# --- MAIN TOOL BOX ---
st.markdown('<div class="tool-container">', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["☁️ Upload File", "⚡ Test Nhanh"])

with tab1:
    uploaded_file = st.file_uploader("Upload Word File", type=["docx"], label_visibility="collapsed")
    
    if uploaded_file:
        st.markdown(f"<div style='text-align:center; color:#059669; margin-top:10px;'><i class='fa-solid fa-check'></i> Đã chọn: <b>{uploaded_file.name}</b></div>", unsafe_allow_html=True)

    with st.expander("⚙️ Tùy chỉnh nâng cao (Tùy chọn)"):
        c1, c2 = st.columns(2)
        with c1:
            st.checkbox("Xóa dòng trống", value=True, key="opt_clean")
            st.checkbox("Chuẩn hóa font", value=True, key="opt_font")
            st.checkbox("Chỉnh lề", value=True, key="opt_margins")
        with c2:
            st.checkbox("Tạo mục lục", value=True, key="opt_toc")
            st.checkbox("Đánh số trang", value=True, key="opt_page_numbers")
            st.number_input("Giãn dòng", 1.0, 2.0, 1.3, 0.1, key="line_spacing")

    if st.button("Bắt đầu xử lý ngay", key="btn_process"):
        if uploaded_file:
            with st.spinner("Đang xử lý tài liệu với AI..."):
                try:
                    bytes_data = uploaded_file.read()
                    opts = collect_options()
                    stream, name = format_uploaded_stream(bytes_data, uploaded_file.name, opts)
                    st.session_state["result_stream"] = stream
                    st.session_state["result_name"] = name
                    stream.seek(0)
                    st.session_state["result_doc"] = Document(stream)
                    st.success("Xử lý thành công! Kéo xuống để tải về.")
                except Exception as e:
                    st.error(f"Lỗi: {e}")
        else:
            st.warning("Vui lòng chọn file trước khi xử lý.")

with tab2:
    st.info("Sử dụng file mẫu có sẵn để trải nghiệm tính năng mà không cần upload.")
    if st.button("🚀 Chạy Test Ngay", key="btn_test_quick"):
        test_path = Path("test.docx")
        # Giả lập tạo file test nếu không có (cho demo)
        if not test_path.exists():
            doc = Document()
            doc.add_heading('Test Document', 0)
            doc.add_paragraph('This is a test paragraph.')
            doc.save(test_path)
            
        if test_path.exists():
             with st.spinner("Đang chạy test..."):
                try:
                    with open(test_path, "rb") as f:
                        bytes_data = f.read()
                    opts = collect_options()
                    stream, name = format_uploaded_stream(bytes_data, "test_result.docx", opts)
                    st.session_state["result_stream"] = stream
                    st.session_state["result_name"] = name
                    stream.seek(0)
                    st.session_state["result_doc"] = Document(stream)
                    st.success("Test thành công! Kéo xuống để xem kết quả.")
                except Exception as e:
                    st.error(f"Lỗi: {e}")
        else:
            st.error("Không tìm thấy file test.docx")

st.markdown('</div>', unsafe_allow_html=True) # End Tool Container

# --- RESULTS SECTION ---
if "result_stream" in st.session_state:
    st.markdown('<div style="max-width:800px; margin: 40px auto; padding: 20px; background: #ECFDF5; border: 1px solid #10B981; border-radius: 8px;">', unsafe_allow_html=True)
    st.markdown("### 🎉 Tài liệu của bạn đã sẵn sàng!")
    
    col_res1, col_res2 = st.columns([3, 1])
    with col_res1:
        st.write(f"File: **{st.session_state['result_name']}**")
    with col_res2:
        st.session_state["result_stream"].seek(0)
        st.download_button(
            label="⬇️ Tải xuống",
            data=st.session_state["result_stream"],
            file_name=st.session_state["result_name"],
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True
        )
    
    with st.expander("👁️ Xem trước tài liệu"):
        if "result_doc" in st.session_state:
            display_preview(st.session_state["result_doc"])
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- FEATURES SECTION (HTML) ---
st.markdown("""
<div class="features-sec">
    <div class="sec-title">
        <h2>EasyWord Làm Được Gì?</h2>
        <p>Khám phá các tính năng mạnh mẽ giúp công việc của bạn hiệu quả hơn</p>
    </div>
    <div class="grid-container">
        <div class="f-card">
            <div class="icon-box bg-blue"><i class="fa-solid fa-file-lines"></i></div>
            <h3>Tự Động Định Dạng</h3>
            <p style="color:#6B7280">AI tự động nhận diện và áp dụng định dạng chuẩn (Heading, Paragraph, List) cho tài liệu.</p>
        </div>
        <div class="f-card">
            <div class="icon-box bg-green"><i class="fa-solid fa-check-double"></i></div>
            <h3>Kiểm Tra Chính Tả</h3>
            <p style="color:#6B7280">Phát hiện và sửa lỗi chính tả, ngữ pháp tự động với độ chính xác cao.</p>
        </div>
        <div class="f-card">
            <div class="icon-box bg-purple"><i class="fa-solid fa-palette"></i></div>
            <h3>Template Đa Dạng</h3>
            <p style="color:#6B7280">Hàng trăm mẫu tài liệu chuyên nghiệp sẵn có cho mọi mục đích: Báo cáo, CV.</p>
        </div>
        <div class="f-card">
            <div class="icon-box bg-orange"><i class="fa-solid fa-sliders"></i></div>
            <h3>Tùy Chỉnh Linh Hoạt</h3>
            <p style="color:#6B7280">Điều chỉnh font chữ, màu sắc, căn lề chỉ với vài cú click chuột.</p>
        </div>
        <div class="f-card">
            <div class="icon-box bg-red"><i class="fa-solid fa-bolt"></i></div>
            <h3>Xử Lý Siêu Nhanh</h3>
            <p style="color:#6B7280">Xử lý tài liệu trong vài giây dù file lớn hay phức tạp.</p>
        </div>
        <div class="f-card">
            <div class="icon-box bg-teal"><i class="fa-solid fa-shield-halved"></i></div>
            <h3>Bảo Mật Tuyệt Đối</h3>
            <p style="color:#6B7280">Mọi tài liệu được mã hóa end-to-end, đảm bảo an toàn riêng tư.</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- CTA SECTION ---
st.markdown("""
<div class="cta-sec">
    <h2 style="font-size: 2.5rem; margin-bottom: 20px;">Sẵn Sàng Bắt Đầu?</h2>
    <p style="font-size: 1.1rem; opacity: 0.9;">Tham gia hàng nghìn người dùng đang tin dùng EasyWord mỗi ngày.</p>
    <a href="#" class="btn-cta-white">Đăng Ký Miễn Phí Ngay</a>
</div>
""", unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("""
<footer class="main-footer">
    <div class="footer-grid">
        <div class="f-col">
            <a href="#" class="logo-area" style="color:white; margin-bottom:20px;"><i class="fa-solid fa-file-word"></i> EasyWord</a>
            <p style="font-size:0.9rem;">Giải pháp tạo tài liệu Word thông minh hàng đầu Việt Nam.</p>
        </div>
        <div class="f-col">
            <h4>Sản phẩm</h4>
            <a href="#">Tính năng</a><a href="#">Bảng giá</a><a href="#">Templates</a>
        </div>
        <div class="f-col">
            <h4>Hỗ trợ</h4>
            <a href="#">Trung tâm trợ giúp</a><a href="#">Liên hệ</a><a href="#">Cộng đồng</a>
        </div>
        <div class="f-col">
            <h4>Pháp lý</h4>
            <a href="#">Điều khoản</a><a href="#">Bảo mật</a>
        </div>
    </div>
    <div style="text-align:center; border-top:1px solid #374151; padding-top:20px; font-size:0.9rem;">
        &copy; 2026 EasyWord. All rights reserved.
    </div>
</footer>
""", unsafe_allow_html=True)