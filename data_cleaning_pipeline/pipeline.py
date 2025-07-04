from data_cleaning_pipeline.utils import ingestion
from data_cleaning_pipeline.cleaning import profiler
from data_cleaning_pipeline.cleaning import missing
from data_cleaning_pipeline.cleaning import duplicate_handler

def clean_data(source, file_type='csv', **kwargs):
    df, ingestion_report =ingestion.load_data(source, file_type=file_type, **kwargs)
    if df is None:
        return None, ingestion_report

    reports = {'ingestion': ingestion_report}

    # profiling
    reports['intial_profile'] = profiler._initial_report(df)
    reports['categorical_profile'] = profiler.generate_categorical_profile(df)
    reports['visual_profile'] = profiler.generate_visual_profile(df, output_dir="profiling_reports")

    #Missing
    cleaned_df, missing_report = missing.handle_missing(df, strategy='impute', numeric_method='auto',categorical_method='mode',
                                        constant_value=None,drop_threshold=0.05,skew_threshold=1.0)



    reports['missing_handler'] = missing_report

    #duplicate handler
    cleaned_df, duplicate_report = duplicate_handler.duplicate_handler(cleaned_df, subset=None, keep='first', action='remove')
    reports['duplicate_handling'] = duplicate_report

    return cleaned_df, reports
