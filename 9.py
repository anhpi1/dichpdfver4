"""
7.py — Render HTML từ JSON đã có size.
Đọc 6.json, sử dụng trường "size" của mỗi block để đặt font-size tĩnh, 
KHÔNG dùng JavaScript tính toán font-size nữa.
"""

import json
import os
import re
from html import escape

# ==================== CONFIG ====================
INPUT_JSON = "8.json"
OUTPUT_HTML = "9.html"
SCALE = 1.5      # 1 PDF point → 1.5 CSS pixel
DEFAULT_FONT_SIZE = 10

# Bảng màu viền debug
DEBUG_COLORS = {
    "text":               "#4CAF50",
    "title":              "#FF9800",
    "image":              "#E91E63",
    "table":              "#2196F3",
    "interline_equation": "#9C27B0",
    "list":               "#00BCD4",
    "code":               "#795548",
}


# ==================== MATH PROCESSING ====================

LATEX_PATTERN = re.compile(
    r'(?:'
      r'(?:'
        r'\{[^{}]*\\[a-zA-Z]+[^{}]*\}'              
        r'|'
        r'\\[a-zA-Z]+\s*(?:\{[^{}]*\})?'             
        r'|'
        r'\b[a-zA-Z0-9]+'
      r')'
      r'(?:\s*[_^]\s*\{[^{}]*\})+'
    r')'
    r'|'
    r'\{[^{}]*\\[a-zA-Z]+[^{}]*\}'
    r'|'
    r'\\[a-zA-Z]+\s*(?:\{[^{}]*\})?'
)

def process_math_in_text(text):
    parts = []
    last_end = 0

    for match in LATEX_PATTERN.finditer(text):
        start, end = match.span()
        matched_text = match.group(0)
        
        if matched_text.strip() == '\\':
            continue

        if start > last_end:
            parts.append(escape(text[last_end:start]))

        latex_clean = matched_text.strip()
        latex_clean = re.sub(r'\{\s+', '{', latex_clean)
        latex_clean = re.sub(r'\s+\}', '}', latex_clean)

        parts.append(f'<span class="math">{escape(latex_clean)}</span>')
        last_end = end

    if last_end < len(text):
        parts.append(escape(text[last_end:]))

    full_html = ''.join(parts)
    return full_html


# ==================== RENDER BLOCK ====================

def extract_list_texts(element):
    texts = []
    if isinstance(element, dict):
        if element.get('content'):
            texts.append(element['content'])
        for key in ['spans', 'lines', 'blocks']:
            if key in element:
                for sub in element[key]:
                    texts.extend(extract_list_texts(sub))
    return texts

def get_debug_color(btype):
    return DEBUG_COLORS.get(btype, '#9E9E9E')

_block_counter = [0]

def render_block(block, scale):
    x1, y1, x2, y2 = block['bbox']
    w = (x2 - x1) * scale
    h = (y2 - y1) * scale
    left = x1 * scale
    top = y1 * scale
    btype = block.get('type', 'text')
    color = get_debug_color(btype)
    
    # Lấy font size đã tính toán từ 6.py, mặc định là DEFAULT_FONT_SIZE
    font_size = block.get('size', DEFAULT_FONT_SIZE)
    # Style tĩnh thay vì js fitText
    font_style = f"font-size:{font_size}px; line-height:{int(font_size * 1.3)}px;"

    if w <= 2 or h <= 2:
        return ''

    _block_counter[0] += 1
    bid = _block_counter[0]

    pos = (
        f'position:absolute;left:{left:.1f}px;top:{top:.1f}px;'
        f'width:{w:.1f}px;height:{h:.1f}px;'
        f'overflow:hidden;box-sizing:border-box;'
    )

    debug_label = f'<span class="dbg-label" style="background:{color};">#{bid} {btype}</span>'

    # ── Ảnh ──
    if block.get('image_path'):
        img = block['image_path']
        if not img.startswith(('http', '/', '..')):
            img = f'../images/{img}'
        return (
            f'<div class="blk" style="{pos}border-color:{color};" data-t="{btype}">'
            f'{debug_label}'
            f'<img src="{escape(img)}" style="width:100%;height:100%;object-fit:contain;display:block;"/>'
            f'</div>'
        )

    content = block.get('content', '').strip()

    # ── Code Block ──
    if btype == 'code':
        # Phục hồi dấu xuống dòng bị mất do quá trình dịch merge text
        if '\n' not in content and '//' in content:
            content = re.sub(r'\s+([A-Z][A-Z0-9_-]+(?:\s+[A-Z0-9.E-]+)?\s+//)', r'\n\1', content)
        
        return (
            f'<div class="blk code-block" style="{pos}border-color:{color};" data-t="code">'
            f'{debug_label}'
            f'<pre class="fit" style="margin:0; width:100%; height:100%; overflow:hidden; font-family:Consolas, monospace; white-space:pre-wrap;">'
            f'<code style="{font_style} display:block; width:100%; height:100%;">{escape(content)}</code>'
            f'</pre>'
            f'</div>'
        )

    # ── List ──
    if btype == 'list' and 'blocks' in block:
        items = []
        for sub in block.get('blocks', []):
            txts = extract_list_texts(sub)
            if txts:
                txt = ' '.join(txts)
                txt = re.sub(r'^[\s\u2022\u25e6\u2023\u25b8\u25aa\u25ab\u2013\u2014\ufffd\xef\xbf\xbd]+\s*', '', txt)
                items.append(txt)
        if items:
            lis = ''.join(f'<li style="margin-bottom:4px;">{process_math_in_text(t)}</li>' for t in items)
            return (
                f'<div class="blk" style="{pos}border-color:{color};" data-t="list">'
                f'{debug_label}'
                f'<ul class="fit" style="{font_style} margin:0;padding-left:16px;">{lis}</ul>'
                f'</div>'
            )

    # ── Table ──
    if content.startswith('<table'):
        return (
            f'<div class="blk" style="{pos}border-color:{color};" data-t="table">'
            f'{debug_label}'
            f'<div class="fit tw" style="{font_style}">{content}</div>'
            f'</div>'
        )

    # ── Text thường ──
    if content:
        processed = process_math_in_text(content)
        return (
            f'<div class="blk" style="{pos}border-color:{color};" data-t="{btype}">'
            f'{debug_label}'
            f'<span class="fit" style="{font_style}">{processed}</span>'
            f'</div>'
        )

    return ''


