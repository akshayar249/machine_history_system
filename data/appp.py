
import streamlit as st
import pandas as pd
import os
import re

# ---------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------

st.set_page_config(
    page_title="Machine History Search",
    page_icon="🏭",
    layout="wide"
)

st.title("🏭 Machine History Management System")
st.write("Search and retrieve machine history records.")

# ---------------------------------------
# FILE PATHS
# ---------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

EXCEL_PATH = os.path.join(
    BASE_DIR, "data", "formatted.xlsx"
)

PDF_FOLDER = os.path.join(
    BASE_DIR, "data", "pdfs"
)

# ---------------------------------------
# LOAD EXCEL DATA
# ---------------------------------------

@st.cache_data
def load_data():

    sheets = pd.read_excel(
        EXCEL_PATH,
        sheet_name=None,
        dtype=str
    )

    for name in sheets:
        sheets[name] = sheets[name].fillna("")

    return sheets


if not os.path.exists(EXCEL_PATH):
    st.error("formatted.xlsx not found.")
    st.stop()

try:
    sheets = load_data()

except Exception as e:
    st.error(f"Error loading Excel: {e}")
    st.stop()


# ---------------------------------------
# LOAD WORKSHEETS
# ---------------------------------------

details = sheets.get(
    "Machine Details",
    pd.DataFrame()
)

history = sheets.get(
    "Machine History Full",
    pd.DataFrame()
)

history_lines = sheets.get(
    "History Lines",
    pd.DataFrame()
)

components = sheets.get(
    "Component Register",
    pd.DataFrame()
)

pages = sheets.get(
    "All PDF Pages",
    pd.DataFrame()
)


if details.empty:
    st.error("Machine Details sheet is empty.")
    st.stop()


# ---------------------------------------
# COLUMN IDENTIFICATION
# ---------------------------------------

def find_column(df, candidates):

    for col in df.columns:

        normalized = re.sub(
            r"[^a-z0-9]",
            "",
            str(col).lower()
        )

        for candidate in candidates:

            target = re.sub(
                r"[^a-z0-9]",
                "",
                candidate.lower()
            )

            if normalized == target:
                return col

    return None


customer_col = find_column(
    details,
    ["Customer Name", "Customer"]
)

model_col = find_column(
    details,
    ["Machine Model Number", "Model Number",
     "Machine Model", "Model"]
)

machine_col = find_column(
    details,
    ["Machine Number", "Machine No",
     "Serial Number", "Serial No"]
)

pdf_col = find_column(
    details,
    ["Source PDF", "PDF File",
     "Filename", "Source File"]
)


# ---------------------------------------
# SEARCH INTERFACE
# ---------------------------------------

st.sidebar.header("Machine Search")

search_type = st.sidebar.selectbox(
    "Search by",
    [
        "All Fields",
        "Customer Name",
        "Machine Model Number",
        "Machine Number",
        "PDF Filename"
    ]
)

search_query = st.sidebar.text_input(
    "Enter search keyword"
)

filtered = details.copy()

column_map = {
    "Customer Name": customer_col,
    "Machine Model Number": model_col,
    "Machine Number": machine_col,
    "PDF Filename": pdf_col
}

if search_query:

    if search_type == "All Fields":

        mask = pd.Series(
            False,
            index=filtered.index
        )

        for col in filtered.columns:

            mask |= filtered[col].astype(str).str.contains(
                re.escape(search_query),
                case=False,
                na=False
            )

        filtered = filtered[mask]

    else:

        col = column_map.get(search_type)

        if col:

            filtered = filtered[
                filtered[col].astype(str).str.contains(
                    re.escape(search_query),
                    case=False,
                    na=False
                )
            ]


# ---------------------------------------
# DASHBOARD METRICS
# ---------------------------------------

c1, c2, c3 = st.columns(3)

c1.metric(
    "Total Machine Records",
    len(details)
)

c2.metric(
    "Matching Records",
    len(filtered)
)

pdf_files = []

if os.path.exists(PDF_FOLDER):

    pdf_files = [
        f for f in os.listdir(PDF_FOLDER)
        if f.lower().endswith(".pdf")
    ]

c3.metric(
    "PDF Documents",
    len(pdf_files)
)


# ---------------------------------------
# SEARCH RESULTS
# ---------------------------------------

st.divider()

st.subheader("Machine Search Results")

if filtered.empty:

    st.warning("No matching machine records found.")

    st.stop()


st.dataframe(
    filtered,
    use_container_width=True,
    hide_index=True
)


# ---------------------------------------
# SELECT MACHINE
# ---------------------------------------

def make_label(row):

    fields = []

    for col in [
        customer_col,
        model_col,
        machine_col
    ]:

        if col and str(row.get(col, "")).strip():

            fields.append(
                str(row[col]).strip()
            )

    return " | ".join(fields)


options = {}

for idx, row in filtered.iterrows():

    label = make_label(row)

    if pdf_col:

        filename = str(
            row.get(pdf_col, "")
        ).strip()

        if filename:
            label += " | " + filename

    options[label or f"Record {idx}"] = idx


selected = st.selectbox(
    "Select a machine to view its history",
    list(options.keys())
)

selected_index = options[selected]

record = details.loc[selected_index]


# ---------------------------------------
# MACHINE DETAILS
# ---------------------------------------

st.divider()

st.header("Machine Information")

left, middle, right = st.columns(3)

