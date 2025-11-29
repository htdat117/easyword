import logging
import traceback

from flask import Blueprint, jsonify, request, send_file

from app.services.report_formatter import format_uploaded_stream, generate_template_stream

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
        return send_file(
            stream,
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            as_attachment=True,
            download_name=filename,
        )
    except Exception as exc:
        logging.error("Lỗi chuẩn hóa: %s", exc)
        logging.debug(traceback.format_exc())
        return jsonify({"error": "Lỗi xử lý file", "details": str(exc)}), 500

