# Changelog

Tất cả các thay đổi quan trọng của dự án sẽ được ghi lại trong file này.

## [2.0.0] - 2026-01-12

### ✨ Added - Chức năng mới
- **Chuyển đổi sang Streamlit**: Hoàn toàn tái cấu trúc từ Flask sang Streamlit
- **Giao diện mới**: UI hiện đại, đẹp mắt với CSS tùy chỉnh
- **Preview trực tiếp**: Xem trước file Word ngay trong trình duyệt
- **Tabs navigation**: Tách biệt rõ ràng giữa "Tạo mới" và "Chuẩn hóa"
- **Sidebar options**: Tùy chọn định dạng dễ dàng ở thanh bên
- **Session state**: Lưu trữ file đã xử lý để tải về nhiều lần
- **Progress indicators**: Spinner và progress bar khi xử lý
- **Success/Error messages**: Thông báo rõ ràng, dễ hiểu
- **File upload widget**: Upload file drag & drop tiện lợi
- **Download buttons**: Tải về file dễ dàng một cú click
- **Config file**: `.streamlit/config.toml` cho cấu hình theme
- **Quick start scripts**: `run_streamlit.bat` và `run_streamlit.sh`
- **Documentation**: README.md, README_STREAMLIT.md, QUICKSTART.md
- **.gitignore**: Ignore các file không cần thiết

### 🔧 Changed - Thay đổi
- **Requirements.txt**: Loại bỏ Flask, thêm Streamlit
- **Main entry point**: Từ `main.py` (Flask) sang `streamlit_app.py`
- **Architecture**: Từ API-based sang single-page app
- **Preview method**: Từ iframe sang HTML embed trực tiếp
- **File handling**: Session-based thay vì temporary files

### 🚀 Improved - Cải thiện
- **User Experience**: Giao diện trực quan, dễ sử dụng hơn nhiều
- **Setup**: Không cần cấu hình phức tạp, chỉ cần `pip install` và `streamlit run`
- **Performance**: Load nhanh hơn, không cần khởi động server riêng
- **Responsive**: Tự động responsive trên mobile và tablet
- **Error handling**: Xử lý lỗi tốt hơn với thông báo rõ ràng
- **Documentation**: Tài liệu đầy đủ, chi tiết hơn

### 📁 File Structure Changes
```
Added:
├── streamlit_app.py          ⭐ NEW - Main Streamlit app
├── .streamlit/config.toml    ⭐ NEW - Streamlit config
├── README.md                 ⭐ NEW - Main README
├── README_STREAMLIT.md       ⭐ NEW - Detailed guide
├── QUICKSTART.md             ⭐ NEW - Quick start guide
├── CHANGELOG.md              ⭐ NEW - This file
├── run_streamlit.bat         ⭐ NEW - Windows script
├── run_streamlit.sh          ⭐ NEW - Mac/Linux script
└── .gitignore                ⭐ NEW - Git ignore

Deprecated (not deleted, but no longer used):
├── main.py                   ⚠️ OLD - Flask entry point
├── frontend/index.html       ⚠️ OLD - Flask frontend
└── app/routes/               ⚠️ OLD - Flask routes

Kept (still in use):
├── app/config.py             ✅ - Configuration
├── app/services/             ✅ - Word processing logic
└── app/utils/                ✅ - Utility functions
```

### 🎨 UI/UX Improvements
- Modern gradient buttons
- Clean card-based layout
- Professional color scheme (Purple gradient)
- Info boxes with icons
- Better spacing and typography
- Smooth animations and transitions
- Mobile-friendly responsive design

### 🔒 Security
- File size limit configuration
- File type validation
- XSS protection enabled
- Secure file handling

---

## [1.0.0] - 2024 (Original Flask Version)

### ✨ Features
- Tạo báo cáo Word mới từ template
- Chuẩn hóa file Word theo chuẩn UEL
- API endpoints với Flask
- Frontend HTML/CSS/JS
- Preview PDF trong modal
- Download file đã xử lý
- Tùy chọn định dạng đa dạng

### 🛠️ Technologies
- Backend: Flask 3.0.0
- CORS: flask-cors 4.0.0
- Document: python-docx 1.1.0
- Frontend: Vanilla JS, HTML, CSS

---

## Migration Guide: Flask → Streamlit

### Để chạy phiên bản mới (Streamlit):
```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

### Để chạy phiên bản cũ (Flask):
```bash
pip install Flask==3.0.0 flask-cors==4.0.0
python main.py
```

### Key Differences

| Aspect | Flask (v1) | Streamlit (v2) |
|--------|-----------|----------------|
| **Setup** | Complex | Simple |
| **UI** | HTML/CSS/JS | Python only |
| **Preview** | Modal iframe | Direct embed |
| **State** | Stateless API | Session state |
| **Deploy** | Server needed | Streamlit Cloud |
| **Learning** | Web dev needed | Python only |

---

## Future Plans (v2.1+)

### Planned Features
- [ ] Export to PDF directly
- [ ] Multiple templates
- [ ] Cloud storage integration
- [ ] Collaborative editing
- [ ] Version history
- [ ] Batch processing
- [ ] Custom style profiles
- [ ] AI-powered content suggestions

### Potential Improvements
- [ ] Dark mode support
- [ ] Multi-language interface
- [ ] Advanced formatting options
- [ ] Integration with Google Docs
- [ ] Mobile app version
- [ ] Browser extension

---

**Maintained by**: Personal Project  
**Last Updated**: 2026-01-12

