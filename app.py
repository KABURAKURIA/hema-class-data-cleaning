import streamlit as st
import pandas as pd
import numpy as np
import re

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Hemaclass Data Cleaner",
    page_icon="🩸",
    layout="wide"
)

# ==========================================
# 2. HEMACLASS DATA CLEANER IMPLEMENTATION
# ==========================================
class HemaclassDataCleaner:
    """Automated data cleaner specifically tailored for the Hemaclass dataset."""
    def __init__(self, df):
        self.df = df.copy()

    def clean(self):
        self._drop_empty_and_duplicates()
        self._clean_strings()
        self._clean_age_and_sex()
        self._clean_dates()
        self._clean_booleans()
        self._clean_numerics()
        self._cross_validate()
        return self.df

    def _drop_empty_and_duplicates(self):
        # Drop completely empty columns and rows
        self.df.dropna(how='all', axis=1, inplace=True)
        self.df.dropna(how='all', axis=0, inplace=True)
        # Drop identical duplicate records
        self.df.drop_duplicates(inplace=True)

    def _clean_strings(self):
        # Strip whitespace from string columns
        for col in self.df.select_dtypes(include=['object']).columns:
            self.df[col] = self.df[col].apply(lambda x: str(x).strip() if pd.notnull(x) else x)
            # Convert 'nan' strings to actual np.nan
            self.df[col] = self.df[col].replace({'nan': np.nan, 'None': np.nan, 'invalid': np.nan})

    def _clean_age_and_sex(self):
        # Clean Age: Set negative and impossible ages (>120) to NaN
        if 'age' in self.df.columns:
            self.df['age'] = pd.to_numeric(self.df['age'], errors='coerce')
            self.df.loc[(self.df['age'] < 0) | (self.df['age'] > 120), 'age'] = np.nan

        # Clean Sex: Standardize to Male/Female
        if 'sex' in self.df.columns:
            sex_map = {
                'm': 'Male', 'male': 'Male', '1': 'Male',
                'f': 'Female', 'female': 'Female', 'woman': 'Female', '0': 'Female'
            }
            self.df['sex'] = self.df['sex'].str.lower().map(sex_map).fillna(self.df['sex'])

    def _clean_dates(self):
        if 'dob' in self.df.columns:
            # Parse dates and coerce invalid dates to NaT (Not a Time)
            self.df['dob'] = pd.to_datetime(self.df['dob'], errors='coerce').dt.strftime('%Y-%m-%d')

    def _clean_booleans(self):
        # Common boolean/symptom columns
        bool_cols =[
            'diabetes', 'hypertension', 'sickle_cell_trait', 'malaria_history',
            'fever', 'chills', 'headache', 'muscle_aches', 'fatigue', 'loss_of_appetite',
            'jaundice', 'abdominal_pain', 'joint_pain', 'splenomegaly_symptom',
            'malaria_rdt', 'pallor', 'jaundice_exam', 'splenomegaly_exam', 'lymphadenopathy'
        ]

        def to_bool(val):
            if pd.isna(val): return np.nan
            val_str = str(val).strip().lower()
            if val_str in ['true', '1', '1.0', 'yes', 'y', 't', 'pos', 'positive']: return True
            if val_str in ['false', '0', '0.0', 'no', 'n', 'f', 'neg', 'negative']: return False
            return np.nan

        for col in bool_cols:
            if col in self.df.columns:
                self.df[col] = self.df[col].apply(to_bool)

    def _clean_numerics(self):
        # Clean continuous variables (e.g., hemoglobin percentages, vitals)
        def clamp_numeric(col_name, min_val, max_val):
            if col_name in self.df.columns:
                self.df[col_name] = pd.to_numeric(self.df[col_name], errors='coerce')
                self.df.loc[(self.df[col_name] < min_val) | (self.df[col_name] > max_val), col_name] = np.nan

        clamp_numeric('hb_a', 0, 100)
        clamp_numeric('hb_s', 0, 100)
        clamp_numeric('hb_f', 0, 100)
        clamp_numeric('temp', 30, 45)       # Celcius realistic limits
        clamp_numeric('heart_rate', 30, 250)
        clamp_numeric('resp_rate', 8, 60)

    def _cross_validate(self):
        # Clinical Rule: If Hemoglobin is significantly low (< 10.0), flag Pallor as True
        if 'hb' in self.df.columns and 'pallor' in self.df.columns:
            self.df['hb'] = pd.to_numeric(self.df['hb'], errors='coerce')
            mask = (self.df['hb'] < 10.0)
            self.df.loc[mask, 'pallor'] = True

