import pandas as pd
import numpy as np

def duplicate_handler(df, subset=None, keep='first', action='remove', verbose: bool = False):
    """
    Handles duplicate rows in a DataFrame
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame
    subset : list, optional
        List of columns to consider for duplicate detection
        If None, considers all columns
    keep : str
        Which duplicates to keep: 'first', 'last', or False (keep none)
    action : str
        Action to take: 'remove' or 'flag'
        - 'remove': Remove duplicate rows
        - 'flag': Add 'is_duplicate' column marking duplicates
    verbose : bool
        Whether to print progress messages
    
    Returns:
    --------
    cleaned_df : pd.DataFrame
        DataFrame with duplicates handled
    report : dict
        Detailed report of duplicate handling
    """
    if df is None or df.empty:
        return df, {'error': 'Empty DataFrame provided'}
    
    initial_shape = df.shape
    report = {
        'operation': 'duplicate_handling',
        'initial_shape': initial_shape,
        'subset_columns': subset if subset else 'all_columns',
        'keep_strategy': keep,
        'action': action
    }

    #count duplicates
    duplicate_mask = df.duplicated(subset=subset, keep=keep)
    duplicate_count =duplicate_mask.sum()
    report['duplicate_count_before'] = int(duplicate_count)

    if action == 'remove':
        cleaned_df = df.drop_duplicates(subset=subset, keep=keep).reset_index(drop=True)
        report['action'] = 'removed'

    elif action == 'flag':
        cleaned_df = df.copy()
        cleaned_df['is_duplicate'] = duplicate_mask
        report['action'] = 'flagged'

    else:
        raise ValueError(f"Invalid action: {action}. Use 'remove' or 'flag'.")

    # Count duplicates after removal
    if action == 'remove':
        duplicate_count_after = cleaned_df.duplicated(subset=subset, keep=False).sum()
        report['duplicate_count_after'] = int(duplicate_count_after)
        report['final_shape'] = cleaned_df.shape
        report['rows_removed'] = int(initial_shape[0] - cleaned_df.shape[0])
    else:
        report['duplicate_count_after'] = int(duplicate_count)
        report['final_shape'] = cleaned_df.shape

    report['duplicates_removed'] = int(duplicate_count - report['duplicate_count_after'])
    report['duplicate_percentage'] = round((duplicate_count / initial_shape[0] * 100), 2) if initial_shape[0] > 0 else 0
    
    # Additional statistics
    if subset:
        report['partial_duplicate_check'] = True
        report['columns_checked'] = subset
    else:
        report['partial_duplicate_check'] = False
        report['columns_checked'] = 'all'
    
    if verbose:
        print(f"  ✓ Found {duplicate_count} duplicate rows ({report['duplicate_percentage']:.1f}%)")
        if action == 'remove':
            print(f"  ✓ Removed {report['duplicates_removed']} duplicate rows")

    return cleaned_df, report