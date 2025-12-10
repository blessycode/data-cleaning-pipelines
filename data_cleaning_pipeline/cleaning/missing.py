import numpy as np
import pandas as pd
from scipy import stats
from sklearn.impute import KNNImputer, SimpleImputer
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
import warnings

warnings.filterwarnings('ignore')


class DataCleaner:
    """Comprehensive data cleaning toolkit"""

    def __init__(self, verbose=True):
        self.verbose = verbose
        self.reports = {}

    def _log(self, message):
        """Helper method for logging"""
        if self.verbose:
            print(f"🔧 {message}")

    def handle_missing_values(self, df, strategy='impute', **kwargs):
        """
        Handle missing values with multiple strategies

        Parameters:
        -----------
        df : pd.DataFrame
            Input dataframe
        strategy : str
            'impute', 'drop', 'none', 'advanced'
        **kwargs : additional parameters

        Returns:
        --------
        cleaned_df : pd.DataFrame
        report : dict
        """

        # Initialize report
        report = {
            'operation': 'missing_value_handling',
            'strategy': strategy,
            'initial_missing_count': int(df.isnull().sum().sum()),
            'initial_missing_percentage': round(df.isnull().sum().sum() / (df.shape[0] * df.shape[1]) * 100, 3),
            'columns_with_missing': df.columns[df.isnull().any()].tolist(),
            'missing_by_column': df.isnull().sum().to_dict()
        }

        cleaned_df = df.copy()

        # ---------------------------------------------------------
        # 1) Always remove columns with 100% missing values
        # ---------------------------------------------------------
        columns_100_missing = cleaned_df.columns[cleaned_df.isnull().mean() == 1.0]
        if len(columns_100_missing) > 0:
            cleaned_df = cleaned_df.drop(columns=columns_100_missing)
            report['dropped_100_missing_columns'] = list(columns_100_missing)
            self._log(f"Dropped {len(columns_100_missing)} columns with 100% missing values")

        # ---------------------------------------------------------
        # 2) Strategy: DROP
        # ---------------------------------------------------------
        if strategy == 'drop':
            cleaned_df, drop_report = self._drop_missing_strategy(cleaned_df, **kwargs)
            report.update(drop_report)

        # ---------------------------------------------------------
        # 3) Strategy: IMPUTE (Basic)
        # ---------------------------------------------------------
        elif strategy == 'impute':
            cleaned_df, impute_report = self._impute_missing_strategy(cleaned_df, **kwargs)
            report.update(impute_report)

        # ---------------------------------------------------------
        # 4) Strategy: ADVANCED (ML-based)
        # ---------------------------------------------------------
        elif strategy == 'advanced':
            cleaned_df, advanced_report = self._advanced_imputation_strategy(cleaned_df, **kwargs)
            report.update(advanced_report)

        # ---------------------------------------------------------
        # 5) Strategy: NONE (Skip)
        # ---------------------------------------------------------
        elif strategy == 'none':
            report['message'] = "Missing value handling skipped"
            self._log("Skipping missing value handling")

        else:
            raise ValueError(f"Invalid strategy: {strategy}. Choose from: 'drop', 'impute', 'advanced', 'none'")

        # ---------------------------------------------------------
        # Final statistics
        # ---------------------------------------------------------
        report['final_missing_count'] = int(cleaned_df.isnull().sum().sum())
        report['final_missing_percentage'] = round(
            cleaned_df.isnull().sum().sum() / (cleaned_df.shape[0] * cleaned_df.shape[1]) * 100, 3
        )
        report['improvement_percentage'] = round(
            (report['initial_missing_percentage'] - report['final_missing_percentage']), 3
        )

        self.reports['missing_values'] = report
        return cleaned_df, report

    def _drop_missing_strategy(self, df, **kwargs):
        """Internal method for drop strategy"""
        report = {'drop_strategy': 'custom'}
        cleaned_df = df.copy()

        # Get parameters
        drop_columns_threshold = kwargs.get('drop_columns_threshold', 0.3)
        drop_rows_threshold = kwargs.get('drop_rows_threshold', 0.5)
        drop_specific_columns = kwargs.get('drop_specific_columns', None)

        # Drop specific columns if provided
        if drop_specific_columns:
            columns_to_drop = [col for col in drop_specific_columns if col in cleaned_df.columns]
            cleaned_df = cleaned_df.drop(columns=columns_to_drop, errors='ignore')
            report['dropped_specific_columns'] = columns_to_drop
            self._log(f"Dropped {len(columns_to_drop)} specified columns")

        # Drop columns exceeding threshold
        columns_to_drop = cleaned_df.columns[cleaned_df.isnull().mean() > drop_columns_threshold]
        if len(columns_to_drop) > 0:
            cleaned_df = cleaned_df.drop(columns=columns_to_drop)
            report['dropped_high_missing_columns'] = list(columns_to_drop)
            report['column_drop_threshold'] = drop_columns_threshold
            self._log(f"Dropped {len(columns_to_drop)} columns with >{drop_columns_threshold * 100}% missing values")

        # Drop rows exceeding threshold
        rows_to_drop = cleaned_df.index[cleaned_df.isnull().mean(axis=1) > drop_rows_threshold]
        if len(rows_to_drop) > 0:
            cleaned_df = cleaned_df.drop(index=rows_to_drop)
            report['dropped_rows_count'] = len(rows_to_drop)
            report['row_drop_threshold'] = drop_rows_threshold
            self._log(f"Dropped {len(rows_to_drop)} rows with >{drop_rows_threshold * 100}% missing values")

        return cleaned_df, report

    def _impute_missing_strategy(self, df, **kwargs):
        """Internal method for basic imputation strategy"""
        report = {'imputation_strategy': 'basic'}
        cleaned_df = df.copy()

        # Get parameters
        numeric_method = kwargs.get('numeric_method', 'auto')
        categorical_method = kwargs.get('categorical_method', 'mode')
        constant_value = kwargs.get('constant_value', None)
        skew_threshold = kwargs.get('skew_threshold', 1.0)

        # Separate column types
        numeric_cols = cleaned_df.select_dtypes(include=[np.number]).columns
        categorical_cols = cleaned_df.select_dtypes(exclude=[np.number]).columns

        # Numeric imputation
        for col in numeric_cols:
            if cleaned_df[col].isnull().any():
                missing_count = cleaned_df[col].isnull().sum()

                if numeric_method == 'mean':
                    value = cleaned_df[col].mean()
                    method_used = 'mean'

                elif numeric_method == 'median':
                    value = cleaned_df[col].median()
                    method_used = 'median'

                elif numeric_method == 'mode':
                    value = cleaned_df[col].mode()[0] if not cleaned_df[col].mode().empty else 0
                    method_used = 'mode'

                elif numeric_method == 'auto':
                    skewness = cleaned_df[col].skew()
                    if abs(skewness) > skew_threshold:
                        value = cleaned_df[col].median()
                        method_used = 'median (skewed)'
                    else:
                        value = cleaned_df[col].mean()
                        method_used = 'mean (normal)'
                    report[f'{col}_skewness'] = round(skewness, 3)

                elif numeric_method == 'constant':
                    if constant_value is None:
                        raise ValueError("Constant value required for numeric_method='constant'")
                    value = constant_value
                    method_used = 'constant'

                else:
                    raise ValueError(f"Invalid numeric_method: {numeric_method}")

                cleaned_df[col].fillna(value, inplace=True)
                report[f'{col}_imputation'] = {
                    'method': method_used,
                    'value': float(value) if pd.notna(value) else None,
                    'missing_count': int(missing_count)
                }

        # Categorical imputation
        for col in categorical_cols:
            if cleaned_df[col].isnull().any():
                missing_count = cleaned_df[col].isnull().sum()

                if categorical_method == 'mode':
                    value = cleaned_df[col].mode()[0] if not cleaned_df[col].mode().empty else 'Unknown'
                    method_used = 'mode'

                elif categorical_method == 'constant':
                    if constant_value is None:
                        raise ValueError("Constant value required for categorical_method='constant'")
                    value = constant_value
                    method_used = 'constant'

                elif categorical_method == 'unknown':
                    value = 'Unknown'
                    method_used = 'unknown'

                else:
                    raise ValueError(f"Invalid categorical_method: {categorical_method}")

                cleaned_df[col].fillna(value, inplace=True)
                report[f'{col}_imputation'] = {
                    'method': method_used,
                    'value': str(value),
                    'missing_count': int(missing_count)
                }

        return cleaned_df, report

    def _advanced_imputation_strategy(self, df, **kwargs):
        """Internal method for advanced ML-based imputation"""
        report = {'imputation_strategy': 'advanced'}
        cleaned_df = df.copy()

        # Get parameters
        method = kwargs.get('advanced_method', 'knn')
        n_neighbors = kwargs.get('n_neighbors', 5)
        max_iter = kwargs.get('max_iter', 10)

        # Separate numeric and categorical columns
        numeric_cols = cleaned_df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = cleaned_df.select_dtypes(exclude=[np.number]).columns.tolist()

        # First handle categorical columns with mode imputation
        for col in categorical_cols:
            if cleaned_df[col].isnull().any():
                mode_value = cleaned_df[col].mode()[0] if not cleaned_df[col].mode().empty else 'Unknown'
                cleaned_df[col].fillna(mode_value, inplace=True)

        # Handle numeric columns with advanced methods
        if len(numeric_cols) > 0:
            numeric_df = cleaned_df[numeric_cols].copy()

            if method == 'knn':
                imputer = KNNImputer(n_neighbors=n_neighbors)
                imputed_array = imputer.fit_transform(numeric_df)
                cleaned_df[numeric_cols] = imputed_array
                report['method_details'] = f'KNN Imputer (n_neighbors={n_neighbors})'

            elif method == 'iterative':
                imputer = IterativeImputer(max_iter=max_iter, random_state=42)
                imputed_array = imputer.fit_transform(numeric_df)
                cleaned_df[numeric_cols] = imputed_array
                report['method_details'] = f'Iterative Imputer (max_iter={max_iter})'

            elif method == 'mice':
                # MICE implementation using IterativeImputer
                imputer = IterativeImputer(
                    max_iter=max_iter,
                    random_state=42,
                    estimator=None  # Default: BayesianRidge
                )
                imputed_array = imputer.fit_transform(numeric_df)
                cleaned_df[numeric_cols] = imputed_array
                report['method_details'] = f'MICE Imputer (max_iter={max_iter})'

            else:
                raise ValueError(f"Invalid advanced_method: {method}")

            report['numeric_columns_imputed'] = numeric_cols
            report['categorical_columns_imputed'] = categorical_cols

        return cleaned_df, report

    def handle_outliers(self, df, method='iqr', **kwargs):
        """
        Detect and handle outliers

        Parameters:
        -----------
        df : pd.DataFrame
        method : str - 'iqr', 'zscore', 'percentile', 'isolation_forest', 'none'

        Returns:
        --------
        cleaned_df : pd.DataFrame
        report : dict
        """

        report = {
            'operation': 'outlier_handling',
            'method': method,
            'columns_analyzed': df.select_dtypes(include=[np.number]).columns.tolist()
        }

        cleaned_df = df.copy()
        numeric_cols = df.select_dtypes(include=[np.number]).columns

        if method == 'none' or len(numeric_cols) == 0:
            report['message'] = 'Outlier handling skipped'
            return cleaned_df, report

        outlier_report = {}
        total_outliers = 0

        for col in numeric_cols:
            col_data = cleaned_df[col].dropna()

            if method == 'iqr':
                Q1 = col_data.quantile(0.25)
                Q3 = col_data.quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR

                outliers = col_data[(col_data < lower_bound) | (col_data > upper_bound)]

            elif method == 'zscore':
                z_scores = np.abs(stats.zscore(col_data))
                outliers = col_data[z_scores > 3]  # 3 standard deviations
                lower_bound = col_data.mean() - 3 * col_data.std()
                upper_bound = col_data.mean() + 3 * col_data.std()

            elif method == 'percentile':
                lower_bound = col_data.quantile(0.01)
                upper_bound = col_data.quantile(0.99)
                outliers = col_data[(col_data < lower_bound) | (col_data > upper_bound)]

            else:
                raise ValueError(f"Invalid method: {method}")

            outlier_count = len(outliers)
            outlier_percentage = (outlier_count / len(col_data)) * 100

            outlier_report[col] = {
                'outlier_count': int(outlier_count),
                'outlier_percentage': round(outlier_percentage, 3),
                'lower_bound': round(float(lower_bound), 3),
                'upper_bound': round(float(upper_bound), 3),
                'method': method
            }

            total_outliers += outlier_count

            # Handle outliers if requested
            handle_action = kwargs.get('handle_action', 'detect_only')

            if handle_action == 'remove':
                # Remove rows with outliers
                outlier_indices = outliers.index
                cleaned_df = cleaned_df.drop(index=outlier_indices)

            elif handle_action == 'cap':
                # Cap outliers at bounds
                cleaned_df.loc[cleaned_df[col] < lower_bound, col] = lower_bound
                cleaned_df.loc[cleaned_df[col] > upper_bound, col] = upper_bound

            elif handle_action == 'impute':
                # Replace outliers with median
                median_val = col_data.median()
                cleaned_df.loc[outliers.index, col] = median_val

        report['outlier_details'] = outlier_report
        report['total_outliers_detected'] = int(total_outliers)
        report['handle_action'] = kwargs.get('handle_action', 'detect_only')

        if kwargs.get('handle_action') != 'detect_only':
            report['rows_after_handling'] = cleaned_df.shape[0]

        self.reports['outliers'] = report
        return cleaned_df, report

    def handle_duplicates(self, df, method='remove', subset=None, **kwargs):
        """
        Handle duplicate rows

        Parameters:
        -----------
        df : pd.DataFrame
        method : str - 'remove', 'mark', 'keep_first', 'keep_last', 'none'
        subset : list - columns to consider for duplicates

        Returns:
        --------
        cleaned_df : pd.DataFrame
        report : dict
        """

        report = {
            'operation': 'duplicate_handling',
            'method': method,
            'initial_rows': df.shape[0],
            'duplicate_count': 0
        }

        cleaned_df = df.copy()

        if method == 'none':
            report['message'] = 'Duplicate handling skipped'
            return cleaned_df, report

        # Find duplicates
        if subset:
            duplicates = cleaned_df.duplicated(subset=subset, keep=False)
        else:
            duplicates = cleaned_df.duplicated(keep=False)

        duplicate_count = duplicates.sum()
        report['duplicate_count'] = int(duplicate_count)
        report['duplicate_percentage'] = round((duplicate_count / len(cleaned_df)) * 100, 3)

        if duplicate_count == 0:
            report['message'] = 'No duplicates found'
            return cleaned_df, report

        if method == 'remove':
            # Remove all duplicates (keeping none)
            cleaned_df = cleaned_df.drop_duplicates(keep=False)
            report['rows_removed'] = int(duplicate_count)
            report['final_rows'] = cleaned_df.shape[0]
            self._log(f"Removed {duplicate_count} duplicate rows")

        elif method == 'mark':
            # Mark duplicates with a new column
            cleaned_df['is_duplicate'] = duplicates
            report['mark_column_added'] = 'is_duplicate'

        elif method == 'keep_first':
            # Keep first occurrence
            before_rows = len(cleaned_df)
            cleaned_df = cleaned_df.drop_duplicates(keep='first')
            report['rows_removed'] = before_rows - cleaned_df.shape[0]
            report['final_rows'] = cleaned_df.shape[0]

        elif method == 'keep_last':
            # Keep last occurrence
            before_rows = len(cleaned_df)
            cleaned_df = cleaned_df.drop_duplicates(keep='last')
            report['rows_removed'] = before_rows - cleaned_df.shape[0]
            report['final_rows'] = cleaned_df.shape[0]

        else:
            raise ValueError(f"Invalid method: {method}")

        self.reports['duplicates'] = report
        return cleaned_df, report

    def handle_inconsistent_data(self, df, **kwargs):
        """
        Handle inconsistent data types and values

        Parameters:
        -----------
        df : pd.DataFrame

        Returns:
        --------
        cleaned_df : pd.DataFrame
        report : dict
        """

        report = {
            'operation': 'inconsistency_handling',
            'columns_processed': [],
            'type_conversions': {},
            'value_corrections': {}
        }

        cleaned_df = df.copy()

        for col in cleaned_df.columns:
            col_report = {}

            # Check for mixed types
            unique_types = cleaned_df[col].apply(type).unique()
            if len(unique_types) > 1:
                # Try to convert to consistent type
                try:
                    # Try numeric conversion first
                    converted = pd.to_numeric(cleaned_df[col], errors='coerce')
                    if not converted.isna().all():
                        cleaned_df[col] = converted
                        col_report['converted_to'] = 'numeric'
                    else:
                        # Try datetime
                        converted = pd.to_datetime(cleaned_df[col], errors='coerce')
                        if not converted.isna().all():
                            cleaned_df[col] = converted
                            col_report['converted_to'] = 'datetime'
                        else:
                            # Convert to string
                            cleaned_df[col] = cleaned_df[col].astype(str)
                            col_report['converted_to'] = 'string'
                except:
                    cleaned_df[col] = cleaned_df[col].astype(str)
                    col_report['converted_to'] = 'string'

            # Check for inconsistent casing in strings
            if cleaned_df[col].dtype == 'object':
                # Count unique casings
                unique_values = cleaned_df[col].dropna().unique()
                if len(unique_values) > 0:
                    # Standardize casing if needed
                    sample = unique_values[0]
                    if isinstance(sample, str):
                        # Check if mixed casing exists
                        has_lower = any(isinstance(v, str) and v.islower() for v in unique_values)
                        has_upper = any(isinstance(v, str) and v.isupper() for v in unique_values)

                        if has_lower and has_upper:
                            # Convert to title case
                            cleaned_df[col] = cleaned_df[col].str.title()
                            col_report['casing_standardized'] = 'title_case'

            # Check for leading/trailing whitespace
            if cleaned_df[col].dtype == 'object':
                before = cleaned_df[col].astype(str).str.strip()
                if not cleaned_df[col].equals(before):
                    cleaned_df[col] = before
                    col_report['whitespace_trimmed'] = True

            if col_report:
                report['columns_processed'].append(col)
                report['type_conversions'][col] = col_report

        self.reports['inconsistent_data'] = report
        return cleaned_df, report

    def normalize_data(self, df, method='minmax', **kwargs):
        """
        Normalize numerical data

        Parameters:
        -----------
        df : pd.DataFrame
        method : str - 'minmax', 'zscore', 'robust', 'none'

        Returns:
        --------
        normalized_df : pd.DataFrame
        report : dict
        """

        report = {
            'operation': 'data_normalization',
            'method': method,
            'columns_normalized': []
        }

        normalized_df = df.copy()
        numeric_cols = df.select_dtypes(include=[np.number]).columns

        if method == 'none' or len(numeric_cols) == 0:
            report['message'] = 'Normalization skipped'
            return normalized_df, report

        normalization_params = {}

        for col in numeric_cols:
            col_data = normalized_df[col].dropna()

            if method == 'minmax':
                min_val = col_data.min()
                max_val = col_data.max()

                if max_val > min_val:  # Avoid division by zero
                    normalized_df[col] = (normalized_df[col] - min_val) / (max_val - min_val)
                    normalization_params[col] = {'min': float(min_val), 'max': float(max_val)}

            elif method == 'zscore':
                mean_val = col_data.mean()
                std_val = col_data.std()

                if std_val > 0:  # Avoid division by zero
                    normalized_df[col] = (normalized_df[col] - mean_val) / std_val
                    normalization_params[col] = {'mean': float(mean_val), 'std': float(std_val)}

            elif method == 'robust':
                median_val = col_data.median()
                iqr_val = col_data.quantile(0.75) - col_data.quantile(0.25)

                if iqr_val > 0:  # Avoid division by zero
                    normalized_df[col] = (normalized_df[col] - median_val) / iqr_val
                    normalization_params[col] = {'median': float(median_val), 'iqr': float(iqr_val)}

            report['columns_normalized'].append(col)

        report['normalization_parameters'] = normalization_params
        self.reports['normalization'] = report

        return normalized_df, report

    def clean_all(self, df, steps=None, **kwargs):
        """
        Complete data cleaning pipeline

        Parameters:
        -----------
        df : pd.DataFrame
        steps : list - cleaning steps to perform
        **kwargs : parameters for each step

        Returns:
        --------
        cleaned_df : pd.DataFrame
        comprehensive_report : dict
        """

        if steps is None:
            steps = ['missing', 'duplicates', 'outliers', 'inconsistent', 'normalize']

        comprehensive_report = {
            'pipeline_steps': steps,
            'initial_shape': df.shape,
            'initial_info': {
                'missing_percentage': round(df.isnull().sum().sum() / (df.shape[0] * df.shape[1]) * 100, 3),
                'duplicate_percentage': round(df.duplicated().mean() * 100, 3)
            }
        }

        cleaned_df = df.copy()
        step_reports = {}

        # Execute each cleaning step
        for step in steps:
            self._log(f"Executing step: {step}")

            if step == 'missing':
                missing_kwargs = kwargs.get('missing_kwargs', {})
                cleaned_df, report = self.handle_missing_values(cleaned_df, **missing_kwargs)
                step_reports['missing_values'] = report

            elif step == 'duplicates':
                duplicate_kwargs = kwargs.get('duplicate_kwargs', {})
                cleaned_df, report = self.handle_duplicates(cleaned_df, **duplicate_kwargs)
                step_reports['duplicates'] = report

            elif step == 'outliers':
                outlier_kwargs = kwargs.get('outlier_kwargs', {})
                cleaned_df, report = self.handle_outliers(cleaned_df, **outlier_kwargs)
                step_reports['outliers'] = report

            elif step == 'inconsistent':
                inconsistent_kwargs = kwargs.get('inconsistent_kwargs', {})
                cleaned_df, report = self.handle_inconsistent_data(cleaned_df, **inconsistent_kwargs)
                step_reports['inconsistent_data'] = report

            elif step == 'normalize':
                normalize_kwargs = kwargs.get('normalize_kwargs', {})
                cleaned_df, report = self.normalize_data(cleaned_df, **normalize_kwargs)
                step_reports['normalization'] = report

            else:
                self._log(f"Warning: Unknown step '{step}' skipped")

        # Final statistics
        comprehensive_report['final_shape'] = cleaned_df.shape
        comprehensive_report['step_reports'] = step_reports
        comprehensive_report['overall_improvement'] = {
            'rows_reduction_percentage': round((1 - cleaned_df.shape[0] / df.shape[0]) * 100, 3),
            'data_quality_score': self._calculate_quality_score(cleaned_df)
        }

        self._log(f"Cleaning complete! Final shape: {cleaned_df.shape}")
        return cleaned_df, comprehensive_report

    def _calculate_quality_score(self, df):
        """Calculate overall data quality score"""
        score = 100

        # Penalize for missing values
        missing_percent = df.isnull().sum().sum() / (df.shape[0] * df.shape[1]) * 100
        score -= missing_percent * 2  # Double penalty for missing values

        # Penalize for duplicates
        duplicate_percent = df.duplicated().mean() * 100
        score -= duplicate_percent

        # Ensure score is between 0 and 100
        return max(0, min(100, round(score, 2)))

    def get_summary_report(self):
        """Get summary of all cleaning operations performed"""
        summary = {
            'operations_performed': list(self.reports.keys()),
            'total_operations': len(self.reports)
        }

        for operation, report in self.reports.items():
            summary[operation] = {
                'key_metrics': {
                    k: v for k, v in report.items()
                    if isinstance(v, (int, float, str, bool)) and not k.startswith('_')
                }
            }

        return summary


# Convenience functions for backward compatibility
def handle_missing(df, strategy='impute', **kwargs):
    """Legacy function for missing value handling"""
    cleaner = DataCleaner(verbose=False)
    return cleaner.handle_missing_values(df, strategy=strategy, **kwargs)


def clean_data_pipeline(df, steps=None, **kwargs):
    """Legacy function for complete cleaning pipeline"""
    cleaner = DataCleaner(verbose=True)
    return cleaner.clean_all(df, steps=steps, **kwargs)