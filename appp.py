
import streamlit as st
import pandas as pd
import os
import re

# =====================================================
# 1. STREAMLIT CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="Machine History Management System",
    page_icon="🏭",
    layout="wide"
)

st.title("🏭 Machine History Management System")
st.write("Search and retrieve machine history records.")

# =====================================================
# 2. AUTOMATIC FILE PATH DETECTION
# =====================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

EXCEL_LOCATIONS = [
    os.path.join(BASE_DIR, "formatted.xlsx"),
    os.path.join(BASE_DIR, "data", "formatted.xlsx"),
    os.path.join(BASE_DIR, "formatted", "formatted.xlsx")
]

EXCEL_PATH = next(
    (p for p in EXCEL_LOCATIONS if os.path.isfile(p)),
    None
)

PDF_LOCATIONS = [
    os.path.join(BASE_DIR, "data", "pdfs"),
    os.path.join(BASE_DIR, "pdfs"),
    os.path.join(BASE_DIR, "data")
]

if EXCEL_PATH is None:
    st.error("formatted.xlsx not found.")
    st.write("Checked locations:")
    for path in EXCEL_LOCATIONS:
        st.code(path)
    st.stop()

# =====================================================
# 3. LOAD EXCEL WORKBOOK
# =====================================================

@st.cache_data
def load_workbook(path, modified_time):

    workbook = pd.read_excel(
        path,
        sheet_name=None,
        dtype=str
    )

    for sheet in workbook:
        workbook[sheet] = workbook[sheet].fillna("")

    return workbook


try:
    sheets = load_workbook(
        EXCEL_PATH,
        os.path.getmtime(EXCEL_PATH)
    )

except Exception as error:
    st.error(f"Unable to load Excel workbook: {error}")
    st.stop()


# =====================================================
# 4. LOAD ALL WORKSHEETS
# =====================================================

details = sheets.get("Machine Details", pd.DataFrame())
history = sheets.get("Machine History Full", pd.DataFrame())
history_lines = sheets.get("History Lines", pd.DataFrame())
components = sheets.get("Component Register", pd.DataFrame())
all_pages = sheets.get("All PDF Pages", pd.DataFrame())

if details.empty:
    st.error("Machine Details sheet is empty.")
    st.stop()


# =====================================================
# 5. HELPER FUNCTIONS
# =====================================================

def search_dataframe(df, keyword):

    if df.empty:
        return df.copy()

    if not keyword:
        return df.copy()

    mask = pd.Series(False, index=df.index)

    for col in df.columns:
        mask |= df[col].astype(str).str.contains(
            re.escape(keyword),
            case=False,
            na=False
        )

    return df[mask].copy()


def filter_by_pdf(df, filename):

    if df.empty or not filename:
        return df.iloc[0:0].copy()

    if "Source PDF" not in df.columns:
        return df.iloc[0:0].copy()

    return df[
        df["Source PDF"].astype(str).str.strip().str.lower()
        == filename.strip().lower()
    ].copy()


def get_pdf_path(filename):

    if not filename:
        return None

    filename = os.path.basename(filename)

    for folder in PDF_LOCATIONS:

        path = os.path.join(folder, filename)

        if os.path.isfile(path):
            return path

    return None


def get_value(row, column):

    if column not in row.index:
        return "Not available"

    value = str(row[column]).strip()

    return value if value else "Not available"


# =====================================================
# 6. SIDEBAR SEARCH
# =====================================================

st.sidebar.title("🔎 Machine Search")

search_type = st.sidebar.selectbox(
    "Search Category",
    [
        "All Fields",
        "Customer Name",
        "Machine Model Number",
        "Machine Number",
        "Work Order Number",
        "Customer PO Number",
        "Order Acceptance Number",
        "PDF Filename"
    ]
)

search_keyword = st.sidebar.text_input(
    "Enter Search Keyword",
    placeholder="Customer / Model / Machine No."
)

