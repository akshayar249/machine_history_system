from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
PDF_DIR = BASE_DIR / 'data' / 'pdfs'
PAGE_DIR = BASE_DIR / 'data' / 'pages'
DB_PATH = BASE_DIR / 'data' / 'machine_history.db'
EXPORT_PATH = BASE_DIR / 'data' / 'extracted_data.xlsx'
RENDER_DPI = 300
# If Tesseract is not on PATH, uncomment and set this on Windows:
# import pytesseract
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
