
"""OCR baseline for scanned machine-history PDFs."""

import re
import argparse
from pathlib import Path

import fitz
import cv2
import numpy as np
import pytesseract

from config import PDF_DIR, PAGE_DIR, RENDER_DPI
from database import (
    init_db,
    save_machine,
    save_page,
    save_component
)

# Tesseract installation on your Windows computer
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


def clean(text):
    return re.sub(r"\s+", " ", (text or "")).strip()


def ocr(image, psm=6):
    return pytesseract.image_to_string(
        image,
        config=f"--oem 3 --psm {psm}"
    )


def render_pdf(pdf_path):
    """Convert PDF pages into high-resolution images."""

    PAGE_DIR.mkdir(parents=True, exist_ok=True)

    document = fitz.open(pdf_path)
    output = []

    for index, page in enumerate(document):

        pix = page.get_pixmap(
            matrix=fitz.Matrix(
                RENDER_DPI / 72,
                RENDER_DPI / 72
            ),
            alpha=False
        )

        image_path = PAGE_DIR / (
            f"{Path(pdf_path).stem}_page_{index + 1:03d}.png"
        )

        pix.save(str(image_path))

        output.append((index + 1, image_path))

    document.close()

    return output


def machine_fields(text):
    """Extract customer name, machine model and machine number."""

    lines = [
        clean(line)
        for line in text.splitlines()
        if clean(line)
    ]

    def find(labels):

        for index, line in enumerate(lines):

            for label in labels:

                match = re.search(
                    label,
                    line,
                    re.IGNORECASE
                )

                if match:

                    value = clean(
                        line[match.end():].strip(" :-#")
                    )

                    if value:
                        return value

                    if index + 1 < len(lines):
                        return lines[index + 1]

        return None

    customer = find([
        r"customer\s*name",
        r"customer"
    ])

    model = find([
        r"machine\s*model",
        r"model\s*of\s*machine"
    ])

    number = find([
        r"machine\s*(?:no\.?|number|#)",
        r"machine\s*serial\s*(?:no\.?|number)"
    ])

    return customer, model, number


