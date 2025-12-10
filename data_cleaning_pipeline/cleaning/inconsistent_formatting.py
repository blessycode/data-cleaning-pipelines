"""
Enhanced Inconsistent Formatting Module
Comprehensive formatting standardization and cleaning
"""

import pandas as pd
import numpy as np
import re
from typing import Dict, List, Optional, Tuple, Any
import warnings

warnings.filterwarnings('ignore')


def is_valid_numeric(value):
    """
    Checks if a value is a valid numeric string (int or float).
    Returns True if valid, False otherwise.
    """
    if pd.isna(value):
        return False
    return re.match(r'^-?\d+(\.\d+)?$', str(value).strip()) is not None


def clean_inconsistent_formatting(
    df: pd.DataFrame,
    string_case: str = 'lower',       # 'lower', 'upper', None
    replace_spaces: bool = True,
    replace_special: bool = True,
    numeric_cleaning: bool = True,
    data_clean: bool = True,
    datetime_columns: Optional[List[str]] = None,
    replace_empty_with_nan: bool = True,
    trim_whitespace: bool = True,
    normalize_unicode: bool = True,
    verbose: bool = True
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Enhanced inconsistent formatting cleaning with comprehensive options
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    string_case : str
        Case normalization: 'lower', 'upper', or None
    replace_spaces : bool
        Replace spaces in column names
    replace_special : bool
        Replace special characters in column names
    numeric_cleaning : bool
        Convert string numbers to numeric types
    data_clean : bool
        Perform additional data cleaning (strip, categorize)
    datetime_columns : list, optional
        List of columns to convert to datetime
    replace_empty_with_nan : bool
        Replace empty strings with NaN
    trim_whitespace : bool
        Trim whitespace from string values
    normalize_unicode : bool
        Normalize unicode characters
    verbose : bool
        Whether to print progress messages
        
    Returns:
    --------
    cleaned_df : pd.DataFrame
        Cleaned DataFrame
    report : dict
        Comprehensive cleaning report
    """
    if verbose:
        print(f"🧹 Cleaning inconsistent formatting in {len(df.columns)} columns...")
    
    cleaned_df = df.copy()
    report = {
        'operation': 'inconsistent_formatting_cleaning',
        'columns_processed': len(df.columns)
    }

    # -------------------------
    # 1. Case normalization
    # -------------------------
    if string_case in ['lower', 'upper']:
        str_cols = cleaned_df.select_dtypes(include='object').columns
        for col in str_cols:
            if string_case == 'lower':
                cleaned_df[col] = cleaned_df[col].apply(
                    lambda x: x.lower() if isinstance(x, str) else x
                )
            elif string_case == 'upper':
                cleaned_df[col] = cleaned_df[col].apply(
                    lambda x: x.upper() if isinstance(x, str) else x
                )
        report['string_case_normalized'] = {
            'columns': list(str_cols),
            'case': string_case,
            'count': len(str_cols)
        }

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
    # 4. Trim whitespace and normalize
    # -------------------------
    if trim_whitespace:
        trimmed_columns = []
        for col in cleaned_df.select_dtypes(include='object').columns:
            before = cleaned_df[col].astype(str).str.len().sum()
            cleaned_df[col] = cleaned_df[col].astype(str).str.strip()
            after = cleaned_df[col].str.len().sum()
            if before != after:
                trimmed_columns.append(col)
        report['whitespace_trimmed'] = {
            'columns': trimmed_columns,
            'count': len(trimmed_columns)
        }
    
    # -------------------------
    # 5. Unicode normalization
    # -------------------------
    if normalize_unicode:
        try:
            import unicodedata
            normalized_columns = []
            for col in cleaned_df.select_dtypes(include='object').columns:
                cleaned_df[col] = cleaned_df[col].apply(
                    lambda x: unicodedata.normalize('NFKD', str(x)) if isinstance(x, str) else x
                )
                normalized_columns.append(col)
            report['unicode_normalized'] = {
                'columns': normalized_columns,
                'count': len(normalized_columns)
            }
        except ImportError:
            if verbose:
                print("  ⚠️  unicodedata not available, skipping unicode normalization")
    
    # -------------------------
    # 6. Low-cardinality string -> category
    # -------------------------
    if data_clean:
        categorized_columns = []
        for col in cleaned_df.select_dtypes(include='object').columns:
            if cleaned_df[col].nunique() < 0.5 * len(cleaned_df) and cleaned_df[col].nunique() > 0:
                cleaned_df[col] = cleaned_df[col].astype('category')
                categorized_columns.append(col)
        report['converted_to_category'] = {
            'columns': categorized_columns,
            'count': len(categorized_columns)
        }

    # -------------------------
    # 7. Datetime conversion
    # -------------------------
    if datetime_columns:
        converted = []
        failed = []
        for col in datetime_columns:
            if col in cleaned_df.columns:
                try:
                    before_type = str(cleaned_df[col].dtype)
                    cleaned_df[col] = pd.to_datetime(cleaned_df[col], errors='coerce')
                    after_type = str(cleaned_df[col].dtype)
                    if before_type != after_type:
                        converted.append(col)
                except Exception as e:
                    failed.append({'column': col, 'error': str(e)})
        report['datetime_converted'] = {
            'successful': converted,
            'failed': failed,
            'count': len(converted)
        }

    # -------------------------
    # 8. Replace empty strings with NaN
    # -------------------------
    if replace_empty_with_nan:
        empty_count_before = (cleaned_df == "").sum().sum()
        cleaned_df.replace("", pd.NA, inplace=True)
        empty_count_after = (cleaned_df == "").sum().sum()
        report['empty_strings_replaced'] = {
            'before': int(empty_count_before),
            'after': int(empty_count_after),
            'replaced': int(empty_count_before - empty_count_after)
        }
    
    # Summary
    report['summary'] = {
        'total_operations': len([k for k in report.keys() if k != 'operation' and k != 'summary' and k != 'columns_processed']),
        'final_shape': {'rows': len(cleaned_df), 'columns': len(cleaned_df.columns)}
    }
    
    if verbose:
        print(f"✓ Formatting cleaned: {report['summary']['total_operations']} operations completed")

    return cleaned_df, report
