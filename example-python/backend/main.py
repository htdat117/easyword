"""
EasyWord - FastAPI Backend
Serves frontend files and provides API endpoints for document processing.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import uuid
import io
import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add app directory to path for imports
current_dir = Path(__file__).parent.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Import processing logic
try:
    from app.services.report_formatter import format_uploaded_stream
    from app.config import TEMP_DIR
except ImportError as e:
    logger.error(f"Import error: {e}")
    logger.info("Make sure to run from the example-python directory")

# Create FastAPI app
app = FastAPI(
    title="EasyWord API",
    description="API for processing Word documents",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files - serve frontend
frontend_path = Path(__file__).parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

# ============================================================================
# PAGES - Serve HTML files
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve the landing page"""
    index_file = frontend_path / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return HTMLResponse("<h1>EasyWord - Coming Soon</h1>")

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Serve the dashboard page"""
    dashboard_file = frontend_path / "dashboard.html"
    if dashboard_file.exists():
        return FileResponse(dashboard_file)
    return HTMLResponse("<h1>Dashboard - Coming Soon</h1>")

@app.get("/login", response_class=HTMLResponse)
async def login():
    """Serve the login page"""
    login_file = frontend_path / "login.html"
    if login_file.exists():
        return FileResponse(login_file)
    return HTMLResponse("<h1>Login - Coming Soon</h1>")

@app.get("/register", response_class=HTMLResponse)
async def register():
    """Serve the register page"""
    register_file = frontend_path / "register.html"
    if register_file.exists():
        return FileResponse(register_file)
    return HTMLResponse("<h1>Register - Coming Soon</h1>")

# ============================================================================
# API ENDPOINTS
# ============================================================================

def get_processing_options():
    """Default processing options"""
    return {
        "clean_whitespace": True,
        "normalize_font": True,
        "adjust_margins": True,
        "indent_spacing": True,
        "heading_detection": True,
        "format_tables": True,
        "insert_toc": True,
        "add_page_numbers": True,
        "line_spacing": 1.3,
        "auto_numbered_heading": True,
    }

@app.post("/api/process")
async def process_file(file: UploadFile = File(...)):
    """
    Process an uploaded DOCX file.
    Returns the processed file as a download.
    """
    if not file.filename.endswith('.docx'):
        raise HTTPException(status_code=400, detail="Only .docx files are supported")
    
    try:
        # Read file content
        content = await file.read()
        
        # Process the file
        options = get_processing_options()
        result_stream, result_name = format_uploaded_stream(content, file.filename, options)
        
        # Return the processed file
        result_stream.seek(0)
        
        return StreamingResponse(
            result_stream,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f'attachment; filename="{result_name}"'
            }
        )
    except Exception as e:
        logger.error(f"Processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/test")
async def run_test():
    """
    Run a quick test with the sample file.
    Returns the processed file.
    """
    test_file = Path(__file__).parent.parent / "test.docx"
    
    if not test_file.exists():
        raise HTTPException(status_code=404, detail="Test file not found")
    
    try:
        # Read test file
        with open(test_file, 'rb') as f:
            content = f.read()
        
        # Process the file
        options = get_processing_options()
        result_stream, result_name = format_uploaded_stream(content, "test_result.docx", options)
        
        # Return the processed file
        result_stream.seek(0)
        
        return StreamingResponse(
            result_stream,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f'attachment; filename="{result_name}"'
            }
        )
    except Exception as e:
        logger.error(f"Test error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}

# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