def detect_table_rows(binary):
    """
    Detect ruled cells and attempt to extract
    Component Name, Model, Make and Type.

    This is a first-pass detector. All results
    must be checked against the original PDF.
    """

    height, width = binary.shape

    inverted = 255 - binary

    horizontal_kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT,
        (max(25, width // 35), 1)
    )

    vertical_kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT,
        (1, max(25, height // 35))
    )

    horizontal = cv2.morphologyEx(
        inverted,
        cv2.MORPH_OPEN,
        horizontal_kernel
    )

    vertical = cv2.morphologyEx(
        inverted,
        cv2.MORPH_OPEN,
        vertical_kernel
    )

    grid = cv2.add(horizontal, vertical)

    contours, _ = cv2.findContours(
        grid,
        cv2.RETR_TREE,
        cv2.CHAIN_APPROX_SIMPLE
    )

    boxes = []

    for contour in contours:

        x, y, w, h = cv2.boundingRect(contour)

        if (
            w > 30
            and h > 12
            and w < width * 0.98
            and h < height * 0.5
        ):

            duplicate = any(
                abs(x - bx) < 5
                and abs(y - by) < 5
                and abs(w - bw) < 10
                and abs(h - bh) < 10
                for bx, by, bw, bh in boxes
            )

            if not duplicate:
                boxes.append((x, y, w, h))

    # Group cells by vertical position.

    groups = []

    for box in sorted(boxes, key=lambda item: (item[1], item[0])):

        x, y, w, h = box
        center_y = y + h / 2

        group = next(
            (
                item for item in groups
                if abs(item[0] - center_y) < max(12, h * 0.45)
            ),
            None
        )

        if group is None:
            group = [center_y, []]
            groups.append(group)

        group[1].append(box)

    records = []

    for _, cells in sorted(groups, key=lambda item: item[0]):

        cells.sort(key=lambda item: item[0])

        if len(cells) < 3:
            continue

        values = []

        for x, y, w, h in cells:

            crop = binary[
                max(0, y + 3):min(height, y + h - 3),
                max(0, x + 3):min(width, x + w - 3)
            ]

            if crop.size:
                value = clean(ocr(crop, 7))
            else:
                value = ""

            values.append(value)

        records.append(values)

    # Identify table headers.

    header = None
    results = []

    for values in records:

        combined = " ".join(values).lower()

        if (
            "model" in combined
            and "make" in combined
            and "type" in combined
        ):
            header = [value.lower() for value in values]
            continue

        if not header:
            continue

        def find_column(words):

            for index, value in enumerate(header):

                if any(word in value for word in words):
                    return index

            return None

        model_index = find_column(["model"])
        make_index = find_column(["make", "manufacturer"])
        type_index = find_column(["type"])

        if any(index is None for index in (
            model_index,
            make_index,
            type_index
        )):
            continue

        def get_value(index):

            if index < len(values):
                return values[index]

            return ""

        component_name = get_value(0)
        component_model = get_value(model_index)
        component_make = get_value(make_index)
        component_type = get_value(type_index)

        if any((
            component_name,
            component_model,
            component_make,
            component_type
        )):

            results.append((
                component_name,
                component_model,
                component_make,
                component_type
            ))

    return results


def process_pdf(pdf_path):

    init_db()

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(pdf_path)

    print(f"\nProcessing: {pdf_path.name}")

    pages = render_pdf(pdf_path)

    all_page_text = []
    processed_pages = []

    for page_number, image_path in pages:

        print(f"OCR page {page_number}/{len(pages)}")

        image = cv2.imread(str(image_path))

        if image is None:
            print(f"Could not read page {page_number}")
            continue

        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )

        denoised = cv2.fastNlMeansDenoising(
            gray,
            None,
            10,
            7,
            21
        )

        binary = cv2.adaptiveThreshold(
            denoised,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31,
            11
        )

        text1 = ocr(gray, 6)
        text2 = ocr(binary, 6)

        text = (
            text1
            if len(text1.strip()) >= len(text2.strip())
            else text2
        )

        all_page_text.append(
            f"\n--- PAGE {page_number} ---\n{text}"
        )

        processed_pages.append(
            (page_number, image_path, text, binary)
        )

    combined_text = "\n".join(all_page_text)

    customer, model, number = machine_fields(
        combined_text
    )

    machine_id = save_machine(
        customer,
        model,
        number,
        pdf_path.name
    )

    raw_path = PAGE_DIR / (
        f"{pdf_path.stem}_raw_ocr.txt"
    )

    raw_path.write_text(
        combined_text,
        encoding="utf-8"
    )

    component_count = 0

    for page_number, image_path, text, binary in processed_pages:

        relative_path = str(
            image_path.relative_to(PDF_DIR.parent)
        )

        save_page(
            machine_id,
            page_number,
            text,
            relative_path
        )

        rows = detect_table_rows(binary)

        for row in rows:

            save_component(
                machine_id,
                *row,
                page_number
            )

            component_count += 1

    print("\n========== EXTRACTION SUMMARY ==========")

    print("PDF:", pdf_path.name)
    print("Machine ID:", machine_id)
    print("Customer:", customer)
    print("Machine Model:", model)
    print("Machine Number:", number)
    print("Component rows:", component_count)
    print("Raw OCR:", raw_path)

    print("========================================\n")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--pdf",
        help="Optional path to a specific PDF"
    )

    args = parser.parse_args()

    if args.pdf:

        process_pdf(Path(args.pdf))

    else:

        PDF_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        pdf_files = sorted(
            PDF_DIR.glob("*.pdf")
        )

        if not pdf_files:

            print("No PDF files found:", PDF_DIR)

        else:

            for pdf_file in pdf_files:

                process_pdf(pdf_file)

