# 📄 Ứng Dụng Chuẩn Hóa Báo Cáo Word UEL

Ứng dụng web được xây dựng bằng **Streamlit** giúp chuẩn hóa báo cáo Word theo định dạng chuẩn của **Trường Đại học Kinh tế - Luật (UEL)**.

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31.1-red)
![License](https://img.shields.io/badge/License-MIT-green)

</div>

## ✨ Tính Năng Chính

| Tính năng | Mô tả |
|-----------|-------|
| 📝 **Tạo Báo Cáo Mới** | Tạo file Word mới từ template với cấu trúc hoàn chỉnh |
| 🔄 **Chuẩn Hóa File** | Upload và tự động chuẩn hóa file Word có sẵn |
| 👁️ **Xem Trước** | Preview kết quả trực tiếp trong trình duyệt |
| ⚙️ **Tùy Chỉnh** | Nhiều tùy chọn định dạng linh hoạt |
| 📊 **Chuẩn UEL** | Tuân thủ 100% tiêu chuẩn định dạng UEL |

## 🚀 Quick Start

### Yêu Cầu Hệ Thống
- Python 3.8 trở lên
- pip (Python package manager)
- Microsoft Word (để mở và cập nhật file kết quả)

### Cài Đặt & Chạy

```bash
# 1. Cài đặt thư viện
pip install -r requirements.txt

# 2. Chạy ứng dụng
streamlit run streamlit_app.py
```

Hoặc chạy nhanh bằng script:
- **Windows**: Double-click `run_streamlit.bat`
- **Mac/Linux**: `./run_streamlit.sh`

Ứng dụng sẽ mở tại: **http://localhost:8501**

## 📖 Hướng Dẫn Sử Dụng

### 1️⃣ Tạo Báo Cáo Mới

1. Mở tab **"Tạo Báo Cáo Mới"**
2. Điền thông tin:
   - Họ tên sinh viên
   - Mã số sinh viên
   - Lớp/Khoa
   - Tiêu đề báo cáo
   - Năm học
   - Nội dung (tùy chọn)
3. Nhấn **"Tạo File Word"**
4. Tải về file

### 2️⃣ Chuẩn Hóa File Có Sẵn

1. Mở tab **"Chuẩn Hóa File Có Sẵn"**
2. Upload file `.docx`
3. Nhấn **"Chuẩn Hóa File"**
4. Xem preview
5. Tải về file đã chuẩn hóa

### 3️⃣ Cập Nhật Mục Lục

**⚠️ QUAN TRỌNG:** Sau khi tải file về, bắt buộc phải cập nhật mục lục:

1. Mở file trong Microsoft Word
2. Nhấn **Ctrl + A** (chọn toàn bộ)
3. Nhấn **F9** (Update Fields)
4. Chọn **"Update entire table"**
5. Lưu file

## 📋 Tiêu Chuẩn Định Dạng UEL

| Thành phần | Định dạng |
|------------|-----------|
| Font chữ nội dung | Times New Roman 13pt |
| Font chữ tiêu đề | Times New Roman 14pt |
| Lề trái | 3cm |
| Lề phải | 2cm |
| Lề trên/dưới | 2cm |
| Giãn dòng | 1.3 (tùy chỉnh) |
| Thụt đầu dòng | 1.27cm |
| Căn lề | Justified (2 bên) |

## 🎨 Giao Diện

Ứng dụng có giao diện hiện đại, dễ sử dụng với:
- **Sidebar**: Tùy chọn định dạng
- **Tab 1**: Tạo báo cáo mới
- **Tab 2**: Chuẩn hóa file có sẵn
- **Preview**: Xem trước kết quả

## ⚙️ Tùy Chọn Định Dạng

Sidebar cung cấp các tùy chọn:

- ✅ Xóa dòng trống & dấu cách thừa
- ✅ Áp dụng font Times New Roman
- ✅ Thiết lập lề chuẩn UEL
- ✅ Thụt đầu dòng & giãn dòng
- ✅ Nhận diện & chuẩn hóa tiêu đề
- ✅ Chuẩn hóa bảng
- ✅ Chèn mục lục tự động
- ✅ Đánh số trang
- ✅ Chọn kiểu số trang (Ả Rập/La Mã)

## 📁 Cấu Trúc Dự Án

```
example-python/
├── .streamlit/
│   └── config.toml           # Cấu hình Streamlit
├── app/
│   ├── config.py             # Cấu hình ứng dụng
│   ├── services/             # Logic xử lý Word
│   │   ├── docx_fields.py
│   │   ├── docx_styles.py
│   │   └── report_formatter.py
│   └── utils/
│       └── options.py
├── streamlit_app.py          # ⭐ File chính
├── requirements.txt          # Dependencies
├── README.md                 # File này
├── README_STREAMLIT.md       # Hướng dẫn chi tiết
├── QUICKSTART.md             # Hướng dẫn nhanh
├── run_streamlit.bat         # Script Windows
└── run_streamlit.sh          # Script Mac/Linux
```

## 🛠️ Công Nghệ Sử Dụng

- **[Streamlit](https://streamlit.io/)**: Framework web app Python
- **[python-docx](https://python-docx.readthedocs.io/)**: Xử lý file Word

## 🐛 Xử Lý Lỗi

### Lỗi: ModuleNotFoundError

```bash
pip install -r requirements.txt
```

### Lỗi: Address already in use

```bash
streamlit run streamlit_app.py --server.port 8502
```

### Lỗi: File quá lớn

Chỉnh trong `.streamlit/config.toml`:

```toml
[server]
maxUploadSize = 500  # MB
```

### Xóa cache

```bash
streamlit cache clear
```

## 📚 Tài Liệu

- [QUICKSTART.md](QUICKSTART.md) - Hướng dẫn chạy nhanh
- [README_STREAMLIT.md](README_STREAMLIT.md) - Hướng dẫn chi tiết
- [HUONG_DAN_CAU_HINH.md](HUONG_DAN_CAU_HINH.md) - Cấu hình nâng cao

## 💡 Tips

### Tối Ưu Hiệu Suất
- Upload file nhỏ hơn 10MB
- Sử dụng file .docx chuẩn (không convert từ PDF)

### Tùy Chỉnh Nhanh
- Bật/tắt tùy chọn trong sidebar
- Điều chỉnh giãn dòng theo nhu cầu

### Preview Hiệu Quả
- Luôn xem preview trước khi tải về
- Kiểm tra mục lục, số trang, tiêu đề

## 🔄 Phiên Bản

### Version 2.0 (Streamlit) - Hiện tại ⭐
- ✅ Giao diện đẹp, hiện đại
- ✅ Dễ cài đặt và sử dụng
- ✅ Preview trực tiếp
- ✅ Không cần setup phức tạp

### Version 1.0 (Flask) - Cũ
- Giao diện HTML/CSS/JS
- API Backend Flask
- Cần setup frontend + backend

## 🤝 Đóng Góp

Mọi đóng góp đều được chào đón! Vui lòng:
1. Fork repo
2. Tạo branch mới
3. Commit changes
4. Push và tạo Pull Request

## 📝 License

MIT License - Phát triển cho mục đích học tập và nghiên cứu.

## 👨‍💻 Tác Giả

**Personal Project**  
Phát triển cho Trường Đại học Kinh tế - Luật (UEL)

## 📞 Hỗ Trợ

Nếu gặp vấn đề:
1. Kiểm tra [QUICKSTART.md](QUICKSTART.md)
2. Xem [README_STREAMLIT.md](README_STREAMLIT.md)
3. Đọc log trong terminal
4. Xóa cache: `streamlit cache clear`

---

<div align="center">

**⭐ Nếu hữu ích, hãy cho repo một ngôi sao! ⭐**

Made with ❤️ for UEL Students

</div>