column_mapping = {
    "Customer Name": "Customer Name",
    "Machine Model Number": "Machine Model Number",
    "Machine Number": "Machine Number",
    "Work Order Number": "Work Order Number",
    "Customer PO Number": "Customer PO Number",
    "Order Acceptance Number": "Order Acceptance Number",
    "PDF Filename": "Source PDF"
}


# =====================================================
# 7. FILTER MACHINE RECORDS
# =====================================================

filtered = details.copy()

if search_keyword:

    if search_type == "All Fields":

        filtered = search_dataframe(
            filtered,
            search_keyword
        )

    else:

        column = column_mapping[search_type]

        filtered = filtered[
            filtered[column].astype(str).str.contains(
                re.escape(search_keyword),
                case=False,
                na=False
            )
        ]


# =====================================================
# 8. DASHBOARD METRICS
# =====================================================

total_records = len(details)

total_customers = details[
    "Customer Name"
].replace("", pd.NA).nunique()

total_pdfs = details[
    "Source PDF"
].replace("", pd.NA).nunique()

available_pdfs = []

for folder in PDF_LOCATIONS:

    if os.path.isdir(folder):

        available_pdfs.extend([
            f for f in os.listdir(folder)
            if f.lower().endswith(".pdf")
        ])

available_pdfs = list(set(available_pdfs))

c1, c2, c3, c4 = st.columns(4)

c1.metric("Machine Records", total_records)
c2.metric("Customers", total_customers)
c3.metric("PDFs in Database", total_pdfs)
c4.metric("PDF Files Found", len(available_pdfs))

st.success("Excel database connected successfully!")

with st.expander("Database information"):
    st.write("Excel file:", EXCEL_PATH)
    st.write("PDF folders checked:", PDF_LOCATIONS)


# =====================================================
# 9. SEARCH RESULTS
# =====================================================

st.divider()

st.header("Machine Search Results")

st.write(f"Matching records: {len(filtered)}")

if filtered.empty:

    st.warning("No matching records found.")

    st.stop()

display_columns = [
    "Customer Name",
    "Machine Model Number",
    "Machine Number",
    "Machine Description",
    "Customer Location",
    "Work Order Number",
    "Source PDF"
]

st.dataframe(
    filtered[display_columns],
    use_container_width=True,
    hide_index=True
)


# =====================================================
# 10. SELECT MACHINE
# =====================================================

st.divider()

st.header("Select Machine Record")

options = []

for idx, row in filtered.iterrows():

    label = (
        f"{row['Customer Name']} | "
        f"{row['Machine Model Number']} | "
        f"{row['Machine Number']} | "
        f"{row['Source PDF']}"
    )

    options.append((label, idx))


selected_label = st.selectbox(
    "Choose a machine",
    [x[0] for x in options]
)

selected_index = next(
    x[1] for x in options
    if x[0] == selected_label
)

record = details.loc[selected_index]

source_pdf = str(
    record["Source PDF"]
).strip()


# =====================================================
# 11. MACHINE INFORMATION
# =====================================================

st.divider()

st.header("📋 Machine Information")

c1, c2, c3 = st.columns(3)

c1.metric(
    "Customer Name",
    get_value(record, "Customer Name")
)

c2.metric(
    "Machine Model",
    get_value(record, "Machine Model Number")
)

c3.metric(
    "Machine Number",
    get_value(record, "Machine Number")
)


# =====================================================
# 12. COMPLETE MACHINE DETAILS
# =====================================================

with st.expander(
    "View Complete Machine Details",
    expanded=True
):

    left, right = st.columns(2)

    with left:

        st.subheader("Customer Details")

        for col in [
            "Customer Name",
            "Customer Location",
            "Customer PO Number"
        ]:

            st.write(
                f"**{col}:** {get_value(record, col)}"
            )

    with right:

        st.subheader("Machine Details")

        for col in [
            "Machine Model Number",
            "Machine Number",
            "Machine Description",
            "Work Order Number",
            "Order Acceptance Number",
            "Total Pages",
            "History Pages",
            "History Detection Method"
        ]:

            st.write(
                f"**{col}:** {get_value(record, col)}"
            )


