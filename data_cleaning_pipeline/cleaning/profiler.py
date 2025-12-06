import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import normaltest

# ----------------------------------------
# 1. BASIC PROFILE
# ----------------------------------------
def generate_basic_profile(df):
    profile = {}

    profile["n_rows"] = df.shape[0]
    profile["n_columns"] = df.shape[1]
    profile["memory_usage_mb"] = round(df.memory_usage().sum() / (1024**2), 3)
    
    profile["dtypes"] = df.dtypes.apply(lambda x: x.name).to_dict()

    profile["missing_count"] = df.isnull().sum().to_dict()
    profile["missing_percent"] = (df.isnull().mean() * 100).round(3).to_dict()

    profile["duplicate_rows"] = int(df.duplicated().sum())
    profile["empty_columns"] = df.columns[df.isnull().all()].tolist()

    return profile


# ----------------------------------------
# 2. NUMERICAL PROFILE
# ----------------------------------------
def generate_numeric_profile(df):
    num_cols = df.select_dtypes(include=[np.number]).columns
    stats = {}

    for col in num_cols:
        col_data = df[col].dropna()

        stat = {
            "count": int(col_data.count()),
            "mean": col_data.mean(),
            "median": col_data.median(),
            "std": col_data.std(),
            "min": col_data.min(),
            "max": col_data.max(),
            "skewness": col_data.skew(),
            "kurtosis": col_data.kurtosis(),
            "missing_percent": round(df[col].isnull().mean() * 100, 3),
        }

        # Normality test
        try:
            _, pvalue = normaltest(col_data)
            stat["normality_pvalue"] = round(pvalue, 6)
            stat["is_normal"] = pvalue > 0.05
        except:
            stat["normality_pvalue"] = None
            stat["is_normal"] = None

        # Outlier detection
        Q1 = col_data.quantile(0.25)
        Q3 = col_data.quantile(0.75)
        IQR = Q3 - Q1
        outliers = col_data[(col_data < Q1 - 1.5*IQR) | (col_data > Q3 + 1.5*IQR)]

        stat["outlier_count"] = int(outliers.shape[0])
        stat["outlier_percent"] = round((outliers.shape[0] / len(col_data)) * 100, 3)

        stats[col] = stat

    return stats


# ----------------------------------------
# 3. CATEGORICAL PROFILE
# ----------------------------------------
def generate_categorical_profile(df):
    cat_cols = df.select_dtypes(include=['object', 'category']).columns
    stats = {}

    for col in cat_cols:
        col_data = df[col].dropna()

        stats[col] = {
            "unique_count": int(col_data.nunique()),
            "top_values": col_data.value_counts().head(5).to_dict(),
            "missing_percent": round(df[col].isnull().mean() * 100, 3),
            "dominant_percent": round(col_data.value_counts(normalize=True).iloc[0] * 100, 3)
                if len(col_data) > 0 else None
        }

    return stats


# ----------------------------------------
# 4. DATETIME PROFILE
# ----------------------------------------
def generate_datetime_profile(df):
    dt_cols = [col for col in df.columns if np.issubdtype(df[col].dtype, np.datetime64)]
    stats = {}

    for col in dt_cols:
        col_data = df[col].dropna()
        stats[col] = {
            "min_date": str(col_data.min()),
            "max_date": str(col_data.max()),
            "range_days": int((col_data.max() - col_data.min()).days)
        }

    return stats


# ----------------------------------------
# 5. MIXED TYPE DETECTION
# ----------------------------------------
def detect_mixed_types(df):
    mixed = {}

    for col in df.columns:
        unique_types = set(type(x) for x in df[col].dropna().sample(
            min(len(df), 200), random_state=42
        ))
        if len(unique_types) > 1:
            mixed[col] = list(unique_types)

    return mixed


# ----------------------------------------
# 6. CORRELATION ANALYSIS
# ----------------------------------------
def generate_correlations(df):
    correlations = {}

    # Numeric correlations
    num_cols = df.select_dtypes(include=[np.number])
    if num_cols.shape[1] > 1:
        correlations["pearson"] = num_cols.corr(method="pearson").round(4).to_dict()
        correlations["spearman"] = num_cols.corr(method="spearman").round(4).to_dict()

    # High correlation pairs
    high_corr = []
    if num_cols.shape[1] > 1:
        corr_matrix = num_cols.corr().abs()
        upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
        high_corr = [
            (col, idx, upper.loc[col, idx])
            for col in upper.columns
            for idx in upper.index
            if pd.notnull(upper.loc[col, idx]) and upper.loc[col, idx] > 0.8
        ]

    correlations["high_correlations"] = high_corr

    return correlations


# ----------------------------------------
# 7. MISSINGNESS PATTERNS
# ----------------------------------------
def generate_missingness_patterns(df):
    patterns = {}

    patterns["rows_with_missing"] = int(df.isnull().any(axis=1).sum())
    patterns["columns_missing_more_than_50_percent"] = df.columns[df.isnull().mean() > 0.5].tolist()

    return patterns


# ----------------------------------------
# 8. FULL PROFILING WRAPPER
# ----------------------------------------
def generate_full_profile(df):
    return {
        "basic_profile": generate_basic_profile(df),
        "numeric_profile": generate_numeric_profile(df),
        "categorical_profile": generate_categorical_profile(df),
        "datetime_profile": generate_datetime_profile(df),
        "mixed_types": detect_mixed_types(df),
        "correlations": generate_correlations(df),
        "missingness_patterns": generate_missingness_patterns(df)
    }
