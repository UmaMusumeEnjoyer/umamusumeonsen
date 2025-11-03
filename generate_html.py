import json
import os

# --- Tên file cấu hình ---
CHARACTER_DATA_FILE = "character_data.json"   # Đọc để lấy TẤT CẢ nhân vật
FILTERED_DATA_FILE = "filtered_characters.json" # Đọc để lấy KẾT QUẢ LỌC
CONDITIONS_FILE = "conditions.json"             # Đọc để lấy MÔ TẢ ĐIỀU KIỆN
OUTPUT_HTML_FILE = "index.html"                 # File HTML đầu ra
CONDITION_IMAGES_DIR = "pictures"               # Thư mục chứa ảnh điều kiện


def load_all_characters():
    """Tải danh sách TÊN và AVATAR của tất cả nhân vật."""
    try:
        with open(CHARACTER_DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return [{"tên": char.get("tên"), "avatar": char.get("avatar")} for char in data]
    except FileNotFoundError:
        print(f"❌ Lỗi: Không tìm thấy '{CHARACTER_DATA_FILE}'.")
        return []
    except Exception as e:
        print(f"❌ Lỗi khi đọc {CHARACTER_DATA_FILE}: {e}")
        return []


def build_character_conditions_map():
    """Đảo ngược filtered_characters.json → {Tên NV: [ID điều kiện]}"""
    char_map = {}
    try:
        with open(FILTERED_DATA_FILE, 'r', encoding='utf-8') as f:
            filtered_data = json.load(f)

        for condition_id, characters in filtered_data.items():
            for char in characters:
                char_name = char.get('tên')
                if char_name:
                    if char_name not in char_map:
                        char_map[char_name] = []
                    char_map[char_name].append(int(condition_id))

        for char_name in char_map:
            char_map[char_name].sort()

        return char_map

    except FileNotFoundError:
        print(f"❌ Lỗi: Không tìm thấy '{FILTERED_DATA_FILE}'.")
        return {}
    except Exception as e:
        print(f"❌ Lỗi khi đọc {FILTERED_DATA_FILE}: {e}")
        return {}


def load_conditions_info():
    """Tải ID và mô tả của các điều kiện."""
    conditions_map = {}
    try:
        with open(CONDITIONS_FILE, 'r', encoding='utf-8') as f:
            conditions_data = json.load(f)

        for condition in conditions_data.get("filter_conditions", []):
            conditions_map[str(condition['id'])] = condition.get('description', 'Không có mô tả.')

        return conditions_map
    except FileNotFoundError:
        print(f"❌ Lỗi: Không tìm thấy '{CONDITIONS_FILE}'.")
        return {}
    except Exception as e:
        print(f"❌ Lỗi khi đọc {CONDITIONS_FILE}: {e}")
        return {}


def generate_html_page():
    """Tạo trang HTML tĩnh với JavaScript nhúng."""
    print("🚀 Bắt đầu tạo trang HTML...")

    all_characters = load_all_characters()
    character_conditions_map = build_character_conditions_map()
    conditions_info_map = load_conditions_info()

    if not all_characters:
        print("❌ Không có dữ liệu nhân vật. Hủy tạo file HTML.")
        return

    js_all_characters = json.dumps(all_characters, ensure_ascii=False)
    js_char_conditions_map = json.dumps(character_conditions_map, ensure_ascii=False)
    js_conditions_info_map = json.dumps(conditions_info_map, ensure_ascii=False)
    js_condition_images_dir = json.dumps(CONDITION_IMAGES_DIR)

    html_content = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Danh Sách Nhân Vật Umamusume</title>
    <link rel="stylesheet" href="style.css">
    <style>
        .character-item {{
            display: inline-block;
            text-align: center;
            margin: 10px;
            cursor: pointer;
        }}
        .character-item img {{
            width: 100px;
            height: 100px;
            border-radius: 10px;
        }}
        .modal {{
            display: none;
            position: fixed;
            z-index: 1;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            overflow: auto;
            background-color: rgba(0,0,0,0.6);
        }}
        .modal-content {{
            background-color: #fff;
            margin: 10% auto;
            padding: 20px;
            border-radius: 10px;
            width: 80%;
            max-width: 800px;
        }}
        .close-btn {{
            float: right;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
        }}
        .condition-gallery {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }}
        .condition-gallery img {{
            width: 120px;
            height: 120px;
            object-fit: contain;
            border: 2px solid #ddd;
            border-radius: 8px;
        }}
    </style>
