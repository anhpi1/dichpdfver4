"""
Translate 2.txt to Vietnamese via NVIDIA NIM API.
Batches multiple lines per call using token counting.
Output per subfolder: temp/3.txt
"""

import json
import os
import threading
import time
import transformers
from openai import OpenAI, APIError

# ─── Configurable NVIDIA NIM Parameters ───────────────────────────────────
NVIDIA_API_KEY_ENV = os.getenv("NVIDIA_API_KEY")
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
NVIDIA_MODEL = "deepseek-ai/deepseek-v4-flash"

# Token limits — NVIDIA NIM enforces much lower caps vs DeepSeek
MAX_OUTPUT_TOKENS = 16000
MAX_INPUT_TOKENS =   1024

# Rate limiting
API_DELAY = 2.0        # seconds between API calls
RETRY_DELAY = 60      # seconds between retries
MAX_RETRIES = 10
# ────────────────────────────────────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(BASE_DIR, "input")
TOKENIZER_DIR = "deepseek-ai/DeepSeek-V3"

client = OpenAI(
    api_key=NVIDIA_API_KEY_ENV,
    base_url=NVIDIA_BASE_URL,
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

# Precompute system + wrapper overhead tokens

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


def translate_batch(batch_texts):
    """Translate a list of section texts as one API call."""
    joined = "\n\n".join(batch_texts)
    for attempt in range(MAX_RETRIES):
        stop_timer = False
        t0 = time.time()

        def timer():
            while not stop_timer:
                t = time.time() - t0
                print(f"\r    Waiting... {t:.0f}s", end="", flush=True)
                time.sleep(0.25)

        t = threading.Thread(target=timer, daemon=True)
        t.start()
        try:
            resp = client.chat.completions.create(
                model=NVIDIA_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": joined},
                ],
                temperature=0.3,
                top_p=0.95,
                max_tokens=MAX_OUTPUT_TOKENS,
                extra_body={"thinking": {"type": "disabled"}},
            )
            stop_timer = True
            t.join(0.5)
            elapsed = time.time() - t0
            code = getattr(resp, 'response', None)
            code = code.status_code if code else '?'
            print(f"\r    [{code}] Done in {elapsed:.1f}s{' ' * 12}")
            return resp.choices[0].message.content.strip()
        except APIError as e:
            stop_timer = True
            t.join(0.5)
            code = e.status_code or '?'
            print(f"\r    [{code}] API error (attempt {attempt+1}): {e}")
        except Exception as e:
            stop_timer = True
            t.join(0.5)
            print(f"\r    [{code}] Error (attempt {attempt+1}): {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
    return joined


for folder in sorted(os.listdir(INPUT_DIR)):
    folder_path = os.path.join(INPUT_DIR, folder)
    if not os.path.isdir(folder_path) or folder == "sample":
        continue

    src = os.path.join(folder_path, "temp", "2.txt")
    if not os.path.exists(src):
        print(f"[{folder}] Skipping -- no 2.txt")
        continue

    with open(src, "r", encoding="utf-8") as f:
        lines = f.readlines()

    batches = batch_lines(lines)
    total_batches = len(batches)
    print(f"[{folder}] {len(lines)} lines, batched into {total_batches} call(s)")

    translated_parts = []
    for i, batch in enumerate(batches):
        batch_token_count = sum(len(tokenizer.encode(t)) for t in batch)
        print(f"  Batch {i+1}/{total_batches} ({len(batch)} lines, ~{batch_token_count} tokens)...")
        translated = translate_batch(batch)
        translated_parts.append(translated)

        # Rate limiting: delay between API calls
        if i < total_batches - 1:
            time.sleep(API_DELAY)

    dst = os.path.join(folder_path, "temp", "3.txt")
    with open(dst, "w", encoding="utf-8") as f:
        f.write("\n".join(translated_parts))

    print(f"[{folder}] Translated. Output: {dst}")