# main_pipeline.py

from data_cleaning_pipeline.utils import ingestion
from data_cleaning_pipeline.cleaning import profiler
from data_cleaning_pipeline.cleaning import missing
from data_cleaning_pipeline.cleaning import duplicate_handler
from data_cleaning_pipeline.cleaning import outlier_handler
from data_cleaning_pipeline.cleaning import column_handlr
from data_cleaning_pipeline.cleaning import inconsistent_formatting
from data_cleaning_pipeline.cleaning.data_conversion import DataConverter


def clean_data(source, file_type='csv', apply_feature_engineering=True, **kwargs):
    """
    Main pipeline to clean data:
    1. Ingestion
    2. Column cleaning
    3. Inconsistent formatting
    4. Profiling
    5. Missing values handling
    6. Duplicate handling
    7. Outlier handling
    8. Optional feature engineering (scaling, encoding)

    Args:
        source (str): File path or URL.
        file_type (str): 'csv', 'excel', etc.
        apply_feature_engineering (bool): Whether to apply DataConverter.
        **kwargs: Extra arguments for ingestion.load_data.

    Returns:
        transformed_df (pd.DataFrame): Cleaned (and optionally transformed) DataFrame.
        reports (dict): Detailed cleaning and profiling reports.
    """

    # ----------------------------
    # 1️⃣ Load data
    # ----------------------------
    df, ingestion_report = ingestion.load_data(source, file_type=file_type, **kwargs)
    if df is None:
        return None, ingestion_report

    reports = {'ingestion': ingestion_report}

    # ----------------------------
    # 2️⃣ Column name cleaning
    # ----------------------------
    df, column_report = column_handlr.clean_column_names(df)
    reports['column_cleaning'] = column_report

    # ----------------------------
    # 3️⃣ Inconsistent formatting
    # ----------------------------
    df, format_report = inconsistent_formatting.clean_inconsistent_formatting(df)
    reports['format_cleaning'] = format_report

    # ----------------------------
    # 4️⃣ Profiling
    # ----------------------------
    reports['initial_profile'] = profiler.generate_basic_profile(df)
    reports['categorical_profile'] = profiler.generate_categorical_profile(df)
    reports['visual_profile'] = profiler.generate_visual_profile(df, output_dir="profiling_reports")

    # ----------------------------
    # 5️⃣ Missing value handling
    # ----------------------------
    cleaned_df, missing_report = missing.handle_missing(
        df,
        strategy='impute',
        numeric_method='auto',
        categorical_method='mode',
        constant_value=None,
        drop_threshold=0.05,
        skew_threshold=1.0
    )
    reports['missing_handler'] = missing_report

    # ----------------------------
    # 6️⃣ Duplicate handling
    # ----------------------------
    cleaned_df, duplicate_report = duplicate_handler.duplicate_handler(
        cleaned_df,
        subset=None,
        keep='first',
        action='remove'
    )
    reports['duplicate_handling'] = duplicate_report

    # ----------------------------
    # 7️⃣ Outlier handling
    # ----------------------------
    cleaned_df, outlier_report = outlier_handler.handle_outliers(
        cleaned_df,
        method='iqr',
        threshold=3.0,
        iqr_factor=1.5,
        mcd_threshold=0.975,
        action='remove',
        hypothesis_test=True,
        significance_level=0.05
    )
    reports['outlier_handling'] = outlier_report

    # ----------------------------
    # 8️⃣ Optional Feature Engineering (DataConverter)
    # ----------------------------
    if apply_feature_engineering:
        numeric_cols = cleaned_df.select_dtypes(include='number').columns.tolist()
        cat_cols = cleaned_df.select_dtypes(include='object').columns.tolist()

        converter = DataConverter(
            categorical_features=cat_cols,
            numerical_features=numeric_cols,
            encoding_method='onehot',
            scaling_method='minmax',
            imputation_strategy='mean'
        )
        transformed_df = converter.fit_transform(cleaned_df)

        reports['feature_engineering'] = {
            'categorical_features': cat_cols,
            'numerical_features': numeric_cols,
            'transformed_columns': transformed_df.columns.tolist()
        }
    else:
        transformed_df = cleaned_df

    return transformed_df, reports
