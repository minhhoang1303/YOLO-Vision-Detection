# YOLO Vision Detection Platform

## Giới thiệu

**YOLO Vision Detection** là nền tảng mã nguồn mở được thiết kế cho **nghiên cứu và giáo dục** về thị giác máy tính (Computer Vision), đặc biệt trong lĩnh vực **Object Detection** sử dụng mô hình YOLO (You Only Look Once).

Dự án này phù hợp cho:
- Sinh viên học về Deep Learning và Computer Vision
- Nghiên cứu sinh thực hành object detection
- Giảng viên làm tài liệu giảng dạy
- Nhà phát triển xây dựng ứng dụng AI

## Tính năng chính

### 1. Gán nhãn dữ liệu (Labeling)
- Giao diện web trực quan, dễ sử dụng
- Vẽ bounding box trên ảnh
- Hỗ trợ nhiều classes với màu sắc phân biệt
- Upload ảnh từ máy tính hoặc chụp từ camera
- Import/Export dữ liệu labels

### 2. Quản lý Dự án (Project Management)
- Hỗ trợ nhiều dự án riêng biệt
- Mỗi dự án có dataset, models và settings riêng
- Dễ dàng chuyển đổi giữa các dự án

### 3. Huấn luyện mô hình (Training)
- Sử dụng YOLOv8/Ultralytics framework
- Nhiều lựa chọn model: nano, small, medium, large
- Cấu hình epochs, image size, batch size
- Theo dõi tiến trình training real-time
- Tự động export sang format YOLO

### 4. Nhận diện thời gian thực (Real-time Detection)
- Detection từ camera (webcam)
- Auto-start khi chọn model
- Hiển thị FPS và số objects phát hiện
- Model caching để tăng hiệu suất
- Hỗ trợ CPU (phù hợp với máy không có GPU tương thích)

## Yêu cầu hệ thống

### Yêu cầu tối thiểu
- Python 3.8+
- RAM: 8GB
- Ổ cứng: 5GB free space

### Yêu cầu khuyến nghị (để training nhanh hơn)
- GPU NVIDIA với CUDA support
- RAM: 16GB+
- Ổ cứng SSD: 10GB+ free space

### Lưu ý về GPU
- Chương trình sẽ tự động chạy trên CPU nếu GPU không khả dụng
- Training trên CPU chậm hơn nhưng vẫn hoạt động tốt cho mục đích học tập

## Cài đặt

### 1. Clone hoặc tải project
```bash
git clone <repo-url>
cd "YOLO Vision Detection"
```

### 2. Tạo môi trường ảo (khuyến nghị)
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 4. Chạy ứng dụng
```bash
python app.py
# hoặc
python main.py
```

### 5. Truy cập giao diện web
Mở trình duyệt: **http://localhost:5000**

## Hướng dẫn sử dụng

### Bước 1: Tạo Project mới
1. Nhấn nút **📂 Dự án**
2. Nhấn **Tạo Dự án mới**
3. Nhập tên dự án và nhấn **Tạo**

### Bước 2: Thêm Classes
1. Nhấn **🏷️ Quản lý Classes**
2. Nhập tên class (ví dụ: "car", "person", "dog")
3. Chọn màu sắc phân biệt
4. Nhấn **Thêm**

### Bước 3: Upload ảnh
1. Nhấn **📁 Upload Ảnh**
2. Chọn nhiều ảnh từ máy tính
3. Hoặc nhấn **📷 Camera** để chụp ảnh trực tiếp

### Bước 4: Gán nhãn (Labeling)
1. Chọn ảnh từ danh sách bên trái
2. Chọn class từ danh sách
3. Vẽ bounding box bằng cách kéo chuột trên ảnh
4. Nhãn sẽ tự động lưu

### Bước 5: Export dữ liệu
1. Nhấn **📤 Export YOLO**
2. Dữ liệu sẽ được export sang format YOLO

### Bước 6: Train Model
1. Nhấn **🚀 Train Model**
2. Chọn model type (yolov8n khuyến nghị cho beginners)
3. Cấu hình epochs (50-100 cho kết quả tốt)
4. Nhấn **Bắt đầu Train**
5. Theo dõi tiến trình trong giao diện

