"""
4.py — Gộp file 2.json (bộ khung skeleton) và 3.txt (bản dịch) lại với nhau.
Thay thế các marker [*] trong 2.json bằng nội dung tương ứng từ 3.txt.

Quy tắc xử lý thiếu dòng:
  Nếu marker [N] không tìm thấy dòng tương ứng trong 3.txt,
  lấy dòng [N-1] chia đôi nội dung:
    - Nửa đầu giữ lại cho [N-1]
    - Nửa sau gán cho [N]
"""

import json
import os
import re

INPUT_JSON = "2.json"
INPUT_TXT = "3.txt"
OUTPUT_JSON = "4.json"


def parse_translated_lines(txt_path):
    """
    Đọc file 3.txt và parse ra dict: { số_thứ_tự: nội_dung }
    Mỗi dòng có dạng: "nội dung dịch [42]"
    """
    mapping = {}
    with open(txt_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line.strip():
                continue

            # Tìm marker [*] ở cuối dòng
            match = re.search(r'\[(\d+)\]\s*$', line)
            if match:
                idx = int(match.group(1))
                # Lấy nội dung phía trước marker
                content = line[:match.start()].strip()
                mapping[idx] = content
            else:
                # Dòng không có marker -> bỏ qua (hoặc có thể là dòng rác)
                pass

    return mapping


def fill_missing(mapping, max_idx):
    """
    Quét từ 1 đến max_idx.
    Nếu marker [N] bị thiếu, lấy dòng [N-1] chia đôi:
      - Nửa đầu giữ lại cho [N-1]
      - Nửa sau gán cho [N]
    """
    for i in range(1, max_idx + 1):
        if i not in mapping:
            prev = i - 1
            if prev in mapping and mapping[prev]:
                text = mapping[prev]
                # Chia đôi theo từ (word) để không cắt giữa chừng 1 từ
                words = text.split()
                mid = len(words) // 2
                if mid == 0:
                    mid = 1  # Đảm bảo nửa đầu có ít nhất 1 từ

                first_half = " ".join(words[:mid])
                second_half = " ".join(words[mid:])

                mapping[prev] = first_half
                mapping[i] = second_half
                print(f"  [!] Marker [{i}] thieu -> chia doi [{prev}]")
            else:
                # Trường hợp cả [N-1] cũng không có -> để trống
                mapping[i] = ""
                print(f"  [!] Marker [{i}] thieu va [{prev}] cung khong co -> de trong")


def find_max_marker(data, current_max=0):
    """Tìm số marker lớn nhất trong JSON skeleton."""
    if isinstance(data, dict):
        for key, value in data.items():
            if key == "content" and isinstance(value, str):
                match = re.match(r'^\[(\d+)\]$', value.strip())
                if match:
                    num = int(match.group(1))
                    if num > current_max:
                        current_max = num
            current_max = find_max_marker(value, current_max)
    elif isinstance(data, list):
        for item in data:
            current_max = find_max_marker(item, current_max)
    return current_max


def replace_markers(data, mapping):
    """
    Đệ quy thay thế các marker [*] trong JSON bằng nội dung từ mapping.
    """
    if isinstance(data, dict):
        for key, value in data.items():
            if key == "content" and isinstance(value, str):
                match = re.match(r'^\[(\d+)\]$', value.strip())
                if match:
                    idx = int(match.group(1))
                    if idx in mapping:
                        data[key] = mapping[idx]
                    else:
                        # Không tìm thấy -> giữ nguyên marker
                        print(f"  [?] Marker [{idx}] khong co trong 3.txt, giu nguyen")
            else:
                replace_markers(value, mapping)
    elif isinstance(data, list):
        for item in data:
            replace_markers(item, mapping)


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_base_dir = os.path.join(script_dir, "input")

    if not os.path.exists(input_base_dir):
        print(f"Loi: Khong tim thay thu muc {input_base_dir}.")
        return

    for folder in sorted(os.listdir(input_base_dir)):
        folder_path = os.path.join(input_base_dir, folder)
        if not os.path.isdir(folder_path):
            continue

        temp_dir = os.path.join(folder_path, "temp")
        json_path = os.path.join(temp_dir, INPUT_JSON)
        txt_path = os.path.join(temp_dir, INPUT_TXT)
        output_path = os.path.join(temp_dir, OUTPUT_JSON)

        if not os.path.exists(json_path):
            continue
        if not os.path.exists(txt_path):
            print(f"[{folder}] Bo qua -- khong co file temp/{INPUT_TXT}")
            continue

        print(f"[{folder}] Dang gop {INPUT_JSON} + {INPUT_TXT} -> {OUTPUT_JSON}...")

        # 1. Đọc JSON skeleton
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 2. Parse bản dịch từ 3.txt
        mapping = parse_translated_lines(txt_path)
        print(f"  Tim thay {len(mapping)} dong dich trong {INPUT_TXT}")

        # 3. Tìm marker lớn nhất trong JSON
        max_marker = find_max_marker(data)
        print(f"  Marker lon nhat trong {INPUT_JSON}: [{max_marker}]")

        # 4. Xử lý các dòng bị thiếu (chia đôi dòng trước đó)
        fill_missing(mapping, max_marker)

        # 5. Thay thế marker trong JSON bằng nội dung dịch
        replace_markers(data, mapping)

        # 6. Lưu kết quả
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        print(f"[{folder}] Hoan thanh! Output: {output_path}")


if __name__ == "__main__":
    main()
