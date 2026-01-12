# Hướng Dẫn Cấu Hình Định Dạng Word

## 📁 File cấu hình chính: `app/config.py`

Tất cả các thông số về **font chữ**, **cỡ chữ**, **màu sắc**, **lề trang** được quản lý tập trung tại file `app/config.py`.

---

## 🎨 Các cấu hình có thể chỉnh sửa

### 1. Font chữ (FONT CHỮ)

```python
STANDARD_FONT = "Times New Roman"  # Font chữ chuẩn cho toàn bộ tài liệu
FALLBACK_FONT = "Arial"            # Font dự phòng nếu Times New Roman không có
```

**Các font phổ biến:**
- `"Times New Roman"` - Font chuẩn báo cáo
- `"Arial"` - Font sans-serif
- `"Calibri"` - Font hiện đại
- `"Tahoma"` - Font dễ đọc

---

### 2. Cỡ chữ (CỠ CHỮ)

```python
BODY_FONT_SIZE = Pt(13)           # Cỡ chữ nội dung văn bản
HEADING_FONT_SIZE = Pt(14)        # Cỡ chữ tiêu đề
TOC_FONT_SIZE = Pt(13)            # Cỡ chữ mục lục
PAGE_NUMBER_FONT_SIZE = Pt(13)    # Cỡ chữ số trang
CAPTION_FONT_SIZE = Pt(10)        # Cỡ chữ chú thích hình/bảng
LIST_FONT_SIZE = Pt(13)           # Cỡ chữ danh sách
```

**Hướng dẫn đổi cỡ chữ:**
```python
# Ví dụ: Đổi cỡ chữ nội dung từ 13 sang 14
BODY_FONT_SIZE = Pt(14)

# Ví dụ: Đổi cỡ chữ tiêu đề từ 14 sang 16
HEADING_FONT_SIZE = Pt(16)
```

---

### 3. Màu sắc (MÀU SẮC)

```python
DEFAULT_TEXT_COLOR = RGBColor(0, 0, 0)      # Màu đen (mặc định)
HEADING_COLOR = RGBColor(0, 0, 0)           # Màu tiêu đề
TOC_COLOR = RGBColor(0, 0, 0)               # Màu mục lục
CAPTION_COLOR = RGBColor(0, 0, 0)           # Màu chú thích
ERROR_COLOR = RGBColor(200, 0, 0)           # Màu đỏ (lỗi/cảnh báo)
LINK_COLOR = RGBColor(0, 0, 255)            # Màu xanh dương (link)
```

**Hướng dẫn đổi màu:**
```python
# Cú pháp: RGBColor(R, G, B)
# R, G, B là các giá trị từ 0-255

# Ví dụ một số màu phổ biến:
RGBColor(0, 0, 0)       # Đen
RGBColor(255, 255, 255) # Trắng
RGBColor(255, 0, 0)     # Đỏ
RGBColor(0, 255, 0)     # Xanh lá
RGBColor(0, 0, 255)     # Xanh dương
RGBColor(128, 128, 128) # Xám
RGBColor(0, 128, 255)   # Xanh da trời
```

---

### 4. Định dạng đoạn văn (ĐỊNH DẠNG ĐOẠN)

```python
LINE_SPACING = 1.5                # Khoảng cách dòng (1.0, 1.5, 2.0, v.v.)
PARAGRAPH_INDENT = Cm(1.27)       # Thụt lề đầu dòng (cm)
SPACE_BEFORE = Pt(0)              # Khoảng cách trước đoạn
SPACE_AFTER = Pt(0)               # Khoảng cách sau đoạn
```

**Hướng dẫn chỉnh sửa:**
```python
# Đổi khoảng cách dòng sang 1.0 (đơn) hoặc 2.0 (đôi)
LINE_SPACING = 2.0

# Đổi thụt lề đầu dòng
PARAGRAPH_INDENT = Cm(1.0)  # 1cm
PARAGRAPH_INDENT = Cm(1.5)  # 1.5cm
```

---

### 5. Lề trang (LỀ TRANG)

```python
UEL_MARGINS = {
    "top": Cm(2),      # Lề trên: 2cm
    "bottom": Cm(2),   # Lề dưới: 2cm
    "left": Cm(3),     # Lề trái: 3cm
    "right": Cm(2),    # Lề phải: 2cm
}
```

**Hướng dẫn chỉnh lề:**
```python
# Ví dụ: Đổi lề theo chuẩn A4
UEL_MARGINS = {
    "top": Cm(2.5),
    "bottom": Cm(2.5),
    "left": Cm(3.0),
    "right": Cm(2.0),
}
```

---

### 6. Cấu hình Style chi tiết

#### Style cho Caption (chú thích)
```python
CAPTION_STYLE_CONFIG = {
    "font_name": STANDARD_FONT,
    "font_size": CAPTION_FONT_SIZE,
    "color": CAPTION_COLOR,
    "italic": True,    # In nghiêng
    "bold": False,     # Không in đậm
}
```

#### Style cho UEL Figure (chú thích hình)
```python
UEL_FIGURE_STYLE_CONFIG = {
    "font_name": STANDARD_FONT,
    "font_size": BODY_FONT_SIZE,
    "color": CAPTION_COLOR,
    "italic": True,
    "bold": False,
    "alignment": "center",  # Căn giữa
}
```

