# column_handler.py

import pandas as pd
import re

def clean_column_names(df, lowercase=True, replace_spaces=True, replace_special=True, ensure_unique=True):
    """
    Cleans column names in a DataFrame for consistency and pipeline safety.

    Args:
        df (pd.DataFrame): Input DataFrame.
        lowercase (bool): Whether to lowercase column names.
        replace_spaces (bool): Whether to replace spaces with underscores.
        replace_special (bool): Whether to replace special characters with underscores.
        ensure_unique (bool): Whether to ensure unique column names by appending suffixes.

    Returns:
        cleaned_df (pd.DataFrame): DataFrame with cleaned column names.
        report (dict): Mapping of original to cleaned column names and duplicates.
    """
    cleaned_df = df.copy()
    original_columns = cleaned_df.columns.tolist()
    cleaned_columns = []

    for col in original_columns:
        new_col = col.strip()
        if lowercase:
            new_col = new_col.lower()
        if replace_spaces:
            new_col = new_col.replace(" ", "_")
        if replace_special:
            new_col = re.sub(r'[^A-Za-z0-9_\-]', '_', new_col)
        cleaned_columns.append(new_col)

    if ensure_unique:
        seen = {}
        for i, col in enumerate(cleaned_columns):
            if col in seen:
                seen[col] += 1
                cleaned_columns[i] = f"{col}_{seen[col]}"
            else:
                seen[col] = 0

    cleaned_df.columns = cleaned_columns
    report = {
        'original_to_cleaned': dict(zip(original_columns, cleaned_columns)),
        'duplicates_fixed': {col: count for col, count in seen.items() if count > 0}
    }

    return cleaned_df, report