# ==================== CONVERT ====================

def convert(input_path, output_path, scale):
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    pages = data.get('pdf_info', [])
    all_pages = []
    _block_counter[0] = 0

    for page in pages:
        pw, ph = page.get('page_size', [612, 792])
        blocks = page.get('para_blocks', [])

        parts = []
        for b in blocks:
            html = render_block(b, scale)
            if html:
                parts.append(html)

        page_html = (
            f'<div class="pg" style="'
            f'width:{pw * scale:.0f}px;height:{ph * scale:.0f}px;'
            f'position:relative;background:#fff;'
            f'margin:30px auto;'
            f'box-shadow:0 4px 24px rgba(0,0,0,0.3);'
            f'">\n'
            + '\n'.join(parts)
            + '\n</div>'
        )
        all_pages.append(page_html)

    html = TEMPLATE.replace('{{PAGES}}', '\n'.join(all_pages))

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"  Pages: {len(pages)}, Blocks: {_block_counter[0]}, Output: {output_path}")


# ==================== HTML TEMPLATE ====================

TEMPLATE = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>PDF Replica Viewer</title>

<!-- KaTeX -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css"/>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>

<style>
* { margin:0; padding:0; box-sizing:border-box; }
body {
    font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
    background: #525659;
    padding: 30px 0;
    min-height: 100vh;
}
.pg {
    overflow: hidden;
    page-break-after: always;
}

.blk {
    border: 2px solid transparent;
    transition: border-color 0.2s;
}

.dbg-label {
    display: none;
    position: absolute;
    top: 0; left: 0;
    color: #fff;
    font-size: 10px;
    font-weight: bold;
    padding: 2px 6px;
    border-radius: 0 0 6px 0;
    z-index: 10;
    opacity: 0.95;
    line-height: 1.2;
    pointer-events: none;
    box-shadow: 1px 1px 4px rgba(0,0,0,0.3);
}

body.debug .blk {
    border-style: dashed !important;
    background-color: rgba(0,0,0,0.02);
}
body:not(.debug) .blk {
    border-color: transparent !important;
}
body.debug .dbg-label {
    display: block;
}

#debug-btn {
    position: fixed;
    top: 12px;
    right: 16px;
    z-index: 9999;
    background: #333;
    color: #aaa;
    border: 1px solid #555;
    padding: 8px 16px;
    border-radius: 6px;
    font-size: 14px;
    font-weight: bold;
    cursor: pointer;
    font-family: 'Segoe UI', sans-serif;
    transition: all 0.2s;
    box-shadow: 0 4px 6px rgba(0,0,0,0.3);
}
#debug-btn:hover { background: #444; color: #fff; }
#debug-btn.active { background: #ff5722; color: #fff; border-color: #ff5722; }

.fit {
    display: block;
    word-wrap: break-word;
    overflow-wrap: break-word;
}

.code-block {
    background-color: transparent;
    border-radius: 0;
    border: none !important;
}

.tw table {
    border-collapse: collapse;
    width: 100%;
}
.tw td, .tw th {
    border: 1px solid #bbb;
    padding: 2px 4px;
}

.math .katex {
    font-size: 1.05em !important;
}
</style>
</head>
<body>

<button id="debug-btn" onclick="toggleDebug()">🔍 Debug OFF</button>

{{PAGES}}

<script>
function toggleDebug() {
    document.body.classList.toggle('debug');
    var btn = document.getElementById('debug-btn');
    btn.classList.toggle('active');
    btn.textContent = document.body.classList.contains('debug')
        ? '🔍 Debug ON'
        : '🔍 Debug OFF';
}

window.addEventListener('load', function() {
    // Render math
    if (typeof katex === 'undefined') {
        console.warn('KaTeX not loaded');
    } else {
        var mathEls = document.querySelectorAll('.math');
        for (var i = 0; i < mathEls.length; i++) {
            var el = mathEls[i];
            var tex = el.textContent;
            try {
                katex.render(tex, el, {
                    throwOnError: false,
                    displayMode: false,
                    output: 'html'
                });
            } catch (e) {
                console.warn('KaTeX error:', tex, e);
            }
        }
    }
});
</script>

</body>
</html>'''


# ==================== MAIN ====================

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
        out = os.path.join(temp, OUTPUT_HTML)

        if os.path.exists(inp):
            print(f'[{folder}] Tao HTML tu {INPUT_JSON} -> {OUTPUT_HTML}')
            convert(inp, out, SCALE)


if __name__ == '__main__':
    main()
