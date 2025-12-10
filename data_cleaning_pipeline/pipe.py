from data_cleaning_pipeline.utils import ingestion
from data_cleaning_pipeline.cleaning import profiling
import pandas as pd
import os
import json
from datetime import datetime
from typing import Optional, Dict, Any, Tuple
import plotly.io as pio
import numpy as np


def ensure_output_directory(base_dir: str = "data_pipeline_output"):
    """Ensure output directories exist."""
    directories = {
        "reports": os.path.join(base_dir, "reports"),
        "visualizations": os.path.join(base_dir, "visualizations"),
        "exports": os.path.join(base_dir, "exports"),
        "logs": os.path.join(base_dir, "logs")
    }

    for dir_name, dir_path in directories.items():
        os.makedirs(dir_path, exist_ok=True)

    return directories


def save_visualizations(visualizations: Dict[str, Any], output_dir: str):
    """Save Plotly visualizations to files."""
    saved_files = []

    for viz_name, viz_data in visualizations.items():
        if isinstance(viz_data, dict):
            # Multiple plots (e.g., numerical_distributions)
            for plot_name, fig in viz_data.items():
                if hasattr(fig, 'to_dict'):  # Check if it's a Plotly figure
                    filename = f"{viz_name}_{plot_name}.html"
                    filepath = os.path.join(output_dir, filename)

                    # Save as interactive HTML
                    pio.write_html(fig, filepath, auto_open=False)

                    # Also save as static image
                    img_path = os.path.join(output_dir, f"{viz_name}_{plot_name}.png")
                    try:
                        fig.write_image(img_path, width=1200, height=800)
                        saved_files.append(img_path)
                    except:
                        pass  # Skip if export fails

                    saved_files.append(filepath)
        elif hasattr(viz_data, 'to_dict'):  # Single plot
            filename = f"{viz_name}.html"
            filepath = os.path.join(output_dir, filename)
            pio.write_html(viz_data, filepath, auto_open=False)

            # Save as static image
            img_path = os.path.join(output_dir, f"{viz_name}.png")
            try:
                viz_data.write_image(img_path, width=1200, height=800)
                saved_files.append(img_path)
            except:
                pass

            saved_files.append(filepath)

    return saved_files


def save_report_to_json(report: Dict[str, Any], output_dir: str, filename: str):
    """Save report as JSON with proper serialization."""

    def recursive_serialize(obj):
        """Recursively serialize objects to JSON-serializable format."""
        # Handle None
        if obj is None:
            return None

        # Handle numpy types
        if isinstance(obj, np.generic):
            return obj.item()  # Convert numpy scalars to Python types

        # Handle numpy arrays
        if isinstance(obj, np.ndarray):
            return obj.tolist()

        # Handle pandas Timestamp
        if isinstance(obj, pd.Timestamp):
            return obj.isoformat()

        # Handle datetime
        if isinstance(obj, datetime):
            return obj.isoformat()

        # Handle pandas Series
        if isinstance(obj, pd.Series):
            return obj.tolist()

        # Handle pandas DataFrame
        if isinstance(obj, pd.DataFrame):
            return obj.to_dict(orient='records')

        # Handle dictionaries
        if isinstance(obj, dict):
            return {key: recursive_serialize(value) for key, value in obj.items()}

        # Handle lists/tuples
        if isinstance(obj, (list, tuple)):
            return [recursive_serialize(item) for item in obj]

        # Handle sets
        if isinstance(obj, set):
            return [recursive_serialize(item) for item in obj]

        # Handle other pandas NA values
        if pd.isna(obj):
            return None

        # Try to convert to string if nothing else works
        try:
            # For any object with a to_dict method
            if hasattr(obj, 'to_dict'):
                return recursive_serialize(obj.to_dict())
            # For any object that can be converted to string
            return str(obj)
        except:
            return str(obj)

    try:
        serialized_report = recursive_serialize(report)

        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(serialized_report, f, indent=2, ensure_ascii=False)

        return filepath
    except Exception as e:
        print(f"❌ Failed to save JSON report: {str(e)}")
        return None


