# Cấu Hình Font Cho Mục Lục (TOC) - Times New Roman 13pt

## 📋 Tổng Quan

Hệ thống đã được cấu hình để **đảm bảo TẤT CẢ nội dung trong Mục Lục và Danh Mục Hình Ảnh đều sử dụng font Times New Roman 13pt**.

---

## ✅ Những Gì Đã Được Cấu Hình

### 1. **Mục Lục (MỤC LỤC)**
- ✅ Font: **Times New Roman**
- ✅ Cỡ chữ: **13pt**
- ✅ Khoảng cách dòng: **1.5**
- ✅ Không in đậm, không in nghiêng (nội dung)
- ✅ Tiêu đề "MỤC LỤC": In đậm, căn giữa

### 2. **Danh Mục Hình Ảnh (DANH MỤC HÌNH ẢNH)**
- ✅ Font: **Times New Roman**
- ✅ Cỡ chữ: **13pt**
- ✅ Khoảng cách dòng: **1.5**
- ✅ Không in đậm, không in nghiêng (nội dung)
- ✅ Tiêu đề "DANH MỤC HÌNH ẢNH": In đậm, căn giữa

---

## 🎯 Các Style TOC Được Tự Động Tạo

Hệ thống tự động tạo và cấu hình các style sau với **Times New Roman 13pt**:

| Style | Mô tả | Font | Cỡ chữ | Thụt lề |
|-------|-------|------|--------|---------|
| TOC 1 | Mục cấp 1 | Times New Roman | 13pt | 0.5 inch |
| TOC 2 | Mục cấp 2 | Times New Roman | 13pt | 1.0 inch |
| TOC 3 | Mục cấp 3 | Times New Roman | 13pt | 1.5 inch |
| ... | ... | Times New Roman | 13pt | ... |
| TOC 9 | Mục cấp 9 | Times New Roman | 13pt | 4.5 inch |

---

## ⚙️ File Cấu Hình: `app/config.py`

### Cấu hình cỡ chữ TOC
```python
TOC_FONT_SIZE = Pt(13)  # Cỡ chữ 13pt cho tất cả mục lục
```

### Cấu hình style TOC
```python
# Cấu hình cho nội dung mục lục
TOC_STYLE_CONFIG = {
    "font_name": STANDARD_FONT,      # "Times New Roman"
    "font_size": TOC_FONT_SIZE,      # Pt(13)
    "color": TOC_COLOR,              # RGBColor(0, 0, 0) - Đen
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

---

## 🔧 Module Xử Lý: `app/services/docx_styles.py`

### Hàm quan trọng:

#### 1. `_copy_heading_style_to_toc(doc)`
- **Chức năng**: Tạo và cấu hình tất cả TOC styles (TOC 1-9)
- **Font**: Times New Roman (từ config)
- **Size**: 13pt (từ config)
- **East Asian Font**: Được set đúng cho tiếng Việt

#### 2. `_format_toc_paragraphs(doc)`
- **Chức năng**: Format tất cả paragraphs trong mục lục
- **Áp dụng cho**: Tất cả đoạn có style bắt đầu bằng "TOC"
- **Font**: Times New Roman 13pt

#### 3. `_ensure_east_asia_font(run)`
- **Chức năng**: Đảm bảo font East Asian (tiếng Việt) đúng
- **Quan trọng**: Font tiếng Việt phải được set riêng trong XML

---

## 📝 Cách Sử Dụng

### Để thay đổi cỡ chữ mục lục:

1. Mở file `app/config.py`
2. Tìm dòng:
   ```python
   TOC_FONT_SIZE = Pt(13)
   ```
3. Đổi thành cỡ chữ mong muốn:
   ```python
   TOC_FONT_SIZE = Pt(12)  # Hoặc 14, 15...
   ```
4. Lưu file → Server tự động reload

### Để thay đổi font mục lục:

1. Mở file `app/config.py`
2. Tìm dòng:
   ```python
   STANDARD_FONT = "Times New Roman"
   ```
3. Đổi thành font mong muốn:
   ```python
   STANDARD_FONT = "Arial"  # Hoặc font khác
   ```
4. Lưu file → Server tự động reload

### Để in nghiêng nội dung mục lục:

1. Mở file `app/config.py`
2. Tìm `TOC_STYLE_CONFIG`
3. Đổi `"italic": False` thành `"italic": True`
4. Lưu file → Server tự động reload

---

## ✨ Tính Năng Đặc Biệt

### 1. **Tự động tạo TOC styles**
- Nếu document không có sẵn TOC 1, TOC 2... styles
- Hệ thống sẽ **tự động tạo** với cấu hình đúng

### 2. **Force set font trong XML**
- Không chỉ set qua Python API
- Còn set trực tiếp trong XML để đảm bảo Word nhận đúng
- Bao gồm cả: `w:ascii`, `w:hAnsi`, `w:eastAsia`, `w:cs`

### 3. **East Asian Font Support**
- Đặc biệt quan trọng cho **tiếng Việt**
- Đảm bảo các ký tự có dấu hiển thị đúng font

---

## 🧪 Kiểm Tra Kết Quả

### Sau khi format file Word:

1. **Mở file Word đã format**
2. **Bấm Ctrl + A** (chọn tất cả)
3. **Bấm F9** (Update fields) → Chọn **"Update entire table"**
4. **Kiểm tra mục lục:**
   - Font: Times New Roman ✅
   - Cỡ chữ: 13pt ✅
   - Khoảng cách dòng: 1.5 ✅

### Log từ server:
```
✅ Đang tạo TOC với font = Times New Roman, size = 13.0pt
✅ POST /api/format-report HTTP/1.1" 200
```

---

## 📚 Tài Liệu Liên Quan

- **Hướng dẫn cấu hình tổng quát**: `HUONG_DAN_CAU_HINH.md`
- **File cấu hình chính**: `app/config.py`
- **Module xử lý styles**: `app/services/docx_styles.py`
- **Module xử lý fields**: `app/services/docx_fields.py`

---

## ❓ FAQ

### Q: Tại sao cần bấm F9 trong Word?
**A**: Mục lục là một **field động** trong Word. Khi mở file, Word chỉ hiển thị nội dung cũ. Bấm F9 để Word **tạo lại** mục lục với style mới.

### Q: Font vẫn không đúng sau khi bấm F9?
**A**: Kiểm tra:
1. File `app/config.py` có đúng `STANDARD_FONT = "Times New Roman"`?
2. Server đã reload sau khi thay đổi config?
3. Đã chọn "Update entire table" khi bấm F9?

### Q: Làm sao để mục lục không in nghiêng?
**A**: Trong `app/config.py`, đảm bảo:
```python
TOC_STYLE_CONFIG = {
    ...
    "italic": False,  # Phải là False
}
```

### Q: Có thể dùng cỡ chữ khác cho từng cấp TOC không?
**A**: Hiện tại tất cả cấp dùng chung `TOC_FONT_SIZE`. Nếu cần khác nhau, phải customize code trong `docx_styles.py`.

---

## 🎉 Kết Luận

Hệ thống đã được cấu hình **tập trung** và **tự động** để đảm bảo:

✅ **Tất cả nội dung mục lục**: Times New Roman 13pt  
✅ **Tất cả nội dung danh mục hình ảnh**: Times New Roman 13pt  
✅ **Dễ dàng thay đổi**: Chỉ cần sửa trong `app/config.py`  
✅ **Tự động reload**: Flask debug mode tự động áp dụng thay đổi  

**Tác giả**: AI Assistant  
**Ngày**: 2026-01-09  
**Version**: 1.0



