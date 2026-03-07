# 🩸 Hemaclass Data Cleaner: A Comprehensive Line-by-Line Guide

Welcome to the comprehensive guide to the **Hemaclass Data Cleaner** application! This highly professional document will walk you through the `app.py` script, breaking down the code line-by-line (and section-by-section). We will explore how modern Python tools like **Streamlit** (for the UI), **Pandas** (for data manipulation), and **NumPy** (for mathematical operations and missing data representation) are seamlessly integrated to create a robust data cleaning pipeline.

---

## 1. Imports and Setup

```python
import streamlit as st
import pandas as pd
import numpy as np
import re
```
*   `import streamlit as st`: Streamlit is the core framework used to build the interactive web application interface instantly.
*   `import pandas as pd`: Pandas is the workhorse for data manipulation. It structures our clinical data into highly efficient DataFrame objects.
*   `import numpy as np`: NumPy provides support for mathematical operations and, crucially in this app, the `np.nan` object which represents missing or invalid data.
*   `import re`: The regular expressions module, used for advanced string matching and manipulation.

---

## 2. Page Configuration

```python
# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Hemaclass Data Cleaner",
    page_icon="🩸",
    layout="wide"
)
```
*   `st.set_page_config(...)`: This Streamlit function must be the first Streamlit command called. It configures the web page's title (seen in the browser tab), sets a custom favicon (`🩸`), and forces the layout to use the full width of the screen (`layout="wide"`).

---

## 3. The Data Cleaning Engine (`HemaclassDataCleaner` class)

This class encapsulates all the data cleaning logic using Pandas and NumPy.

```python
class HemaclassDataCleaner:
    """Automated data cleaner specifically tailored for the Hemaclass dataset."""
    def __init__(self, df):
        self.df = df.copy()
```
*   `def __init__(self, df)`: The constructor initializes the class with a dataset.
*   `self.df = df.copy()`: A copy of the Pandas DataFrame (`df`) is stored to prevent modifying the original data unexpectedly.

### Orchestrating the Pipeline
```python
    def clean(self):
        self._drop_empty_and_duplicates()
        self._clean_strings()
        self._clean_age_and_sex()
        self._clean_dates()
        self._clean_booleans()
        self._clean_numerics()
        self._cross_validate()
        return self.df
```
*   `def clean(self)`: This acts as the main orchestrator method. It sequentially calls specialized internal methods (`_drop_...`, `_clean_...`) to process the DataFrame and finally returns the fully cleaned dataset.

### Handling Structural Messiness
```python
    def _drop_empty_and_duplicates(self):
        # Drop completely empty columns and rows
        self.df.dropna(how='all', axis=1, inplace=True)
        self.df.dropna(how='all', axis=0, inplace=True)
        # Drop identical duplicate records
        self.df.drop_duplicates(inplace=True)
```
*   `self.df.dropna(...)`: A powerful Pandas method to handle missing data.
    *   `how='all', axis=1`: Drops entire columns (axis=1) if *all* their values are missing.
    *   `how='all', axis=0`: Drops entire rows (axis=0) if *all* their values are missing.
*   `inplace=True`: Modifies the DataFrame directly in memory rather than returning a new object.
*   `self.df.drop_duplicates(...)`: Identifies and removes exact duplicate rows from the dataset.

### Standardizing Strings
```python
    def _clean_strings(self):
        # Strip whitespace from string columns
        for col in self.df.select_dtypes(include=['object']).columns:
            self.df[col] = self.df[col].apply(lambda x: str(x).strip() if pd.notnull(x) else x)
            # Convert 'nan' strings to actual np.nan
            self.df[col] = self.df[col].replace({'nan': np.nan, 'None': np.nan, 'invalid': np.nan})
```
*   `self.df.select_dtypes(include=['object'])`: Filters the DataFrame to only look at columns containing string/text data.
*   `.apply(lambda x: str(x).strip() ...)`: Applies a quick function to strip leading and trailing whitespace from every string, provided it is not null (`pd.notnull(x)`).
*   `.replace(...)`: Maps string placeholders for missing data (like `'nan'` or `'invalid'`) to the standardized missing value marker, `np.nan`.