left.metric(
    "Customer Name",
    str(record.get(customer_col, ""))
    if customer_col else "N/A"
)

middle.metric(
    "Machine Model",
    str(record.get(model_col, ""))
    if model_col else "N/A"
)

right.metric(
    "Machine Number",
    str(record.get(machine_col, ""))
    if machine_col else "N/A"
)


with st.expander(
    "View all machine details",
    expanded=True
):

    for col in details.columns:

        value = str(record.get(col, "")).strip()

        if value:

            st.write(
                f"**{col}:** {value}"
            )


# ---------------------------------------
# IDENTIFY SOURCE PDF
# ---------------------------------------

source_pdf = ""

if pdf_col:

    source_pdf = str(
        record.get(pdf_col, "")
    ).strip()


def filter_pdf(df):

    if df.empty or not source_pdf:
        return df.iloc[0:0]

    source_col = find_column(
        df,
        [
            "Source PDF",
            "PDF File",
            "Filename",
            "Source File"
        ]
    )

    if not source_col:
        return df.iloc[0:0]

    return df[
        df[source_col].astype(str).str.strip().str.lower()
        == source_pdf.lower()
    ]


# ---------------------------------------
# ORIGINAL PDF
# ---------------------------------------

st.divider()

st.header("Original Machine History Document")

pdf_path = os.path.join(
    PDF_FOLDER,
    os.path.basename(source_pdf)
)

if source_pdf and os.path.isfile(pdf_path):

    with open(pdf_path, "rb") as file:

        st.download_button(
            "Download Original PDF",
            data=file.read(),
            file_name=os.path.basename(source_pdf),
            mime="application/pdf"
        )

else:

    st.warning(
        f"Original PDF not found: {source_pdf}"
    )


# ---------------------------------------
# HISTORY AND COMPONENT TABS
# ---------------------------------------

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "Machine History",
        "History Line Search",
        "Components",
        "PDF Page Information"
    ]
)


# ---------------------------------------
# MACHINE HISTORY
# ---------------------------------------

with tab1:

    st.subheader("Complete Machine History")

    machine_history = filter_pdf(history)

    if machine_history.empty:

        st.info("No history records available.")

    else:

        for i, (_, row) in enumerate(
            machine_history.iterrows()
        ):

            page_col = find_column(
                machine_history,
                ["Page Number", "Page"]
            )

            text_col = find_column(
                machine_history,
                [
                    "Complete Page Text",
                    "Page Text",
                    "Extracted Text"
                ]
            )

            page = (
                row.get(page_col, i + 1)
                if page_col else i + 1
            )

            with st.expander(
                f"History - Page {page}"
            ):

                if text_col:

                    st.text_area(
                        "Extracted Information",
                        str(row.get(text_col, "")),
                        height=250,
                        key=f"history_{selected_index}_{i}"
                    )

                else:

                    st.write(row.to_dict())


# ---------------------------------------
# HISTORY LINE SEARCH
# ---------------------------------------

with tab2:

    st.subheader("Search History Entries")

    machine_lines = filter_pdf(history_lines)

    keyword = st.text_input(
        "Search dates, service details, parts or descriptions"
    )

    if keyword and not machine_lines.empty:

        text_col = find_column(
            machine_lines,
            ["Extracted Text", "Text", "History Line"]
        )

        if text_col:

            machine_lines = machine_lines[
                machine_lines[text_col].astype(str).str.contains(
                    re.escape(keyword),
                    case=False,
                    na=False
                )
            ]

    if machine_lines.empty:

        st.info("No matching history entries.")

    else:

        st.dataframe(
            machine_lines,
            use_container_width=True,
            hide_index=True
        )


# ---------------------------------------
# COMPONENT REGISTER
# ---------------------------------------

with tab3:

    st.subheader("Machine Components")

    machine_components = filter_pdf(components)

    component_keyword = st.text_input(
        "Search component information"
    )

    if component_keyword and not machine_components.empty:

        mask = pd.Series(
            False,
            index=machine_components.index
        )

        for col in machine_components.columns:

            mask |= machine_components[col].astype(str).str.contains(
                re.escape(component_keyword),
                case=False,
                na=False
            )

        machine_components = machine_components[mask]

    if machine_components.empty:

        st.info("No component records found.")

    else:

        st.dataframe(
            machine_components,
            use_container_width=True,
            hide_index=True
        )


# ---------------------------------------
# PDF PAGE INFORMATION
# ---------------------------------------

with tab4:

    st.subheader("Extracted PDF Page Information")

    machine_pages = filter_pdf(pages)

    page_keyword = st.text_input(
        "Search all extracted page text"
    )

    if page_keyword and not machine_pages.empty:

        text_col = find_column(
            machine_pages,
            [
                "Complete Extracted Text",
                "Extracted Text",
                "Page Text"
            ]
        )

        if text_col:

            machine_pages = machine_pages[
                machine_pages[text_col].astype(str).str.contains(
                    re.escape(page_keyword),
                    case=False,
                    na=False
                )
            ]

    if machine_pages.empty:

        st.info("No matching PDF pages.")

    else:

        st.dataframe(
            machine_pages,
            use_container_width=True,
            hide_index=True
        )


# ---------------------------------------
# FOOTER
# ---------------------------------------

st.divider()

st.caption(
    "Internal Machine History Management System | "
    "Verify critical extracted information against original PDFs."
)
