# outlier_handler.py

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Union, Optional
from dataclasses import dataclass
import json

# Helper functions for outlier handling
def grubbs_test(series: pd.Series, alpha: float = 0.05) -> List[int]:
    """
    Grubbs' test for outliers (simplified implementation)
    Returns indices of outliers
    """
    if len(series) < 3:
        return []
    
    series_clean = series.dropna()
    if len(series_clean) < 3:
        return []
    
    mean = series_clean.mean()
    std = series_clean.std()
    
    if std == 0:
        return []
    
    # Calculate G statistic for each point
    z_scores = np.abs((series_clean - mean) / std)
    max_idx = z_scores.idxmax()
    max_z = z_scores.max()
    
    # Critical value approximation (simplified)
    n = len(series_clean)
    t_critical = stats.t.ppf(1 - alpha / (2 * n), n - 2)
    g_critical = ((n - 1) / np.sqrt(n)) * np.sqrt(t_critical ** 2 / (n - 2 + t_critical ** 2))
    
    outliers = []
    if max_z > g_critical:
        outliers.append(max_idx)
    
    return outliers


def handle_outliers(df: pd.DataFrame, 
                   method: str = 'iqr',
                   threshold: float = 3.0,
                   iqr_factor: float = 1.5,
                   mcd_threshold: float = 0.975,
                   action: str = 'flag',
                   hypothesis_test: bool = False,
                   significance_level: float = 0.05) -> Tuple[pd.DataFrame, Dict]:
    """
    Handle outliers in a DataFrame using various methods
    """
    df_clean = df.copy()
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    report = {
        'method': method,
        'action': action,
        'n_outliers_detected': 0,
        'columns_processed': numeric_cols,
        'outlier_details': {}
    }
    
    outlier_indices = set()
    
    for col in numeric_cols:
        series = df_clean[col].dropna()
        if len(series) == 0:
            continue
        
        col_outliers = []
        
        if method == 'iqr':
            Q1 = series.quantile(0.25)
            Q3 = series.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - iqr_factor * IQR
            upper_bound = Q3 + iqr_factor * IQR
            col_outliers = series[(series < lower_bound) | (series > upper_bound)].index.tolist()
            
        elif method == 'zscore':
            z_scores = np.abs(stats.zscore(series))
            col_outliers = series[z_scores > threshold].index.tolist()
            
        elif method == 'mcd':
            # Simplified MCD - using percentile approach
            lower_bound = series.quantile(1 - mcd_threshold)
            upper_bound = series.quantile(mcd_threshold)
            col_outliers = series[(series < lower_bound) | (series > upper_bound)].index.tolist()
        
        if col_outliers:
            outlier_indices.update(col_outliers)
            report['outlier_details'][col] = {
                'count': len(col_outliers),
                'indices': col_outliers[:10]  # Limit to first 10 for report
            }
    
    report['n_outliers_detected'] = len(outlier_indices)
    
    # Apply action
    if action == 'remove':
        df_clean = df_clean.drop(index=list(outlier_indices))
        report['rows_removed'] = len(outlier_indices)
        
    elif action == 'cap':
        for col in numeric_cols:
            series = df_clean[col].dropna()
            if len(series) == 0:
                continue
            
            if method == 'iqr':
                Q1 = series.quantile(0.25)
                Q3 = series.quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - iqr_factor * IQR
                upper_bound = Q3 + iqr_factor * IQR
                df_clean.loc[df_clean[col] < lower_bound, col] = lower_bound
                df_clean.loc[df_clean[col] > upper_bound, col] = upper_bound
                
            elif method == 'zscore':
                mean = series.mean()
                std = series.std()
                if std > 0:
                    df_clean.loc[df_clean[col] < (mean - threshold * std), col] = mean - threshold * std
                    df_clean.loc[df_clean[col] > (mean + threshold * std), col] = mean + threshold * std
    
    elif action == 'flag':
        df_clean['is_outlier'] = df_clean.index.isin(outlier_indices)
        report['outlier_flag_column'] = 'is_outlier'
    
    return df_clean, report