#### Style cho các cấp Heading
```python
# Heading 1 (Tiêu đề cấp 1)
HEADING1_STYLE_CONFIG = {
    "font_name": STANDARD_FONT,
    "font_size": Pt(16),
    "color": HEADING_COLOR,
    "bold": True,
    "italic": False,
    "all_caps": False,
}

# Heading 2 (Tiêu đề cấp 2)
HEADING2_STYLE_CONFIG = {
    "font_name": STANDARD_FONT,
    "font_size": Pt(14),
    "color": HEADING_COLOR,
    "bold": True,
    "italic": False,
}

# Heading 3 (Tiêu đề cấp 3)
HEADING3_STYLE_CONFIG = {
    "font_name": STANDARD_FONT,
    "font_size": Pt(13),
    "color": HEADING_COLOR,
    "bold": True,
    "italic": False,
}
```

#### Style cho Mục lục (TOC - Table of Contents)

**⭐ QUAN TRỌNG: Cấu hình này đảm bảo TẤT CẢ nội dung trong "MỤC LỤC" và "DANH MỤC HÌNH ẢNH" đều dùng font Times New Roman 13pt**

```python
# Cấu hình style cho nội dung Mục lục
TOC_STYLE_CONFIG = {
    "font_name": STANDARD_FONT,      # Times New Roman
    "font_size": TOC_FONT_SIZE,      # 13pt
    "color": TOC_COLOR,              # Màu đen
    "bold": False,                   # Không in đậm
    "italic": False,                 # Không in nghiêng
    "line_spacing": 1.5,             # Khoảng cách dòng 1.5
}

# Cấu hình tiêu đề "MỤC LỤC"
TOC_HEADING_CONFIG = {
    "font_name": STANDARD_FONT,
    "font_size": TOC_FONT_SIZE,
    "color": HEADING_COLOR,
    "bold": True,                    # In đậm
    "italic": False,
    "alignment": "center",           # Căn giữa
}

# Cấu hình tiêu đề "DANH MỤC HÌNH ẢNH"
TOF_HEADING_CONFIG = {
    "font_name": STANDARD_FONT,
    "font_size": TOC_FONT_SIZE,
    "color": HEADING_COLOR,
    "bold": True,                    # In đậm
    "italic": False,
    "alignment": "center",           # Căn giữa
}
```

**Hướng dẫn thay đổi:**
```python
# Ví dụ: Đổi cỡ chữ mục lục từ 13pt sang 12pt
TOC_FONT_SIZE = Pt(12)

# Ví dụ: Đổi khoảng cách dòng mục lục từ 1.5 sang 1.0
TOC_STYLE_CONFIG = {
    ...
    "line_spacing": 1.0,  # Thay đổi ở đây
}

# Ví dụ: In nghiêng nội dung mục lục
TOC_STYLE_CONFIG = {
    ...
    "italic": True,  # Thay đổi ở đây
}
```

---

## 🔧 Cách áp dụng thay đổi

1. **Mở file** `app/config.py`
2. **Chỉnh sửa** các giá trị theo ý muốn
3. **Lưu file** (Ctrl + S)
4. **Khởi động lại server** Flask (nếu đang chạy):
   - Nhấn `Ctrl + C` để dừng server
   - Chạy lại: `python main.py`

---

## ✅ Ví dụ thay đổi thường gặp

### Ví dụ 1: Đổi toàn bộ font sang Arial
```python
STANDARD_FONT = "Arial"
```

### Ví dụ 2: Tăng cỡ chữ nội dung lên 14
```python
BODY_FONT_SIZE = Pt(14)
```

### Ví dụ 3: Đổi tiêu đề sang màu xanh dương
```python
HEADING_COLOR = RGBColor(0, 0, 255)
```

### Ví dụ 4: Đổi khoảng cách dòng sang đôi (2.0)
```python
LINE_SPACING = 2.0
```

### Ví dụ 5: Đổi lề trái sang 3.5cm
```python
UEL_MARGINS = {
    "top": Cm(2),
    "bottom": Cm(2),
    "left": Cm(3.5),    # Thay đổi ở đây
    "right": Cm(2),
}
```

---

## 📝 Ghi chú quan trọng

- **Đơn vị đo:**
  - `Pt()` - Point (dùng cho cỡ chữ, khoảng cách)
  - `Cm()` - Centimeter (dùng cho lề, thụt lề)
  - `Inches()` - Inch

- **Quy đổi:**
  - 1 inch = 2.54 cm
  - 1 cm = 0.39 inch
  - 12 pt = 16 px (gần đúng)

- **Font chữ:**
  - Chỉ sử dụng các font đã cài đặt trong hệ thống
  - Nếu font không tồn tại, Word sẽ dùng font mặc định

---

## 🚀 Kiểm tra sau khi thay đổi

1. Khởi động lại server
2. Vào trình duyệt: http://127.0.0.1:5000
3. Upload file Word và chuẩn hóa
4. Kiểm tra định dạng output

---

## ❓ Câu hỏi thường gặp

**Q: Tôi đổi config nhưng không thấy thay đổi?**
- A: Hãy chắc chắn bạn đã lưu file và khởi động lại server Flask.

**Q: Làm sao để khôi phục cấu hình mặc định?**
- A: Xem file `app/config.py` ban đầu hoặc sử dụng Git để revert.

**Q: Có thể dùng font tiếng Việt không?**
- A: Có, "Times New Roman" hỗ trợ tốt tiếng Việt. Các font khác như "Arial", "Tahoma" cũng hỗ trợ.

---

**Tác giả:** AI Assistant
**Cập nhật:** 2026-01-09