# ==========================================
# 3. MOCK DATA GENERATOR
# ==========================================
def generate_mock_data():
    data = {
        'patient_id':['PAT-1001', 'PAT-1002', 'INV-1003', np.nan, 'PAT-1005'],
        'name': ['John  Doe ', ' Jane Smith', ' Bob ', 'Alice  Johnson', ' Charlie Brown '],
        'age':[45.5, 30, -5, 150, np.nan], # Float age, negative age, outlier age, missing age
        'sex':['Male', 'f', 'woman', 'MALE ', '1'],
        'dob':['1980-01-01', '02/15/1990', 'invalid_date', '1970/12/31', np.nan],
        'address':['123 Main St  ', '456 Oak Ave', '  789 Pine Ln', '321 Maple Dr', '  654 Elm St  '],
        'contact_info':['555-123-4567', '555 987 6543', 'invalid', '(555) 111-2222', np.nan],
        'diabetes': [True, 'yes', '0', 1.0, np.nan],
        'hypertension': ['True', 'No', False, 'Y', 'N'],
        'medical_history_other':['Asthma', np.nan, '  None  ', 'Bronchitis', np.nan],
        'sickle_cell_trait': [True, False, True, False, np.nan],
        'malaria_history': [1, 0, 1, np.nan, 0],
        'family_history_other':[np.nan, 'Heart Disease', np.nan, np.nan, 'Cancer'],
        'allergies':['Peanuts', np.nan, 'Dust', np.nan, 'Latex'],
        'current_medications':[np.nan, 'Ibuprofen', np.nan, 'Aspirin', np.nan],
        'fever':['yes', 'no', '1', '0', np.nan],
        'chills':[True, False, np.nan, True, False],
        'headache': ['true', 'false', 'T', 'F', np.nan],
        'muscle_aches':[1.0, 0.0, 1.0, 0.0, np.nan],
        'fatigue':['Y', 'N', 'y', 'n', np.nan],
        'loss_of_appetite':[True, False, True, False, True],
        'jaundice': ['yes', 'no', 'yes', 'no', 'yes'],
        'abdominal_pain': [1, 0, 1, 0, 1],
        'joint_pain': ['True', 'False', 'True', 'False', 'True'],
        'splenomegaly_symptom': ['yes', 'no', 'yes', 'no', 'yes'],
        'hb':[14.5, 5.0, 12.0, 16.0, np.nan], # Row 2 has low hb (5.0) for pallor cross-val
        'wbc':[8.5, 15.2, np.nan, 5.0, 12.0],
        'platelets':[250, np.nan, 100, 300, 150],
        'malaria_microscopy': ['Positive', 'Negative', 'pos', 'neg', '1'],
        'malaria_rdt': ['true', 'false', '0', 'Positive', 'Negative'],
        'hb_a':[96.5, 60.0, 150.0, np.nan, 95.0], # 150 is outlier percentage
        'hb_s':[0.5, 30.0, -10.0, np.nan, 1.0],   # -10 is outlier percentage
        'hb_f':[1.0, 10.0, 50.0, np.nan, 1.5],
        'lft':['Normal', 'Elevated AST/ALT', np.nan, 'Normal', 'Normal'],
        'kft':['Normal', 'Normal', 'Normal', np.nan, 'Normal'],
        'temp':[37.2, 39.5, 50.0, 20.0, np.nan], # Outliers 50 and 20
        'bp':['120/80', '140 / 90', '110-70', '130/85', np.nan],
        'heart_rate':[80, 110, 300, 20, np.nan], # Outliers 300 and 20
        'resp_rate': [16, 24, 70, 5, np.nan],     # Outliers 70 and 5
        'pallor':[False, np.nan, False, False, False],
        'jaundice_exam':['yes', 'no', 'yes', 'no', 'yes'],
        'splenomegaly_exam':['yes', 'no', 'yes', 'no', 'yes'],
        'lymphadenopathy': ['yes', 'no', 'yes', 'no', 'yes'],
        'notes':['Patient feels  fine. ', 'nan', ' Follow up needed. ', np.nan, ' ']
    }

    df = pd.DataFrame(data)
    # Inject empty columns/rows and duplicates
    df['empty_col'] = np.nan
    df.loc[len(df)] = pd.Series([np.nan] * len(df.columns), index=df.columns)
    df.loc[len(df)] = df.iloc[0].copy()
    
    return df

