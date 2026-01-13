# 🚀 EasyWord - Landing Page

Website landing page chính thức của EasyWord - Giải pháp tạo tài liệu Word thông minh.

## 📁 Cấu trúc dự án

```
Personal Project/
│
├── index.html                  # Trang chủ landing page
│
├── assets/                     # Thư mục chứa tất cả assets
│   ├── css/
│   │   └── style.css          # File CSS chính
│   ├── images/
│   │   └── logo.jpg           # Logo EasyWord
│   └── js/
│       └── main.js            # JavaScript cho tương tác
│
├── example-python/             # Streamlit app (dự án riêng)
│
└── README.md                   # File này
```

## ✨ Tính năng Landing Page

### 🎨 **Thiết kế**
- ✅ Header cố định với logo và buttons Đăng nhập/Đăng ký
- ✅ Hero section với tiêu đề nổi bật
- ✅ Upload area với drag & drop
- ✅ 6 feature cards mô tả tính năng EasyWord
- ✅ CTA section kêu gọi hành động
- ✅ Footer đầy đủ với links

### 🔧 **Chức năng**
- ✅ Upload file với drag-and-drop
- ✅ Kiểm tra định dạng file (DOC, DOCX, TXT)
- ✅ Giới hạn kích thước file (max 10MB)
- ✅ Preview file đã chọn
- ✅ Scroll animations
- ✅ Responsive design (mobile, tablet, desktop)

### 🎯 **Công nghệ sử dụng**
- HTML5
- CSS3 (Custom properties, Grid, Flexbox)
- Vanilla JavaScript (ES6+)
- Google Fonts (Inter)

## 🚀 Cách sử dụng

### Chạy local
1. Mở file `index.html` trong trình duyệt
2. Hoặc dùng Live Server extension trong VS Code

### Deploy lên hosting

#### **Netlify** (Khuyến nghị)
```bash
# Drag & drop thư mục vào Netlify Dashboard
# Hoặc dùng CLI
netlify deploy
```

#### **Vercel**
```bash
vercel
```

#### **GitHub Pages**
1. Push code lên GitHub
2. Settings → Pages → Source: main branch
3. Truy cập: `https://username.github.io/repo-name`

#### **FTP/cPanel**
Upload tất cả files (giữ nguyên cấu trúc thư mục) lên hosting

## 📝 Tùy chỉnh

### Thay logo
Thay file `assets/images/logo.jpg` bằng logo mới

### Đổi màu chủ đạo
Mở `assets/css/style.css`, tìm `:root` và sửa:
```css
--primary-blue: #2563eb;  /* Đổi sang màu khác */
```

### Chỉnh sửa nội dung
Mở `index.html` và chỉnh sửa text trong các tags

### Thêm tính năng mới
Thêm feature card mới trong section `.features-grid`

## 🎨 Features Showcase

Landing page giới thiệu 6 tính năng chính:

1. 🎯 **Tự Động Định Dạng** - AI tự động format tài liệu
2. ✅ **Kiểm Tra Chính Tả** - Sửa lỗi tiếng Việt & tiếng Anh
3. 🎨 **Template Đa Dạng** - Hàng trăm mẫu sẵn có
4. ⚙️ **Tùy Chỉnh Linh Hoạt** - Điều chỉnh mọi chi tiết
5. ⚡ **Xử Lý Siêu Nhanh** - AI xử lý trong vài giây
6. 🔒 **Bảo Mật Tuyệt Đối** - Mã hóa end-to-end

## 🌐 Browser Support

- ✅ Chrome/Edge (Latest)
- ✅ Firefox (Latest)
- ✅ Safari (Latest)
- ✅ Mobile browsers

## 📱 Responsive Breakpoints

- Desktop: > 768px
- Tablet: 481px - 768px
- Mobile: ≤ 480px

## 📄 License

All rights reserved © 2026 EasyWord
