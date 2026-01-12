# 📄 Ứng Dụng Chuẩn Hóa Báo Cáo Word - Streamlit Version

Ứng dụng web giúp chuẩn hóa báo cáo Word theo định dạng UEL (Đại học Kinh tế - Luật).

## ✨ Tính năng

### 1. 📝 Tạo Báo Cáo Mới
- Tạo file Word mới theo mẫu chuẩn UEL
- Điền thông tin sinh viên, tiêu đề, nội dung
- Tự động tạo cấu trúc báo cáo hoàn chỉnh
- Bao gồm: bìa, lời cam đoan, lời cảm ơn, mục lục, nội dung chính, kết luận, tài liệu tham khảo

### 2. 🔄 Chuẩn Hóa File Có Sẵn
- Tải lên file Word (.docx) cần chuẩn hóa
- Tự động điều chỉnh theo tiêu chuẩn UEL
- Xem trước kết quả trước khi tải về
- Tải về file đã được chuẩn hóa

### 3. ⚙️ Tùy Chọn Định Dạng
- **Font chữ**: Times New Roman 13pt/14pt
- **Lề trang**: Trái 3cm, Phải 2cm, Trên/Dưới 2cm
- **Giãn dòng**: Tùy chỉnh (mặc định 1.3)
- **Thụt đầu dòng**: 1.27cm
- **Mục lục tự động**: Mục lục và Danh mục hình ảnh
- **Đánh số trang**: Ả Rập hoặc La Mã
- **Nhận diện tiêu đề**: Tự động format tiêu đề
- **Chuẩn hóa bảng**: Format nội dung trong bảng

## 🚀 Cài Đặt và Chạy

### Yêu cầu
- Python 3.8 trở lên
- pip (Python package manager)

### Bước 1: Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### Bước 2: Chạy ứng dụng

```bash
streamlit run streamlit_app.py
```

Ứng dụng sẽ tự động mở trong trình duyệt tại địa chỉ: `http://localhost:8501`

### Bước 3: Dừng ứng dụng

Nhấn `Ctrl + C` trong terminal để dừng server.

## 📖 Hướng Dẫn Sử Dụng

### Tạo Báo Cáo Mới

1. Chọn tab **"Tạo Báo Cáo Mới"**
2. Điền thông tin:
   - Họ tên sinh viên
   - Mã số sinh viên (MSSV)
   - Lớp/Khoa
   - Tiêu đề báo cáo
   - Năm học
   - Giảng viên hướng dẫn
   - Địa điểm
3. Điền nội dung bổ sung (tùy chọn):
   - Phần mở đầu
   - Nội dung chính
   - Giải pháp/Kiến nghị
   - Kết luận
   - Tài liệu tham khảo
4. Nhấn **"Tạo File Word"**
5. Tải file về máy

### Chuẩn Hóa File Có Sẵn

1. Chọn tab **"Chuẩn Hóa File Có Sẵn"**
2. Nhấn **"Browse files"** và chọn file .docx cần chuẩn hóa
3. Nhấn **"Chuẩn Hóa File"**
4. Xem trước kết quả trong phần **"Xem Trước File"**
5. Nhấn **"Tải File Về"** để tải về máy

### Tùy Chỉnh Định Dạng

Sử dụng sidebar bên trái để:
- Bật/tắt các tùy chọn chuẩn hóa
- Điều chỉnh giãn dòng
- Chọn kiểu đánh số trang

## ⚠️ Lưu Ý Quan Trọng

### Cập nhật Mục Lục

Sau khi tải file về, **BẮT BUỘC** phải cập nhật mục lục trong Microsoft Word:

1. Mở file trong Microsoft Word
2. Nhấn **Ctrl + A** (chọn toàn bộ văn bản)
3. Nhấn **F9** (hoặc chuột phải → Update Field)
4. Chọn **"Update entire table"**
5. Nhấn **OK**

Việc này sẽ cập nhật:
- Mục lục (Table of Contents)
- Danh mục hình ảnh (List of Figures)
- Số trang chính xác

### Định Dạng UEL Chuẩn

Ứng dụng tự động áp dụng các tiêu chuẩn sau:

| Thành phần | Định dạng |
|------------|-----------|
| **Font chữ nội dung** | Times New Roman 13pt |
| **Font chữ tiêu đề** | Times New Roman 14pt |
| **Lề trái** | 3cm |
| **Lề phải** | 2cm |
| **Lề trên** | 2cm |
| **Lề dưới** | 2cm |
| **Giãn dòng** | 1.3 (tùy chỉnh được) |
| **Thụt đầu dòng** | 1.27cm |
| **Căn lề** | Justified (2 bên) |

