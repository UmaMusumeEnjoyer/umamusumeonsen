import os
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

# --- CÁC HẰNG SỐ ---
BASE_URL = "https://gametora.com"
INPUT_FILE = "character_urls.txt"
OUTPUT_FILE = "character_data.json"
WAIT_TIMEOUT = 10 # Thời gian tối đa (giây) để đợi một trang load

def setup_driver():
    """Cấu hình và khởi tạo Chrome WebDriver."""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        print(f"Lỗi khi khởi tạo WebDriver: {e}")
        print("Hãy đảm bảo bạn đã cài đặt ChromeDriver và nó tương thích với phiên bản Chrome của bạn.")
        return None

def read_urls_from_file(filename):
    """Đọc danh sách URL từ file .txt."""
    if not os.path.exists(filename):
        print(f"Lỗi: Không tìm thấy file '{filename}'.")
        print("Vui lòng chạy script crawl URL đầu tiên để tạo file này.")
        return []
        
    with open(filename, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]
    
    print(f"Đã đọc {len(urls)} URL từ '{filename}'")
    return urls

def parse_character_page(soup, page_url):
    """Bóc tách dữ liệu chi tiết từ trang của một nhân vật."""
    
    # 1. Lấy tên nhân vật
    name_element = soup.select_one("div.characters_infobox_character_name__Cm6EY a")
    name = name_element.text.strip() if name_element else "Không tìm thấy tên"

    # 2. Lấy avatar
    avatar_element = soup.select_one("img[src*='/images/umamusume/characters/chara_stand_']")
    avatar_src = avatar_element['src'] if avatar_element else ""
    avatar_url = BASE_URL + avatar_src if avatar_src.startswith('/') else avatar_src

    # 3. Lấy Objectives
    objective_elements = soup.select("div.characters_objective__8UMWo")
    
    junior_data = {"race": [], "time": []}
    classic_data = {"race": [], "time": []}
    senior_data = {"race": [], "time": []}

    for obj in objective_elements:
        text_box = obj.select_one("div.characters_objective_text__n0G1a")
        if not text_box:
            continue
            
        divs = text_box.find_all('div', recursive=False)
        
        if len(divs) < 3: 
            continue
            
        try:
            title = divs[0].get_text(strip=True)
            turn = divs[1].get_text(strip=True)
            period_text = divs[2].get_text(strip=True)
            details = divs[3].get_text(strip=True) if len(divs) > 3 else ""
            
            race_str = f"{title} ({details})" if details else title
            time_str = f"{turn} ({period_text})"
            
            if "Junior Class" in period_text:
                junior_data["race"].append(race_str)
                junior_data["time"].append(time_str)
            elif "Classic Class" in period_text:
                classic_data["race"].append(race_str)
                classic_data["time"].append(time_str)
            elif "Senior Class" in period_text:
                senior_data["race"].append(race_str)
                senior_data["time"].append(time_str)
                
        except Exception as e:
            print(f"  [Lỗi nhỏ] Lỗi khi parse một objective: {e}")

    # 4. Xây dựng JSON output
    character_json = {
        "tên": name,
        "avatar": avatar_url,
        "số race": len(objective_elements), # Tổng số objectives
        "junior": junior_data,
        "classic": classic_data,
        "senior": senior_data,
        "nguồn": page_url # Thêm nguồn để dễ debug
    }
    
    return character_json

def append_data_to_json(data_item, filename):
    """
    Nối một item dữ liệu vào file JSON.
    Đọc danh sách hiện có, thêm item mới, và ghi lại.
    """
    data_list = []
    try:
        # Đọc file trước nếu nó tồn tại và không rỗng
        if os.path.exists(filename) and os.path.getsize(filename) > 0:
            with open(filename, 'r', encoding='utf-8') as f:
                data_list = json.load(f)
                # Đảm bảo dữ liệu đọc được là một list
                if not isinstance(data_list, list):
                    print(f"  [CẢNH BÁO] File {filename} không chứa list. Bắt đầu lại với list rỗng.")
                    data_list = []
    except (json.JSONDecodeError):
        print(f"  [CẢNH BÁO] File {filename} bị lỗi JSON. Bắt đầu lại với list rỗng.")
        data_list = [] # File bị hỏng, bắt đầu lại
    except FileNotFoundError:
        pass # File chưa tồn tại, sẽ được tạo ở bước ghi
    except Exception as e:
        print(f"  [LỖI] Lỗi khi đọc {filename}: {e}")
        return # Không tiếp tục nếu không đọc được

    # Thêm dữ liệu mới
    data_list.append(data_item)

    # Ghi lại toàn bộ danh sách
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data_list, f, indent=4, ensure_ascii=False)
    except IOError as e:
        print(f"  [LỖI NGHIÊM TRỌNG] Không thể ghi vào file {filename}: {e}")


def main():
    """Hàm chính điều khiển luồng crawl."""
    print("=== BẮT ĐẦU CRAWL DỮ LIỆU CHI TIẾT ===\n")
    
    # Đọc URL từ file
    urls_to_crawl = read_urls_from_file(INPUT_FILE)
    if not urls_to_crawl:
        print("\n=== KẾT THÚC (Không có URL để crawl) ===")
        return

    # Khởi tạo driver
    driver = setup_driver()
    if not driver:
        print("\n=== KẾT THÚC (Lỗi Driver) ===")
        return
        
    # *** THAY ĐỔI: Khởi tạo file JSON rỗng ban đầu ***
    # Ghi một danh sách rỗng để khởi tạo file (hoặc xóa file cũ)
    try:
        print(f"Khởi tạo/Làm rỗng file output: {OUTPUT_FILE}")
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, indent=4)
    except IOError as e:
        print(f"[LỖI] Không thể khởi tạo file {OUTPUT_FILE}: {e}")
        driver.quit()
        return

    # *** THAY ĐỔI: Bỏ list 'all_character_data' ***
    
    total_urls = len(urls_to_crawl)
    success_count = 0
    
    print(f"\nChuẩn bị crawl {total_urls} trang nhân vật...")
    
    try:
        for i, url in enumerate(urls_to_crawl):
            print(f"\nĐang crawl {i+1}/{total_urls}: {url}")
            
            try:
                # Truy cập trang
                driver.get(url)
                
                # Đợi cho đến khi phần objectives xuất hiện
                WebDriverWait(driver, WAIT_TIMEOUT).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.characters_objective_box__6g9it"))
                )
                
                time.sleep(0.5)
                
                # Lấy source HTML và parse
                page_source = driver.page_source
                soup = BeautifulSoup(page_source, 'html.parser')
                
                # Bóc tách dữ liệu
                data = parse_character_page(soup, url)
                
                # *** THAY ĐỔI: Lưu ngay lập tức vào file ***
                append_data_to_json(data, OUTPUT_FILE)
                
                print(f"  -> Hoàn tất và ĐÃ LƯU: {data['tên']}")
                success_count += 1

            except Exception as e:
                print(f"  [LỖI] Không thể crawl {url}: {e}")
                # Tiếp tục với URL tiếp theo

    except Exception as e:
        print(f"Một lỗi nghiêm trọng xảy ra (có thể do driver): {e}")
    finally:
        # Luôn đóng trình duyệt
        print("\nĐang đóng trình duyệt...")
        driver.quit()

    # *** THAY ĐỔI: Bỏ phần lưu tổng cuối cùng ***

    print("\n=== HOÀN THÀNH ===")
    print(f"Đã crawl và lưu thành công {success_count}/{total_urls} nhân vật.")
    print(f"Dữ liệu đã được lưu liên tục vào file: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()