def print_test_header(test_name: str):
    """Print formatted test header."""
    print("\n" + "═" * 70)
    print(f"🧪 {test_name}")
    print("═" * 70)


def print_test_section(section_name: str):
    """Print formatted test section."""
    print(f"\n📌 {section_name}")
    print("─" * 40)


def print_test_result(test_name: str, status: str, details: str = ""):
    """Print formatted test result."""
    if status.lower() == "pass":
        icon = "✅"
        color = "\033[92m"  # Green
    elif status.lower() == "warning":
        icon = "⚠️ "
        color = "\033[93m"  # Yellow
    else:
        icon = "❌"
        color = "\033[91m"  # Red

    reset = "\033[0m"
    print(f"{color}{icon} {test_name}: {status.upper()}{reset}")
    if details:
        print(f"   Details: {details}")


def pretty_print_ingestion_report(report):
    """Nicely formatted terminal report for ingestion."""
    print_test_header("INGESTION REPORT")

    info = report.get("info", {})

    # ----------------- ERROR HANDLING -----------------
    if report["status"] == "error":
        print_test_result("Ingestion", "FAILED", report.get('errors', 'Unknown error'))
        print(f"📁 Source: {report.get('source')}")
        print(f"📂 Type: {report.get('file_type')}")
        return

    # ----------------- SUMMARY -----------------
    print_test_section("SUMMARY")
    print(f"📊 Rows: {info.get('rows', 'N/A'):,}")
    print(f"🔢 Columns: {info.get('columns', 'N/A')}")
    print(f"💾 Memory: {info.get('memory_usage_mb', 'N/A')} MB")
    print(f"📦 File Size: {info.get('file_size_mb', 'N/A')} MB")

    # ----------------- COLUMN TYPES -----------------
    column_types = info.get("column_types", {})
    if column_types:
        print_test_section("COLUMN TYPE DISTRIBUTION")
        type_counts = {}
        for dtype in column_types.values():
            dtype_str = str(dtype)
            type_counts[dtype_str] = type_counts.get(dtype_str, 0) + 1

        for dtype, count in sorted(type_counts.items()):
            print(f"  {dtype:<25} {count:>3} columns")

    # ----------------- DATA QUALITY CHECKS -----------------
    print_test_section("DATA QUALITY CHECKS")

    # Check for empty DataFrame
    if info.get('rows', 0) == 0:
        print_test_result("Empty Dataset", "FAILED", "Dataset contains 0 rows")
    else:
        print_test_result("Dataset Loaded", "PASS", f"{info.get('rows'):,} rows loaded")

    # Check for empty columns
    all_columns = info.get('column_names', [])
    if all_columns and len(all_columns) > 0:
        print_test_result("Column Names", "PASS", f"{len(all_columns)} columns found")
    else:
        print_test_result("Column Names", "WARNING", "No columns found")

    # Check memory usage
    mem_usage = info.get('memory_usage_mb', 0)
    if mem_usage > 1000:
        print_test_result("Memory Usage", "WARNING", f"{mem_usage} MB is large")
    elif mem_usage > 0:
        print_test_result("Memory Usage", "PASS", f"{mem_usage} MB")

    print("\n" + "═" * 70)


