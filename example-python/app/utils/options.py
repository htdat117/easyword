import json
import logging

from app.config import LINE_SPACING


DEFAULT_OPTIONS = {
    "clean_whitespace": True,
    "normalize_font": True,
    "heading_detection": True,
    "auto_numbered_heading": True,  # Tự động đánh tiêu đề dựa trên số thứ tự (1., 1.1., 1.1.1., ...)
    "adjust_margins": True,
    "indent_spacing": True,
    "format_tables": True,
    "insert_toc": True,
    "add_page_numbers": True,
    "page_number_style": "arabic",
    "line_spacing": LINE_SPACING,
}


def _to_bool(value):
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)


def merge_options(raw_options):
    options = DEFAULT_OPTIONS.copy()
    if raw_options is None:
        return options

    if isinstance(raw_options, str):
        try:
            raw_options = json.loads(raw_options)
        except json.JSONDecodeError:
            logging.warning("Không parse được options, sử dụng mặc định.")
            return options

    if not isinstance(raw_options, dict):
        return options

    for key, default_value in DEFAULT_OPTIONS.items():
        if key not in raw_options:
            continue
        incoming = raw_options[key]
        if isinstance(default_value, bool):
            options[key] = _to_bool(incoming)
        elif isinstance(default_value, (int, float)) and isinstance(incoming, (int, float, str)):
            try:
                options[key] = float(incoming)
            except ValueError:
                options[key] = default_value
        else:
            options[key] = incoming
    return options

