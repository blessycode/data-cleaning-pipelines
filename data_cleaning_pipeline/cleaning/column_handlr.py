# column_handler.py

import pandas as pd
import re

def clean_column_names(df, lowercase=True, replace_spaces=True, replace_special=True, 
                       ensure_unique=True, verbose: bool = False):
    """
    Cleans column names in a DataFrame for consistency and pipeline safety.

    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    lowercase : bool
        Whether to lowercase column names
    replace_spaces : bool
        Whether to replace spaces with underscores
    replace_special : bool
        Whether to replace special characters with underscores
    ensure_unique : bool
        Whether to ensure unique column names by appending suffixes
    verbose : bool
        Whether to print progress messages

    Returns:
    --------
    cleaned_df : pd.DataFrame
        DataFrame with cleaned column names
    report : dict
        Mapping of original to cleaned column names and duplicates
    """
    if df is None or df.empty:
        return df, {'error': 'Empty DataFrame provided'}
    
    cleaned_df = df.copy()
    original_columns = cleaned_df.columns.tolist()
    cleaned_columns = []
    report = {
        'operation': 'column_name_cleaning',
        'initial_columns': original_columns,
        'settings': {
            'lowercase': lowercase,
            'replace_spaces': replace_spaces,
            'replace_special': replace_special,
            'ensure_unique': ensure_unique
        }
    }

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
    
    # Build comprehensive report
    column_mapping = dict(zip(original_columns, cleaned_columns))
    changed_columns = {orig: new for orig, new in column_mapping.items() if orig != new}
    
    report['original_to_cleaned'] = column_mapping
    report['duplicates_fixed'] = {col: count for col, count in seen.items() if count > 0} if ensure_unique else {}
    report['columns_changed'] = len(changed_columns)
    report['columns_renamed'] = changed_columns
    report['final_columns'] = cleaned_columns
    report['columns_modified'] = len(changed_columns) > 0
    
    if verbose:
        if changed_columns:
            print(f"  ✓ Cleaned {len(changed_columns)} column names")
            if report['duplicates_fixed']:
                print(f"  ✓ Fixed {len(report['duplicates_fixed'])} duplicate column names")
        else:
            print(f"  ✓ Column names already clean")

    return cleaned_df, report