### Demographics: Age and Sex
```python
    def _clean_age_and_sex(self):
        # Clean Age: Set negative and impossible ages (>120) to NaN
        if 'age' in self.df.columns:
            self.df['age'] = pd.to_numeric(self.df['age'], errors='coerce')
            self.df.loc[(self.df['age'] < 0) | (self.df['age'] > 120), 'age'] = np.nan
```
*   `pd.to_numeric(..., errors='coerce')`: Converts the 'age' column to numeric values. If it encounters a non-numeric string, it coerces it into `NaN`.
*   `self.df.loc[...]`: Uses Pandas label-based indexing to find rows where age is logically impossible (< 0 or > 120) and overwrites them with `np.nan`.

```python
        # Clean Sex: Standardize to Male/Female
        if 'sex' in self.df.columns:
            sex_map = {
                'm': 'Male', 'male': 'Male', '1': 'Male',
                'f': 'Female', 'female': 'Female', 'woman': 'Female', '0': 'Female'
            }
            self.df['sex'] = self.df['sex'].str.lower().map(sex_map).fillna(self.df['sex'])
```
*   `sex_map`: A dictionary used to map various messy string inputs to clean "Male" or "Female" categories.
*   `.str.lower().map(...)`: Converts all text to lowercase and translates it using the dictionary.
*   `.fillna(...)`: Ensures that if a value wasn't in our dictionary, it retains its original value rather than being wiped out.

### Date Normalization
```python
    def _clean_dates(self):
        if 'dob' in self.df.columns:
            # Parse dates and coerce invalid dates to NaT (Not a Time)
            self.df['dob'] = pd.to_datetime(self.df['dob'], errors='coerce').dt.strftime('%Y-%m-%d')
```
*   `pd.to_datetime(...)`: A highly intelligent Pandas function that parses various date string formats into standard datetime objects. Invalid dates become `NaT` (Not a Time).
*   `.dt.strftime('%Y-%m-%d')`: Formats the parsed dates back into a uniform string structure (Year-Month-Day).

### Boolean Formatting
```python
    def _clean_booleans(self):
        bool_cols = [ 'diabetes', 'hypertension', ... ] # (List abbreviated)

        def to_bool(val):
            if pd.isna(val): return np.nan
            val_str = str(val).strip().lower()
            if val_str in ['true', '1', '1.0', 'yes', 'y', 't', 'pos', 'positive']: return True
            if val_str in ['false', '0', '0.0', 'no', 'n', 'f', 'neg', 'negative']: return False
            return np.nan

        for col in bool_cols:
            if col in self.df.columns:
                self.df[col] = self.df[col].apply(to_bool)
```
*   `pd.isna(val)`: A Pandas check to see if a value is missing.
*   The `to_bool` function normalizes diverse positive indicators (like 'yes', '1', 'pos') to a standard Python `True` boolean, and negative indicators to `False`. It's applied via the `.apply()` method across relevant columns.

### Numeric Outlier Mitigation
```python
    def _clean_numerics(self):
        def clamp_numeric(col_name, min_val, max_val):
            if col_name in self.df.columns:
                self.df[col_name] = pd.to_numeric(self.df[col_name], errors='coerce')
                self.df.loc[(self.df[col_name] < min_val) | (self.df[col_name] > max_val), col_name] = np.nan

        clamp_numeric('hb_a', 0, 100)
        # ... (other clamping applied to vitals)
```
*   `clamp_numeric`: A helper function to enforce logical clinical boundaries (e.g., temperatures must be between 30 and 45 Celsius). Out-of-bounds metrics are converted to `np.nan` via `.loc` masking.

### Rule-based Cross Validation
```python
    def _cross_validate(self):
        # Clinical Rule: If Hemoglobin is significantly low (< 10.0), flag Pallor as True
        if 'hb' in self.df.columns and 'pallor' in self.df.columns:
            self.df['hb'] = pd.to_numeric(self.df['hb'], errors='coerce')
            mask = (self.df['hb'] < 10.0)
            self.df.loc[mask, 'pallor'] = True
```
*   `mask = (self.df['hb'] < 10.0)`: Creates a boolean mask array representing rows where the patient's hemoglobin is critically low.
*   `self.df.loc[mask, 'pallor'] = True`: For those specific rows, it cross-references the 'pallor' symptom column and enforces it to `True`.

---

## 4. The Streamlit User Interface (`main` function)

The `main()` function constructs the interactive visual dashboard that users engage with.

