"""
Output Generation Module
Handles exporting data in various formats and generating comprehensive reports
"""

import pandas as pd
import numpy as np
import json
import os
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')


class OutputGenerator:
    """
    Comprehensive output generation class for data exports and reports
    """
    
    def __init__(self, output_dir: str = "data_pipeline_output", verbose: bool = True):
        self.output_dir = output_dir
        self.verbose = verbose
        self.ensure_directories()
        
    def _log(self, message: str):
        """Helper method for logging"""
        if self.verbose:
            print(f"  ✓ {message}")
    
    def ensure_directories(self):
        """Ensure output directories exist"""
        directories = {
            "exports": os.path.join(self.output_dir, "exports"),
            "reports": os.path.join(self.output_dir, "reports"),
            "logs": os.path.join(self.output_dir, "logs"),
            "archives": os.path.join(self.output_dir, "archives")
        }
        
        for dir_path in directories.values():
            os.makedirs(dir_path, exist_ok=True)
        
        return directories
    
    def export_dataframe(self, df: pd.DataFrame, 
                        filename: str,
                        formats: List[str] = ['csv', 'excel', 'json', 'parquet'],
                        include_index: bool = False) -> Dict[str, str]:
        """
        Export DataFrame to multiple formats
        
        Parameters:
        -----------
        df : pd.DataFrame
            DataFrame to export
        filename : str
            Base filename (without extension)
        formats : list
            List of formats to export: ['csv', 'excel', 'json', 'parquet', 'html']
        include_index : bool
            Whether to include index in export
            
        Returns:
        --------
        exported_files : dict
            Dictionary mapping format to file path
        """
        exported_files = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        exports_dir = os.path.join(self.output_dir, "exports")
        
        base_filename = f"{filename}_processed_{timestamp}"
        
        for fmt in formats:
            try:
                if fmt.lower() == 'csv':
                    filepath = os.path.join(exports_dir, f"{base_filename}.csv")
                    df.to_csv(filepath, index=include_index)
                    exported_files['csv'] = filepath
                    self._log(f"Exported CSV: {filepath}")
                
                elif fmt.lower() == 'excel':
                    filepath = os.path.join(exports_dir, f"{base_filename}.xlsx")
                    df.to_excel(filepath, index=include_index, engine='openpyxl')
                    exported_files['excel'] = filepath
                    self._log(f"Exported Excel: {filepath}")
                
                elif fmt.lower() == 'json':
                    filepath = os.path.join(exports_dir, f"{base_filename}.json")
                    # Use records format for better JSON structure
                    df.to_json(filepath, orient='records', date_format='iso', index=include_index)
                    exported_files['json'] = filepath
                    self._log(f"Exported JSON: {filepath}")
                
                elif fmt.lower() == 'parquet':
                    filepath = os.path.join(exports_dir, f"{base_filename}.parquet")
                    df.to_parquet(filepath, index=include_index, engine='pyarrow')
                    exported_files['parquet'] = filepath
                    self._log(f"Exported Parquet: {filepath}")
                
                elif fmt.lower() == 'html':
                    filepath = os.path.join(exports_dir, f"{base_filename}.html")
                    html_table = df.to_html(index=include_index, classes='table table-striped')
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(f"<html><head><title>{filename}</title></head><body>{html_table}</body></html>")
                    exported_files['html'] = filepath
                    self._log(f"Exported HTML: {filepath}")
                    
            except Exception as e:
                if self.verbose:
                    print(f"  ⚠️  Could not export {fmt.upper()}: {str(e)}")
                continue
        
        return exported_files
    
    def generate_summary_report(self, df: pd.DataFrame, 
                               reports: Dict[str, Any],
                               filename: str = "pipeline_summary") -> str:
        """
        Generate comprehensive summary report
        
        Parameters:
        -----------
        df : pd.DataFrame
            Final processed DataFrame
        reports : dict
            Dictionary of all pipeline reports
        filename : str
            Base filename for report
            
        Returns:
        --------
        report_path : str
            Path to generated report file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        reports_dir = os.path.join(self.output_dir, "reports")
        
        summary = {
            'generated_at': datetime.now().isoformat(),
            'dataset_info': {
                'shape': {
                    'rows': int(df.shape[0]),
                    'columns': int(df.shape[1])
                },
                'memory_usage_mb': float(df.memory_usage(deep=True).sum() / (1024 ** 2)),
                'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()}
            },
            'data_quality': {
                'missing_values': {
                    'total': int(df.isnull().sum().sum()),
                    'percentage': float(df.isnull().sum().sum() / (df.shape[0] * df.shape[1]) * 100)
                },
                'duplicate_rows': {
                    'count': int(df.duplicated().sum()),
                    'percentage': float(df.duplicated().sum() / len(df) * 100)
                }
            },
            'pipeline_reports': reports,
            'columns_summary': {}
        }
        
        # Add column summaries
        for col in df.columns:
            col_data = df[col].dropna()
            col_info = {
                'dtype': str(df[col].dtype),
                'null_count': int(df[col].isnull().sum()),
                'null_percentage': float(df[col].isnull().sum() / len(df) * 100),
                'unique_values': int(df[col].nunique())
            }
            
            if pd.api.types.is_numeric_dtype(df[col]) and len(col_data) > 0:
                col_info['statistics'] = {
                    'min': float(col_data.min()),
                    'max': float(col_data.max()),
                    'mean': float(col_data.mean()),
                    'median': float(col_data.median()),
                    'std': float(col_data.std())
                }
            
            summary['columns_summary'][col] = col_info
        
        # Save report
        report_path = os.path.join(reports_dir, f"{filename}_{timestamp}.json")
        
        # Convert numpy types to native Python types for JSON serialization
        def convert_to_serializable(obj):
            if isinstance(obj, (np.integer, np.int64, np.int32)):
                return int(obj)
            elif isinstance(obj, (np.floating, np.float64, np.float32)):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {k: convert_to_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_to_serializable(item) for item in obj]
            elif pd.isna(obj):
                return None
            else:
                return obj
        
        serializable_summary = convert_to_serializable(summary)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(serializable_summary, f, indent=2, default=str)
        
        self._log(f"Generated summary report: {report_path}")
        
        return report_path
    
    def generate_execution_log(self, execution_info: Dict[str, Any],
                              filename: str = "execution_log") -> str:
        """
        Generate execution log
        
        Parameters:
        -----------
        execution_info : dict
            Execution information (timing, steps, etc.)
        filename : str
            Base filename for log
            
        Returns:
        --------
        log_path : str
            Path to generated log file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        logs_dir = os.path.join(self.output_dir, "logs")
        
        log_data = {
            'execution_time': datetime.now().isoformat(),
            **execution_info
        }
        
        log_path = os.path.join(logs_dir, f"{filename}_{timestamp}.json")
        
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, default=str)
        
        self._log(f"Generated execution log: {log_path}")
        
        return log_path
    
    def export_all_formats(self, df: pd.DataFrame, 
                          reports: Dict[str, Any],
                          base_filename: str,
                          formats: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Export data and generate all reports in one call
        
        Parameters:
        -----------
        df : pd.DataFrame
            DataFrame to export
        reports : dict
            Pipeline reports
        base_filename : str
            Base filename for all exports
        formats : list, optional
            Formats to export (default: ['csv', 'excel', 'json'])
            
        Returns:
        --------
        output_files : dict
            Dictionary of all generated files
        """
        if formats is None:
            formats = ['csv', 'excel', 'json']
        
        output_files = {
            'exports': {},
            'reports': {},
            'logs': {}
        }
        
        # Export data
        output_files['exports'] = self.export_dataframe(df, base_filename, formats)
        
        # Generate summary report
        summary_report = self.generate_summary_report(df, reports, f"{base_filename}_summary")
        output_files['reports']['summary'] = summary_report
        
        return output_files


def export_data(df: pd.DataFrame, 
                filename: str,
                output_dir: str = "data_pipeline_output",
                formats: List[str] = ['csv', 'excel', 'json'],
                verbose: bool = True) -> Dict[str, str]:
    """
    Convenience function to export data
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame to export
    filename : str
        Base filename
    output_dir : str
        Output directory
    formats : list
        Formats to export
    verbose : bool
        Whether to print progress
        
    Returns:
    --------
    exported_files : dict
        Dictionary of exported files
    """
    generator = OutputGenerator(output_dir=output_dir, verbose=verbose)
    return generator.export_dataframe(df, filename, formats)

