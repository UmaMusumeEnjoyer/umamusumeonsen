import json
import re
import os

# --- Tên file cấu hình ---
CHARACTER_DATA_FILE = "character_data.json" # File data từ script crawl
CONDITIONS_FILE = "conditions.json"       # File điều kiện mới của bạn
OUTPUT_FILE = "filtered_characters.json"  # File kết quả

def parse_time_string(time_str):
    """
    Phân tích chuỗi thời gian từ JSON của nhân vật.
    Input: "Turn 27 (previous + 14) (Classic Class, Early February)"
    Output: {'class': 'Classic', 'half': 'Early', 'month': 'February'}
    """
    match = re.search(
        r'\((Junior|Classic|Senior) Class, (Early|Late) (January|February|March|April|May|June|July|August|September|October|November|December)\)', 
        time_str
    )
    if match:
        return {
            "class": match.group(1),
            "half": match.group(2),  # "Early" or "Late"
            "month": match.group(3)
        }
    return None

def is_time_in_period(parsed_time, period_string):
    """
    Kiểm tra xem một thời điểm (đã phân tích) có nằm trong khoảng thời gian (từ điều kiện) không.
    """
    month = parsed_time["month"]
    half = parsed_time["half"]
    char_class = parsed_time["class"]

    if period_string == "December (Junior)":
        return month == "December" and char_class == "Junior"
    
    if period_string == "May (second half) to July (first half) (Classic)":
        if char_class != "Classic": 
            return False
        if month == "May" and half == "Late": 
            return True
        if month == "June": # Bất kể Early/Late
            return True
        if month == "July" and half == "Early": 
            return True
        return False
    
    ### THAY ĐỔI 1: "December" CHỈ ĐẾM JUNIOR CLASS ###
    if period_string == "December": # Yêu cầu mới: Chỉ áp dụng cho Junior
        return month == "December" and char_class == "Junior"
    
    if period_string == "Classic (start) to November (first half) (Classic)": # Dùng cho ID 7
        if char_class != "Classic": 
            return False
        # Bao gồm tất cả các tháng của Classic trước November
        classic_months = ["January","February", "March", "April", "May", "June", "July", "August", "September", "October"]
        if month in classic_months: 
            return True
        if month == "November" and half == "Early": 
            return True
        return False

    ### THAY ĐỔI 2: XỬ LÝ LOGIC CLASSIC -> SENIOR ###
    if period_string == "November (second half) to January (first half)":
        # 1. Nửa cuối Tháng 11 (thuộc Classic Class)
        if month == "November" and half == "Late" and char_class == "Classic":
            return True
        # 2. Cả Tháng 12 (thuộc Classic Class)
        if month == "December" and char_class == "Classic":
            return True
        # 3. Nửa đầu Tháng 1 (thuộc Senior Class)
        if month == "January" and half == "Early" and char_class == "Senior":
            return True
        return False # Không khớp với logic trên

    print(f"  [Cảnh báo] Không nhận dạng được khoảng thời gian: {period_string}")
    return False

