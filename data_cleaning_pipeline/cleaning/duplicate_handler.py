import pandas as pd
import numpy as np

def duplicate_handler(df, subset=None, keep='first', action='remove'):
    """handles duplicates rows
    parameters:
    - subset: list of columns for partial duplicate
    -keep: first, last or false
    -action: remove duplicate, flag to add a is_duplicate column

    returns:
    -cleaned dataframe with duplicates handled
    -report: dictionary detailing duplicate rows

    """

    report = {}

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
        duplicate_count_after = cleaned_df.duplicated(subset=subset, keep=False).sum
        report['duplicate_count_after'] = int(duplicate_count_after)

    else:
        report['duplicate_count_after'] = int(duplicate_count)

    report['duplicates_removed'] = int(duplicate_count - report['duplicate_count_after'])

    return cleaned_df, report