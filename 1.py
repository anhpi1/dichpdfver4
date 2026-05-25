import json
import os

INPUT_JSON = "layout.json"
OUTPUT_JSON = "1.json"

def extract_data(element, data):
    """
    Hàm đệ quy để thu thập toàn bộ image_path và content/html
    từ các spans, lines, blocks con bên trong block hiện tại.
    """
    # Nếu phần tử hiện tại là 1 dict (có thể là span, line, hoặc sub-block)
    if isinstance(element, dict):
        if element.get("image_path"):
            data["images"].append(element["image_path"])
        if element.get("html"):
            data["texts"].append(element["html"])
        if element.get("content"):
            data["texts"].append(element["content"])

        # Duyệt tiếp vào sâu bên trong
        for key in ["spans", "lines", "blocks"]:
            if key in element:
                for sub_element in element[key]:
                    extract_data(sub_element, data)

def process_layout(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for page in data.get("pdf_info", []):
        # 1. Xóa preproc_blocks
        if "preproc_blocks" in page:
            del page["preproc_blocks"]
            
        # 2. Quét toàn bộ block trong para_blocks
        para_blocks = page.get("para_blocks", [])
        for block in para_blocks:
            # Bỏ qua không làm phẳng nếu là list box
            if block.get("type") == "list":
                continue

            extracted = {"images": [], "texts": []}
            extract_data(block, extracted)

            # Xóa cấu trúc lines và blocks lộn xộn cũ
            block.pop("lines", None)
            block.pop("blocks", None)

            # Nếu block có ảnh -> Chỉ giữ lại ảnh, vứt bỏ toàn bộ text
            if extracted["images"]:
                # Giữ lại ảnh đầu tiên tìm thấy (thường mỗi block chỉ có 1 ảnh chính)
                block["image_path"] = extracted["images"][0]
            else:
                # Nếu không có ảnh -> Gộp toàn bộ text thành 1 chuỗi duy nhất
                if extracted["texts"]:
                    # Gộp bằng dấu cách như ví dụ của bạn
                    block["content"] = " ".join(extracted["texts"])

    # Lưu lại file mới
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"Hoan thanh! Da xoa preproc_blocks, don dep para_blocks va luu tai: {output_path}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_base_dir = os.path.join(script_dir, "input")
    
    if not os.path.exists(input_base_dir):
        print(f"Khong tim thay thu muc: {input_base_dir}")
    else:
        for folder in os.listdir(input_base_dir):
            folder_path = os.path.join(input_base_dir, folder)
            if not os.path.isdir(folder_path):
                continue
                
            input_path = os.path.join(folder_path, INPUT_JSON)
            temp_dir = os.path.join(folder_path, "temp")
            os.makedirs(temp_dir, exist_ok=True)
            output_path = os.path.join(temp_dir, OUTPUT_JSON)
            
            if os.path.exists(input_path):
                print(f"[{folder}] Dang don dep {INPUT_JSON} -> temp/{OUTPUT_JSON}...")
                process_layout(input_path, output_path)
            else:
                pass # Bo qua neu khong co file
