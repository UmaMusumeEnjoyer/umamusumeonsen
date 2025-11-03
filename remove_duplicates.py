"""
Script để xóa các URL trùng lặp dựa trên tên nhân vật
Giữ lại URL đầu tiên cho mỗi tên nhân vật
"""

def remove_duplicate_urls(input_file, output_file):
    # Dictionary để theo dõi các tên nhân vật đã gặp
    seen_characters = {}
    unique_urls = []
    
    # Đọc file
    with open(input_file, 'r', encoding='utf-8') as f:
        urls = f.readlines()
    
    for url in urls:
        url = url.strip()
        if not url:
            continue
            
        # Lấy tên nhân vật từ URL (phần sau dấu "-" cuối cùng)
        # Ví dụ: .../100101-special-week -> special-week
        character_name = url.split('/')[-1].split('-', 1)[-1]
        
        # Nếu chưa gặp nhân vật này, thêm vào danh sách
        if character_name not in seen_characters:
            seen_characters[character_name] = url
            unique_urls.append(url)
            print(f"Giữ lại: {url} (Nhân vật: {character_name})")
        else:
            print(f"Bỏ qua (trùng lặp): {url} (Nhân vật: {character_name})")
    
    # Ghi file mới
    with open(output_file, 'w', encoding='utf-8') as f:
        for url in unique_urls:
            f.write(url + '\n')
    
    print(f"\n{'='*60}")
    print(f"Tổng số URL ban đầu: {len([u for u in urls if u.strip()])}")
    print(f"Số URL sau khi xóa trùng: {len(unique_urls)}")
    print(f"Đã xóa: {len([u for u in urls if u.strip()]) - len(unique_urls)} URL trùng lặp")
    print(f"Kết quả đã được lưu vào: {output_file}")
    print(f"{'='*60}")

if __name__ == "__main__":
    input_file = "character_urls.txt"
    output_file = "character_urls.txt"
    
    remove_duplicate_urls(input_file, output_file)