@dataclass
class OutlierConfig:
    """Configuration for outlier detection and handling"""
    method: str = 'iqr'  # 'zscore', 'iqr', 'mcd', 'isolation_forest', 'local_outlier_factor'
    action: str = 'flag'  # 'remove', 'cap', 'flag', 'winsorize'
    threshold: float = 3.0  # For z-score
    iqr_factor: float = 1.5  # For IQR
    mcd_threshold: float = 0.975  # For MCD
    hypothesis_test: bool = False
    significance_level: float = 0.05
    multivariate_methods: bool = False  # Use multivariate detection methods
    contamination: float = 0.1  # For isolation forest and LOF
    random_state: int = 42


class OutlierHandler:
    """
    Comprehensive outlier detection and handling class
    """
    
    def __init__(self, config: Optional[OutlierConfig] = None):
        self.config = config or OutlierConfig()
        self.report = {}
        self.detection_stats = {}
        
    def detect_outliers(self, df: pd.DataFrame, columns: Optional[List[str]] = None) -> Dict:
        """
        Detect outliers using multiple methods and return comprehensive statistics
        """
        if columns is None:
            columns = df.select_dtypes(include='number').columns.tolist()
        
        results = {
            'univariate': {},
            'multivariate': {},
            'summary': {}
        }
        
        # Univariate methods
        for col in columns:
            col_results = {}
            series = df[col].dropna()
            
            # Z-score method
            z_scores = np.abs(stats.zscore(series))
            z_outliers = np.sum(z_scores > self.config.threshold)
            col_results['zscore'] = int(z_outliers)
            
            # IQR method
            Q1 = series.quantile(0.25)
            Q3 = series.quantile(0.75)
            IQR = Q3 - Q1
            iqr_outliers = np.sum((series < (Q1 - self.config.iqr_factor * IQR)) | 
                                 (series > (Q3 + self.config.iqr_factor * IQR)))
            col_results['iqr'] = int(iqr_outliers)
            
            # Modified Z-score (more robust)
            median = series.median()
            mad = stats.median_abs_deviation(series, scale='normal')
            modified_z = 0.6745 * (series - median) / mad
            mod_z_outliers = np.sum(np.abs(modified_z) > self.config.threshold)
            col_results['modified_zscore'] = int(mod_z_outliers)
            
            # Grubbs test if requested
            if self.config.hypothesis_test:
                grubbs_outliers = grubbs_test(df[col], alpha=self.config.significance_level)
                col_results['grubbs'] = len(grubbs_outliers)
            
            results['univariate'][col] = col_results
            
            # Store detection stats
            self.detection_stats[col] = {
                'mean': float(series.mean()),
                'std': float(series.std()),
                'median': float(series.median()),
                'min': float(series.min()),
                'max': float(series.max()),
                'Q1': float(Q1),
                'Q3': float(Q3),
                'IQR': float(IQR),
                'missing': int(df[col].isna().sum()),
                'total': len(df[col])
            }
        
        # Multivariate methods if enabled
        if self.config.multivariate_methods and len(columns) > 1:
            results['multivariate'] = self._detect_multivariate_outliers(df[columns])
        
        # Summary statistics
        results['summary'] = {
            'n_columns': len(columns),
            'n_rows': len(df),
            'total_missing': df[columns].isna().sum().sum(),
            'methods_used': list(results['univariate'].get(columns[0], {}).keys()) if columns else []
        }
        
        self.report['detection'] = results
        return results
    
    def _detect_multivariate_outliers(self, df: pd.DataFrame) -> Dict:
        """
        Detect outliers using multivariate methods
        """
        from sklearn.ensemble import IsolationForest
        from sklearn.neighbors import LocalOutlierFactor
        from sklearn.covariance import EllipticEnvelope
        
        results = {}
        df_clean = df.dropna()
        
        if len(df_clean) < 10:  # Need sufficient data
            return results
        
        # Isolation Forest
        iso_forest = IsolationForest(
            contamination=self.config.contamination,
            random_state=self.config.random_state
        )
        iso_pred = iso_forest.fit_predict(df_clean)
        results['isolation_forest'] = int(np.sum(iso_pred == -1))
        
        # Local Outlier Factor
        lof = LocalOutlierFactor(
            contamination=self.config.contamination,
            novelty=False
        )
        lof_pred = lof.fit_predict(df_clean)
        results['local_outlier_factor'] = int(np.sum(lof_pred == -1))
        
        # Elliptic Envelope (MCD-based)
        try:
            envelope = EllipticEnvelope(
                contamination=self.config.contamination,
                random_state=self.config.random_state
            )
            env_pred = envelope.fit_predict(df_clean)
            results['elliptic_envelope'] = int(np.sum(env_pred == -1))
        except:
            results['elliptic_envelope'] = 0
        
        return results
    
    def handle_outliers(self, df: pd.DataFrame, 
                       config: Optional[OutlierConfig] = None) -> Tuple[pd.DataFrame, Dict]:
        """
        Main method to handle outliers based on configuration
        """
        if config:
            self.config = config
        
        # Use your existing handle_outliers function
        cleaned_df, report = handle_outliers(
            df,
            method=self.config.method,
            threshold=self.config.threshold,
            iqr_factor=self.config.iqr_factor,
            mcd_threshold=self.config.mcd_threshold,
            action=self.config.action,
            hypothesis_test=self.config.hypothesis_test,
            significance_level=self.config.significance_level
        )
        
        # Enhanced reporting
        self.report['handling'] = report
        self.report['config'] = self.config.__dict__
        
        # Add pre/post comparison
        if 'is_outlier' in cleaned_df.columns:
            self.report['outlier_proportion'] = float(cleaned_df['is_outlier'].mean())
        
        return cleaned_df, self.report
    
    def visualize_outliers(self, df: pd.DataFrame, columns: Optional[List[str]] = None,
                          figsize: Tuple[int, int] = (15, 10)):
        """
        Create visualizations for outlier detection
        """
        if columns is None:
            columns = df.select_dtypes(include='number').columns.tolist()
        
        n_cols = len(columns)
        n_rows = (n_cols + 2) // 3
        
        fig, axes = plt.subplots(n_rows, 3, figsize=figsize)
        axes = axes.flatten()
        
        for idx, col in enumerate(columns):
            if idx >= len(axes):
                break
                
            ax = axes[idx]
            series = df[col].dropna()
            
            # Box plot
            ax.boxplot(series, vert=True)
            ax.set_title(f'{col}\n(n={len(series)})')
            ax.set_ylabel('Value')
            
            # Mark outliers (IQR method)
            Q1 = series.quantile(0.25)
            Q3 = series.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - self.config.iqr_factor * IQR
            upper_bound = Q3 + self.config.iqr_factor * IQR
            
            outliers = series[(series < lower_bound) | (series > upper_bound)]
            if len(outliers) > 0:
                ax.scatter(np.ones(len(outliers)), outliers.values, 
                          color='red', alpha=0.5, label=f'Outliers ({len(outliers)})')
                ax.legend()
        
        # Hide empty subplots
        for idx in range(len(columns), len(axes)):
            axes[idx].set_visible(False)
        
        plt.suptitle('Outlier Detection - Box Plots', fontsize=16)
        plt.tight_layout()
        
        return fig
    
    def compare_methods(self, df: pd.DataFrame, columns: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Compare different outlier detection methods
        """
        if columns is None:
            columns = df.select_dtypes(include='number').columns.tolist()
        
        comparison = []
        
        for method in ['zscore', 'iqr', 'mcd']:
            temp_config = OutlierConfig(method=method, action='flag')
            temp_handler = OutlierHandler(temp_config)
            cleaned_df, report = temp_handler.handle_outliers(df[columns].copy())
            
            n_outliers = report['handling']['n_outliers_detected']
            comparison.append({
                'method': method,
                'outliers_detected': n_outliers,
                'percentage': (n_outliers / len(df)) * 100
            })
        
        return pd.DataFrame(comparison)
    
    def save_report(self, filepath: str):
        """Save outlier detection report to file"""
        # Convert numpy types to Python native types for JSON serialization
        def convert_to_serializable(obj):
            if isinstance(obj, (np.integer, np.floating)):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {k: convert_to_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_to_serializable(item) for item in obj]
            else:
                return obj
        
        serializable_report = convert_to_serializable(self.report)
        
        with open(filepath, 'w') as f:
            json.dump(serializable_report, f, indent=2, default=str)
    
    @classmethod
    def load_report(cls, filepath: str) -> Dict:
        """Load outlier detection report from file"""
        with open(filepath, 'r') as f:
            return json.load(f)


def create_outlier_pipeline(df: pd.DataFrame, 
                          detection_config: OutlierConfig,
                          handling_config: OutlierConfig) -> Tuple[pd.DataFrame, Dict]:
    """
    Create a pipeline for outlier detection and handling
    """
    # Step 1: Detect and analyze
    detector = OutlierHandler(detection_config)
    detection_report = detector.detect_outliers(df)
    
    # Step 2: Visualize (optional)
    fig = detector.visualize_outliers(df)
    
    # Step 3: Handle outliers
    handler = OutlierHandler(handling_config)
    cleaned_df, handling_report = handler.handle_outliers(df)
    
    # Combine reports
    full_report = {
        'detection': detection_report,
        'handling': handling_report,
        'visualization_saved': fig is not None
    }
    
    return cleaned_df, full_report


def winsorize_data(df: pd.DataFrame, 
                  columns: Optional[List[str]] = None,
                  limits: Tuple[float, float] = (0.05, 0.05)) -> pd.DataFrame:
    """
    Winsorize data - cap outliers at specified percentiles
    """
    if columns is None:
        columns = df.select_dtypes(include='number').columns.tolist()
    
    df_clean = df.copy()
    
    for col in columns:
        lower = df_clean[col].quantile(limits[0])
        upper = df_clean[col].quantile(1 - limits[1])
        df_clean[col] = np.clip(df_clean[col], lower, upper)
    
    return df_clean


def analyze_outlier_impact(df_original: pd.DataFrame, 
                          df_cleaned: pd.DataFrame,
                          columns: Optional[List[str]] = None) -> Dict:
    """
    Analyze the impact of outlier removal on statistical properties
    """
    if columns is None:
        columns = df_original.select_dtypes(include='number').columns.tolist()
    
    impact_report = {}
    
    for col in columns:
        original = df_original[col].dropna()
        cleaned = df_cleaned[col].dropna()
        
        if len(original) == 0 or len(cleaned) == 0:
            continue
        
        impact_report[col] = {
            'original_stats': {
                'mean': float(original.mean()),
                'std': float(original.std()),
                'median': float(original.median()),
                'skew': float(original.skew()),
                'kurtosis': float(original.kurtosis())
            },
            'cleaned_stats': {
                'mean': float(cleaned.mean()),
                'std': float(cleaned.std()),
                'median': float(cleaned.median()),
                'skew': float(cleaned.skew()),
                'kurtosis': float(cleaned.kurtosis())
            },
            'percentage_change': {
                'mean': ((cleaned.mean() - original.mean()) / original.mean()) * 100,
                'std': ((cleaned.std() - original.std()) / original.std()) * 100,
                'median': ((cleaned.median() - original.median()) / original.median()) * 100
            },
            'n_removed': len(original) - len(cleaned) if 'is_outlier' in df_cleaned.columns else 0
        }
    
    return impact_report