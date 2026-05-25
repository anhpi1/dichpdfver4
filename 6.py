import json
import os

INPUT_JSON = "5.json"
OUTPUT_JSON = "6.json"
SCALE = 1.5

def extract_list_texts(element):
    texts = []
    if isinstance(element, dict):
        if element.get('content'):
            texts.append(element['content'])
        for key in ['spans', 'lines', 'blocks']:
            if key in element:
                for sub in element[key]:
                    texts.extend(extract_list_texts(sub))
    elif isinstance(element, list):
        for item in element:
            texts.extend(extract_list_texts(item))
    return texts

def get_text_from_block(block):
    btype = block.get('type', 'text')
    if btype == 'list':
        items = []
        for sub in block.get('blocks', []):
            txts = extract_list_texts(sub)
            if txts:
                items.append(' '.join(txts))
        return '\n'.join(items)
    return block.get('content', '')

def get_char_width_em(c, btype):
    if btype == 'code':
        return 0.6  # Monospace
    
    if c.isupper(): return 0.72
    elif c.islower(): return 0.52
    elif c.isdigit(): return 0.60
    elif c.isspace(): return 0.28
    else: return 0.50

def get_word_width_em(word, btype):
    return sum(get_char_width_em(c, btype) for c in word)

def simulate_font_size(w, h, text, font_size, btype):
    lh = int(font_size * 1.3)
    if lh == 0: return False
    
    effective_w = w
    if btype == 'list':
        effective_w = max(1, w - 16) # padding-left: 16px
        
    used_h = 0
    lines = 1
    current_line_width_px = 0
    space_px = get_char_width_em(' ', btype) * font_size
    
    paragraph_lines = text.split('\n')
    for i, p_line in enumerate(paragraph_lines):
        words = p_line.split()
        for word in words:
            word_px = get_word_width_em(word, btype) * font_size
            
            if word_px > effective_w:
                return False
                
            needed_px = word_px
            if current_line_width_px > 0:
                needed_px += space_px
                
            if current_line_width_px + needed_px <= effective_w:
                current_line_width_px += needed_px
            else:
                lines += 1
                current_line_width_px = word_px
                
        used_h += lines * lh
        if btype == 'list':
            used_h += 4 # margin-bottom: 4px
            
        lines = 1
        current_line_width_px = 0
        
        if used_h > h:
            return False
            
    return used_h <= h

def estimate_font_size(w, h, text, btype):
    if not text.strip():
        return 12
        
    lo = 1
    hi = int(h)
    best = 12
    
    while lo <= hi:
        mid = (lo + hi) // 2
        if simulate_font_size(w, h, text, mid, btype):
            best = mid
            lo = mid + 1
        else:
            hi = mid - 1
            
    if best < 6: best = 6
    if best > 200: best = 200
    
    # Bo gioi han size chu toi da (cap) theo yeu cau cua user
    # De cho text to nhat co the, lap day khung ma khong bi tran ra ngoai
    return best

def calculate_block_sizes(blocks):
    for b in blocks:
        btype = b.get('type', 'text')
        
        if btype in ('image', 'table', 'chart', 'interline_equation'):
            if 'image_path' in b:
                continue
            if btype in ('image', 'table'):
                continue
            
        x1, y1, x2, y2 = b.get('bbox', [0, 0, 0, 0])
        w = max(0, x2 - x1) * SCALE
        h = max(0, y2 - y1) * SCALE
        
        if w <= 2 or h <= 2:
            continue
            
        text = get_text_from_block(b)
        
        # Dong bo logic phuc hoi xuong dong cua code block giong het trong 7.py
        if btype == 'code':
            if '\n' not in text and '//' in text:
                import re
                text = re.sub(r'\s+([A-Z][A-Z0-9_-]+(?:\s+[A-Z0-9.E-]+)?\s+//)', r'\n\1', text)
                
        size = estimate_font_size(w, h, text, btype)
        b['size'] = size

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
            print(f'[{folder}] Tinh toan size chu: {INPUT_JSON} -> {OUTPUT_JSON}')
            with open(inp, 'r', encoding='utf-8') as f:
                data = json.load(f)

            pages = data.get('pdf_info', [])
            for page in pages:
                blocks = page.get('para_blocks', [])
                calculate_block_sizes(blocks)

            with open(out, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    main()
