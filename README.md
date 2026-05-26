# Hệ thống Tái tạo & Dàn trang Tài liệu Tự động (Document Reconstruction Pipeline)

Hệ thống này là một chuỗi đường ống (pipeline) gồm các script Python chạy nối tiếp nhau, nhằm mục đích xử lý dữ liệu JSON trích xuất từ PDF (ví dụ qua MinerU), sau đó tính toán lại không gian, phục hồi text, bẻ khóa giao diện, và cuối cùng xuất ra một file PDF mới hoàn mỹ với độ chính xác cao.

## 📦 Yêu cầu Cài đặt (Installation & Setup)

Hệ thống yêu cầu Python 3.8+ và một số thư viện chuyên dụng. Bạn nên tạo môi trường ảo (virtual environment) trước khi cài đặt.

### 1. Cài đặt các thư viện Python
Mở Terminal/Command Prompt và chạy các lệnh sau:
```bash
# Cài đặt các thư viện lõi
pip install openai transformers playwright

# Tải và cài đặt trình duyệt Chromium (phục vụ bước 10 xuất PDF)
playwright install chromium
```

### 2. Cấu hình API Key (Môi trường)
Bước 3 (`3.1.py` hoặc `3.2.py`) yêu cầu kết nối đến API của DeepSeek hoặc NVIDIA NIM. Bạn phải thiết lập biến môi trường (Environment Variable) chứa khóa API trước khi chạy code.

**Dành cho Windows:**
- Dùng **PowerShell** (Khuyên dùng):
  ```powershell
  $env:DEEPSEEK_API_KEY="sk-chuoi-api-key-cua-ban"
  $env:NVIDIA_API_KEY="nvapi-chuoi-api-key-cua-ban"
  ```
- Dùng **Command Prompt (CMD)**:
  ```cmd
  set DEEPSEEK_API_KEY=sk-chuoi-api-key-cua-ban
  set NVIDIA_API_KEY=nvapi-chuoi-api-key-cua-ban
  ```

**Dành cho Linux / macOS:**
- Dùng **Bash/Zsh**:
  ```bash
  export DEEPSEEK_API_KEY="sk-chuoi-api-key-cua-ban"
  export NVIDIA_API_KEY="nvapi-chuoi-api-key-cua-ban"
  ```

*(Lưu ý: API Key chỉ tồn tại tạm thời trong phiên Terminal hiện tại. Nếu bạn mở cửa sổ Terminal mới, bạn sẽ phải thiết lập lại).*

---

## 🚀 Hướng dẫn chạy (Workflow)

Để chạy toàn bộ hệ thống, bạn cần đặt các file dữ liệu đầu vào theo đúng cấu trúc:
```text
input/
  ├── ten_file_pdf_1/
  │    ├── layout.json      (File JSON gốc ban đầu trích xuất từ MinerU)
  │    └── images/          (Thư mục chứa các ảnh gốc)
  └── ten_file_pdf_2/
       ├── layout.json
       └── images/
```

Khi chạy các script, hệ thống sẽ tự động tạo ra thư mục `temp/` bên trong mỗi thư mục PDF để lưu trữ các file trung gian (từ `1.json` đến `10.pdf`).

Sau đó, hãy chạy lần lượt các script theo thứ tự từ 1 đến 10:
```bash
python 1.py
python 2.py
python 3.1.py  # Hoặc python 3.2.py nếu dùng NVIDIA NIM ưu tiên 3.1 dịch thuật ổn định hơn
python 4.py
python 5.py
python 6.py
python 7.py
python 8.py
python 9.py
python 10.py
```

---

## ⚙️ Chi tiết các Bước và Tham số cấu hình (Parameters)