def pretty_print_profiling_report(profile: Dict[str, Any], show_details: bool = True):
    """Nicely formatted terminal report for profiling with test-style output."""
    print_test_header("PROFILING REPORT")

    basic = profile.get("basic", {})
    summary = profile.get("summary", {})
    missing_info = basic.get("missing_values", {})
    duplicates = basic.get("duplicates", {})

    # ----------------- OVERVIEW -----------------
    print_test_section("DATASET OVERVIEW")
    print(f"📊 Total Rows: {summary.get('total_rows', 'N/A'):,}")
    print(f"🔢 Total Columns: {summary.get('total_columns', 'N/A')}")
    print(f"📈 Numerical: {summary.get('numerical_columns', 'N/A')}")
    print(f"🏷️  Categorical: {summary.get('categorical_columns', 'N/A')}")
    print(f"📅 DateTime: {summary.get('datetime_columns', 'N/A')}")

    # ----------------- DATA QUALITY TESTS -----------------
    print_test_section("DATA QUALITY TESTS")

    # Missing values test
    missing_pct = missing_info.get('total_missing_percent', 0)
    if missing_pct > 50:
        print_test_result("Missing Values", "FAILED", f"{missing_pct:.1f}% missing - Critical")
    elif missing_pct > 20:
        print_test_result("Missing Values", "WARNING", f"{missing_pct:.1f}% missing - High")
    elif missing_pct > 5:
        print_test_result("Missing Values", "WARNING", f"{missing_pct:.1f}% missing - Moderate")
    else:
        print_test_result("Missing Values", "PASS", f"{missing_pct:.1f}% missing - Acceptable")

    # Duplicates test
    duplicate_pct = duplicates.get('duplicate_percent', 0)
    if duplicate_pct > 30:
        print_test_result("Duplicate Rows", "FAILED", f"{duplicate_pct:.1f}% duplicates")
    elif duplicate_pct > 10:
        print_test_result("Duplicate Rows", "WARNING", f"{duplicate_pct:.1f}% duplicates")
    else:
        print_test_result("Duplicate Rows", "PASS", f"{duplicate_pct:.1f}% duplicates")

    # Empty columns test
    empty_cols = basic.get("empty_columns", [])
    if empty_cols:
        print_test_result("Empty Columns", "FAILED", f"{len(empty_cols)} completely empty")
    else:
        print_test_result("Empty Columns", "PASS", "No empty columns")

    # Mixed types test
    mixed = profile.get("mixed_types", {})
    if mixed:
        print_test_result("Mixed Data Types", "FAILED", f"{len(mixed)} columns with mixed types")
    else:
        print_test_result("Mixed Data Types", "PASS", "No mixed types found")

    # ----------------- NUMERICAL ANALYSIS -----------------
    numerical = profile.get("numerical", {})
    if numerical and show_details:
        print_test_section("NUMERICAL COLUMNS ANALYSIS")

        for col, stats in list(numerical.items())[:5]:  # Show top 5
            print(f"\n📐 {col}:")

            # Basic stats
            print(f"  Mean: {stats.get('mean', 'N/A'):.2f} | "
                  f"Std: {stats.get('std', 'N/A'):.2f} | "
                  f"Range: {stats.get('range', 'N/A'):.2f}")

            # Outlier test
            outliers_pct = stats.get('outliers', {}).get('iqr_percent', 0)
            if outliers_pct > 10:
                print(f"  ⚠️  Outliers: {outliers_pct:.1f}% (High)")
            elif outliers_pct > 5:
                print(f"  ⚠️  Outliers: {outliers_pct:.1f}% (Moderate)")
            else:
                print(f"  ✓ Outliers: {outliers_pct:.1f}% (Low)")

            # Normality test
            is_normal = stats.get('is_normal')
            if is_normal is not None:
                if is_normal:
                    print(f"  ✓ Normally distributed (p={stats.get('normality_pvalue', 'N/A'):.4f})")
                else:
                    print(f"  ⚠️  Not normally distributed (p={stats.get('normality_pvalue', 'N/A'):.4f})")

            # Quality flags
            flags = stats.get('quality_flags', {})
            issues = []
            for flag_name, flag_value in flags.items():
                if flag_value:
                    issues.append(flag_name.replace('_', ' '))
            if issues:
                print(f"  ❗ Issues: {', '.join(issues)}")

        if len(numerical) > 5:
            print(f"\n📋 ... and {len(numerical) - 5} more numerical columns")

    # ----------------- CATEGORICAL ANALYSIS -----------------
    categorical = profile.get("categorical", {})
    if categorical and show_details:
        print_test_section("CATEGORICAL COLUMNS ANALYSIS")

        for col, stats in list(categorical.items())[:3]:  # Show top 3
            print(f"\n🏷️  {col}:")
            print(f"  Unique values: {stats.get('unique_count', 'N/A')}")

            # Distribution info
            distribution = stats.get('distribution', {})
            dominant_pct = distribution.get('dominant_percent', 0)
            if dominant_pct > 80:
                print(f"  ⚠️  High dominance: {dominant_pct:.1f}% in top category")
            elif dominant_pct > 50:
                print(f"  ⚠️  Moderate dominance: {dominant_pct:.1f}% in top category")

            # Rare values
            rare_pct = stats.get('rare_values', {}).get('rare_percent', 0)
            if rare_pct > 30:
                print(f"  ⚠️  Many rare values: {rare_pct:.1f}%")

            # Quality flags
            flags = stats.get('quality_flags', {})
            issues = []
            for flag_name, flag_value in flags.items():
                if flag_value:
                    issues.append(flag_name.replace('_', ' '))
            if issues:
                print(f"  ❗ Issues: {', '.join(issues)}")

    # ----------------- CORRELATION ANALYSIS -----------------
    correlations = profile.get("correlations", {})
    if correlations:
        print_test_section("CORRELATION ANALYSIS")

        high_corr = correlations.get("high_correlations", [])
        if high_corr:
            print(f"🔗 High Correlations Found: {len(high_corr)} pairs")
            for pair in high_corr[:3]:
                print(f"  • {pair.get('feature1', '?')} ↔ {pair.get('feature2', '?')}: "
                      f"{pair.get('correlation', 0):.3f}")
            print_test_result("High Correlations", "WARNING",
                              f"{len(high_corr)} highly correlated feature pairs found")
        else:
            print_test_result("High Correlations", "PASS", "No high correlations found")

    # ----------------- RECOMMENDATIONS -----------------
    print_test_section("RECOMMENDATIONS")

    recommendations = []

    # Missing data recommendations
    if missing_pct > 5:
        recommendations.append("Consider imputation for missing values")

    # Duplicate recommendations
    if duplicate_pct > 10:
        recommendations.append("Remove duplicate rows")

    # Outlier recommendations
    if numerical:
        high_outlier_cols = []
        for col, stats in numerical.items():
            if stats.get('outliers', {}).get('iqr_percent', 0) > 10:
                high_outlier_cols.append(col)
        if high_outlier_cols:
            recommendations.append(f"Investigate outliers in: {', '.join(high_outlier_cols[:3])}")

    # Correlation recommendations
    if high_corr:
        recommendations.append("Consider removing one of each highly correlated pair")

    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
    else:
        print("✓ Data quality is good. No immediate actions needed.")

    print("\n" + "═" * 70)


