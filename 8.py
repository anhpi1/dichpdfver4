import json
import os
import sys
import importlib.util

# Import 6.py functions for extracting text
script_dir = os.path.dirname(os.path.abspath(__file__))
module_path = os.path.join(script_dir, '6.py')
spec = importlib.util.spec_from_file_location("module6", module_path)
module6 = importlib.util.module_from_spec(spec)
sys.modules["module6"] = module6
spec.loader.exec_module(module6)

# ==================== CONFIG ====================
INPUT_JSON = "7.json"
OUTPUT_JSON = "8.json"
CONFIDENCE_LEVEL = 0.90  # Độ tin cậy (0.90 = giữ lại 90% từ bé nhất, loại bỏ 10% lớn nhất)
# ================================================

def trimmed_mean(arr, confidence=0.90):
    if not arr:
        return 0
    arr.sort()
    # Tính từ 0 đến y (chỉ loại bỏ phần top lớn nhất)
    end = int(len(arr) * confidence)
    sliced = arr[:end]
    if not sliced:
        return sum(arr) / len(arr)
    return sum(sliced) / len(sliced)

def normalize_sizes(pages):
    title_sizes = []
    body_sizes = []
    
    # B1: Thong ke tung tu vao mang de loai bo outlier
    for page in pages:
        for block in page.get('para_blocks', []):
            if 'size' in block:
                text = module6.get_text_from_block(block)
                words = len(text.split())
                if words == 0:
                    continue
                    
                if block.get('type') == 'title':
                    title_sizes.extend([block['size']] * words)
                else:
                    body_sizes.extend([block['size']] * words)
                    
    # Tinh trung binh co trong so, cat bo ngoai le dua tren CONFIDENCE_LEVEL
    avg_title = trimmed_mean(title_sizes, CONFIDENCE_LEVEL)
    avg_body = trimmed_mean(body_sizes, CONFIDENCE_LEVEL)
    
    # Lam tron xuong de tranh tran khung
    avg_title = int(avg_title)
    avg_body = int(avg_body)
    
    print(f"  Average Title Size: {avg_title}")
    print(f"  Average Body Size: {avg_body}")
    
    # B2: Cat ngon cac block vuot qua muc trung binh
    capped_titles = 0
    capped_bodies = 0
    
    for page in pages:
        for block in page.get('para_blocks', []):
            if 'size' in block:
                btype = block.get('type')
                curr_size = block['size']
                
                if btype == 'title':
                    if avg_title > 0 and curr_size > avg_title:
                        block['size'] = avg_title
                        capped_titles += 1
                else:
                    if avg_body > 0 and curr_size > avg_body:
                        block['size'] = avg_body
                        capped_bodies += 1
                        
    print(f"  Capped {capped_titles} titles down to {avg_title}")
    print(f"  Capped {capped_bodies} body blocks down to {avg_body}")

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base = os.path.join(script_dir, 'input')
    if not os.path.exists(base):
        return

    for folder in sorted(os.listdir(base)):
        fp = os.path.join(base, folder)
        if not os.path.isdir(fp):
            continue

        temp = os.path.join(fp, 'temp')
        inp = os.path.join(temp, INPUT_JSON)
        out = os.path.join(temp, OUTPUT_JSON)

        if os.path.exists(inp):
            print(f'[{folder}] Chuan hoa size chu: {INPUT_JSON} -> {OUTPUT_JSON}')
            with open(inp, 'r', encoding='utf-8') as f:
                data = json.load(f)

            pages = data.get('pdf_info', [])
            normalize_sizes(pages)

            with open(out, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    main()
