# 🏇 Uma Musume Character Filter

Dự án web crawling và lọc nhân vật từ game **Uma Musume Pretty Derby** dựa trên điều kiện về thời gian đua (race objectives). Thu thập dữ liệu từ [GameTora](https://gametora.com/umamusume/characters) và tạo trang web hiển thị nhân vật phù hợp với các điều kiện được định nghĩa trước.

---

## 📋 Mục Lục

- [Tổng Quan](#-tổng-quan)
- [Tính Năng](#-tính-năng)
- [Cấu Trúc Dự Án](#-cấu-trúc-dự-án)
- [Cài Đặt](#-cài-đặt)
- [Hướng Dẫn Sử Dụng](#-hướng-dẫn-sử-dụng)
- [File Cấu Hình](#-file-cấu-hình)
- [Công Nghệ Sử Dụng](#-công-nghệ-sử-dụng)

---

## 🎯 Tổng Quan

Dự án này giúp người chơi Uma Musume tìm kiếm nhân vật phù hợp dựa trên lịch trình đua (race schedule) của họ. Hệ thống crawl toàn bộ dữ liệu nhân vật từ GameTora, phân tích thời gian các cuộc đua mục tiêu (objectives), sau đó lọc theo các điều kiện phức tạp về khoảng thời gian.

### Workflow
```
1. Crawl URLs      → 2. Crawl Details  → 3. Filter Data   → 4. Generate HTML
   (crawl_links)      (character_crawl)    (filter_chars)     (generate_html)
```

---

## ✨ Tính Năng

- **🔍 Web Crawling**: Thu thập tự động dữ liệu từ 200+ nhân vật
- **🎯 Lọc Thông Minh**: Lọc nhân vật theo điều kiện phức tạp về thời gian đua
- **🌐 Giao Diện Web**: Hiển thị kết quả trên trang HTML tương tác
- **🔎 Tìm Kiếm**: Tìm kiếm nhân vật theo tên
- **📊 Chi Tiết Modal**: Xem thông tin chi tiết và điều kiện phù hợp khi click vào nhân vật
- **🖼️ Hình Ảnh**: Hiển thị avatar và hình ảnh điều kiện

---

## 📁 Cấu Trúc Dự Án

```
GaiNguaOnsen/
│
├── 🐍 Python Scripts
│   ├── crawl_links.py          # Crawl danh sách URL nhân vật
│   ├── character_crawl.py      # Crawl chi tiết từng nhân vật
│   ├── remove_duplicates.py    # Xóa URL trùng lặp
│   ├── filter_characters.py    # Lọc nhân vật theo điều kiện
│   └── generate_html.py        # Tạo trang web HTML
│
├── 📄 Data Files
│   ├── character_urls.txt      # Danh sách URL đã crawl
│   ├── character_data.json     # Dữ liệu chi tiết nhân vật
│   ├── conditions.json         # Định nghĩa điều kiện lọc
│   └── filtered_characters.json # Kết quả sau khi lọc
│
├── 🌐 Web Files
│   ├── index.html              # Trang web chính
│   ├── style.css               # File CSS
│   └── pictures/               # Hình ảnh điều kiện
│
└── 📚 Documentation
    └── README.md               # File này
```

---

## 🚀 Cài Đặt

### Yêu Cầu Hệ Thống

- Python 3.8+
- Google Chrome Browser
- ChromeDriver (tương thích với phiên bản Chrome)

### Cài Đặt Thư Viện

```powershell
# Tạo virtual environment
python -m venv venv

# Kích hoạt virtual environment
.\venv\Scripts\Activate.ps1

# Cài đặt các thư viện cần thiết
pip install requests beautifulsoup4 selenium
```

### Cài Đặt ChromeDriver

1. Kiểm tra phiên bản Chrome: `chrome://version`
2. Tải ChromeDriver tương ứng: https://chromedriver.chromium.org/
3. Đặt ChromeDriver vào PATH hoặc cùng thư mục dự án

---

## 📖 Hướng Dẫn Sử Dụng

### Bước 1: Crawl Danh Sách URL

```powershell
python crawl_links.py
```

**Output**: `character_urls.txt` - Danh sách URL của tất cả nhân vật

### Bước 2: Xóa URL Trùng Lặp (Tùy Chọn)

```powershell
python remove_duplicates.py
```

Script này sẽ xóa các URL của cùng một nhân vật (chỉ giữ lại 1 version).

### Bước 3: Crawl Chi Tiết Nhân Vật

```powershell
python character_crawl.py
```

**Output**: `character_data.json` - Dữ liệu chi tiết bao gồm:
- Tên nhân vật
- Avatar
- Race objectives (Junior/Classic/Senior)
- Thời gian các cuộc đua

⏱️ **Lưu ý**: Quá trình này có thể mất 30-60 phút tùy số lượng nhân vật.

### Bước 4: Lọc Nhân Vật Theo Điều Kiện

```powershell
python filter_characters.py
```

**Input**: 
- `character_data.json` - Dữ liệu nhân vật
- `conditions.json` - Điều kiện lọc

**Output**: `filtered_characters.json` - Kết quả lọc theo từng ID điều kiện

### Bước 5: Tạo Trang Web

```powershell
python generate_html.py
```

**Output**: `index.html` - Trang web hiển thị kết quả

Mở file `index.html` trong trình duyệt để xem kết quả!

---

## ⚙️ File Cấu Hình

### `conditions.json`

File này định nghĩa các điều kiện lọc nhân vật. Cấu trúc:

```json
{
  "filter_conditions": [
    {
      "id": 1,
      "logic": "AND",
      "description": "Mô tả điều kiện",
      "rules": [
        {
          "target": "target_race",
          "time_period": "December (Junior)",
          "condition": "at_least_one"
        }
      ]
    }
  ]
}
```

#### Các Loại Condition

- `at_least_one`: Ít nhất 1 cuộc đua (≥1)
- `none`: Không có cuộc đua nào (=0)
- `one_or_less`: Tối đa 1 cuộc đua (≤1)
- `two_or_more`: Ít nhất 2 cuộc đua (≥2)
- `two_or_fewer`: Tối đa 2 cuộc đua (≤2)
- `three_or_more`: Ít nhất 3 cuộc đua (≥3)

#### Các Khoảng Thời Gian Hỗ Trợ

- `"December (Junior)"` - Tháng 12 Junior Class
- `"December"` - Tháng 12 (chỉ Junior)
- `"May (second half) to July (first half) (Classic)"` - Nửa cuối tháng 5 đến đầu tháng 7 (Classic)
- `"November (second half) to January (first half)"` - Nửa cuối tháng 11 (Classic) đến đầu tháng 1 (Senior)
- `"Classic (start) to November (first half) (Classic)"` - Từ đầu Classic đến nửa đầu tháng 11

#### Logic

- `"AND"`: Tất cả các rules phải thỏa mãn
- `"OR"`: Chỉ cần 1 rule thỏa mãn

---

## 🛠️ Công Nghệ Sử Dụng

### Backend
- **Python 3**: Ngôn ngữ lập trình chính
- **Selenium**: Web automation và crawling JavaScript-rendered pages
- **BeautifulSoup4**: Parse HTML
- **Requests**: HTTP requests

### Frontend
- **HTML5**: Cấu trúc trang web
- **CSS3**: Styling
- **JavaScript (Vanilla)**: Tương tác và lọc dữ liệu

### Data Format
- **JSON**: Lưu trữ và trao đổi dữ liệu
- **UTF-8**: Encoding để hỗ trợ tiếng Việt và tiếng Nhật

---

## 📝 Lưu Ý

1. **ChromeDriver**: Đảm bảo ChromeDriver tương thích với phiên bản Chrome của bạn
2. **Rate Limiting**: Script có built-in delays để tránh bị ban IP
3. **Headless Mode**: Crawling chạy ở chế độ headless (không hiển thị trình duyệt)
4. **Incremental Save**: Dữ liệu được lưu liên tục trong quá trình crawl để tránh mất dữ liệu

---

## 🤝 Đóng Góp

Mọi đóng góp đều được chào đón! Hãy tạo issue hoặc pull request nếu bạn có ý tưởng cải tiến.

---

## 📄 License

Dự án này được tạo ra cho mục đích học tập và cá nhân. Dữ liệu được crawl từ GameTora thuộc quyền sở hữu của họ.

---

## 🙏 Cảm Ơn

- **GameTora**: Nguồn dữ liệu chính thức
- **Uma Musume Pretty Derby**: Game gốc của Cygames

---

**Được tạo với ❤️ bởi UmaMusumeEnjoyer**
