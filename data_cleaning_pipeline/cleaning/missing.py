import numpy as np
import pandas as pd

def handle_missing(
        df, 
        strategy='impute', 
        numeric_method='auto', 
        categorical_method='mode',
        constant_value=None, 
        drop_threshold=0.05, 
        drop_specific_columns=None,
        skew_threshold=1.0
    ):

    report = {
        'initial_missing_count': df.isnull().sum().to_dict(),
        'initial_missing_percentage': (df.isnull().mean() * 100).to_dict(),
    }

    cleaned_df = df.copy()

    # ---------------------------------------------------------
    # 1) Always remove columns with 100% missing values
    # ---------------------------------------------------------
    columns_100_missing = cleaned_df.columns[cleaned_df.isnull().mean() == 1.0]
    if len(columns_100_missing) > 0:
        cleaned_df = cleaned_df.drop(columns=columns_100_missing, axis=1)
        report['dropped_100_missing_columns'] = list(columns_100_missing)

    # ---------------------------------------------------------
    # 2) Strategy: DROP Missing Data
    # ---------------------------------------------------------
    if strategy == 'drop':
        if drop_specific_columns:
            cleaned_df = cleaned_df.drop(drop_specific_columns, axis=1)
            report['dropped_columns'] = drop_specific_columns
        else:
            # Drop columns exceeding threshold
            columns_to_drop = cleaned_df.columns[cleaned_df.isnull().mean() > drop_threshold]
            cleaned_df = cleaned_df.drop(columns_to_drop, axis=1)
            report['dropped_columns'] = list(columns_to_drop)

            # Drop rows exceeding threshold
            rows_to_drop = cleaned_df.index[cleaned_df.isnull().mean(axis=1) > drop_threshold]
            cleaned_df = cleaned_df.drop(index=rows_to_drop)
            report['dropped_rows_count'] = len(rows_to_drop)

    # ---------------------------------------------------------
    # 3) Strategy: IMPUTE Missing Data
    # ---------------------------------------------------------
    elif strategy == 'impute':
        numeric_cols = cleaned_df.select_dtypes(include='number').columns
        categorical_cols = cleaned_df.select_dtypes(exclude='number').columns

        # Numeric Imputation
        for column in numeric_cols:
            if cleaned_df[column].isnull().any():
                if numeric_method == 'mean':
                    value = cleaned_df[column].mean()

                elif numeric_method == 'median':
                    value = cleaned_df[column].median()

                elif numeric_method == 'auto':
                    skewness = cleaned_df[column].skew()
                    if abs(skewness) > skew_threshold:
                        value = cleaned_df[column].median()
                        report[f'{column}_imputation_method'] = 'median (skewness detected)'
                    else:
                        value = cleaned_df[column].mean()
                        report[f'{column}_imputation_method'] = 'mean (approx. normal)'
                else:
                    raise ValueError(f"Invalid numeric method: {numeric_method}")

                cleaned_df[column].fillna(value, inplace=True)

        # Categorical Imputation
        for column in categorical_cols:
            if cleaned_df[column].isnull().any():
                if categorical_method == 'mode':
                    value = cleaned_df[column].mode()[0]

                elif categorical_method == 'constant':
                    if constant_value is None:
                        raise ValueError("Constant value is required when using categorical method='constant'")
                    value = constant_value

                else:
                    raise ValueError(f"Invalid categorical method: {categorical_method}")

                cleaned_df[column].fillna(value, inplace=True)

    # ---------------------------------------------------------
    # 4) Strategy: None (Skip)
    # ---------------------------------------------------------
    elif strategy == 'none':
        report['message'] = "Missing Value Handling skipped (strategy='none')."
    
    else:
        raise ValueError(f"Invalid strategy: {strategy}")

    # ---------------------------------------------------------
    # Final report
    # ---------------------------------------------------------
    report["final_missing_count"] = cleaned_df.isnull().sum().to_dict()
    report["final_missing_percentage"] = (cleaned_df.isnull().mean() * 100).to_dict()

    return cleaned_df, report