def clean_data(
        source: Optional[str] = None,
        file_type: str = 'csv',
        profile_data: bool = True,
        include_visuals: bool = False,
        columns_to_plot: Optional[list] = None,
        sql_query: Optional[str] = None,
        sql_conn_str: Optional[str] = None,
        save_output: bool = True,
        output_dir: str = "data_pipeline_output",
        show_detailed_profile: bool = True,
        **kwargs
) -> Tuple[Optional[pd.DataFrame], Dict[str, Any], Dict[str, Any]]:
    """
    Main pipeline to clean and profile data with enhanced reporting.

    Returns:
    --------
    tuple : (DataFrame, reports_dict, output_files_dict)
    """

    # Initialize output tracking
    output_files = {
        "reports": [],
        "visualizations": [],
        "exports": []
    }

    # Ensure output directories
    if save_output:
        directories = ensure_output_directory(output_dir)

    # Generate timestamp for file naming
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = "unknown"
    if source:
        base_name = os.path.splitext(os.path.basename(source))[0]
    elif sql_query:
        base_name = "sql_query"

    reports = {}

    # ---------------------------- 1️⃣ INGEST ----------------------------
    print("🔄 Starting Data Ingestion...")
    df, ingestion_report = ingestion.load_data(
        source=source,
        file_type=file_type,
        sql_query=sql_query,
        sql_conn_str=sql_conn_str,
        **kwargs
    )

    reports["ingestion"] = ingestion_report

    # Pretty terminal output for ingestion
    pretty_print_ingestion_report(ingestion_report)

    if df is None:
        print("❌ Ingestion failed. Stopping pipeline.")
        return None, reports, output_files

    print("✅ Ingestion completed successfully!")

    # Save ingestion report
    if save_output:
        ingestion_file = save_report_to_json(
            ingestion_report,
            directories["reports"],
            f"{base_name}_ingestion_{timestamp}.json"
        )
        if ingestion_file:
            output_files["reports"].append(ingestion_file)
            print(f"📄 Ingestion report saved: {ingestion_file}")

    # ---------------------------- 2️⃣ PROFILING ----------------------------
    if profile_data:
        print("\n🔄 Starting Data Profiling...")

        # Generate comprehensive profile
        profile = profiling.generate_comprehensive_profile(
            df=df,
            include_visuals=include_visuals,
            columns_to_plot=columns_to_plot
        )

        reports["profiling"] = profile

        # Pretty terminal output for profiling
        pretty_print_profiling_report(profile, show_detailed_profile)

        # Save profiling report
        if save_output:
            profiling_file = save_report_to_json(
                profile,
                directories["reports"],
                f"{base_name}_profiling_{timestamp}.json"
            )
            if profiling_file:
                output_files["reports"].append(profiling_file)
                print(f"📄 Profiling report saved: {profiling_file}")

        # Save visualizations if generated
        if include_visuals and profile.get("visualizations"):
            viz = profile["visualizations"]
            print("\n🎨 Generating visualizations...")

            saved_viz = save_visualizations(viz, directories["visualizations"])
            output_files["visualizations"].extend(saved_viz)

            print(f"📈 Visualizations saved: {len(saved_viz)} files")
            for viz_file in saved_viz[:5]:  # Show first 5
                print(f"  • {os.path.basename(viz_file)}")
            if len(saved_viz) > 5:
                print(f"    ... and {len(saved_viz) - 5} more")

        print("✅ Profiling completed successfully!")

    # ---------------------------- 3️⃣ EXPORT DATA ----------------------------
    if save_output and df is not None:
        print("\n💾 Exporting processed data...")

        # Export as CSV
        csv_file = os.path.join(directories["exports"], f"{base_name}_processed_{timestamp}.csv")
        try:
            df.to_csv(csv_file, index=False)
            output_files["exports"].append(csv_file)
            print(f"📊 Data exported to CSV: {csv_file}")
        except Exception as e:
            print(f"❌ Failed to export CSV: {str(e)}")

        # Export as Parquet (if pandas supports it)
        try:
            parquet_file = os.path.join(directories["exports"], f"{base_name}_processed_{timestamp}.parquet")
            df.to_parquet(parquet_file, index=False)
            output_files["exports"].append(parquet_file)
            print(f"📊 Data exported to Parquet: {parquet_file}")
        except Exception as e:
            # Silently fail for parquet if not supported
            pass

    # ---------------------------- 4️⃣ SUMMARY ----------------------------
    print(f"\n{'=' * 70}")
    print("✨ PIPELINE COMPLETED SUCCESSFULLY!")
    print("=" * 70)

    # Summary statistics
    total_missing = 0
    duplicate_pct = 0
    if reports.get("profiling"):
        total_missing = reports.get("profiling", {}).get("basic", {}).get("missing_values", {}).get("total_missing", 0)
        duplicate_pct = reports.get("profiling", {}).get("basic", {}).get("duplicates", {}).get("duplicate_percent", 0)

    print(f"\n📋 FINAL SUMMARY:")
    print(f"  • Dataset: {df.shape[0]:,} rows × {df.shape[1]} columns")
    if df.shape[0] * df.shape[1] > 0:
        print(f"  • Missing Values: {total_missing:,} ({total_missing / (df.shape[0] * df.shape[1]) * 100:.1f}%)")
    print(f"  • Duplicate Rows: {duplicate_pct:.1f}%")
    print(f"  • Reports Generated: {len(output_files.get('reports', []))}")
    print(f"  • Visualizations Saved: {len(output_files.get('visualizations', []))}")
    print(f"  • Exports Created: {len(output_files.get('exports', []))}")

    if save_output:
        print(f"\n📁 Output Directory: {output_dir}/")
        for dir_type, files in output_files.items():
            if files:
                print(f"  📂 {dir_type.capitalize()}: {len(files)} files")

    return df, reports, output_files