## 🛠️ Cấu Trúc Thư Mục

```
example-python/
├── .streamlit/
│   └── config.toml          # Cấu hình Streamlit
├── app/
│   ├── config.py            # Cấu hình ứng dụng
│   ├── routes/              # API routes (Flask - không dùng)
│   ├── services/            # Logic xử lý Word
│   │   ├── docx_fields.py
│   │   ├── docx_styles.py
│   │   └── report_formatter.py
│   └── utils/               # Utilities
│       └── options.py
├── streamlit_app.py         # File chính Streamlit ⭐
├── requirements.txt         # Dependencies
└── README_STREAMLIT.md      # Hướng dẫn này
```

## 🔧 Cấu Hình

### Chỉnh sửa màu sắc và theme

Sửa file `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#667eea"        # Màu chính
backgroundColor = "#f5f6fb"     # Màu nền
secondaryBackgroundColor = "#ffffff"
textColor = "#2b2d42"           # Màu chữ
font = "sans serif"
```

### Chỉnh sửa cấu hình UEL

Sửa file `app/config.py`:

```python
# Font chữ
STANDARD_FONT = "Times New Roman"
BODY_FONT_SIZE = Pt(13)
HEADING_FONT_SIZE = Pt(14)

# Lề trang
UEL_MARGINS = {
    "top": Cm(2),
    "bottom": Cm(2),
    "left": Cm(3),
    "right": Cm(2),
}

# Giãn dòng
LINE_SPACING = 1.5
```

## 🐛 Xử Lý Lỗi Thường Gặp

### Lỗi: "ModuleNotFoundError"

```bash
pip install -r requirements.txt
```

### Lỗi: "Address already in use"

Port 8501 đã được sử dụng. Chạy với port khác:

```bash
streamlit run streamlit_app.py --server.port 8502
```

### Lỗi: "File too large"

Tăng giới hạn upload trong `.streamlit/config.toml`:

```toml
[server]
maxUploadSize = 500  # MB
```

### File Word không hiển thị đúng

- Đảm bảo file là định dạng .docx (không phải .doc)
- Mở file trong Word và nhấn Ctrl+A → F9 để cập nhật
- Kiểm tra file không bị lỗi hoặc corrupt

## 📚 Thư Viện Sử Dụng

- **Streamlit**: Framework web app
- **python-docx**: Xử lý file Word

## 🔄 Chuyển Đổi từ Flask

Ứng dụng này được chuyển đổi từ phiên bản Flask sang Streamlit:

- ✅ **Ưu điểm**: Giao diện đẹp hơn, dễ sử dụng, không cần setup phức tạp
- ✅ **Giữ nguyên**: Toàn bộ logic xử lý Word
- ✅ **Cải thiện**: Preview trực tiếp trong trình duyệt

### Để chạy phiên bản Flask cũ (nếu cần):

```bash
pip install Flask==3.0.0 flask-cors==4.0.0
python main.py
```

## 💡 Tips & Tricks

### 1. Tối ưu hiệu suất

- Upload file nhỏ hơn 10MB để xử lý nhanh hơn
- Sử dụng file .docx chuẩn (không phải convert từ PDF)

### 2. Tùy chỉnh nhanh

- Sử dụng sidebar để bật/tắt các tính năng không cần
- Giảm giãn dòng xuống 1.0 nếu muốn nội dung gọn hơn

### 3. Xem trước hiệu quả

- Luôn xem preview trước khi tải về
- Kiểm tra mục lục, số trang, và format tiêu đề

## 📞 Hỗ Trợ

Nếu gặp vấn đề:

1. Kiểm tra phiên bản Python: `python --version`
2. Cài đặt lại dependencies: `pip install -r requirements.txt --force-reinstall`
3. Xóa cache Streamlit: `streamlit cache clear`
4. Đọc log trong terminal để xem lỗi chi tiết

## 📝 License

Công cụ này được phát triển cho mục đích học tập và nghiên cứu tại Trường Đại học Kinh tế - Luật (UEL).

---

**Phát triển bởi**: Personal Project  
**Phiên bản**: 2.0 (Streamlit)  
**Cập nhật**: 2026