### Bước 1: `1.py` - Dọn dẹp JSON (Data Cleanup)
**Chức năng:** Tiền xử lý dữ liệu từ file `layout.json` ban đầu. Thuật toán loại bỏ các block rác (`preproc_blocks`), gom dồn các đoạn chữ nhỏ lẻ (spans/lines) thành một chuỗi `content` duy nhất cho dễ xử lý. Nếu một block chứa cả chữ và ảnh, thuật toán ưu tiên giữ lại đường dẫn ảnh (`image_path`).
- Đầu vào: `layout.json`
- Đầu ra: `1.json`

### Bước 2: `2.py` - Tạo khung xương (Skeleton Extraction)
**Chức năng:** Trích xuất toàn bộ văn bản ra một file `2.txt` độc lập để phục vụ việc dịch thuật. Đồng thời, đánh dấu vị trí của từng đoạn văn bản trong file `1.json` bằng các con số ID như `[1]`, `[2]` để tạo thành một bộ khung xương (`2.json`).
- Đầu vào: `1.json`
- Đầu ra: `2.txt` (Text gốc để dịch), `2.json` (Bộ khung xương)

### Bước 3: `3.1.py` & `3.2.py` - Dịch thuật Tự động (AI Translation)
**Chức năng:** Cắt file `2.txt` thành các phần nhỏ (batch) và gọi API của LLM để dịch tự động sang Tiếng Việt. Giữ nguyên các ID đánh dấu `[1]`, `[2]` ở cuối mỗi dòng.
- **3.1.py**: Dùng cho DeepSeek/OpenAI (general API).
- **3.2.py**: Dùng riêng cho nền tảng NVIDIA NIM (được tinh chỉnh Rate limit và token cap).
- Đầu vào: `2.txt`
- Đầu ra: `3.txt` (Text đã dịch)
- **Tham số chính:**
  - Cần tinh chỉnh cấu hình Token và API Key môi trường (`NVIDIA_API_KEY` nếu dùng 3.2.py).
**Lưu ý**
- ưu tiên 3.1 dịch thuật ổn định hơn

### Bước 4: `4.py` - Lấp đầy khung xương (Translation Merger)
**Chức năng:** Bơm nội dung từ file dịch `3.txt` trở lại vào bộ khung `2.json`. Đặc biệt, có tích hợp cơ chế sửa lỗi: nếu LLM dịch thiếu một vài dòng (marker biến mất), thuật toán sẽ tự động cắt đôi dòng liền trước đó để bù đắp vào chỗ khuyết, tránh làm gãy luồng tài liệu.
- Đầu vào: `2.json`, `3.txt`
- Đầu ra: `4.json`

### Bước 5: `5.py` - Phục hồi Bounding Box (Kéo giãn không gian)
**Chức năng:** Xử lý tình trạng chữ quá to hoặc bị tràn do bounding box ban đầu quá chật hẹp. Thuật toán sẽ tự động giãn rộng bounding box theo các hướng để tạo thêm không gian cho nội dung.
- Đầu vào: `4.json`
- Đầu ra: `5.json`

### Bước 6: `6.py` - Công cụ Giả lập Nhồi chữ (Font Size Estimator)
**Chức năng:** Tính toán cỡ chữ (font-size) tối đa có thể nhét vừa vào bounding box thông qua thuật toán Tìm kiếm nhị phân (Binary Search). Xử lý chính xác các thành phần như `list` (căn lề, bullet), `code` (monospace, xuống dòng), và `text` thông thường.
- Đầu vào: `5.json`
- Đầu ra: `6.json`
- **Tham số chính:**
  - `SCALE = 1.5`: Tỷ lệ phóng to từ PDF point sang CSS pixel.

