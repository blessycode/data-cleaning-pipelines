from data_cleaning_pipeline.utils import ingestion
from data_cleaning_pipeline.cleaning import profiler
from data_cleaning_pipeline.cleaning import missing
from data_cleaning_pipeline.cleaning import duplicate_handler
from data_cleaning_pipeline.cleaning import outlier_handler
from data_cleaning_pipeline.cleaning import column_handlr
from data_cleaning_pipeline.cleaning import inconsistent_formatting



def clean_data(source, file_type='csv', **kwargs):
    df, ingestion_report = ingestion.load_data(source, file_type=file_type, **kwargs)
    if df is None:
        return None, ingestion_report

    reports = {'ingestion': ingestion_report}

    # 1 Column name cleaning
    df, column_report = column_handlr.clean_column_names(df)
    reports['column_cleaning'] = column_report

    # 2 Inconsistent formatting cleaning
    df, format_report = inconsistent_formatting.clean_inconsistent_formatting(df)
    reports['format_cleaning'] = format_report

    # 3 Profiling
    reports['initial_profile'] = profiler.generate_initial_report(df)
    reports['categorical_profile'] = profiler.generate_categorical_profile(df)
    reports['visual_profile'] = profiler.generate_visual_profile(df, output_dir="profiling_reports")

    # 4 Missing value handling
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

    # 5️ Duplicate handling
    cleaned_df, duplicate_report = duplicate_handler.duplicate_handler(
        cleaned_df,
        subset=None,
        keep='first',
        action='remove'
    )
    reports['duplicate_handling'] = duplicate_report

    # 6️ Outlier handling
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

    return cleaned_df, reports
