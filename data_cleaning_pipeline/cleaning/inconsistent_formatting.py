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

    # 1️ Case normalization for string columns
    if string_case == 'lower':
        for col in cleaned_df.select_dtypes(include='object').columns:
            cleaned_df[col] = cleaned_df[col].map(lambda x: x.lower() if isinstance(x, str) else x)
    elif string_case == 'upper':
        for col in cleaned_df.select_dtypes(include='object').columns:
            cleaned_df[col] = cleaned_df[col].map(lambda x: x.upper() if isinstance(x, str) else x)

    # 2️ Replace spaces and special characters in column names
    original_cols = cleaned_df.columns.tolist()
    cleaned_cols = cleaned_df.columns
    if replace_spaces:
        cleaned_cols = cleaned_cols.str.replace(" ", "_")
    if replace_special:
        cleaned_cols = cleaned_cols.str.replace(r'[^A-Za-z0-9_\-]', '_', regex=True)
    cleaned_df.columns = cleaned_cols
    report['column_name_mapping'] = dict(zip(original_cols, cleaned_cols))

    # 3️ Numeric cleaning with custom regex validation
    if numeric_cleaning:
        converted_columns = []
        for col in cleaned_df.columns:
            if cleaned_df[col].dtype == 'object':
                cleaned_df[col] = cleaned_df[col].apply(lambda x: x if is_valid_numeric(x) else pd.NA)
                cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors='coerce')
                converted_columns.append(col)
        report['numeric_cleaned_columns'] = converted_columns

    # 4️ Data type cleaning (strip and convert low-cardinality to category)
    if data_clean:
        categorized_columns = []
        for col in cleaned_df.columns:
            if cleaned_df[col].dtype == 'object':
                cleaned_df[col] = cleaned_df[col].str.strip()
                if cleaned_df[col].nunique() < 0.5 * len(cleaned_df):
                    cleaned_df[col] = cleaned_df[col].astype('category')
                    categorized_columns.append(col)
        report['converted_to_category'] = categorized_columns

    # 5️ Datetime conversion
    if datetime_columns:
        converted = []
        for col in datetime_columns:
            if col in cleaned_df.columns:
                cleaned_df[col] = pd.to_datetime(cleaned_df[col], errors='coerce')
                converted.append(col)
        report['datetime_converted'] = converted

    # 6 Replace empty strings with NaN
    if replace_empty_with_nan:
        cleaned_df.replace("", pd.NA, inplace=True)

    return cleaned_df, report