### Bước 7: `7.py` - Thuật toán San sẻ Nội dung (Content Balancing)
**Chức năng:** Khắc phục tình trạng các ô chữ "bé tí" nhưng chứa quá nhiều text khiến cỡ chữ bị tụt xuống quá nhỏ. Thuật toán dùng cơ chế **Multi-pass** để tự động bốc tách một nửa số từ ở ô chật chội và dán nối mượt mà sang ô lân cận rộng rãi hơn, lặp lại cho đến khi mọi ô đều đạt chuẩn.
- Đầu vào: `6.json`
- Đầu ra: `7.json`
- **Tham số chính:**
  - `MIN_FONT_SIZE = 12`: Ngưỡng kích thước chữ tối thiểu. Bất cứ block văn bản nào có cỡ chữ `< 12` đều sẽ kích hoạt quá trình san sẻ sang hàng xóm để được nâng cỡ chữ lên.

### Bước 8: `8.py` - Chuẩn hóa Kích thước chữ (Font Size Normalization)
**Chức năng:** Cắt bỏ sự lồi lõm của tài liệu bằng cách loại bỏ các đoạn chữ phình to bất thường hoặc quá bé rác. Hệ thống tách làm 2 luồng riêng biệt: Tiêu đề (`title`) và Văn bản (`body`). Tính toán giá trị trung bình dựa trên **trọng số số lượng từ**, sử dụng thuật toán **Trimmed Mean** để lọc nhiễu.
- Đầu vào: `7.json`
- Đầu ra: `8.json`
- **Tham số chính:**
  - `TITLE_CONFIDENCE_LEVEL = 0.90`: Độ tin cậy cho tiêu đề. Hệ thống sẽ **cắt bỏ đáy** (loại bỏ 10% các từ có kích thước bé nhất) và tính trung bình phần to còn lại (từ 10% đến 100%) để tránh bị tụt size do nhiễu rác.
  - `BODY_CONFIDENCE_LEVEL = 0.90`: Độ tin cậy cho văn bản. Hệ thống sẽ **cắt ngọn** (loại bỏ 10% các từ có kích thước to khổng lồ nhất) và tính trung bình phần bé còn lại (từ 0% đến 90%) để tránh bị bóp méo khung chữ.

### Bước 9: `9.py` - Trình xuất HTML tĩnh (HTML Renderer)
**Chức năng:** Kết hợp dữ liệu văn bản, tọa độ absolute và kích thước chữ đã tính toán để sinh ra file HTML. Tích hợp KaTeX để render hoàn hảo các công thức toán học nội suy.
- Đầu vào: `8.json`
- Đầu ra: `9.html`
- **Tham số chính:**
  - `DEBUG_COLORS`: Bảng màu viền cho từng loại block khi bật chế độ Debug trên trình duyệt. (Ở chế độ bình thường, viền được làm trong suốt).
  - Khả năng Debug UI: Mở file `.html` trên trình duyệt và bấm nút "Debug" ở góc phải để hiện/ẩn viền block.

### Bước 10: `10.py` - Kết xuất PDF (PDF Exporter)
**Chức năng:** Sử dụng trình duyệt ảo Chromium (Playwright) để tải file HTML, chờ đợi công thức toán (KaTeX) render hoàn tất, sau đó in ra file PDF chuẩn kích thước gốc đến từng pixel.
- Đầu vào: `9.html`
- Đầu ra: `10.pdf`
- **Yêu cầu hệ thống:** Cần cài đặt Playwright (`pip install playwright` và `playwright install chromium`).

---

## 🛠 Lời khuyên
- Các tham số như `MIN_FONT_SIZE` trong `7.py`, hay `TITLE_CONFIDENCE_LEVEL` / `BODY_CONFIDENCE_LEVEL` trong `8.py` là cực kỳ quan trọng để thay đổi hành vi hiển thị của tài liệu. Nếu thấy phần thân chữ trung bình vẫn quá to, hãy giảm `BODY_CONFIDENCE_LEVEL` xuống `0.80` để gạt bỏ nhiều nhiễu hơn.
- Nếu bạn chỉ muốn tinh chỉnh ở khâu xuất PDF, bạn chỉ việc chạy lại `python 10.py` mà không cần chạy lại các bước giả lập.