### Initialization & State Management
```python
def main():
    st.title("🩸 Hemaclass Data Cleaning Pipeline")
    st.markdown("Upload your clinical records export...")

    if 'use_mock' not in st.session_state:
        st.session_state.use_mock = False
    if 'cleaned_df' not in st.session_state:
        st.session_state.cleaned_df = None
```
*   `st.title(...)` and `st.markdown(...)`: Render the large page header and description text.
*   `st.session_state`: A critical Streamlit feature. Because Streamlit scripts rerun entirely upon any user interaction, `session_state` allows variables (like whether we are using mock data, or the cleaned dataset itself) to persist across those reruns.

### Layout & Inputs
```python
    col1, col2 = st.columns([2, 1])
    with col1:
        uploaded_file = st.file_uploader("Upload Raw CSV", type=["csv"])
    with col2:
        st.write("<br>", unsafe_allow_html=True)
        st.button("🧪 Generate & Load Mock Dataset", on_click=set_mock_true)
```
*   `st.columns([2, 1])`: Creates a side-by-side layout, with the left column being twice as wide as the right column.
*   `st.file_uploader(...)`: Provides a drag-and-drop widget for the user to upload CSV files.
*   `st.button(..., on_click=set_mock_true)`: Displays a clickable button. When clicked, it executes the `set_mock_true` callback function to update our `session_state`.

### Data Ingestion
```python
    raw_df = None
    if uploaded_file is not None:
        st.session_state.use_mock = False
        raw_df = pd.read_csv(uploaded_file)
    elif st.session_state.use_mock:
        raw_df = generate_mock_data()
```
*   `pd.read_csv(...)`: A core Pandas function that instantly parses the uploaded CSV file into a working DataFrame object.
*   If no file is uploaded but the mock button was clicked, it relies on our `generate_mock_data()` helper to supply a synthetic messy dataset.

### Pipeline Execution
```python
    if st.button("✨ Run Cleaning Pipeline", type="primary"):
        if raw_df is not None:
            try:
                cleaner = HemaclassDataCleaner(raw_df)
                cleaned_df = cleaner.clean()
                st.session_state.cleaned_df = cleaned_df
                st.success("✅ Data cleaned successfully!")
            except Exception as e:
                st.error(f"❌ Error occurred during cleaning: {str(e)}")
```
*   `st.button(..., type="primary")`: A primary button (usually highlighted in color) that triggers the core action.
*   When clicked, the script instantiates the `HemaclassDataCleaner`, calls `.clean()`, stores the result in the session state, and renders a green `st.success(...)` banner. If Python encounters an error, it is gracefully caught and displayed via a red `st.error(...)` banner.

### Visualizing Results & Exporting
```python
    if raw_df is not None or st.session_state.cleaned_df is not None:
        tab1, tab2 = st.tabs(["Preview Original Data", "Preview Cleaned Data"])

        with tab1:
            if raw_df is not None:
                st.dataframe(raw_df.head(10), use_container_width=True)
                st.caption(f"Original Dimensions: {raw_df.shape[0]} rows, {raw_df.shape[1]} cols")
```
*   `st.tabs(...)`: Organizes the UI into clickable tabs, saving vertical space.
*   `st.dataframe(...)`: A highly interactive tabular view to render the Pandas DataFrame in the browser. `.head(10)` ensures we only load the top 10 rows for a quick preview.
*   `st.caption(...)`: Renders small, muted text to display the DataFrame's dimensions (`.shape`).

```python
        with tab2:
            if st.session_state.cleaned_df is not None:
                # ... (displays the cleaned dataframe)
                csv_buffer = st.session_state.cleaned_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Cleaned CSV File",
                    data=csv_buffer,
                    file_name="cleaned_data_output.csv",
                    mime="text/csv",
                    type="primary"
                )
```
*   `.to_csv(index=False).encode('utf-8')`: Converts the cleaned Pandas DataFrame back into raw CSV string format, omitting the row index, and encodes it as bytes.
*   `st.download_button(...)`: A specialized Streamlit button that prompts the user's browser to download the provided bytes (`data=csv_buffer`) as a file.

---
**Summary**: By combining **Streamlit's** rapid UI components with **Pandas'** and **NumPy's** robust data manipulation capabilities, `app.py` delivers a professional-grade, interactive data cleaning tool in under 250 lines of code.