def profile_existing_dataframe(
        df: pd.DataFrame,
        include_visuals: bool = False,
        columns_to_plot: Optional[list] = None,
        save_output: bool = True,
        output_dir: str = "data_pipeline_output"
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Profile an existing DataFrame with enhanced reporting and saving.
    """

    output_files = {"reports": [], "visualizations": []}

    if save_output:
        directories = ensure_output_directory(output_dir)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    print("\n" + "=" * 70)
    print("🔍 PROFILING EXISTING DATAFRAME")
    print("=" * 70)

    # Generate comprehensive profile
    profile = profiling.generate_comprehensive_profile(
        df=df,
        include_visuals=include_visuals,
        columns_to_plot=columns_to_plot
    )

    # Pretty terminal output
    pretty_print_profiling_report(profile, show_detailed_profile=True)

    # Save profiling report
    if save_output:
        profiling_file = save_report_to_json(
            profile,
            directories["reports"],
            f"dataframe_profiling_{timestamp}.json"
        )
        if profiling_file:
            output_files["reports"].append(profiling_file)
            print(f"\n📄 Profiling report saved: {profiling_file}")

    # Save visualizations if generated
    if include_visuals and profile.get("visualizations"):
        viz = profile["visualizations"]
        saved_viz = save_visualizations(viz, directories["visualizations"])
        output_files["visualizations"].extend(saved_viz)

        print(f"📈 Visualizations saved: {len(saved_viz)} files")

    return profile, output_files


# Convenience functions
def quick_profile(
        source: str,
        file_type: str = 'csv',
        save_output: bool = True,
        **kwargs
) -> Tuple[Optional[pd.DataFrame], Dict[str, Any], Dict[str, Any]]:
    """Quick ingestion and profiling without visualizations."""
    return clean_data(
        source=source,
        file_type=file_type,
        profile_data=True,
        include_visuals=False,
        save_output=save_output,
        **kwargs
    )


def full_analysis(
        source: str,
        file_type: str = 'csv',
        columns_to_plot: Optional[list] = None,
        save_output: bool = True,
        **kwargs
) -> Tuple[Optional[pd.DataFrame], Dict[str, Any], Dict[str, Any]]:
    """Full analysis with ingestion, profiling, and visualizations."""
    return clean_data(
        source=source,
        file_type=file_type,
        profile_data=True,
        include_visuals=True,
        columns_to_plot=columns_to_plot,
        save_output=save_output,
        **kwargs
    )


def ingest_only(
        source: str,
        file_type: str = 'csv',
        save_output: bool = True,
        **kwargs
) -> Tuple[Optional[pd.DataFrame], Dict[str, Any], Dict[str, Any]]:
    """Only ingest data without profiling."""
    return clean_data(
        source=source,
        file_type=file_type,
        profile_data=False,
        include_visuals=False,
        save_output=save_output,
        **kwargs
    )


# Main execution
if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("📊 DATA CLEANING & PROFILING PIPELINE")
    print("=" * 70)

    print("\n✨ Available Functions:")
    print("─" * 40)
    print("1. clean_data()          - Full pipeline with all options")
    print("2. quick_profile()       - Fast ingestion + profiling")
    print("3. full_analysis()       - Complete analysis with visuals")
    print("4. ingest_only()         - Only load data")
    print("5. profile_existing_dataframe() - Profile any DataFrame")

    print("\n📁 Output Features:")
    print("─" * 40)
    print("• Auto-saves reports as JSON")
    print("• Saves visualizations as HTML & PNG")
    print("• Exports processed data")
    print("• Organized folder structure")

    print("\n🎯 Example Usage:")
    print("─" * 40)
    print('df, reports, files = quick_profile("data/sample.csv")')
    print('# Or with full analysis:')
    print('df, reports, files = full_analysis("data/sample.csv", columns_to_plot=["age", "income"])')

    print("\n" + "=" * 70)