def check_character(character, rules, logic):
    """
    Kiểm tra một nhân vật xem có thỏa mãn các quy tắc (rules) hay không,
    dựa trên logic 'AND' hoặc 'OR'.
    """
    
    # 1. Lấy tất cả thời gian đua (objectives) của nhân vật
    all_time_strings = (
        character.get('junior', {}).get('time', []) +
        character.get('classic', {}).get('time', []) +
        character.get('senior', {}).get('time', [])
    )
    
    # 2. Phân tích các chuỗi thời gian đó
    parsed_times = [parse_time_string(t) for t in all_time_strings if parse_time_string(t)]

    # 3. Duyệt qua từng quy tắc và xem nó có ĐÚNG hay SAI
    rule_results = [] # Sẽ lưu [True, False, True] v.v.
    
    for rule in rules:
        period = rule['time_period']
        condition = rule['condition']

        # Đếm số lượng race thỏa mãn khoảng thời gian
        count = 0
        for p_time in parsed_times:
            if is_time_in_period(p_time, period):
                count += 1
        
        # 4. Kiểm tra điều kiện (condition) của quy tắc này
        rule_met = False
        if condition == "at_least_one": # 1+
            rule_met = (count >= 1)
        elif condition == "none": # 0
            rule_met = (count == 0)
        elif condition == "one_or_less": # 0, 1
            rule_met = (count <= 1)
        elif condition == "two_or_more": # 2+
            rule_met = (count >= 2)
        elif condition == "two_or_fewer": # 0, 1, 2
            rule_met = (count <= 2)
        elif condition == "three_or_more": # 3+ (Cho ID 4)
            rule_met = (count >= 3)
        else:
            print(f"  [Lỗi] Không rõ điều kiện: {condition}")
            rule_met = False # Coi như thất bại nếu không hiểu điều kiện
        
        rule_results.append(rule_met)

    # 5. Áp dụng logic tổng (AND / OR)
    if not rule_results:
        return True # Nếu không có quy tắc nào, coi như thỏa mãn

    if logic == "AND":
        # all() trả về True nếu TẤT CẢ item trong list là True
        return all(rule_results)
    elif logic == "OR":
        # any() trả về True nếu CÓ ÍT NHẤT MỘT item trong list là True
        return any(rule_results)

    print(f"  [Lỗi] Không rõ logic: {logic}")
    return False

def main():
    """Hàm chính để chạy bộ lọc."""
    
    # Tải dữ liệu nhân vật
    try:
        with open(CHARACTER_DATA_FILE, 'r', encoding='utf-8') as f:
            characters = json.load(f)
        print(f"✅ Đã tải {len(characters)} nhân vật từ '{CHARACTER_DATA_FILE}'")
    except FileNotFoundError:
        print(f"❌ Lỗi: Không tìm thấy file '{CHARACTER_DATA_FILE}'.")
        return
    except json.JSONDecodeError:
        print(f"❌ Lỗi: File '{CHARACTER_DATA_FILE}' bị hỏng hoặc không phải JSON.")
        return
    except Exception as e:
        print(f"❌ Lỗi khi đọc {CHARACTER_DATA_FILE}: {e}")
        return

    # Tải dữ liệu điều kiện
    try:
        with open(CONDITIONS_FILE, 'r', encoding='utf-8') as f:
            conditions_data = json.load(f)
        conditions = conditions_data.get("filter_conditions", [])
        print(f"✅ Đã tải {len(conditions)} điều kiện lọc từ '{CONDITIONS_FILE}'")
    except FileNotFoundError:
        print(f"❌ Lỗi: Không tìm thấy file '{CONDITIONS_FILE}'.")
        return
    except Exception as e:
        print(f"❌ Lỗi khi đọc {CONDITIONS_FILE}: {e}")
        return

    # Khởi tạo đối tượng kết quả
    filtered_results = {}

    print("\n🚀 Bắt đầu quá trình lọc...")

    # Duyệt qua từng điều kiện
    for condition in conditions:
        condition_id = str(condition['id'])
        
        rules = condition.get('rules', [])
        logic = condition.get('logic', 'AND') # Mặc định là 'AND' nếu không được chỉ định
        
        print(f"\n--- 🔎 Đang lọc cho Điều kiện ID {condition_id} (Logic: {logic}) ---")
        
        filtered_results[condition_id] = []
        
        match_count = 0
        # Duyệt qua từng nhân vật
        for character in characters:
            
            if check_character(character, rules, logic):
                # Nếu thỏa mãn, thêm tên và avatar vào kết quả
                filtered_results[condition_id].append({
                    "tên": character.get('tên', 'N/A'),
                    "avatar": character.get('avatar', 'N/A')
                })
                match_count += 1
        
        print(f"-> Đã tìm thấy {match_count} nhân vật phù hợp.")

    # Lưu kết quả
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(filtered_results, f, indent=4, ensure_ascii=False)
        print(f"\n🎉 Hoàn tất! Đã lưu kết quả lọc vào '{OUTPUT_FILE}'")
    except IOError as e:
        print(f"❌ Lỗi: Không thể ghi file {OUTPUT_FILE}. {e}")
    except Exception as e:
        print(f"❌ Lỗi không xác định khi lưu file: {e}")

# Chạy chương trình
if __name__ == "__main__":
    main()