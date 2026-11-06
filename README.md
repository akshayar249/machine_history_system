# Handwritten Machine Information Sheet Digitization and Search System

### Automated Data Extraction, Structuring and Retrieval of Historical Machine Records

**Repository:** [machine_history_system](https://github.com/akshayar249/machine_history_system)

---

## 1. Project Overview

The Handwritten Machine Information Sheet Digitization and Search System is a Python-based project developed to digitize historical machine information sheets maintained in handwritten PDF documents.

The system uses Optical Character Recognition (OCR) and image processing techniques to recognize information from scanned documents, extract important machine identification details, and organize the available information into a structured Excel workbook.

A Streamlit-based web application provides an interface for employees to search and retrieve machine records using customer names, machine model numbers, and machine numbers.

The current implementation has been developed and tested using **11 original handwritten machine information sheet PDFs**.

## 2. Project Objectives

- Digitize handwritten historical machine information sheets.
- Automate text recognition and information extraction from PDF documents.
- Extract important machine identification fields.
- Organize extracted information into a structured Excel database.
- Develop a searchable web application for machine record retrieval.
- Provide access to recognized machine-history information and original PDF documents.
- Establish a foundation for detailed component-wise machine-history extraction.

## 3. Technologies Used

| Technology | Application |
|---|---|
| Python | Core programming language |
| PyMuPDF | PDF document loading and page processing |
| OpenCV | Image preprocessing and enhancement |
| Tesseract OCR | Optical Character Recognition |
| PyTesseract | Python interface for Tesseract OCR |
| Pandas | Data processing and organization |
| OpenPyXL | Excel workbook handling |
| Streamlit | Web application development |
| Microsoft Excel | Structured data storage |

## 4. System Workflow

The system follows an end-to-end document digitization and information retrieval workflow.

1. **PDF Input:** Load the original handwritten machine information sheet PDFs.
2. **PDF Processing:** Extract individual pages using PyMuPDF.
3. **Image Preprocessing:** Apply grayscale conversion, contrast enhancement, noise reduction and thresholding using OpenCV.
4. **OCR Recognition:** Recognize handwritten and printed text using Tesseract OCR.
5. **Field Extraction:** Identify Customer Name, Machine Model Number and Machine Number.
6. **Data Organization:** Process and organize extracted information using Pandas.
7. **Excel Integration:** Store the available information in a structured workbook named `formatted.xlsx`.
8. **Application Development:** Integrate the Excel workbook with the Streamlit application.
9. **Search and Retrieval:** Allow employees to search for machine records and access the associated information and original PDF documents.

## 5. Current Implementation

The system has been tested using 11 original handwritten machine information sheet PDFs.

### 5.1 Successfully Extracted Information

The current implementation successfully extracts the following three primary machine identification fields across the 11 documents:

- Customer Name
- Machine Model Number
- Machine Number

### 5.2 Excel Database Organization

The extracted information is organized into `formatted.xlsx`, which contains the following worksheets:

| Worksheet | Description |
|---|---|
| Machine Details | Primary machine identification information |
| Machine History Full | Recognized machine-history text |
| History Lines | Machine-history information arranged into individual lines |
| Component Register | Worksheet intended for component-related information |
| All PDF Pages | Information associated with individual processed PDF pages |

The workbook serves as the structured data source for the Streamlit application.

### 5.3 Machine-History Information

The OCR implementation also recognizes portions of the handwritten machine-history sections.

However, the recognized text is not yet consistently mapped to individual component names and their corresponding Make, Model and Type values.

Accurate component-wise key-value extraction remains an area for further development.

## 6. Application Features

The Streamlit-based application provides the following functionalities:

- Dashboard displaying machine record statistics.
- Search by Customer Name.
- Search by Machine Model Number.
- Search by Machine Number.
- Additional search options for available identifiers.
- Display of matching machine records.
- Detailed customer and machine information.
- Access to recognized machine-history text.
- Search functionality for individual history lines.
- Component register viewing.
- Page-wise OCR information access.
- Access to original PDF documents for verification.

## 7. Project Structure

```text
machine_history_system/
│
├── appp.py
├── app.py
├── config.py
├── database.py
├── extract_infosheets.py
│
├── formatted.xlsx
├── M11-467-1_formatted.xlsx
│
├── requirements.txt
├── README.md
├── .gitignore
│
├── data/
│   └── pdfs/
│       ├── M11-467-1.pdf
│       ├── M11-719.pdf
│       └── ... (other original PDF documents)
│
├── static/
│   └── Application assets
│
└── templates/
    └── HTML templates
```

*Note: This represents the main project organization. Actual filenames and subfolders may vary depending on the repository contents.*

## 8. Installation and Setup

Follow these steps to run the application locally.

### Step 1: Clone the Repository

```bash
git clone https://github.com/akshayar249/machine_history_system.git
```

### Step 2: Navigate to the Project Directory

```bash
cd machine_history_system
```

### Step 3: Create a Virtual Environment

```bash
python -m venv .venv
```

Activate the environment on Windows:

```bash
.venv\Scripts\activate
```

### Step 4: Install Dependencies

```bash
python -m pip install --upgrade pip
```

Install the required Python libraries:

```bash
pip install -r requirements.txt
```

### Step 5: Install Tesseract OCR

Tesseract OCR must be installed separately because PyTesseract acts as the Python interface to the OCR engine.

For Windows, download Tesseract OCR from:

https://github.com/UB-Mannheim/tesseract/wiki

Ensure that the Tesseract executable is correctly configured and accessible from your Python environment.

### Step 6: Configure Input Documents

Place the original machine information sheet PDF documents inside:

```text
data/pdfs/
```

Ensure that the required Excel workbook, `formatted.xlsx`, is available in the project directory or the configured location.

### Step 7: Run the Streamlit Application

Execute the following command from the project directory:

```bash
python -m streamlit run appp.py
```

Alternatively:

```bash
streamlit run appp.py
```

The application will start locally and open in your default web browser.

**Default local application address:**

http://localhost:8501

## 9. Current Limitations and Challenges

Several challenges were encountered during the development and testing of the system.

### 9.1 Handwriting Variations

Variations in handwriting styles, character shapes and spacing affect OCR recognition accuracy.

### 9.2 Inconsistent Document Layouts

The arrangement of information differs across the handwritten machine information sheets, making it difficult to apply a single extraction pattern to every document.

### 9.3 Machine-History Key-Value Mapping

The machine-history sections contain component names and their corresponding Make, Model and Type values.

Although portions of the text are recognized by OCR, the system does not consistently preserve the original row-column relationships or associate each component with its correct values.

### 9.4 OCR Recognition Errors

Technical terms, component names and machine model numbers containing combinations of letters and numbers can be incorrectly recognized or fragmented.

### 9.5 Data Organization

The extracted information must maintain its association with the corresponding source PDF to support reliable record retrieval and verification.

## 10. Future Enhancements

Future development will focus on improving machine-history component extraction and information organization.

Planned enhancements include:

- Improving recognition of handwritten component names and associated values.
- Identifying document layouts and table structures.
- Preserving row and column relationships in machine-history sections.
- Correctly mapping individual components with their corresponding Make, Model and Type values.
- Organizing component information into structured key-value records.
- Evaluating advanced OCR and document-understanding models.
- Validating extracted component information against original PDF documents.
- Integrating validated component-level information into the Excel workbook and search application.
- Extending the search application to support detailed component-wise machine-history retrieval.

## 11. Expected Outcome

The intended outcome is to establish a centralized digital system through which employees can search and retrieve historical machine information without manually browsing multiple handwritten PDF documents.

Further improvements in OCR recognition and component-level information extraction will extend the system to support more detailed machine-history retrieval.

## 12. Project Information

**Organization:** Ace Micromatics Group

**Department:** Marketing and Sales Division

**Project Category:** OCR-Based Document Digitization and Search System

**Input Dataset:** 11 Handwritten Machine Information Sheet PDFs

**Primary Application:** Streamlit

**Main Application File:** `appp.py`

**Repository:** https://github.com/akshayar249/machine_history_system

---

*Developed to improve the digitization, organization and retrieval of historical machine information records through OCR-based data extraction and searchable record management.*