</head>
<body>

    <h1>Danh Sách Nhân Vật Umamusume</h1>

    <input type="text" id="search-bar" onkeyup="filterCharacters()" placeholder="Tìm kiếm nhân vật theo tên...">

    <div id="character-grid"></div>

    <div id="character-modal" class="modal">
        <div class="modal-content">
            <span class="close-btn" onclick="closeModal()">&times;</span>
            <div id="modal-body-content"></div>
        </div>
    </div>

<script>
    // --- DỮ LIỆU NHÚNG TỪ PYTHON ---
    const allCharacters = {js_all_characters};
    const characterConditionsMap = {js_char_conditions_map};
    const conditionsInfoMap = {js_conditions_info_map};
    const conditionImagesDir = {js_condition_images_dir};

    function loadAllCharacters() {{
        const grid = document.getElementById('character-grid');
        grid.innerHTML = '';

        allCharacters.forEach(char => {{
            const item = document.createElement('div');
            item.className = 'character-item';
            item.onclick = () => showCharacterDetails(char.tên);
            item.innerHTML = `
                <img src="${{char.avatar || 'https://via.placeholder.com/80?text=No+Img'}}" alt="${{char.tên}}">
                <p>${{char.tên}}</p>
            `;
            grid.appendChild(item);
        }});
    }}

    function filterCharacters() {{
        const input = document.getElementById('search-bar');
        const filter = input.value.toLowerCase();
        const grid = document.getElementById('character-grid');
        const items = grid.getElementsByClassName('character-item');

        for (let i = 0; i < items.length; i++) {{
            const p = items[i].getElementsByTagName('p')[0];
            const txtValue = p.textContent || p.innerText;
            items[i].style.display = txtValue.toLowerCase().includes(filter) ? "" : "none";
        }}
    }}

    function showCharacterDetails(characterName) {{
        const modal = document.getElementById('character-modal');
        const modalContent = document.getElementById('modal-body-content');
        const charData = allCharacters.find(c => c.tên === characterName);
        const matchingConditionIds = characterConditionsMap[characterName] || [];

        let conditionsHTML = '<h3>Điều kiện phù hợp:</h3>';

        if (matchingConditionIds.length > 0) {{
            conditionsHTML += '<div class="condition-gallery">';
            matchingConditionIds.forEach(id => {{
                const imgSrc = `${{conditionImagesDir}}/${{id}}.png`;
                const description = conditionsInfoMap[id] || "Không có mô tả.";
                conditionsHTML += `
                    <div title="${{description}}">
                        <img src="${{imgSrc}}" alt="Điều kiện #${{id}}" onerror="this.src='https://via.placeholder.com/120?text=No+Image'"class="condition-image">
                    </div>
                `;
            }});
            conditionsHTML += '</div>';
        }} else {{
            conditionsHTML += '<p>Không phù hợp với điều kiện nào.</p>';
        }}

        modalContent.innerHTML = `
            <div class="modal-header">
                <img src="${{charData.avatar}}" alt="${{charData.tên}}" style="width:120px;height:120px;border-radius:10px;">
                <h2>${{charData.tên}}</h2>
            </div>
            <div class="modal-body">
                ${{conditionsHTML}}
            </div>
        `;

        modal.style.display = 'block';
    }}

    function closeModal() {{
        document.getElementById('character-modal').style.display = 'none';
    }}

    function closeImageModal() {{
  document.getElementById('image-modal').style.display = 'none';
}}

document.addEventListener('click', function (e) {{
  if (e.target.classList.contains('condition-image')) {{
    const modal = document.getElementById('image-modal');
    const modalImg = document.getElementById('modal-image');
    modal.style.display = 'block';
    modalImg.src = e.target.src;
  }}
}});

    window.onclick = function(event) {{
        const modal = document.getElementById('character-modal');
        if (event.target == modal) {{
            modal.style.display = "none";
        }}
    }}

    window.onload = loadAllCharacters;
</script>


    <!-- Modal phóng to ảnh điều kiện -->
    <div id="image-modal" class="modal">
    <span class="close-btn" onclick="closeImageModal()">&times;</span>
    <img class="modal-content" id="modal-image">
    </div>

</body>
</html>
""".format(
        js_all_characters=js_all_characters,
        js_char_conditions_map=js_char_conditions_map,
        js_conditions_info_map=js_conditions_info_map,
        js_condition_images_dir=js_condition_images_dir
    )

    try:
        with open(OUTPUT_HTML_FILE, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"\n🎉 Đã tạo thành công '{OUTPUT_HTML_FILE}'. Mở file này trong trình duyệt để xem.")
    except IOError as e:
        print(f"❌ Lỗi ghi file {OUTPUT_HTML_FILE}: {e}")
    except Exception as e:
        print(f"❌ Lỗi không xác định khi lưu file: {e}")


if __name__ == "__main__":
    generate_html_page()
