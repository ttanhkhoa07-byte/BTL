# 📊 Phân tích Dữ liệu Điểm thi THPT Quốc gia 2026

Dự án này là một Dashboard tương tác toàn diện dùng để phân tích phổ điểm thi THPT Quốc gia. Hệ thống bao gồm các chức năng: làm sạch dữ liệu, phân tích thống kê cơ bản, so sánh điểm theo khối/tỉnh, trực quan hóa bằng biểu đồ và dự đoán điểm thi bằng Machine Learning.

## 🛠 Các thư viện sử dụng
- **Python 3.8+**
- **Streamlit**: Xây dựng giao diện web Dashboard (UI).
- **Pandas**: Xử lý, làm sạch và phân tích dữ liệu dạng bảng.
- **Matplotlib**: Vẽ và hiển thị các biểu đồ trực quan (cột, phân bố, heatmap).
- **Scikit-learn**: Xây dựng mô hình Học máy (Random Forest) để dự đoán điểm Toán.

## 📁 Cấu trúc thư mục

```text
BTL/
│
├── input/
│   └── diem_thi_THPTQG_2026.csv    # File dữ liệu thô ban đầu (cần có để chạy)
│
├── output/
│   ├── charts/                     # Thư mục lưu các biểu đồ ảnh (.png)
│   ├── diem_thi_clean.csv          # File dữ liệu sau khi được làm sạch
│   ├── cleaning_report.csv         # Báo cáo quá trình làm sạch
│   ├── statistics_summary.csv      # Bảng dữ liệu thống kê lưu tạm
│   └── statistics_by_province.csv  # Bảng dữ liệu thống kê theo tỉnh lưu tạm
│
├── src/
│   ├── clean_data.py               # Chứa logic làm sạch dữ liệu (xử lý NaN, SBD)
│   ├── statistics.py               # Xử lý tính toán thống kê (điểm TB, top...)
│   ├── visualization.py            # Chứa các hàm vẽ biểu đồ Matplotlib
│   └── prediction.py               # Mô hình Machine Learning dự đoán điểm
│
├── .streamlit/
│   └── config.toml                 # File cấu hình màu sắc giao diện (Light Theme)
│
├── app.py                          # File chạy trên Terminal (dạng menu Console)
├── dashboard.py                    # Giao diện chính của Web Dashboard
├── requirements.txt                # Danh sách các thư viện cần cài đặt
└── README.md                       # File tài liệu hướng dẫn
```

## 🚀 Hướng dẫn cài đặt và sử dụng

### Bước 1: Cài đặt thư viện
Mở Terminal / Command Prompt tại thư mục chứa dự án và chạy lệnh sau để cài đặt tất cả thư viện cần thiết:
```bash
pip install -r requirements.txt
```

### Bước 2: Khởi động Dashboard
Chạy lệnh sau để bật giao diện web:
```bash
streamlit run dashboard.py
```
Trình duyệt sẽ tự động mở trang web ở địa chỉ: `http://localhost:8501`.

### Bước 3: Quy trình sử dụng trên Web
1. **Làm sạch dữ liệu**: Tại thanh menu bên trái, chọn "🧹 Làm sạch dữ liệu" và bấm nút **"Chạy làm sạch dữ liệu"**. Bước này sẽ tạo ra file `diem_thi_clean.csv` để các chức năng khác có thể hoạt động.
2. **Khám phá thống kê**: Sử dụng các trang Thống kê theo môn, Thống kê theo khối, So sánh tỉnh để xem các chỉ số.
3. **Biểu đồ trực quan**: Chuyển sang mục "🖼 Biểu đồ", bấm nút tạo biểu đồ để hệ thống sinh ra 10 ảnh phân tích.
4. **Dự đoán ML**: Dùng thử mô hình Random Forest tại trang "🤖 Dự đoán điểm Toán (ML)".

## 💡 Lưu ý
- Nếu không tải được ảnh hoặc báo lỗi không tìm thấy file, hãy chắc chắn bạn đã vào mục **Làm sạch dữ liệu** để tạo file dữ liệu sạch trước.
- File dữ liệu nguồn phải được đặt đúng vào đường dẫn `input/diem_thi_THPTQG_2026.csv`.

