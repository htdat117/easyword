/**
 * EasyWord - Main JavaScript
 * Handles file upload, API calls, and UI interactions
 */

// ==========================================================================
// State Management
// ==========================================================================

let selectedFile = null;
let downloadUrl = null;

// ==========================================================================
// Tab Switching
// ==========================================================================

document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        // Remove active class from all tabs and contents
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

        // Add active class to clicked tab
        btn.classList.add('active');

        // Show corresponding content
        const tabId = btn.dataset.tab + '-tab';
        document.getElementById(tabId).classList.add('active');

        // Hide result section when switching tabs
        hideResult();
    });
});

// ==========================================================================
// File Upload
// ==========================================================================

const fileInput = document.getElementById('file-input');
const dropZone = document.getElementById('drop-zone');

// File input change
fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileSelect(e.target.files[0]);
    }
});

// Drag and drop
dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');

    if (e.dataTransfer.files.length > 0) {
        const file = e.dataTransfer.files[0];
        if (file.name.endsWith('.docx')) {
            handleFileSelect(file);
        } else {
            alert('Chỉ hỗ trợ file .docx');
        }
    }
});

// Click to upload
dropZone.addEventListener('click', () => {
    fileInput.click();
});

function handleFileSelect(file) {
    selectedFile = file;

    // Show file info
    document.getElementById('file-name').textContent = file.name;
    document.getElementById('file-info').style.display = 'flex';
    dropZone.style.display = 'none';

    // Hide previous results
    hideResult();
}

function removeFile() {
    selectedFile = null;
    fileInput.value = '';

    document.getElementById('file-info').style.display = 'none';
    dropZone.style.display = 'block';
}

// ==========================================================================
// API Calls
// ==========================================================================

async function processFile() {
    if (!selectedFile) {
        alert('Vui lòng chọn file trước!');
        return;
    }

    showProcessing();

    try {
        const formData = new FormData();
        formData.append('file', selectedFile);

        const response = await fetch('/api/process', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Có lỗi xảy ra');
        }

        // Get the blob and create download URL
        const blob = await response.blob();
        const contentDisposition = response.headers.get('Content-Disposition');
        let filename = 'formatted-document.docx';

        if (contentDisposition) {
            const match = contentDisposition.match(/filename="([^"]+)"/);
            if (match) filename = match[1];
        }

        downloadUrl = URL.createObjectURL(blob);
        showResult(filename);

    } catch (error) {
        hideProcessing();
        alert('Lỗi: ' + error.message);
    }
}

async function runTest() {
    showProcessing();

    try {
        const response = await fetch('/api/test');

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Có lỗi xảy ra');
        }

        // Get the blob and create download URL
        const blob = await response.blob();
        const contentDisposition = response.headers.get('Content-Disposition');
        let filename = 'formatted-test_result.docx';

        if (contentDisposition) {
            const match = contentDisposition.match(/filename="([^"]+)"/);
            if (match) filename = match[1];
        }

        downloadUrl = URL.createObjectURL(blob);
        showResult(filename);

    } catch (error) {
        hideProcessing();
        alert('Lỗi: ' + error.message);
    }
}

function downloadFile() {
    if (downloadUrl) {
        const filename = document.getElementById('result-filename').textContent;
        const a = document.createElement('a');
        a.href = downloadUrl;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }
}

// ==========================================================================
// Preview Functionality - Modal with Zoom
// ==========================================================================

let currentPDFDocument = null;
let currentZoomScale = 1.0;
let currentPDFData = null;

async function showPreview(isTest = false) {
    const previewModal = document.getElementById('preview-modal');
    const previewFrame = document.getElementById('preview-frame');

    if (!previewModal) return;

    previewModal.style.display = 'flex';
    previewFrame.innerHTML = '<div class="preview-loading"><div class="spinner"></div><p>Đang tạo bản xem trước PDF...</p></div>';

    try {
        let response;

        if (isTest) {
            response = await fetch('/api/preview/test');
        } else if (selectedFile) {
            const formData = new FormData();
            formData.append('file', selectedFile);
            response = await fetch('/api/preview', {
                method: 'POST',
                body: formData
            });
        } else {
            previewFrame.innerHTML = '<p style="text-align:center;color:#fff;">Vui lòng chọn file để xem trước</p>';
            return;
        }

        if (!response.ok) {
            throw new Error('Không thể tạo bản xem trước');
        }

        const data = await response.json();

        if (data.type === 'pdf') {
            // Store PDF data for zoom operations
            currentPDFData = data.content;
            await renderPDFWithZoom(data.content, previewFrame);
            setupZoomControls();
        } else if (data.type === 'html') {
            previewFrame.innerHTML = `
                <div class="html-preview" style="max-height:100%;overflow-y:auto;padding:20px;background:white;border-radius:8px;">
                    ${data.content}
                </div>
            `;
        }
    } catch (error) {
        previewFrame.innerHTML = `<p style="text-align:center;color:#DC2626;">Lỗi: ${error.message}</p>`;
    }
}

// Load PDF.js library if not already loaded
async function loadPDFJS() {
    if (window.pdfjsLib) return;

    return new Promise((resolve, reject) => {
        const script = document.createElement('script');
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js';
        script.onload = () => {
            window.pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
            resolve();
        };
        script.onerror = reject;
        document.head.appendChild(script);
    });
}

