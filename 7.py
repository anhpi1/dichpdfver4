import json
import os
import sys

# Import 6.py functions for size estimation
import importlib.util
script_dir = os.path.dirname(os.path.abspath(__file__))
module_path = os.path.join(script_dir, '6.py')
spec = importlib.util.spec_from_file_location("module6", module_path)
module6 = importlib.util.module_from_spec(spec)
sys.modules["module6"] = module6
spec.loader.exec_module(module6)

INPUT_JSON = "6.json"
OUTPUT_JSON = "7.json"
SCALE = 1.5
MIN_FONT_SIZE = 12

def get_block_size_info(block):
    x1, y1, x2, y2 = block.get('bbox', [0, 0, 0, 0])
    w = max(0, x2 - x1) * SCALE
    h = max(0, y2 - y1) * SCALE
    return w, h

def balance_blocks(pages):
    # Flatten all text blocks with their page/block indices
    text_blocks = []
    for p_idx, page in enumerate(pages):
        blocks = page.get('para_blocks', [])
        for b_idx, block in enumerate(blocks):
            text_blocks.append((p_idx, b_idx, block))
            
    # Multi-pass loop: keep balancing until no more moves are made
    while True:
        any_changes = False
        
        for i in range(len(text_blocks)):
            p_idx, b_idx, block = text_blocks[i]
            
            if block.get('type') != 'text':
                continue
                
            size = block.get('size', 12)
            if size >= MIN_FONT_SIZE:
                continue
                
            # Try to find neighbors of type 'text'
            prev_block = text_blocks[i-1][2] if i > 0 else None
            next_block = text_blocks[i+1][2] if i < len(text_blocks) - 1 else None
            
            target_neighbor = None
            direction = 0 # -1 for prev, 1 for next
            
            # Determine the best neighbor
            prev_valid = prev_block and prev_block.get('type') == 'text'
            next_valid = next_block and next_block.get('type') == 'text'
            
            if prev_valid and next_valid:
                if prev_block.get('size', 0) >= next_block.get('size', 0):
                    target_neighbor = prev_block
                    direction = -1
                else:
                    target_neighbor = next_block
                    direction = 1
            elif prev_valid:
                target_neighbor = prev_block
                direction = -1
            elif next_valid:
                target_neighbor = next_block
                direction = 1
                
            if not target_neighbor:
                continue
                
            # Try moving content
            source_content = block.get('content', '')
            source_words = source_content.split()
            
            if len(source_words) < 2:
                continue # Too few words to split
                
            target_content = target_neighbor.get('content', '')
            target_words = target_content.split()
            
            target_w, target_h = get_block_size_info(target_neighbor)
            
            success = False
            fractions = [1/2, 1/4, 1/8, 1/16, 1/32]
            
            for frac in fractions:
                cut_len = max(1, int(len(source_words) * frac))
                
                if direction == -1: # Move to prev: take from start
                    moving_words = source_words[:cut_len]
                    new_target_words = target_words + moving_words
                else: # Move to next: take from end
                    split_idx = len(source_words) - cut_len
                    moving_words = source_words[split_idx:]
                    new_target_words = moving_words + target_words
                    
                new_target_text = ' '.join(new_target_words)
                
                # Estimate new size for target
                new_size = module6.estimate_font_size(target_w, target_h, new_target_text, 'text')
                
                if new_size >= MIN_FONT_SIZE:
                    # Accept this split!
                    if direction == -1:
                        remain_words = source_words[cut_len:]
                    else:
                        remain_words = source_words[:len(source_words) - cut_len]
                        
                    new_source_text = ' '.join(remain_words)
                    
                    # Update contents
                    block['content'] = new_source_text
                    target_neighbor['content'] = new_target_text
                    
                    # Clean up lines/spans to avoid mismatch with updated content
                    if 'lines' in block: del block['lines']
                    if 'spans' in block: del block['spans']
                    if 'lines' in target_neighbor: del target_neighbor['lines']
                    if 'spans' in target_neighbor: del target_neighbor['spans']
                    
                    # Recalculate size for source
                    source_w, source_h = get_block_size_info(block)
                    block['size'] = module6.estimate_font_size(source_w, source_h, new_source_text, 'text')
                    target_neighbor['size'] = new_size
                    
                    print(f"  Moved {cut_len} words from block {b_idx} to block with size {new_size}")
                    success = True
                    any_changes = True
                    break
                    
        # If we went through all blocks and made no moves, we are stuck or done
        if not any_changes:
            break

def main():
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
            print(f'[{folder}] San se noi dung: {INPUT_JSON} -> {OUTPUT_JSON}')
            with open(inp, 'r', encoding='utf-8') as f:
                data = json.load(f)

            pages = data.get('pdf_info', [])
            balance_blocks(pages)

            with open(out, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    main()
