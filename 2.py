import json
import os

INPUT_JSON = "1.json"
OUTPUT_TXT = "2.txt"
OUTPUT_JSON = "2.json"

def process_data(data, texts_list, counter):
    """
    Đệ quy quét qua toàn bộ cấu trúc JSON.
    Nếu gặp key "content", lấy nội dung ra và thay bằng [*]
    """
    if isinstance(data, dict):
        # Nếu có key content và nó là string
        if "content" in data and isinstance(data["content"], str):
            text = data["content"]
            # Xóa ký tự xuống dòng bên trong text để đảm bảo mỗi content nằm trên 1 dòng duy nhất
            text_clean = text.replace('\n', ' ').replace('\r', '')
            
            marker = f"[{counter[0]}]"
            
            # Ghi vào mảng text
            texts_list.append(f"{text_clean} {marker}")
            
            # Thay thế value trong JSON thành marker để làm khung (skeleton)
            data["content"] = marker
            
            counter[0] += 1
            
        # Tiếp tục đệ quy vào các value của dict
        for key, value in data.items():
            process_data(value, texts_list, counter)
            
    elif isinstance(data, list):
        # Đệ quy vào các phần tử của list
        for item in data:
            process_data(item, texts_list, counter)

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_base_dir = os.path.join(script_dir, "input")

    if not os.path.exists(input_base_dir):
        print(f"Loi: Khong tim thay thu muc {input_base_dir}.")
        return

    for folder in os.listdir(input_base_dir):
        folder_path = os.path.join(input_base_dir, folder)
        if not os.path.isdir(folder_path):
            continue

        temp_dir = os.path.join(folder_path, "temp")
        os.makedirs(temp_dir, exist_ok=True)
        input_path = os.path.join(temp_dir, INPUT_JSON)
        output_txt_path = os.path.join(temp_dir, OUTPUT_TXT)
        output_json_path = os.path.join(temp_dir, OUTPUT_JSON)

        if os.path.exists(input_path):
            print(f"[{folder}] Dang trich xuat {INPUT_JSON}...")
            with open(input_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            texts_list = []
            counter = [1]
            process_data(data, texts_list, counter)

            with open(output_txt_path, "w", encoding="utf-8") as f:
                for line in texts_list:
                    f.write(line + "\n")

            with open(output_json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        else:
            pass # Bo qua neu khong co file

if __name__ == "__main__":
    main()
