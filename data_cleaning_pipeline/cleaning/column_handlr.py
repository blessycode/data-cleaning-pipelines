"""
Enhanced Column Handler Module
Comprehensive column name cleaning and standardization
"""

import pandas as pd
import re
from typing import Dict, List, Optional, Tuple, Any
import warnings

warnings.filterwarnings('ignore')


def clean_column_names(df: pd.DataFrame, 
                       lowercase: bool = True,
                       replace_spaces: bool = True,
                       replace_special: bool = True,
                       ensure_unique: bool = True,
                       max_length: Optional[int] = None,
                       prefix: Optional[str] = None,
                       suffix: Optional[str] = None,
                       verbose: bool = True) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Enhanced column name cleaning with comprehensive options
    
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
    max_length : int, optional
        Maximum length for column names (truncate if longer)
    prefix : str, optional
        Prefix to add to all column names
    suffix : str, optional
        Suffix to add to all column names
    verbose : bool
        Whether to print progress messages
        
    Returns:
    --------
    cleaned_df : pd.DataFrame
        DataFrame with cleaned column names
    report : dict
        Comprehensive report on column name changes
    """
    if verbose:
        print(f"🔧 Cleaning {len(df.columns)} column names...")
    
    cleaned_df = df.copy()
    original_columns = cleaned_df.columns.tolist()
    cleaned_columns = []
    changes_made = []
    
    for col in original_columns:
        new_col = str(col).strip()
        original_col = new_col
        
        # Apply transformations
        if lowercase:
            new_col = new_col.lower()
        
        if replace_spaces:
            new_col = new_col.replace(" ", "_")
            # Replace multiple spaces/underscores with single underscore
            new_col = re.sub(r'[_\s]+', '_', new_col)
        
        if replace_special:
            # Replace special characters but keep alphanumeric, underscore, and hyphen
            new_col = re.sub(r'[^A-Za-z0-9_\-]', '_', new_col)
            # Remove leading/trailing underscores
            new_col = new_col.strip('_')
        
        # Truncate if max_length specified
        if max_length and len(new_col) > max_length:
            new_col = new_col[:max_length]
            changes_made.append(f"{original_col} -> truncated to {max_length} chars")
        
        # Add prefix/suffix
        if prefix:
            new_col = f"{prefix}{new_col}"
        if suffix:
            new_col = f"{new_col}{suffix}"
        
        # Track changes
        if new_col != original_col:
            changes_made.append(f"{original_col} -> {new_col}")
        
        cleaned_columns.append(new_col)
    
    # Ensure uniqueness
    if ensure_unique:
        seen = {}
        duplicates_found = []
        for i, col in enumerate(cleaned_columns):
            if col in seen:
                seen[col] += 1
                cleaned_columns[i] = f"{col}_{seen[col]}"
                duplicates_found.append({
                    'original': original_columns[i],
                    'duplicate_of': col,
                    'renamed_to': cleaned_columns[i]
                })
            else:
                seen[col] = 0
    else:
        duplicates_found = []
    
    # Apply cleaned column names
    cleaned_df.columns = cleaned_columns
    
    # Generate report
    report = {
        'operation': 'column_name_cleaning',
        'total_columns': len(original_columns),
        'columns_changed': len(changes_made),
        'original_to_cleaned': dict(zip(original_columns, cleaned_columns)),
        'changes_made': changes_made,
        'duplicates_fixed': duplicates_found,
        'settings': {
            'lowercase': lowercase,
            'replace_spaces': replace_spaces,
            'replace_special': replace_special,
            'ensure_unique': ensure_unique,
            'max_length': max_length,
            'prefix': prefix,
            'suffix': suffix
        }
    }
    
    if verbose:
        print(f"✓ Column names cleaned: {len(changes_made)} columns modified")
        if duplicates_found:
            print(f"  • {len(duplicates_found)} duplicate names resolved")
    
    return cleaned_df, report
