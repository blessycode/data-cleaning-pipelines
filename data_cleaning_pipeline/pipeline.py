from data_cleaning_pipeline.utils import ingestion
from data_cleaning_pipeline.cleaning import profiler

def clean_data(source, file_type='csv', **kwargs):
    df, ingestion_report =ingestion.load_data(source, file_type=file_type, **kwargs)
    if df is None:
        return None, ingestion_report

    reports = {'ingestion': ingestion_report}

    # profiling
    reports['intial_profile'] = profiler._initial_report(df)
    reports['categorical_profile'] = profiler.generate_categorical_profile(df)
    reports['visual_profile'] = profiler.generate_visual_profile(df, output_dir="profiling_reports")

    return df, reports