// Render PDF with zoom capability
async function renderPDFWithZoom(base64Content, container, scale = null) {
    try {
        await loadPDFJS();

        // Convert base64 to Uint8Array
        const pdfData = atob(base64Content);
        const pdfArray = new Uint8Array(pdfData.length);
        for (let i = 0; i < pdfData.length; i++) {
            pdfArray[i] = pdfData.charCodeAt(i);
        }

        // Load PDF
        const pdf = await pdfjsLib.getDocument({ data: pdfArray }).promise;
        currentPDFDocument = pdf;

        // If scale is not specified, calculate fit-to-width
        if (scale === null) {
            const firstPage = await pdf.getPage(1);
            const viewport = firstPage.getViewport({ scale: 1 });
            const containerWidth = container.clientWidth - 40; // padding
            scale = containerWidth / viewport.width;
            currentZoomScale = scale;
        } else {
            currentZoomScale = scale;
        }

        // Update zoom level display
        updateZoomDisplay();

        // Create container for all pages
        container.innerHTML = '<div id="pdf-pages"></div>';
        const pagesContainer = document.getElementById('pdf-pages');

        // Render each page
        for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
            const page = await pdf.getPage(pageNum);
            const viewport = page.getViewport({ scale: currentZoomScale });

            // Create canvas for this page
            const canvas = document.createElement('canvas');
            canvas.className = 'pdf-page-canvas';
            canvas.width = viewport.width;
            canvas.height = viewport.height;

            const ctx = canvas.getContext('2d');

            // Render page to canvas
            await page.render({
                canvasContext: ctx,
                viewport: viewport
            }).promise;

            pagesContainer.appendChild(canvas);
        }
    } catch (error) {
        container.innerHTML = `<p style="text-align:center;color:#DC2626;">Lỗi render PDF: ${error.message}</p>`;
    }
}

// Setup zoom control event listeners
function setupZoomControls() {
    const zoomInBtn = document.getElementById('zoom-in-btn');
    const zoomOutBtn = document.getElementById('zoom-out-btn');
    const fitWidthBtn = document.getElementById('fit-width-btn');
    const closeBtn = document.getElementById('close-modal-btn');

    if (zoomInBtn) {
        zoomInBtn.onclick = () => zoomIn();
    }

    if (zoomOutBtn) {
        zoomOutBtn.onclick = () => zoomOut();
    }

    if (fitWidthBtn) {
        fitWidthBtn.onclick = () => fitToWidth();
    }

    if (closeBtn) {
        closeBtn.onclick = () => hidePreview();
    }
}

function zoomIn() {
    currentZoomScale = Math.min(currentZoomScale * 1.2, 3.0); // Max 300%
    rerenderPDF();
}

function zoomOut() {
    currentZoomScale = Math.max(currentZoomScale / 1.2, 0.3); // Min 30%
    rerenderPDF();
}

function fitToWidth() {
    const previewFrame = document.getElementById('preview-frame');
    if (currentPDFDocument) {
        renderPDFWithZoom(currentPDFData, previewFrame, null); // null triggers auto-fit
    }
}

function rerenderPDF() {
    const previewFrame = document.getElementById('preview-frame');
    if (currentPDFData && previewFrame) {
        renderPDFWithZoom(currentPDFData, previewFrame, currentZoomScale);
    }
}

function updateZoomDisplay() {
    const zoomLevelSpan = document.getElementById('zoom-level');
    if (zoomLevelSpan) {
        zoomLevelSpan.textContent = Math.round(currentZoomScale * 100) + '%';
    }
}

function hidePreview() {
    const previewModal = document.getElementById('preview-modal');
    if (previewModal) {
        previewModal.style.display = 'none';
    }

    // Clean up
    currentPDFDocument = null;
    currentPDFData = null;
    currentZoomScale = 1.0;
}

// ==========================================================================
// UI Helpers
// ==========================================================================

function showProcessing() {
    // Hide upload area and buttons
    document.querySelectorAll('.tab-content').forEach(c => c.style.display = 'none');
    document.getElementById('processing').style.display = 'block';
    hideResult();
    hidePreview();
}

function hideProcessing() {
    document.getElementById('processing').style.display = 'none';
    // Show active tab content
    document.querySelectorAll('.tab-content').forEach(c => {
        if (c.classList.contains('active')) {
            c.style.display = 'block';
        }
    });
}

function showResult(filename) {
    hideProcessing();
    document.getElementById('result-filename').textContent = filename;
    document.getElementById('result').style.display = 'block';

    // Setup download button
    document.getElementById('download-btn').onclick = downloadFile;

    // Setup preview button if exists
    const previewBtn = document.getElementById('preview-btn');
    if (previewBtn) {
        previewBtn.onclick = () => {
            const activeTab = document.querySelector('.tab-btn.active');
            const isTest = activeTab && activeTab.dataset.tab === 'test';
            showPreview(isTest);
        };
    }
}

function hideResult() {
    document.getElementById('result').style.display = 'none';
    hidePreview();
    if (downloadUrl) {
        URL.revokeObjectURL(downloadUrl);
        downloadUrl = null;
    }
}

// ==========================================================================
// Initialize
// ==========================================================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('EasyWord App Initialized');
});
