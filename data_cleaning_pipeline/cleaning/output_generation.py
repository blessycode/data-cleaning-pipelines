"""
Output Generation Module
Handles exporting cleaned data in multiple formats
"""

import pandas as pd
import numpy as np
import os
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')


class OutputGenerator:
    """
    Comprehensive output generation for cleaned data
    """
    
    def __init__(self, output_dir: str = "data_pipeline_output", verbose: bool = True):
        self.output_dir = output_dir
        self.verbose = verbose
        self.exported_files = []
        
    def _log(self, message: str):
        """Helper method for logging"""
        if self.verbose:
            print(f"💾 {message}")
    
    def export_all(self, df: pd.DataFrame, 
                  base_name: str = "cleaned_data",
                  formats: Optional[List[str]] = None,
                  include_reports: bool = True,
                  reports: Optional[Dict[str, Any]] = None) -> Dict[str, List[str]]:
        """
        Export data in multiple formats
        
        Parameters:
        -----------
        df : pd.DataFrame
            DataFrame to export
        base_name : str
            Base name for output files
        formats : list, optional
            List of formats to export ['csv', 'excel', 'parquet', 'json', 'pickle']
        include_reports : bool
            Whether to include metadata reports
        reports : dict, optional
            Additional reports to include
            
        Returns:
        --------
        exported_files : dict
            Dictionary of exported file paths by format
        """
        if formats is None:
            formats = ['csv', 'excel', 'parquet']
        
        self._log(f"Exporting data in {len(formats)} format(s)...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        exported_files = {fmt: [] for fmt in formats}
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Export in each format
        for fmt in formats:
            try:
                file_path = self._export_format(df, base_name, fmt, timestamp)
                if file_path:
                    exported_files[fmt].append(file_path)
                    self.exported_files.append(file_path)
            except Exception as e:
                self._log(f"⚠️  Failed to export {fmt}: {str(e)}")
        
        # Export metadata and reports
        if include_reports:
            metadata_file = self._export_metadata(df, base_name, timestamp, reports)
            if metadata_file:
                exported_files['metadata'] = [metadata_file]
        
        return exported_files
    
    def _export_format(self, df: pd.DataFrame, base_name: str, 
                      format_type: str, timestamp: str) -> Optional[str]:
        """Export data in specific format"""
        # Map logical format names to proper file extensions
        extension_map = {
            'csv': 'csv',
            'excel': 'xlsx',
            'parquet': 'parquet',
            'json': 'json',
            'pickle': 'pkl',
            'html': 'html'
        }
        
        ext = extension_map.get(format_type, format_type)
        filename = f"{base_name}_{timestamp}.{ext}"
        filepath = os.path.join(self.output_dir, filename)
        
        if format_type == 'csv':
            df.to_csv(filepath, index=False, encoding='utf-8')
            self._log(f"✓ Exported CSV: {filename}")
            
        elif format_type == 'excel':
            df.to_excel(filepath, index=False, engine='openpyxl')
            self._log(f"✓ Exported Excel: {filename}")
            
        elif format_type == 'parquet':
            df.to_parquet(filepath, index=False, engine='pyarrow')
            self._log(f"✓ Exported Parquet: {filename}")
            
        elif format_type == 'json':
            # Export as JSON records
            df.to_json(filepath, orient='records', date_format='iso', indent=2)
            self._log(f"✓ Exported JSON: {filename}")
            
        elif format_type == 'pickle':
            df.to_pickle(filepath)
            self._log(f"✓ Exported Pickle: {filename}")
            
        elif format_type == 'html':
            # Export as HTML table
            html_content = df.to_html(index=False, classes='table table-striped')
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"<html><head><title>{base_name}</title></head><body>{html_content}</body></html>")
            self._log(f"✓ Exported HTML: {filename}")
            
        else:
            self._log(f"⚠️  Unsupported format: {format_type}")
            return None
        
        return filepath
    
    def _export_metadata(self, df: pd.DataFrame, base_name: str, 
                        timestamp: str, reports: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Export metadata and reports"""
        metadata = {
            'export_info': {
                'timestamp': timestamp,
                'base_name': base_name,
                'exported_at': datetime.now().isoformat()
            },
            'dataset_info': {
                'shape': {
                    'rows': int(len(df)),
                    'columns': int(len(df.columns))
                },
                'columns': list(df.columns),
                'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
                'memory_usage_mb': round(df.memory_usage(deep=True).sum() / (1024 ** 2), 2)
            },
            'data_quality': {
                'missing_values': {
                    'total': int(df.isnull().sum().sum()),
                    'percentage': round((df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100, 2),
                    'by_column': {col: int(count) for col, count in df.isnull().sum().items() if count > 0}
                },
                'duplicates': {
                    'count': int(df.duplicated().sum()),
                    'percentage': round((df.duplicated().sum() / len(df)) * 100, 2) if len(df) > 0 else 0
                }
            }
        }
        
        # Add reports if provided
        if reports:
            metadata['reports'] = reports
        
        # Export metadata as JSON
        filename = f"{base_name}_metadata_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, default=str)
        
        self._log(f"✓ Exported metadata: {filename}")
        return filepath
    
    def export_summary_report(self, df: pd.DataFrame, reports: Dict[str, Any],
                             base_name: str = "summary") -> Optional[str]:
        """Export comprehensive summary report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{base_name}_report_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        summary = {
            'export_timestamp': datetime.now().isoformat(),
            'dataset_summary': {
                'shape': {'rows': len(df), 'columns': len(df.columns)},
                'columns': list(df.columns),
                'memory_usage_mb': round(df.memory_usage(deep=True).sum() / (1024 ** 2), 2)
            },
            'pipeline_reports': reports
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, default=str)
        
        self._log(f"✓ Exported summary report: {filename}")
        return filepath


def export_data(df: pd.DataFrame,
               output_dir: str = "data_pipeline_output",
               base_name: str = "cleaned_data",
               formats: Optional[List[str]] = None,
               verbose: bool = True) -> Dict[str, List[str]]:
    """
    Convenience function for exporting data
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame to export
    output_dir : str
        Output directory
    base_name : str
        Base name for files
    formats : list, optional
        Formats to export
    verbose : bool
        Whether to print progress
        
    Returns:
    --------
    exported_files : dict
        Dictionary of exported files
    """
    generator = OutputGenerator(output_dir=output_dir, verbose=verbose)
    return generator.export_all(df, base_name=base_name, formats=formats)

