import os
from pypdf import PdfReader, PdfWriter, Transformation
from pypdf.generic import RectangleObject


def scale_page_to_fit(page, target_w, target_h):
    """Scale page content to fit within target dimensions, preserving aspect ratio."""
    orig_w = float(page.mediabox.width)
    orig_h = float(page.mediabox.height)

    scale = min(target_w / orig_w, target_h / orig_h)
    new_w = orig_w * scale
    new_h = orig_h * scale
    tx = (target_w - new_w) / 2
    ty = (target_h - new_h) / 2

    # Apply scaling + centering transformation to content
    op = Transformation().scale(scale).translate(tx, ty)
    page.add_transformation(op)

    # Resize page to target dimensions
    page.mediabox = RectangleObject((0, 0, target_w, target_h))
    page.cropbox = RectangleObject((0, 0, target_w, target_h))


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_base_dir = os.path.join(script_dir, "input")
    output_base_dir = os.path.join(script_dir, "output")
    os.makedirs(output_base_dir, exist_ok=True)

    if not os.path.exists(input_base_dir):
        print(f"Loi: Khong tim thay thu muc {input_base_dir}.")
        return

    for folder in sorted(os.listdir(input_base_dir)):
        folder_path = os.path.join(input_base_dir, folder)
        if not os.path.isdir(folder_path):
            continue

        temp_dir = os.path.join(folder_path, "temp")
        translated_pdf_path = os.path.join(temp_dir, "10.pdf")

        if not os.path.exists(translated_pdf_path):
            continue

        # Tìm file bản gốc (*_origin.pdf)
        origin_pdf_path = None
        for file in os.listdir(folder_path):
            if file.endswith("_origin.pdf"):
                origin_pdf_path = os.path.join(folder_path, file)
                break

        if not origin_pdf_path:
            print(f"[{folder}] Khong tim thay file *_origin.pdf ban goc.")
            continue

        # Trích xuất tên gốc từ tên thư mục (vd: addendum.pdf-uuid -> addendum.pdf)
        if ".pdf-" in folder:
            orig_name = folder.split(".pdf-")[0] + "_bilingual.pdf"
        else:
            orig_name = folder + "_bilingual.pdf"

        output_path = os.path.join(output_base_dir, orig_name)

        print(f"[{folder}] Dang tron ban goc va ban dich -> {output_path}...")

        try:
            with open(origin_pdf_path, "rb") as f_orig, open(translated_pdf_path, "rb") as f_trans:
                reader_orig = PdfReader(f_orig)
                reader_trans = PdfReader(f_trans)
                writer = PdfWriter()

                max_pages = max(len(reader_orig.pages), len(reader_trans.pages))

                for i in range(max_pages):
                    # Chèn 1 trang bản gốc (đã điều chỉnh tỉ lệ cho vừa với trang dịch)
                    if i < len(reader_orig.pages):
                        orig_page = reader_orig.pages[i]

                        # Lấy kích thước trang dịch tương ứng làm chuẩn
                        if len(reader_trans.pages) > 0:
                            trans_idx = min(i, len(reader_trans.pages) - 1)
                            target_w = float(reader_trans.pages[trans_idx].mediabox.width)
                            target_h = float(reader_trans.pages[trans_idx].mediabox.height)
                            scale_page_to_fit(orig_page, target_w, target_h)

                        writer.add_page(orig_page)

                    # Kế tiếp chèn 1 trang bản dịch
                    if i < len(reader_trans.pages):
                        writer.add_page(reader_trans.pages[i])

                # Lưu thành file bilingual PDF
                with open(output_path, "wb") as out_f:
                    writer.write(out_f)

            print(f"[{folder}] Hoan thanh! Da luu tai: {output_path}")

        except Exception as e:
            print(f"[{folder}] Loi khi tron PDF: {e}")


if __name__ == "__main__":
    main()
