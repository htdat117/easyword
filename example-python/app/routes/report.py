import logging
import traceback
import uuid
from pathlib import Path

from flask import Blueprint, jsonify, request, send_file

from app.config import TEMP_DIR
from app.services.report_formatter import format_uploaded_stream, generate_template_stream, docx_to_html_stream
from docx import Document

report_bp = Blueprint("report", __name__, url_prefix="/api")


@report_bp.route("/generate-report", methods=["POST"])
def generate_report():
    payload = request.json or {}
    try:
        stream, filename = generate_template_stream(payload)
        return send_file(
            stream,
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            as_attachment=True,
            download_name=filename,
        )
    except Exception as exc:
        logging.error("Lỗi tạo báo cáo: %s", exc)
        logging.debug(traceback.format_exc())
        return jsonify({"error": "Không thể tạo báo cáo", "details": str(exc)}), 500


@report_bp.route("/format-report", methods=["POST"])
def format_report():
    if "file" not in request.files:
        return jsonify({"error": "Thiếu file upload"}), 400

    upload = request.files["file"]
    if not upload.filename.lower().endswith(".docx"):
        return jsonify({"error": "Chỉ hỗ trợ file .docx"}), 400

    options_payload = request.form.get("options")

    try:
        file_bytes = upload.read()
        stream, filename = format_uploaded_stream(file_bytes, upload.filename, options_payload)
        
        # Tạo ID duy nhất cho file preview
        file_id = str(uuid.uuid4())
        preview_filename = f"{file_id}.docx"
        preview_path = TEMP_DIR / preview_filename
        
        # Lưu file vào thư mục tạm
        with open(preview_path, "wb") as f:
            stream.seek(0)
            f.write(stream.read())
        
        # Trả về JSON với preview URL thay vì tải về trực tiếp
        return jsonify({
            "success": True,
            "preview_url": f"/api/preview/{file_id}",
            "download_url": f"/api/download/{file_id}",
            "filename": filename,
            "file_id": file_id
        })
    except Exception as exc:
        logging.error("Lỗi chuẩn hóa: %s", exc)
        logging.debug(traceback.format_exc())
        return jsonify({"error": "Lỗi xử lý file", "details": str(exc)}), 500


@report_bp.route("/preview/<file_id>", methods=["GET"])
def preview_file(file_id):
    """Hiển thị preview file - convert Word sang HTML và trả về HTML"""
    try:
        docx_path = TEMP_DIR / f"{file_id}.docx"
        if not docx_path.exists():
            return jsonify({"error": "File không tồn tại hoặc đã hết hạn"}), 404
        
        # Đọc Word document và convert sang HTML
        doc = Document(docx_path)
        html_stream = docx_to_html_stream(doc)
        
        # Trả về HTML
        from flask import Response
        return Response(
            html_stream.read(),
            mimetype="text/html; charset=utf-8",
            headers={"Content-Disposition": "inline"}
        )
    except Exception as exc:
        logging.error("Lỗi preview file: %s", exc)
        logging.debug(traceback.format_exc())
        return jsonify({"error": "Không thể xem preview", "details": str(exc)}), 500


@report_bp.route("/download/<file_id>", methods=["GET"])
def download_file(file_id):
    """Tải về file đã chuẩn hóa"""
    try:
        preview_path = TEMP_DIR / f"{file_id}.docx"
        if not preview_path.exists():
            return jsonify({"error": "File không tồn tại hoặc đã hết hạn"}), 404
        
        # Đọc filename gốc từ query param nếu có
        original_filename = request.args.get("filename", "bao-cao-chuan.docx")
        
        return send_file(
            preview_path,
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            as_attachment=True,
            download_name=original_filename,
        )
    except Exception as exc:
        logging.error("Lỗi download file: %s", exc)
        return jsonify({"error": "Không thể tải file"}), 500

