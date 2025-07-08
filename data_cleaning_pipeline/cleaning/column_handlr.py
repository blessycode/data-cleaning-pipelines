import pandas as pd
import re

def clean_column_names(df, lowercase=True, replace_spaces=True, replace_special=True):
    """
    Cleans column names in a DataFrame for consistency and pipeline safety.

    Args:
        df (pd.DataFrame): Input DataFrame.
        lowercase (bool): Whether to lowercase column names.
        replace_spaces (bool): Whether to replace spaces with underscores.
        replace_special (bool): Whether to replace special characters with underscores.

    Returns:
        cleaned_df (pd.DataFrame): DataFrame with cleaned column names.
        report (dict): Mapping of original to cleaned column names.
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

    cleaned_df.columns = cleaned_columns
    report = dict(zip(original_columns, cleaned_columns))

    return cleaned_df, report