### Bước 7: Detection thời gian thực
1. Nhấn **🤖 Detection Camera**
2. Chọn model đã train
3. Chọn camera
4. Nhấn **▶️ Bắt đầu**
5. Model sẽ tự động detect objects

## Cấu trúc dự án

```
YOLO Vision Detection/
├── app.py                  # Flask API Server
├── main.py                 # Main launcher
├── requirements.txt         # Python dependencies
├── web/                    # Web UI
│   ├── index.html         # Trang chính
│   ├── css/style.css       # Styles
│   └── js/labeling.js      # JavaScript logic
├── projects/               # Dữ liệu projects
│   └── [project_name]/
│       ├── data/
│       │   ├── images/    # Ảnh gốc
│       │   ├── labels/    # Labels JSON
│       │   └── classes.json
│       ├── dataset/      # Dataset export (YOLO format)
│       └── runs/
│           └── train/weights/best.pt  # Model đã train
└── debug/                  # Debug outputs
```

## Thuật ngữ và khái niệm

### Object Detection
Phương pháp thị giác máy tính để xác định vị trí và phân loại objects trong ảnh/video.

### Bounding Box
Hình chữ nhật bao quanh object được phát hiện.

### YOLO (You Only Look Once)
Một trong những thuật toán object detection phổ biến nhất, nổi tiếng về tốc độ và độ chính xác.

### Confidence Score
Điểm tin cậy của model về việc phát hiện object (0-1). Ngưỡng confidence cao hơn = ít detection nhưng chính xác hơn.

### Dataset
Tập hợp dữ liệu (ảnh + labels) dùng để train model.

### Fine-tuning
Quá trình train lại model đã pre-trained với dữ liệu mới.

## Best practices cho việc học tập

### 1. Bắt đầu với ít classes
- Nên bắt đầu với 1-3 classes
- Tăng dần số lượng khi đã quen

### 2. Dataset chất lượng
- **Số lượng**: Tối thiểu 50-100 ảnh/class
- **Đa dạng**: Khác nhau về góc chụp, ánh sáng, kích thước
- **Chất lượng**: Ảnh rõ nét, objects không bị che khuất

### 3. Điều chỉnh ngưỡng (Threshold)
- **Training**: Confidence threshold cao (0.5-0.7) để giảm noise
- **Inference**: Có thể điều chỉnh tùy yêu cầu

### 4. Đánh giá model
- Kiểm tra trên ảnh không có trong training set
- So sánh kết quả với pre-trained model

## Xử lý sự cố

### Model không detect được gì
- **Nguyên nhân phổ biến**: Dataset quá ít (dưới 20 ảnh)
- **Giải pháp**: Thêm nhiều ảnh training hơn (50-100 ảnh)
- **Giải pháp khác**: Sử dụng pre-trained model và fine-tune

### Confidence quá thấp
- Model chưa trained đủ tốt
- Thử tăng epochs (100-200)
- Thêm dữ liệu training đa dạng hơn

### GPU không được nhận diện
- Kiểm tra CUDA installation
- Kiểm tra PyTorch version
- Chương trình sẽ tự động chạy trên CPU

### Camera không hoạt động
- Kiểm tra quyền truy cập camera
- Thử refresh trang và reload
- Kiểm tra camera có đang được sử dụng bởi ứng dụng khác

## Tài liệu tham khảo

- [Ultralytics YOLOv8 Documentation](https://docs.ultralytics.com/)
- [YOLO Paper - You Only Look Once](https://arxiv.org/abs/1506.02640)
- [COCO Dataset](https://cocodataset.org/)
- [Roboflow - Dataset Management](https://roboflow.com/)

## Đóng góp

Dự án này được phát triển cho mục đích **giáo dục và nghiên cứu**. Mọi đóng góp, góp ý và cải tiến đều được hoan nghênh!

## Giấy phép

MIT License - Tự do sử dụng cho mục đích học tập và nghiên cứu.

---

**Lưu ý quan trọng**: Đây là dự án mã nguồn mở cho mục đích giáo dục. Kết quả detection phụ thuộc vào chất lượng dataset và quá trình training. Với dataset nhỏ, model có thể chưa đạt độ chính xác cao - đây là điều bình thường trong quá trình học tập.
