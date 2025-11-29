import os

from flask import Blueprint, jsonify, send_from_directory, current_app

static_bp = Blueprint("static", __name__)


@static_bp.route("/", methods=["GET"])
def serve_index():
    frontend_dir = current_app.config.get("FRONTEND_DIR")
    if not frontend_dir or not os.path.exists(frontend_dir):
        return jsonify(
            {
                "status": "backend ok",
                "message": "Không tìm thấy giao diện. Tạo thư mục 'frontend' và đặt index.html vào đó.",
            }
        )

    index_path = os.path.join(frontend_dir, "index.html")
    if not os.path.exists(index_path):
        return jsonify(
            {
                "status": "backend ok",
                "message": "Thiếu file frontend/index.html",
            }
        )

    return send_from_directory(frontend_dir, "index.html")


@static_bp.route("/<path:filename>")
def serve_static(filename):
    frontend_dir = current_app.config.get("FRONTEND_DIR")
    return send_from_directory(frontend_dir, filename)