# ==========================================
# 4. STREAMLIT APP LOGIC
# ==========================================
def main():
    st.title("🩸 Hemaclass Data Cleaning Pipeline")
    st.markdown("Upload your clinical records export to run the automated 20-dimension cleaning pipeline, or generate a mock messy dataset to test it out.")

    # State management to track what data is loaded
    if 'use_mock' not in st.session_state:
        st.session_state.use_mock = False
    if 'cleaned_df' not in st.session_state:
        st.session_state.cleaned_df = None
        
    def set_mock_true():
        st.session_state.use_mock = True
        st.session_state.cleaned_df = None

    # UI Inputs
    col1, col2 = st.columns([2, 1])
    with col1:
        uploaded_file = st.file_uploader("Upload Raw CSV", type=["csv"])
    with col2:
        st.write("<br>", unsafe_allow_html=True)
        st.button("🧪 Generate & Load Mock Dataset", on_click=set_mock_true)

    # Determine Raw Data
    raw_df = None
    if uploaded_file is not None:
        st.session_state.use_mock = False # Clear mock if real file uploaded
        raw_df = pd.read_csv(uploaded_file)
    elif st.session_state.use_mock:
        raw_df = generate_mock_data()

    # Trigger Pipeline
    if st.button("✨ Run Cleaning Pipeline", type="primary"):
        if raw_df is not None:
            try:
                # Run Data Cleaner
                cleaner = HemaclassDataCleaner(raw_df)
                cleaned_df = cleaner.clean()
                st.session_state.cleaned_df = cleaned_df
                st.success("✅ Data cleaned successfully!")
            except Exception as e:
                st.error(f"❌ Error occurred during cleaning: {str(e)}")
        else:
            st.warning("⚠️ Please upload a CSV file or load the mock data first.")

    # Results Display
    if raw_df is not None or st.session_state.cleaned_df is not None:
        tab1, tab2 = st.tabs(["Preview Original Data", "Preview Cleaned Data"])
        
        with tab1:
            if raw_df is not None:
                st.dataframe(raw_df.head(10), use_container_width=True)
                st.caption(f"Original Dimensions: {raw_df.shape[0]} rows, {raw_df.shape[1]} cols")
                
        with tab2:
            if st.session_state.cleaned_df is not None:
                st.dataframe(st.session_state.cleaned_df.head(10), use_container_width=True)
                st.caption(f"Cleaned Dimensions: {st.session_state.cleaned_df.shape[0]} rows, {st.session_state.cleaned_df.shape[1]} cols")
                
                # File Downloader
                csv_buffer = st.session_state.cleaned_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Cleaned CSV File",
                    data=csv_buffer,
                    file_name="cleaned_data_output.csv",
                    mime="text/csv",
                    type="primary"
                )

if __name__ == "__main__":
    main()
