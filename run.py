from data_cleaning_pipeline.pipe import clean_data
import os
# Replace with your dataset path
data_source = r"C:\Users\blessycode\Downloads\Healthcare.csv"
file_type = "csv"  # csv, excel, sql

# Run the pipeline WITH VISUALIZATIONS ENABLED
# Note: Data cleaning is enabled by default (apply_cleaning=True)
# You can customize cleaning by adding:
#   apply_cleaning=True,  # Enable/disable cleaning (default: True)
#   cleaning_steps=['missing', 'duplicates', 'outliers', 'inconsistent'],  # Custom steps
#   cleaning_kwargs={  # Custom cleaning parameters
#       'missing_kwargs': {'strategy': 'impute', 'numeric_method': 'median'},
#       'duplicate_kwargs': {'method': 'remove'},
#       'outlier_kwargs': {'method': 'iqr', 'handle_action': 'cap'}
#   }
cleaned_df, reports, output_files = clean_data(
    data_source,
    file_type=file_type,
    profile_data=True,
    include_visuals=True,  # ✅ This enables visualizations
    columns_to_plot=['age', 'symptom_count', 'disease', 'gender'],  # ✅ Specify columns to plot
    save_output=True,
    output_dir="data_pipeline_output",
    show_detailed_profile=True,
    apply_cleaning=True  # ✅ Data cleaning enabled (uses DataCleaner class)
)

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
                print(f"    {i + 1}. {os.path.basename(file)}")
            if len(files) > 3:
                print(f"    ... and {len(files) - 3} more")

    # Save cleaned dataset (optional - already saved by pipeline)
    try:
        output_path = r"C:\Users\blessycode\projects\data-cleaning-pipelines\cleaned_dataset.csv"
        cleaned_df.to_csv(output_path, index=False)
        print(f"\n💾 Cleaned data saved to: {output_path}")
    except Exception as e:
        print(f"\n⚠️  Could not save cleaned data: {str(e)}")

    # Check if visualizations were generated
    if 'profiling' in reports and 'visualizations' in reports['profiling']:
        viz = reports['profiling']['visualizations']
        print("\n🎨 VISUALIZATIONS GENERATED:")
        for viz_type, viz_data in viz.items():
            if isinstance(viz_data, dict):
                print(f"  • {viz_type}: {len(viz_data)} plots")
            else:
                print(f"  • {viz_type}: 1 plot")
    else:
        print("\n⚠️  No visualizations were generated. Check if columns_to_plot matches your dataset columns.")

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

    elif step == "cleaning":
        print(f"  Status: ✅ Completed")
        
        # Show pipeline steps executed
        steps = report.get("pipeline_steps", [])
        if steps:
            print(f"  Steps executed: {', '.join(steps)}")
        
        # Show shape changes
        initial_shape = report.get("initial_shape", (0, 0))
        final_shape = report.get("final_shape", (0, 0))
        if initial_shape != final_shape:
            print(f"  Shape change: {initial_shape[0]:,}×{initial_shape[1]} → {final_shape[0]:,}×{final_shape[1]}")
        else:
            print(f"  Final shape: {final_shape[0]:,} rows × {final_shape[1]} columns")
        
        # Show overall improvement
        improvement = report.get("overall_improvement", {})
        quality_score = improvement.get("data_quality_score", None)
        if quality_score is not None:
            print(f"  Data quality score: {quality_score}/100")
        
        rows_reduction = improvement.get("rows_reduction_percentage", 0)
        if rows_reduction > 0:
            print(f"  Rows reduced: {rows_reduction:.1f}%")
        
        # Show step-by-step results
        step_reports = report.get("step_reports", {})
        if step_reports:
            print(f"  Cleaning operations:")
            for step_name, step_report in step_reports.items():
                if step_name == "missing_values":
                    initial = step_report.get("initial_missing_percentage", 0)
                    final = step_report.get("final_missing_percentage", 0)
                    improvement_pct = step_report.get("improvement_percentage", 0)
                    print(f"    • Missing values: {initial:.1f}% → {final:.1f}% (improved by {improvement_pct:.1f}%)")
                elif step_name == "duplicates":
                    dup_count = step_report.get("duplicate_count", 0)
                    if dup_count > 0:
                        print(f"    • Duplicates: {dup_count} rows handled")
                elif step_name == "outliers":
                    total_outliers = step_report.get("total_outliers_detected", 0)
                    if total_outliers > 0:
                        print(f"    • Outliers: {total_outliers} detected")

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

        # Show visualization info
        if 'visualizations' in report:
            print(f"  🎨 Visualizations: {len(report['visualizations'])} types generated")

print("\n" + "=" * 60)
print("✨ PIPELINE EXECUTION COMPLETE")
print("=" * 60)