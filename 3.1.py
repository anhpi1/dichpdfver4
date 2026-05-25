"""
Translate 2.txt to Vietnamese via DeepSeek API.
Batches lines based on token counting.
Output per subfolder: 3.txt
"""

import json
import os
import time
from pikepdf import Page
import transformers
from openai import OpenAI

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(BASE_DIR, "input")
TOKENIZER_DIR = "deepseek-ai/DeepSeek-V3"

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

tokenizer = transformers.AutoTokenizer.from_pretrained(
    TOKENIZER_DIR, trust_remote_code=True
)

SYSTEM_PROMPT = """
You are a professional translator. Translate English to Vietnamese.

RULES
- ABSOLUTELY keep the strange characters as they are and do not infer anything.
- Do not merge lines
- No explanation needed.
"""

MAX_OUTPUT_TOKENS = 384000
MAX_INPUT_TOKENS = 192000


_overhead_text = SYSTEM_PROMPT
_overhead_tokens = len(tokenizer.encode(_overhead_text))


def batch_lines(lines):
    """Group lines into batches respecting MAX_INPUT_TOKENS."""
    batches = []
    current_batch = []
    current_tokens = 0

    for line in lines:
        line = line.strip()
        if not line:
            continue

        line_tokens = len(tokenizer.encode(line))
        total_if_added = _overhead_tokens + current_tokens + line_tokens

        if total_if_added > MAX_INPUT_TOKENS and current_batch:
            batches.append(current_batch)
            current_batch = []
            current_tokens = 0

        current_batch.append(line)
        current_tokens += line_tokens

    if current_batch:
        batches.append(current_batch)

    return batches


def translate_batch(batch_texts, retries=3):
    """Translate a list of lines as one API call."""
    joined = "\n".join(batch_texts)
    for attempt in range(retries):
        try:
            resp = client.chat.completions.create(
                model="deepseek-v4-flash", # Adjust model name if needed
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": joined},
                ],
                temperature=0.3,
                max_tokens=MAX_OUTPUT_TOKENS,
                extra_body={"thinking": {"type": "disabled"}},
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            print(f"  API error (attempt {attempt+1}): {e}")
            if attempt < retries - 1:
                time.sleep(3)
    return joined


if __name__ == "__main__":
    if not os.path.exists(INPUT_DIR):
        print(f"Khong tim thay thu muc: {INPUT_DIR}")
        exit()

    for folder in sorted(os.listdir(INPUT_DIR)):
        folder_path = os.path.join(INPUT_DIR, folder)
        if not os.path.isdir(folder_path) or folder == "sample":
            continue

        temp_dir = os.path.join(folder_path, "temp")
        os.makedirs(temp_dir, exist_ok=True)
        src = os.path.join(temp_dir, "2.txt")
        if not os.path.exists(src):
            print(f"[{folder}] Bo qua -- khong co file temp/2.txt")
            continue

        with open(src, "r", encoding="utf-8") as f:
            lines = f.readlines()

        batches = batch_lines(lines)
        total_batches = len(batches)
        print(f"[{folder}] {len(lines)} lines, chia thanh {total_batches} batch(es)")

        translated_parts = []
        for i, batch in enumerate(batches):
            batch_token_count = sum(len(tokenizer.encode(t)) for t in batch)
            print(f"  Batch {i+1}/{total_batches} ({len(batch)} lines, ~{batch_token_count} tokens)...")
            translated = translate_batch(batch)
            translated_parts.append(translated)

        dst = os.path.join(temp_dir, "3.txt")
        with open(dst, "w", encoding="utf-8") as f:
            f.write("\n".join(translated_parts))

        print(f"[{folder}] Dich xong! Output: {dst}")