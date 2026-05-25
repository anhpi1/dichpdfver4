import json
import os

INPUT_JSON = "4.json"
OUTPUT_JSON = "5.json"
MARGIN = 1

def expand_blocks(blocks, page_w, page_h):
    result = []
    for b in blocks:
        rb = dict(b)
        rb['bbox'] = list(b.get('bbox', [0, 0, 0, 0])); rb['original_bbox'] = list(rb['bbox'])
        result.append(rb)

    result.sort(key=lambda b: (b['bbox'][1], b['bbox'][0]))

    for i, block in enumerate(result):
        if block.get('type') == 'image' or 'image_path' in block:
            continue

        x1, y1, x2, y2 = block['bbox']
        if x2 <= x1 or y2 <= y1:
            continue

        # Mở rộng sang PHẢI
        right_limit = page_w
        for j, other in enumerate(result):
            if j == i: continue
            ox1, oy1, ox2, oy2 = other['bbox']
            if ox1 >= x2 and oy1 < y2 and oy2 > y1:
                right_limit = min(right_limit, ox1)
        block['bbox'][2] = right_limit - MARGIN
        x2 = block['bbox'][2]

        # Mở rộng xuống DƯỚI
        down_limit = page_h
        for j, other in enumerate(result):
            if j == i: continue
            ox1, oy1, ox2, oy2 = other['bbox']
            if oy1 >= y2 and ox1 < x2 and ox2 > x1:
                down_limit = min(down_limit, oy1)
        block['bbox'][3] = down_limit - MARGIN

    return result

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base = os.path.join(script_dir, 'input')

    if not os.path.exists(base):
        print(f'Khong tim thay: {base}')
        return

    for folder in sorted(os.listdir(base)):
        fp = os.path.join(base, folder)
        if not os.path.isdir(fp):
            continue

        temp = os.path.join(fp, 'temp')
        os.makedirs(temp, exist_ok=True)

        inp = os.path.join(temp, INPUT_JSON)
        out = os.path.join(temp, OUTPUT_JSON)

        if os.path.exists(inp):
            print(f'[{folder}] Chay thuat toan xam thuc: {INPUT_JSON} -> {OUTPUT_JSON}')
            with open(inp, 'r', encoding='utf-8') as f:
                data = json.load(f)

            pages = data.get('pdf_info', [])
            for page in pages:
                pw, ph = page.get('page_size', [612, 792])
                blocks = page.get('para_blocks', [])
                page['para_blocks'] = expand_blocks(blocks, pw, ph)

            with open(out, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    main()
