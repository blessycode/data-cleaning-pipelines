"""
Enhanced Duplicate Handler Module
Comprehensive duplicate detection and handling
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import warnings

warnings.filterwarnings('ignore')


def duplicate_handler(df: pd.DataFrame, 
                      subset: Optional[List[str]] = None, 
                      keep: str = 'first',
                      action: str = 'remove',
                      verbose: bool = True) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Enhanced duplicate row handler with comprehensive reporting
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    subset : list, optional
        List of columns for partial duplicate detection
        If None, checks all columns
    keep : str
        Which duplicates to keep: 'first', 'last', or False (keep none)
    action : str
        Action to take: 'remove', 'flag', or 'mark'
    verbose : bool
        Whether to print progress messages
        
    Returns:
    --------
    cleaned_df : pd.DataFrame
        DataFrame with duplicates handled
    report : dict
        Comprehensive report on duplicate handling
    """
    if verbose:
        print(f"🔍 Analyzing duplicates (subset: {subset if subset else 'all columns'})...")
    
    report = {
        'operation': 'duplicate_handling',
        'subset_columns': subset if subset else 'all_columns',
        'keep_strategy': keep,
        'action': action
    }
    
    # Count duplicates before
    duplicate_mask = df.duplicated(subset=subset, keep=keep)
    duplicate_count = duplicate_mask.sum()
    duplicate_percent = (duplicate_count / len(df)) * 100 if len(df) > 0 else 0
    
    report['duplicate_count_before'] = int(duplicate_count)
    report['duplicate_percentage_before'] = round(duplicate_percent, 2)
    
    # Find duplicate groups for detailed analysis
    if subset:
        duplicate_groups = df[df.duplicated(subset=subset, keep=False)].groupby(subset).size()
    else:
        duplicate_groups = df[df.duplicated(keep=False)].groupby(list(df.columns)).size()
    
    report['duplicate_groups'] = int(len(duplicate_groups))
    report['max_duplicates_in_group'] = int(duplicate_groups.max()) if len(duplicate_groups) > 0 else 0
    
    # Handle duplicates based on action
    if action == 'remove':
        cleaned_df = df.drop_duplicates(subset=subset, keep=keep).reset_index(drop=True)
        report['action_taken'] = 'removed'
        
        # Count after removal
        duplicate_count_after = cleaned_df.duplicated(subset=subset, keep=False).sum()
        report['duplicate_count_after'] = int(duplicate_count_after)
        report['rows_removed'] = int(len(df) - len(cleaned_df))
        
    elif action == 'flag':
        cleaned_df = df.copy()
        cleaned_df['is_duplicate'] = duplicate_mask
        report['action_taken'] = 'flagged'
        report['duplicate_count_after'] = int(duplicate_count)
        report['rows_flagged'] = int(duplicate_count)
        
    elif action == 'mark':
        # Mark duplicates with group ID
        cleaned_df = df.copy()
        if subset:
            duplicate_groups = df.groupby(subset).ngroup()
            cleaned_df['duplicate_group_id'] = duplicate_groups
            cleaned_df['is_duplicate'] = df.duplicated(subset=subset, keep=False)
        else:
            duplicate_groups = df.groupby(list(df.columns)).ngroup()
            cleaned_df['duplicate_group_id'] = duplicate_groups
            cleaned_df['is_duplicate'] = df.duplicated(keep=False)
        
        report['action_taken'] = 'marked_with_group_id'
        report['duplicate_count_after'] = int(duplicate_count)
        report['rows_marked'] = int(duplicate_count)
        
    else:
        raise ValueError(f"Invalid action: {action}. Use 'remove', 'flag', or 'mark'.")
    
    # Calculate improvement
    report['duplicates_removed'] = int(duplicate_count - report['duplicate_count_after'])
    report['improvement_percentage'] = round(
        ((duplicate_count - report['duplicate_count_after']) / duplicate_count * 100) 
        if duplicate_count > 0 else 0, 2
    )
    
    # Final statistics
    report['final_shape'] = {
        'rows': len(cleaned_df),
        'columns': len(cleaned_df.columns)
    }
    report['shape_change'] = {
        'rows_removed': len(df) - len(cleaned_df),
        'columns_added': len(cleaned_df.columns) - len(df.columns)
    }
    
    if verbose:
        print(f"✓ Duplicates handled: {report['duplicates_removed']} rows ({report['improvement_percentage']}% reduction)")
    
    return cleaned_df, report