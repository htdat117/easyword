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
            const match = contentDisposition.match(/filename="?(.+)"?/);
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
            const match = contentDisposition.match(/filename="?(.+)"?/);
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
// Preview Functionality
// ==========================================================================

async function showPreview(isTest = false) {
    const previewContainer = document.getElementById('preview-container');
    const previewFrame = document.getElementById('preview-frame');

    if (!previewContainer) return;

    previewContainer.style.display = 'block';
    previewFrame.innerHTML = '<div class="preview-loading"><div class="spinner"></div><p>Đang tạo bản xem trước...</p></div>';

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
            previewFrame.innerHTML = '<p style="text-align:center;color:#6B7280;">Vui lòng chọn file để xem trước</p>';
            return;
        }

        if (!response.ok) {
            throw new Error('Không thể tạo bản xem trước');
        }

        const data = await response.json();

        if (data.type === 'pdf') {
            // Render PDF using PDF.js
            previewFrame.innerHTML = `
                <iframe 
                    src="data:application/pdf;base64,${data.content}" 
                    style="width:100%;height:600px;border:none;border-radius:8px;"
                    title="PDF Preview">
                </iframe>
            `;
        } else if (data.type === 'html') {
            // Render HTML content
            previewFrame.innerHTML = `
                <div class="html-preview" style="max-height:600px;overflow-y:auto;padding:20px;background:white;border-radius:8px;border:1px solid #E5E7EB;">
                    ${data.content}
                </div>
            `;
        }
    } catch (error) {
        previewFrame.innerHTML = `<p style="text-align:center;color:#DC2626;">Lỗi: ${error.message}</p>`;
    }
}

function hidePreview() {
    const previewContainer = document.getElementById('preview-container');
    if (previewContainer) {
        previewContainer.style.display = 'none';
    }
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
