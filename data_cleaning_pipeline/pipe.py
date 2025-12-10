from data_cleaning_pipeline.utils import ingestion
from data_cleaning_pipeline.cleaning import profiling
from data_cleaning_pipeline.cleaning.missing import DataCleaner
from data_cleaning_pipeline.cleaning.outlier_handler import OutlierHandler, OutlierConfig
from data_cleaning_pipeline.cleaning.feature_engineering import FeatureEngineeringAdvisor, suggest_features
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
    
    # Outliers test (from numerical analysis)
    numerical = profile.get("numerical", {})
    if numerical:
        total_outlier_pct = 0
        high_outlier_cols = []
        for col, stats in numerical.items():
            outlier_pct = stats.get('outliers', {}).get('iqr_percent', 0)
            total_outlier_pct += outlier_pct
            if outlier_pct > 10:
                high_outlier_cols.append(f"{col} ({outlier_pct:.1f}%)")
        
        avg_outlier_pct = total_outlier_pct / len(numerical) if len(numerical) > 0 else 0
        if avg_outlier_pct > 10:
            outlier_msg = f"{avg_outlier_pct:.1f}% avg outliers"
            if high_outlier_cols:
                outlier_msg += f" - High in: {', '.join(high_outlier_cols[:2])}"
            print_test_result("Outliers", "WARNING", outlier_msg)
        elif avg_outlier_pct > 5:
            print_test_result("Outliers", "WARNING", f"{avg_outlier_pct:.1f}% average outliers detected")
        else:
            print_test_result("Outliers", "PASS", f"{avg_outlier_pct:.1f}% average outliers (acceptable)")

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
        apply_cleaning: bool = True,
        cleaning_steps: Optional[list] = None,
        cleaning_kwargs: Optional[Dict[str, Any]] = None,
        use_advanced_outlier_handler: bool = False,
        outlier_config: Optional[Dict[str, Any]] = None,
        enable_feature_suggestions: bool = False,
        target_column: Optional[str] = None,
        **kwargs
) -> Tuple[Optional[pd.DataFrame], Dict[str, Any], Dict[str, Any]]:
    """
    Main pipeline to clean and profile data with enhanced reporting.

    Parameters:
    -----------
    source : str, optional
        Path to data file or URL
    file_type : str
        Type of file ('csv', 'excel', etc.)
    profile_data : bool
        Whether to generate data profiling reports
    include_visuals : bool
        Whether to generate visualizations
    columns_to_plot : list, optional
        Specific columns to plot
    sql_query : str, optional
        SQL query for database ingestion
    sql_conn_str : str, optional
        Database connection string
    save_output : bool
        Whether to save reports and exports
    output_dir : str
        Directory for output files
    show_detailed_profile : bool
        Whether to show detailed profiling information
    apply_cleaning : bool
        Whether to apply data cleaning using DataCleaner
    cleaning_steps : list, optional
        List of cleaning steps to perform: ['missing', 'duplicates', 'outliers', 'inconsistent', 'normalize']
        Default: ['missing', 'duplicates', 'outliers', 'inconsistent']
    cleaning_kwargs : dict, optional
        Parameters for cleaning steps. Structure:
        {
            'missing_kwargs': {'strategy': 'impute', 'numeric_method': 'auto', ...},
            'duplicate_kwargs': {'method': 'remove', ...},
            'outlier_kwargs': {'method': 'iqr', 'handle_action': 'detect_only', ...},
            'inconsistent_kwargs': {},
            'normalize_kwargs': {'method': 'none', ...}
        }
    use_advanced_outlier_handler : bool
        Whether to use the advanced OutlierHandler class instead of DataCleaner's basic outlier handling
        Default: False
    outlier_config : dict, optional
        Configuration for OutlierHandler. Structure:
        {
            'method': 'iqr',  # 'iqr', 'zscore', 'mcd'
            'action': 'flag',  # 'remove', 'cap', 'flag', 'winsorize'
            'threshold': 3.0,
            'iqr_factor': 1.5,
            'mcd_threshold': 0.975,
            'hypothesis_test': False,
            'significance_level': 0.05,
            'multivariate_methods': False,
            'contamination': 0.1
        }
    **kwargs : additional arguments for ingestion

    Returns:
    --------
    tuple : (DataFrame, reports_dict, output_files_dict)
        - DataFrame: Cleaned and processed DataFrame
        - reports_dict: Dictionary containing ingestion, cleaning, and profiling reports
        - output_files_dict: Dictionary of saved file paths
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

    # ---------------------------- 2️⃣ DATA CLEANING ----------------------------
    if apply_cleaning:
        print("\n🔄 Starting Data Cleaning...")
        
        # Initialize DataCleaner
        cleaner = DataCleaner(verbose=True)
        
        # Set default cleaning steps if not provided
        if cleaning_steps is None:
            cleaning_steps = ['missing', 'duplicates', 'outliers', 'inconsistent']
        
        # Prepare cleaning kwargs with defaults
        if cleaning_kwargs is None:
            cleaning_kwargs = {}
        
        # Set default parameters for each cleaning step
        default_kwargs = {
            'missing_kwargs': {
                'strategy': 'impute',
                'numeric_method': 'auto',
                'categorical_method': 'mode',
                'skew_threshold': 1.0
            },
            'duplicate_kwargs': {
                'method': 'remove',
                'subset': None
            },
            'outlier_kwargs': {
                'method': 'iqr',
                'handle_action': 'detect_only'
            },
            'inconsistent_kwargs': {},
            'normalize_kwargs': {
                'method': 'none'
            }
        }
        
        # Merge user-provided kwargs with defaults
        for key, default_value in default_kwargs.items():
            if key not in cleaning_kwargs:
                cleaning_kwargs[key] = default_value
            else:
                # Merge nested dicts
                if isinstance(default_value, dict) and isinstance(cleaning_kwargs[key], dict):
                    cleaning_kwargs[key] = {**default_value, **cleaning_kwargs[key]}
        
        # If using advanced outlier handler, remove 'outliers' from steps to avoid double processing
        steps_for_cleaner = cleaning_steps.copy() if cleaning_steps else ['missing', 'duplicates', 'outliers', 'inconsistent']
        if use_advanced_outlier_handler and 'outliers' in steps_for_cleaner:
            steps_for_cleaner.remove('outliers')
            print("📌 Using advanced OutlierHandler - skipping basic outlier handling in DataCleaner")
        
        # Execute cleaning steps
        cleaned_df, cleaning_report = cleaner.clean_all(
            df=df,
            steps=steps_for_cleaner,
            **cleaning_kwargs
        )
        
        reports["cleaning"] = cleaning_report
        
        # Update df to cleaned version
        df = cleaned_df
        
        # Apply advanced outlier handling if requested
        if use_advanced_outlier_handler:
            print("\n🔄 Applying Advanced Outlier Handler...")
            
            # Prepare outlier configuration
            if outlier_config is None:
                outlier_config = {
                    'method': 'iqr',
                    'action': 'flag',
                    'threshold': 3.0,
                    'iqr_factor': 1.5,
                    'mcd_threshold': 0.975,
                    'hypothesis_test': False,
                    'significance_level': 0.05,
                    'multivariate_methods': False,
                    'contamination': 0.1
                }
            
            # Create OutlierConfig
            config = OutlierConfig(**outlier_config)
            
            # Initialize and use OutlierHandler
            outlier_handler = OutlierHandler(config=config)
            
            # Detect outliers first
            detection_report = outlier_handler.detect_outliers(df)
            
            # Handle outliers
            cleaned_df, outlier_report = outlier_handler.handle_outliers(df)
            
            # Combine reports
            advanced_outlier_report = {
                'operation': 'advanced_outlier_handling',
                'detection': detection_report,
                'handling': outlier_report.get('handling', {}),
                'config': outlier_config
            }
            
            reports["advanced_outlier_handling"] = advanced_outlier_report
            df = cleaned_df
            
            # Save advanced outlier report
            if save_output:
                outlier_file = save_report_to_json(
                    advanced_outlier_report,
                    directories["reports"],
                    f"{base_name}_advanced_outliers_{timestamp}.json"
                )
                if outlier_file:
                    output_files["reports"].append(outlier_file)
                    print(f"📄 Advanced outlier report saved: {outlier_file}")
            
            print("✅ Advanced outlier handling completed!")
        
        # Save cleaning report
        if save_output:
            cleaning_file = save_report_to_json(
                cleaning_report,
                directories["reports"],
                f"{base_name}_cleaning_{timestamp}.json"
            )
            if cleaning_file:
                output_files["reports"].append(cleaning_file)
                print(f"📄 Cleaning report saved: {cleaning_file}")
        
        print("✅ Data cleaning completed successfully!")

    # ---------------------------- 3️⃣ PROFILING ----------------------------
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

    # ---------------------------- 4️⃣ FEATURE ENGINEERING SUGGESTIONS ----------------------------
    if enable_feature_suggestions:
        print("\n" + "=" * 70)
        print("🤖 GENERATING AI-BASED FEATURE ENGINEERING SUGGESTIONS")
        print("=" * 70)
        
        try:
            # Import the function to avoid any naming conflicts
            from data_cleaning_pipeline.cleaning.feature_engineering import suggest_features as get_feature_suggestions
            
            # Generate feature engineering suggestions
            feature_suggestions = get_feature_suggestions(
                df=df,
                target_column=target_column,
                verbose=True
            )
            
            reports["feature_engineering"] = feature_suggestions
            
            # Save feature engineering report
            if save_output:
                fe_file = save_report_to_json(
                    feature_suggestions,
                    directories["reports"],
                    f"{base_name}_feature_engineering_{timestamp}.json"
                )
                if fe_file:
                    output_files["reports"].append(fe_file)
                    print(f"\n📄 Feature engineering suggestions saved: {fe_file}")
            
            print("\n✅ Feature engineering suggestions completed successfully!")
            print("=" * 70)
            
        except Exception as e:
            import traceback
            print(f"\n⚠️  Could not generate feature engineering suggestions: {str(e)}")
            print(f"Error details: {traceback.format_exc()}")
            reports["feature_engineering"] = {"error": str(e), "traceback": traceback.format_exc()}

    # ---------------------------- 5️⃣ EXPORT DATA ----------------------------
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

    # ---------------------------- 6️⃣ SUMMARY ----------------------------
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
    
    # Add outlier summary from profiling
    if reports.get("profiling"):
        numerical = reports["profiling"].get("numerical", {})
        if numerical:
            total_outliers = 0
            outlier_cols = []
            for col, stats in numerical.items():
                outlier_count = stats.get('outliers', {}).get('iqr_method', 0)
                outlier_pct = stats.get('outliers', {}).get('iqr_percent', 0)
                total_outliers += outlier_count
                if outlier_pct > 5:
                    outlier_cols.append(f"{col} ({outlier_pct:.1f}%)")
            
            if total_outliers > 0:
                print(f"  • Outliers Detected: {total_outliers:,} total")
                if outlier_cols:
                    print(f"    Columns with >5% outliers: {', '.join(outlier_cols[:3])}")
                    if len(outlier_cols) > 3:
                        print(f"    ... and {len(outlier_cols) - 3} more columns")
            else:
                print(f"  • Outliers: None detected")
    
    # Add cleaning summary if cleaning was performed
    if apply_cleaning and reports.get("cleaning"):
        cleaning_report = reports["cleaning"]
        if "overall_improvement" in cleaning_report:
            improvement = cleaning_report["overall_improvement"]
            print(f"  • Data Quality Score: {improvement.get('data_quality_score', 'N/A')}")
            rows_reduction = improvement.get('rows_reduction_percentage', 0)
            if rows_reduction > 0:
                print(f"  • Rows Reduced: {rows_reduction:.1f}%")
    
    # Add advanced outlier handling summary if used
    if use_advanced_outlier_handler and reports.get("advanced_outlier_handling"):
        outlier_report = reports["advanced_outlier_handling"]
        handling = outlier_report.get("handling", {})
        n_outliers = handling.get("n_outliers_detected", 0)
        action = handling.get("action", "unknown")
        print(f"  • Advanced Outlier Handling: {n_outliers} outliers detected (action: {action})")
    
    # Add feature engineering suggestions summary if generated
    if enable_feature_suggestions and reports.get("feature_engineering"):
        fe_report = reports["feature_engineering"]
        if "error" not in fe_report:
            summary = fe_report.get("summary", {})
            total_suggestions = summary.get("total_suggestions", 0)
            if total_suggestions > 0:
                print(f"  • Feature Engineering Suggestions: {total_suggestions} total suggestions generated")
                quick_wins = summary.get("quick_wins", [])
                if quick_wins:
                    print(f"    Quick wins: {len(quick_wins)} easy-to-implement features")
                priority = summary.get("priority_features", [])
                if priority:
                    print(f"    Priority features: {len(priority)} high-impact suggestions")
    
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
        apply_cleaning: bool = True,
        **kwargs
) -> Tuple[Optional[pd.DataFrame], Dict[str, Any], Dict[str, Any]]:
    """Quick ingestion, cleaning, and profiling without visualizations."""
    return clean_data(
        source=source,
        file_type=file_type,
        profile_data=True,
        include_visuals=False,
        save_output=save_output,
        apply_cleaning=apply_cleaning,
        **kwargs
    )


def full_analysis(
        source: str,
        file_type: str = 'csv',
        columns_to_plot: Optional[list] = None,
        save_output: bool = True,
        apply_cleaning: bool = True,
        **kwargs
) -> Tuple[Optional[pd.DataFrame], Dict[str, Any], Dict[str, Any]]:
    """Full analysis with ingestion, cleaning, profiling, and visualizations."""
    return clean_data(
        source=source,
        file_type=file_type,
        profile_data=True,
        include_visuals=True,
        columns_to_plot=columns_to_plot,
        save_output=save_output,
        apply_cleaning=apply_cleaning,
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
    print("1. clean_data()          - Full pipeline: ingestion + cleaning + profiling")
    print("2. quick_profile()       - Fast ingestion + cleaning + profiling")
    print("3. full_analysis()       - Complete analysis with visuals")
    print("4. ingest_only()         - Only load data")
    print("5. profile_existing_dataframe() - Profile any DataFrame")

    print("\n📁 Output Features:")
    print("─" * 40)
    print("• Auto-saves reports as JSON")
    print("• Saves visualizations as HTML & PNG")
    print("• Exports processed data")
    print("• Organized folder structure")
    print("• Data cleaning with DataCleaner class")
    print("  - Missing value handling (impute/drop/advanced)")
    print("  - Duplicate detection and removal")
    print("  - Outlier detection and handling")
    print("  - Inconsistent data formatting")
    print("  - Optional normalization")

    print("\n🎯 Example Usage:")
    print("─" * 40)
    print('df, reports, files = quick_profile("data/sample.csv")')
    print('# Or with full analysis:')
    print('df, reports, files = full_analysis("data/sample.csv", columns_to_plot=["age", "income"])')
    print('# Custom cleaning:')
    print('df, reports, files = clean_data(')
    print('    "data/sample.csv",')
    print('    cleaning_steps=["missing", "duplicates"],')
    print('    cleaning_kwargs={"missing_kwargs": {"strategy": "impute", "numeric_method": "median"}}')
    print(')')

    print("\n" + "=" * 70)