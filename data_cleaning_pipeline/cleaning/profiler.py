import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def generate_initial_report(df):
    """
    Generates a structured profiling report with key statistics for a dataframe.

    Includes:
    - number of rows and columns
    - data types
    - missing values count and percentage per column
    - duplicate rows count
    - numerical profiling (count, mean, median, std, min, max, skewness, kurtosis)
    """

    report = {}

    # Rows and columns count
    report['number_rows'] = df.shape[0]
    report['number_columns'] = df.shape[1]

    # Data types
    report['data_types'] = df.dtypes.apply(lambda x: x.name).to_dict()

    # Missing values count and percentage
    report['missing_values'] = df.isnull().sum().to_dict()
    report['percent_missing'] = (df.isnull().sum() * 100 / len(df)).to_dict()

    # Duplicate rows
    report['duplicate_rows'] = int(df.duplicated().sum())
    

    # Numerical profiling
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    numerical_stats = {}
    for col in numeric_cols:
        numerical_stats[col] = {
            'count': int(df[col].count()),
            'mean': df[col].mean(),
            'median': df[col].median(),
            'std': df[col].std(),
            'min': df[col].min(),
            'max': df[col].max(),
            'skewness': df[col].skew(),
            'kurtosis': df[col].kurtosis(),
            'missing_percentage': df[col].isnull().mean() * 100
        }
    report['numerical_statistics'] = numerical_stats

    return report

def generate_categorical_profile(df):
    """
    Generates a structured profiling report for categorical columns:
    - unique values count
    - top 5 categories with frequencies
    - missing percentage
    """
    report = {}
    cat_cols = df.select_dtypes(include='object').columns
    for col in cat_cols:
        col_report = {
            'num_unique': int(df[col].nunique()),
            'top_categories': df[col].value_counts().head(5).to_dict(),
            'missing_percentage': df[col].isnull().mean() * 100
        }
        report[col] = col_report

    return report

def generate_visual_profile(df, output_dir="profiling_reports"):
    """
    Generates and saves:
    - missing values heatmap
    - histograms for numeric columns
    - bar plots for top categories in categorical columns

    Returns a dictionary of saved file paths.
    """

    os.makedirs(output_dir, exist_ok=True)
    saved_files = {}

    # Missing values heatmap
    plt.figure(figsize=(14, 6))
    sns.heatmap(df.isnull(), cbar=True, cmap='magma', linewidths=0.3, linecolor='gray')
    plt.title("Missing Data Heatmap", fontsize=14, weight='bold')
    plt.xlabel("Columns")
    plt.ylabel("Rows")
    plt.tight_layout() 
    missing_heatmap_path = os.path.join(output_dir, "missing_values_heatmap.png")
    plt.savefig(missing_heatmap_path, dpi=200)
    plt.close()
    saved_files['missing_values_heatmap'] = missing_heatmap_path
    
    

    # Histograms for numeric columns
    numeric_cols = df.select_dtypes(include='number').columns
    for col in numeric_cols:
        plt.figure(figsize=(9, 5))
        sns.histplot(df[col].dropna(), kde=True, bins=30, edgecolor='black')
        plt.title(f"Distribution of {col}", fontsize=14, weight='bold')
        plt.xlabel(col)
        plt.ylabel("Frequency")
        plt.grid(axis="y", linestyle='--',alpha=0.6)
        plt.tight_layout()
        hist_path = os.path.join(output_dir, f"histogram_{col}.png")
        plt.savefig(hist_path, bbox_inches='tight')
        plt.close()
        saved_files[f"histogram_{col}"] = hist_path
        
        # Density plots for numeric columns
    for col in numeric_cols:
        plt.figure(figsize=(9, 5))
        sns.kdeplot(df[col].dropna(), fill=True, linewidth=2)
        plt.title(f"Density Plot — {col}", fontsize=13, weight='bold')
        plt.xlabel(col)
        plt.ylabel("Density")
        plt.grid(alpha=0.3)
        plt.tight_layout()
        hist_path = os.path.join(output_dir, f"density_{col}.png")
        plt.savefig(hist_path, dpi=200)
        plt.close()
        saved_files[f"density_{col}"] = hist_path

    # Bar plots for categorical columns
    cat_cols = df.select_dtypes(include='object').columns
    for col in cat_cols:
        plt.figure(figsize=(10, 5))
        top_categories = df[col].value_counts().head(10)
        sns.barplot(x=top_categories.index, y=top_categories.values)
        plt.title(f"Top Categories for {col}")
        plt.xlabel(col)
        plt.ylabel("Count")
        plt.xticks(rotation=45)
        barplot_path = os.path.join(output_dir, f"barplot_{col}.png")
        plt.savefig(barplot_path, bbox_inches='tight')
        plt.close()
        saved_files[f"barplot_{col}"] = barplot_path

    return saved_files
