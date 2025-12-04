import pandas as pd
import numpy as np
import re

def is_valid_numeric(value):
    """
    Checks if a value is a valid numeric string (int or float).
    Returns True if valid, False otherwise.
    """
    if pd.isna(value):
        return False
    return re.match(r'^-?\d+(\.\d+)?$', str(value).strip()) is not None

def clean_inconsistent_formatting(
    df,
    string_case='lower',       # 'lower', 'upper', None
    replace_spaces=True,
    replace_special=True,
    numeric_cleaning=True,
    data_clean=True,
    datetime_columns=None,
    replace_empty_with_nan=True
):
    """
    Cleans inconsistent formatting in a DataFrame for pipeline readiness.

    Returns:
        cleaned_df (pd.DataFrame)
        report (dict)
    """
    cleaned_df = df.copy()
    report = {}

    # -------------------------
    # 1. Case normalization
    # -------------------------
    if string_case in ['lower', 'upper']:
        str_cols = cleaned_df.select_dtypes(include='object').columns
        for col in str_cols:
            cleaned_df[col] = cleaned_df[col].map(lambda x: x.lower() if string_case=='lower' and isinstance(x, str)
                                                  else x.upper() if string_case=='upper' and isinstance(x, str)
                                                  else x)
        report['string_case_normalized'] = list(str_cols)

    # -------------------------
    # 2. Column name cleaning
    # -------------------------
    original_cols = cleaned_df.columns.tolist()
    cleaned_cols = cleaned_df.columns
    if replace_spaces:
        cleaned_cols = cleaned_cols.str.replace(" ", "_")
    if replace_special:
        cleaned_cols = cleaned_cols.str.replace(r'[^A-Za-z0-9_\-]', '_', regex=True)
    cleaned_df.columns = cleaned_cols
    report['column_name_mapping'] = dict(zip(original_cols, cleaned_cols))

    # -------------------------
    # 3. Numeric cleaning
    # -------------------------
    if numeric_cleaning:
        converted_columns = []
        for col in cleaned_df.columns:
            if cleaned_df[col].dtype == 'object':
                cleaned_df[col] = cleaned_df[col].apply(lambda x: x if is_valid_numeric(x) else pd.NA)
                cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors='coerce')
                if cleaned_df[col].dtype in ['float64','int64']:
                    converted_columns.append(col)
        report['numeric_cleaned_columns'] = converted_columns

    # -------------------------
    # 4. Low-cardinality string -> category
    # -------------------------
    if data_clean:
        categorized_columns = []
        for col in cleaned_df.select_dtypes(include='object').columns:
            cleaned_df[col] = cleaned_df[col].str.strip()
            if cleaned_df[col].nunique() < 0.5 * len(cleaned_df):
                cleaned_df[col] = cleaned_df[col].astype('category')
                categorized_columns.append(col)
        report['converted_to_category'] = categorized_columns

    # -------------------------
    # 5. Datetime conversion
    # -------------------------
    if datetime_columns:
        converted = []
        for col in datetime_columns:
            if col in cleaned_df.columns:
                cleaned_df[col] = pd.to_datetime(cleaned_df[col], errors='coerce')
                converted.append(col)
        report['datetime_converted'] = converted

    # -------------------------
    # 6. Replace empty strings with NaN
    # -------------------------
    if replace_empty_with_nan:
        cleaned_df.replace("", pd.NA, inplace=True)

    return cleaned_df, report
