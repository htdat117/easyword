# 📄 EasyWord - Chuẩn Hóa Báo Cáo Word

Ứng dụng web để tạo và chuẩn hóa file Word theo chuẩn báo cáo học thuật (UEL).

## ✨ Tính Năng

- ✅ Tạo báo cáo mới với mẫu chuẩn
- ✅ Chuẩn hóa file Word có sẵn
- ✅ Định dạng theo chuẩn UEL (Times New Roman, lề, giãn dòng...)
- ✅ Tự động tạo mục lục
- ✅ Đánh số trang
- ✅ Nhiều tùy chọn định dạng

## 🚀 Cài Đặt và Chạy

### Yêu Cầu

- Python 3.7+
- pip

### Bước 1: Clone Repository

```bash
git clone https://github.com/htdat117/easyword.git
cd easyword/example-python
```

### Bước 2: Cài Đặt Dependencies

```bash
pip install -r requirements.txt
```

### Bước 3: Chạy Ứng Dụng

```bash
python main.py
```

### Bước 4: Mở Trình Duyệt

Mở http://localhost:5000 để sử dụng giao diện:
- **Tạo báo cáo mới**: Nhập thông tin và tạo file Word mẫu
- **Chuẩn hóa file có sẵn**: Upload file `.docx` để chuẩn hóa

## 📁 Cấu Trúc Dự Án

```
example-python/
├── main.py                    # Entry point
├── requirements.txt           # Dependencies
├── app/
│   ├── __init__.py           # Flask app factory
│   ├── config.py             # Cấu hình (font, margin, etc.)
│   ├── routes/
│   │   ├── report.py         # API endpoints
│   │   └── static.py         # Serve frontend
│   ├── services/
│   │   └── report_formatter.py  # Logic xử lý Word
│   └── utils/
│       └── options.py        # Xử lý tùy chọn
└── frontend/
    └── index.html            # Giao diện người dùng
```

## 🎛️ Tùy Chọn Định Dạng

Giao diện cho phép bật/tắt các tính năng:
- Xóa dòng trống & dấu cách thừa
- Áp dụng font Times New Roman 13pt / 14pt
- Thiết lập lề chuẩn UEL (Trái 3.5cm, Phải 2cm, Trên/Dưới 2.5cm)
- Thụt đầu dòng 1cm và giãn dòng 1.3
- Nhận diện & chuẩn hóa tiêu đề
- Chuẩn hóa định dạng trong bảng
- Chèn mục lục tự động
- Đánh số trang (Ả Rập hoặc La Mã)

## 📚 Tài Liệu

Xem file `HUONG_DAN_BAO_CAO_WORD.md` để biết chi tiết về:
- Công nghệ sử dụng
- Lộ trình phát triển
- Tài liệu tham khảo

## 🔧 API Endpoints

### POST `/api/generate-report`

Tạo báo cáo mới từ thông tin nhập vào.

**Request Body:**
```json
{
  "studentName": "Nguyễn Văn A",
  "className": "Công nghệ thông tin K45",
  "reportTitle": "Báo cáo môn...",
  "year": "2024-2025",
  "content": "Nội dung báo cáo...",
  "options": {
    "clean_whitespace": true,
    "normalize_font": true,
    "insert_toc": true,
    ...
  }
}
```

### POST `/api/format-report`

Chuẩn hóa file Word có sẵn.

**Request:** Form data với file `.docx` và options JSON.

## 📝 Ghi Chú

- Sau khi tạo mục lục, nhấn `Ctrl + A` rồi `F9` trong Word để cập nhật
- File Word được tạo theo chuẩn UEL (Trường Đại học Kinh tế - Luật)
- Có thể tùy chỉnh các tùy chọn định dạng theo nhu cầu

## 📄 License

MIT License

## 👤 Tác Giả

- GitHub: [@htdat117](https://github.com/htdat117)
