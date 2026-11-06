# Machine History Database – starter project

This project creates OCR candidates from scanned PDFs, stores machine/component records in SQLite, and provides a searchable Flask website with manual correction.

## Setup (Windows PowerShell)
1. Install Python 3.10–3.12.
2. Install Tesseract OCR. If it is not on PATH, uncomment the Windows executable setting in `config.py` and set the correct path.
3. Open PowerShell in this folder and run:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Process the PDF
Copy `M11-467-1.pdf` into `data\pdfs\`, then run:

```powershell
python extract_infosheets.py
```

Or specify one PDF:

```powershell
python extract_infosheets.py --pdf "data\pdfs\M11-467-1.pdf"
```

## Start website

```powershell
python app.py
```

Open http://127.0.0.1:5000. Search by customer, machine model, or machine number. Open a machine to review and correct the component rows. Click a page number to compare against the scanned page. Export Excel using the link in the header.

## Accuracy note
Handwriting OCR and table reconstruction are difficult. This is a first-pass baseline using Tesseract and OpenCV line detection. It may miss unruled rows, handwritten text, faint lines, or misaligned columns. The website marks candidate component rows as needing review. Use the original page as the source of truth. The extraction rules should be calibrated against representative pages from this exact form before processing all PDFs in bulk.
