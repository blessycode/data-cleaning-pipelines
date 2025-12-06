import pandas as pd
import numpy as np
from sklearn.covariance import MinCovDet
from scipy import stats

def grubbs_test(series, alpha=0.05):
    """
    Performs iterative Grubbs' test to detect outliers in a series.
    Returns the indices of detected outliers.
    """
    outliers = []
    data = series.dropna().copy()

    while True:
        n = len(data)
        if n < 3:
            break

        mean = data.mean()
        std = data.std()
        abs_diff = abs(data - mean)
        G_calculated = abs_diff.max() / std

        # Critical value
        t_crit = stats.t.ppf(1 - alpha / (2 * n), n - 2)
        numerator = (n - 1) * t_crit
        denominator = np.sqrt(n) * np.sqrt(n - 2 + t_crit**2)
        G_critical = numerator / denominator

        if G_calculated > G_critical:
            outlier_idx = abs_diff.idxmax()
            outliers.append(outlier_idx)
            data = data.drop(outlier_idx)
        else:
            break

    return outliers

def handle_outliers(
    df,
    method='zscore',                  # 'zscore', 'iqr', 'mcd'
    threshold=3.0,                    # For z-score
    iqr_factor=1.5,                   # For IQR
    mcd_threshold=0.975,              # quantile for Mahalanobis
    action='remove',                  # 'remove', 'cap', 'flag'
    hypothesis_test=False,            # apply Grubbs if True
    significance_level=0.05
):
    """
    Handles outliers in a DataFrame using specified method and Grubbs' testing.
    """

    report = {'method': method, 'action': action}
    cleaned_df = df.copy()
    numeric_cols = cleaned_df.select_dtypes(include='number').columns

    outlier_indices = set()

    if hypothesis_test:
        report['hypothesis_testing'] = {}
        for col in numeric_cols:
            col_outliers = grubbs_test(cleaned_df[col], alpha=significance_level)
            report['hypothesis_testing'][col] = {
                'n_outliers_detected': len(col_outliers),
                'outlier_indices': col_outliers
            }
            outlier_indices.update(col_outliers)
    else:
        if method == 'zscore':
            z_scores = np.abs(stats.zscore(cleaned_df[numeric_cols], nan_policy='omit'))
            outliers = (z_scores > threshold)
            outlier_indices = set(np.where(outliers)[0])

        elif method == 'iqr':
            Q1 = cleaned_df[numeric_cols].quantile(0.25)
            Q3 = cleaned_df[numeric_cols].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - iqr_factor * IQR
            upper_bound = Q3 + iqr_factor * IQR
            outliers = ((cleaned_df[numeric_cols] < lower_bound) | (cleaned_df[numeric_cols] > upper_bound))
            outlier_indices = set(np.where(outliers.any(axis=1))[0])

        elif method == 'mcd':
            mcd = MinCovDet().fit(cleaned_df[numeric_cols].dropna())
            mahal = mcd.mahalanobis(cleaned_df[numeric_cols].fillna(cleaned_df[numeric_cols].median()))
            threshold_val = np.percentile(mahal, mcd_threshold * 100)
            outliers = mahal > threshold_val
            outlier_indices = set(np.where(outliers)[0])

        else:
            raise ValueError(f"Invalid method: {method}")

    report['n_outliers_detected'] = len(outlier_indices)
    report['outlier_indices'] = list(outlier_indices)

    # Handling based on action
    if action == 'remove':
        cleaned_df = cleaned_df.drop(index=outlier_indices).reset_index(drop=True)
        report['n_rows_removed'] = len(outlier_indices)

    elif action == 'cap':
        for col in numeric_cols:
            if method == 'iqr':
                lower = Q1[col] - iqr_factor * IQR[col]
                upper = Q3[col] + iqr_factor * IQR[col]
                cleaned_df[col] = np.where(
                    cleaned_df[col] < lower, lower,
                    np.where(cleaned_df[col] > upper, upper, cleaned_df[col])
                )
            elif method == 'zscore':
                mean = cleaned_df[col].mean()
                std = cleaned_df[col].std()
                lower = mean - threshold * std
                upper = mean + threshold * std
                cleaned_df[col] = np.where(
                    cleaned_df[col] < lower, lower,
                    np.where(cleaned_df[col] > upper, upper, cleaned_df[col])
                )
            elif method == 'mcd':
                median_val = cleaned_df[col].median()
                cleaned_df.loc[list(outlier_indices), col] = median_val
        report['n_rows_capped'] = len(outlier_indices)

    elif action == 'flag':
        flags = pd.Series(False, index=cleaned_df.index)
        flags.loc[list(outlier_indices)] = True
        cleaned_df['is_outlier'] = flags
        report['n_rows_flagged'] = len(outlier_indices)

    else:
        raise ValueError(f"Invalid action: {action}")

    return cleaned_df, report
