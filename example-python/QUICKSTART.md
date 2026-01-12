# 🚀 Quick Start - Chuẩn Hóa Báo Cáo Word

## Chạy Ứng Dụng Nhanh

### Windows

1. **Mở Command Prompt hoặc PowerShell**
2. **Chạy lệnh:**
   ```bash
   run_streamlit.bat
   ```

   Hoặc:
   ```bash
   streamlit run streamlit_app.py
   ```

### Mac/Linux

1. **Mở Terminal**
2. **Cấp quyền thực thi (lần đầu):**
   ```bash
   chmod +x run_streamlit.sh
   ```
3. **Chạy ứng dụng:**
   ```bash
   ./run_streamlit.sh
   ```

   Hoặc:
   ```bash
   streamlit run streamlit_app.py
   ```

## Cài Đặt Lần Đầu

### Bước 1: Cài đặt thư viện

```bash
pip install -r requirements.txt
```

### Bước 2: Chạy ứng dụng

```bash
streamlit run streamlit_app.py
```

Ứng dụng sẽ tự động mở trong trình duyệt tại: **http://localhost:8501**

## 🎯 Sử Dụng Cơ Bản

### Tạo Báo Cáo Mới
1. Chọn tab **"Tạo Báo Cáo Mới"**
2. Điền thông tin sinh viên
3. Nhấn **"Tạo File Word"**
4. Tải về và sử dụng

### Chuẩn Hóa File Có Sẵn
1. Chọn tab **"Chuẩn Hóa File Có Sẵn"**
2. Upload file .docx
3. Nhấn **"Chuẩn Hóa File"**
4. Xem preview và tải về

## ⚠️ Lưu Ý Quan Trọng

Sau khi tải file về, **BẮT BUỘC** mở trong Word và:
1. Nhấn **Ctrl + A**
2. Nhấn **F9**
3. Chọn **"Update entire table"**

Để cập nhật mục lục và số trang!

## 🐛 Gặp Lỗi?

### Lỗi: ModuleNotFoundError
```bash
pip install -r requirements.txt
```

### Lỗi: Port đã được sử dụng
```bash
streamlit run streamlit_app.py --server.port 8502
```

### Xóa cache
```bash
streamlit cache clear
```

## 📖 Hướng Dẫn Chi Tiết

Xem file **README_STREAMLIT.md** để biết thêm chi tiết.

---

**Chúc bạn sử dụng hiệu quả! 🎉**

