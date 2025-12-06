from data_cleaning_pipeline.pipeline import clean_data

# Replace with your dataset path
data_source = r"C:\Users\blessycode\Documents\home-credit-default-risk\application_train.csv"
file_type = "csv"  # csv, excel, sql

# Run the pipeline
cleaned_df, reports = clean_data(data_source, file_type=file_type)

# Check results
if cleaned_df is not None:
    print("✅ Data cleaned successfully!")
    print(f"Shape: {cleaned_df.shape}")
else:
    print("❌ Pipeline failed. Check ingestion report.")
    print(reports['ingestion'])

# Save cleaned dataset
cleaned_df.to_csv(r"C:\Users\blessycode\projects\data-cleaning-pipelines\cleaned_dataset.csv", index=False)

# Optional: inspect reports
for step, report in reports.items():
    print(f"\n--- {step} ---")
    for key, value in report.items():
        print(f"{key}: {value}")
