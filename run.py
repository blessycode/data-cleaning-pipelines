from data_cleaning_pipeline.pipe import clean_data

# Replace with your dataset path
data_source = r"C:\Users\blessycode\Downloads\Healthcare.csv"
file_type = "csv"  # csv, excel, sql

# Run the pipeline (now returns 3 values)
cleaned_df, reports, output_files = clean_data(data_source, file_type=file_type)

# Check results
if cleaned_df is not None:
    print("\n" + "=" * 60)
    print("✅ DATA CLEANING COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print(f"📊 Cleaned dataset shape: {cleaned_df.shape}")

    # Show basic info about the cleaned data
    print("\n📋 CLEANED DATASET INFO:")
    print(f"  • Rows: {cleaned_df.shape[0]:,}")
    print(f"  • Columns: {cleaned_df.shape[1]}")
    print(f"  • Memory usage: {cleaned_df.memory_usage(deep=True).sum() / (1024 ** 2):.2f} MB")

    # Show missing values in cleaned data
    missing_values = cleaned_df.isnull().sum().sum()
    missing_percentage = (missing_values / (cleaned_df.shape[0] * cleaned_df.shape[1]) * 100)
    print(f"  • Missing values: {missing_values:,} ({missing_percentage:.2f}%)")

    # Show duplicates in cleaned data
    duplicates = cleaned_df.duplicated().sum()
    duplicate_percentage = (duplicates / cleaned_df.shape[0] * 100)
    print(f"  • Duplicate rows: {duplicates:,} ({duplicate_percentage:.2f}%)")

    # Show column types
    print("\n📊 COLUMN TYPES:")
    dtypes = cleaned_df.dtypes.value_counts()
    for dtype, count in dtypes.items():
        print(f"  • {dtype}: {count} columns")

    # Show output files generated
    print("\n📁 GENERATED OUTPUT FILES:")
    for file_type, files in output_files.items():
        if files:
            print(f"  📂 {file_type.capitalize()}: {len(files)} file(s)")
            # Show first 3 files of each type
            for i, file in enumerate(files[:3]):
                print(f"    {i + 1}. {file}")
            if len(files) > 3:
                print(f"    ... and {len(files) - 3} more")

    # Save cleaned dataset (optional - already saved by pipeline)
    try:
        output_path = r"C:\Users\blessycode\projects\data-cleaning-pipelines\cleaned_dataset.csv"
        cleaned_df.to_csv(output_path, index=False)
        print(f"\n💾 Cleaned data saved to: {output_path}")
    except Exception as e:
        print(f"\n⚠️  Could not save cleaned data: {str(e)}")

else:
    print("\n❌ PIPELINE FAILED")
    print("=" * 60)
    if 'ingestion' in reports:
        ingestion_report = reports['ingestion']
        print(f"Error: {ingestion_report.get('errors', 'Unknown error')}")
        print(f"Source: {ingestion_report.get('source')}")
        print(f"File type: {ingestion_report.get('file_type')}")

# Optional: Display summary of reports
print("\n" + "=" * 60)
print("📊 REPORTS SUMMARY")
print("=" * 60)

for step, report in reports.items():
    print(f"\n📌 {step.upper()} REPORT:")

    if step == "ingestion":
        if report.get("status") == "success":
            info = report.get("info", {})
            print(f"  Status: ✅ Success")
            print(f"  Rows loaded: {info.get('rows', 'N/A'):,}")
            print(f"  Columns loaded: {info.get('columns', 'N/A')}")
            print(f"  Memory usage: {info.get('memory_usage_mb', 'N/A')} MB")
        else:
            print(f"  Status: ❌ Failed")
            print(f"  Error: {report.get('errors', 'Unknown error')}")

    elif step == "profiling":
        summary = report.get("summary", {})
        basic = report.get("basic", {})

        print(f"  Status: ✅ Generated")
        print(f"  Dataset size: {summary.get('total_rows', 'N/A'):,} rows × {summary.get('total_columns', 'N/A')} cols")
        print(f"  Numerical columns: {summary.get('numerical_columns', 'N/A')}")
        print(f"  Categorical columns: {summary.get('categorical_columns', 'N/A')}")

        # Data quality issues
        missing_info = basic.get("missing_values", {})
        duplicates = basic.get("duplicates", {})

        missing_pct = missing_info.get('total_missing_percent', 0)
        duplicate_pct = duplicates.get('duplicate_percent', 0)

        issues = []
        if missing_pct > 5:
            issues.append(f"{missing_pct:.1f}% missing values")
        if duplicate_pct > 10:
            issues.append(f"{duplicate_pct:.1f}% duplicates")

        empty_cols = basic.get("empty_columns", [])
        if empty_cols:
            issues.append(f"{len(empty_cols)} empty columns")

        if issues:
            print(f"  ⚠️  Data quality issues: {', '.join(issues)}")
        else:
            print(f"  ✓ Data quality: Good")

# Display quick statistics from profiling if available
if 'profiling' in reports:
    print("\n" + "=" * 60)
    print("📈 QUICK STATISTICS")
    print("=" * 60)

    profile = reports['profiling']
    numerical = profile.get("numerical", {})
    categorical = profile.get("categorical", {})

    if numerical:
        print("\n🔢 NUMERICAL COLUMNS (Sample):")
        for col, stats in list(numerical.items())[:3]:  # Show first 3
            print(f"  • {col}:")
            print(f"    Mean: {stats.get('mean', 'N/A'):.2f}")
            print(f"    Std: {stats.get('std', 'N/A'):.2f}")
            print(f"    Range: {stats.get('range', 'N/A'):.2f}")

    if categorical:
        print("\n🏷️  CATEGORICAL COLUMNS (Sample):")
        for col, stats in list(categorical.items())[:3]:  # Show first 3
            print(f"  • {col}:")
            print(f"    Unique values: {stats.get('unique_count', 'N/A')}")
            dominant_pct = stats.get('distribution', {}).get('dominant_percent', 0)
            if dominant_pct > 50:
                print(f"    Top category: {dominant_pct:.1f}%")

print("\n" + "=" * 60)
print("✨ PIPELINE EXECUTION COMPLETE")
print("=" * 60)