from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

def crawl_character_urls():
    """
    Crawl tất cả URL của các nhân vật từ trang gametora.com
    """
    # URL của trang chứa danh sách nhân vật
    base_url = "https://gametora.com"
    characters_page = "https://gametora.com/umamusume/characters"
    
    # Cấu hình Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Chạy ẩn trình duyệt
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    driver = None
    
    try:
        # Khởi tạo Chrome driver
        print(f"Đang khởi động trình duyệt...")
        driver = webdriver.Chrome(options=chrome_options)
        
        # Truy cập trang
        print(f"Đang truy cập: {characters_page}")
        driver.get(characters_page)
        
        # Đợi trang load (đợi các thẻ nhân vật xuất hiện)
        print("Đang đợi trang tải...")
        time.sleep(5)  # Đợi JavaScript render
        
        # Scroll xuống để load thêm nội dung nếu có lazy loading
        print("Đang scroll để load thêm nội dung...")
        last_height = driver.execute_script("return document.body.scrollHeight")
        for i in range(5):  # Scroll 5 lần
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            print(f"Scroll lần {i+1}: height = {new_height}")
            if new_height == last_height:
                break
            last_height = new_height
        
        # Lấy HTML sau khi JavaScript đã render
        page_source = driver.page_source
        
        # Parse HTML
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Tìm tất cả các thẻ <a> có href chứa /umamusume/characters/
        print("Đang tìm kiếm tất cả link nhân vật...")
        all_links = soup.find_all('a', href=True)
        
        print(f"Tổng số link tìm thấy: {len(all_links)}")
        
        # Lọc các link nhân vật
        character_links = []
        for link in all_links:
            href = link.get('href', '')
            if '/umamusume/characters/' in href and href != '/umamusume/characters':
                character_links.append(link)
        
        print(f"Số link nhân vật tìm thấy: {len(character_links)}")
        
        # Lấy danh sách URL
        urls = []
        for link in character_links:
            href = link.get('href')
            if href:
                # Tạo URL đầy đủ
                full_url = base_url + href if href.startswith('/') else href
                urls.append(full_url)
        
        # Loại bỏ URL trùng lặp
        urls = list(set(urls))
        urls.sort()
        
        print(f"Đã tìm thấy {len(urls)} URL nhân vật")
        
        # Ghi vào file
        output_file = "character_urls.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            for url in urls:
                f.write(url + '\n')
        
        print(f"Đã lưu {len(urls)} URL vào file: {output_file}")
        
        # In ra một vài URL mẫu
        print("\nMột số URL mẫu:")
        for url in urls[:5]:
            print(f"  - {url}")
        
        return urls
        
    except Exception as e:
        print(f"Lỗi: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        # Đóng trình duyệt
        if driver:
            print("Đang đóng trình duyệt...")
            driver.quit()


if __name__ == "__main__":
    print("=== BẮT ĐẦU CRAWL DỮ LIỆU ===\n")
    crawl_character_urls()
    print("\n=== HOÀN THÀNH ===")