# =====================================================
# 13. ORIGINAL PDF DOCUMENT
# =====================================================

st.divider()

st.header("📄 Original Machine History Document")

pdf_path = get_pdf_path(source_pdf)

if pdf_path:

    with open(pdf_path, "rb") as file:

        pdf_bytes = file.read()

    st.download_button(
        "Download Original PDF",
        data=pdf_bytes,
        file_name=os.path.basename(pdf_path),
        mime="application/pdf"
    )

    st.success("Original PDF located successfully.")

else:

    st.warning(
        f"Original PDF not found: {source_pdf}"
    )

    st.info(
        "Place all original PDFs in the data/pdfs folder."
    )


# =====================================================
# 14. MACHINE HISTORY TABS
# =====================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "Machine History",
    "History Line Search",
    "Component Register",
    "All PDF Pages"
])


# =====================================================
# 15. COMPLETE MACHINE HISTORY
# =====================================================

with tab1:

    st.subheader("Complete Machine History")

    machine_history = filter_by_pdf(
        history,
        source_pdf
    )

    if machine_history.empty:

        st.info("No history records found.")

    else:

        for i, (_, row) in enumerate(
            machine_history.iterrows()
        ):

            page = get_value(row, "Page Number")
            method = get_value(row, "Extraction Method")

            with st.expander(
                f"Page {page} | {method}"
            ):

                st.text_area(
                    "Extracted Information",
                    value=str(
                        row.get("Complete Page Text", "")
                    ),
                    height=300,
                    key=f"history_{selected_index}_{i}"
                )


# =====================================================
# 16. HISTORY LINE SEARCH
# =====================================================

with tab2:

    st.subheader("Search Individual History Entries")

    machine_lines = filter_by_pdf(
        history_lines,
        source_pdf
    )

    keyword = st.text_input(
        "Search service history",
        placeholder="Enter date, part number or description"
    )

    if keyword:

        machine_lines = search_dataframe(
            machine_lines,
            keyword
        )

    if machine_lines.empty:

        st.info("No matching history entries.")

    else:

        st.write(
            f"Matching entries: {len(machine_lines)}"
        )

        st.dataframe(
            machine_lines,
            use_container_width=True,
            hide_index=True
        )


# =====================================================
# 17. COMPONENT REGISTER
# =====================================================

with tab3:

    st.subheader("Machine Component Information")

    machine_components = filter_by_pdf(
        components,
        source_pdf
    )

    component_search = st.text_input(
        "Search components",
        placeholder="Component / Model / Make / Rating"
    )

    if component_search:

        machine_components = search_dataframe(
            machine_components,
            component_search
        )

    if machine_components.empty:

        st.info("No component information found.")

    else:

        st.dataframe(
            machine_components,
            use_container_width=True,
            hide_index=True
        )


# =====================================================
# 18. ALL PDF PAGE INFORMATION
# =====================================================

with tab4:

    st.subheader("Extracted PDF Page Information")

    machine_pages = filter_by_pdf(
        all_pages,
        source_pdf
    )

    page_search = st.text_input(
        "Search PDF content",
        placeholder="Enter any word or phrase"
    )

    if page_search:

        machine_pages = search_dataframe(
            machine_pages,
            page_search
        )

    if machine_pages.empty:

        st.info("No matching PDF page information.")

    else:

        st.write(
            f"Matching pages: {len(machine_pages)}"
        )

        st.dataframe(
            machine_pages,
            use_container_width=True,
            hide_index=True
        )


# =====================================================
# 19. FOOTER
# =====================================================

st.divider()

st.caption(
    "Machine History Management System | Internal Employee Portal"
)

st.caption(
    "Verify important extracted information against the original PDF."
)
