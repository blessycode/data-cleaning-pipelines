"""
AI-Based Feature Engineering Suggestion System
Provides intelligent suggestions for feature engineering based on data analysis
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings('ignore')


class FeatureEngineeringAdvisor:
    """
    AI-based feature engineering advisor that analyzes data and suggests
    intelligent feature engineering transformations
    """
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.suggestions = {}
        
    def _log(self, message: str):
        """Helper method for logging"""
        if self.verbose:
            print(f"🤖 {message}")
    
    def analyze_and_suggest(self, df: pd.DataFrame, target_column: Optional[str] = None) -> Dict[str, Any]:
        """
        Comprehensive analysis and feature engineering suggestions
        
        Parameters:
        -----------
        df : pd.DataFrame
            Input dataframe
        target_column : str, optional
            Target column for supervised learning suggestions
            
        Returns:
        --------
        suggestions : dict
            Comprehensive feature engineering suggestions
        """
        self._log("Analyzing dataset for feature engineering opportunities...")
        
        suggestions = {
            'datetime_features': self._suggest_datetime_features(df),
            'numerical_features': self._suggest_numerical_features(df),
            'categorical_features': self._suggest_categorical_features(df),
            'interaction_features': self._suggest_interaction_features(df),
            'aggregation_features': self._suggest_aggregation_features(df),
            'transformation_features': self._suggest_transformation_features(df),
            'time_series_features': self._suggest_time_series_features(df),
            'target_based_suggestions': self._suggest_target_based_features(df, target_column) if target_column else {},
            'summary': {}
        }
        
        # Generate summary
        suggestions['summary'] = self._generate_summary(suggestions)
        
        self.suggestions = suggestions
        return suggestions
    
    def _suggest_datetime_features(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Suggest time series features from datetime columns"""
        suggestions = {
            'datetime_columns': [],
            'time_series_features': [],
            'cyclical_features': [],
            'temporal_features': [],
            'lag_features': [],
            'rolling_features': []
        }
        
        # Detect datetime columns
        datetime_cols = []
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                datetime_cols.append(col)
            else:
                # Try to detect datetime strings
                try:
                    sample = df[col].dropna().iloc[0] if len(df[col].dropna()) > 0 else None
                    if sample and isinstance(sample, str):
                        pd.to_datetime(sample)
                        datetime_cols.append(col)
                except:
                    pass
        
        suggestions['datetime_columns'] = datetime_cols
        
        if not datetime_cols:
            suggestions['message'] = "No datetime columns detected"
            return suggestions
        
        for dt_col in datetime_cols:
            try:
                # Convert to datetime if not already
                if not pd.api.types.is_datetime64_any_dtype(df[dt_col]):
                    df[dt_col] = pd.to_datetime(df[dt_col], errors='coerce')
                
                dt_data = df[dt_col].dropna()
                if len(dt_data) == 0:
                    continue
                
                # Basic temporal features
                suggestions['temporal_features'].append({
                    'base_column': dt_col,
                    'features': [
                        f'{dt_col}_year',
                        f'{dt_col}_month',
                        f'{dt_col}_day',
                        f'{dt_col}_dayofweek',
                        f'{dt_col}_dayofyear',
                        f'{dt_col}_quarter',
                        f'{dt_col}_week',
                        f'{dt_col}_is_weekend',
                        f'{dt_col}_is_month_start',
                        f'{dt_col}_is_month_end',
                        f'{dt_col}_is_quarter_start',
                        f'{dt_col}_is_quarter_end',
                        f'{dt_col}_is_year_start',
                        f'{dt_col}_is_year_end'
                    ],
                    'description': 'Extract year, month, day, day of week, quarter, and boolean flags'
                })
                
                # Cyclical encoding (for periodic patterns)
                suggestions['cyclical_features'].append({
                    'base_column': dt_col,
                    'features': [
                        f'{dt_col}_month_sin',
                        f'{dt_col}_month_cos',
                        f'{dt_col}_dayofweek_sin',
                        f'{dt_col}_dayofweek_cos',
                        f'{dt_col}_hour_sin',
                        f'{dt_col}_hour_cos'
                    ],
                    'description': 'Cyclical encoding for periodic patterns (sin/cos transformations)'
                })
                
                # Time differences
                time_range = dt_data.max() - dt_data.min()
                if time_range.days > 0:
                    suggestions['time_series_features'].append({
                        'base_column': dt_col,
                        'features': [
                            f'{dt_col}_days_since_min',
                            f'{dt_col}_days_since_max',
                            f'{dt_col}_days_until_next',
                            f'{dt_col}_days_since_previous'
                        ],
                        'description': 'Time difference features for time series analysis'
                    })
                
                # Lag features (if time series)
                if len(dt_data) > 10 and dt_data.is_monotonic_increasing:
                    suggestions['lag_features'].append({
                        'base_column': dt_col,
                        'lags': [1, 2, 3, 7, 14, 30],
                        'description': 'Lag features for time series forecasting',
                        'applicable_columns': df.select_dtypes(include=[np.number]).columns.tolist()[:5]  # Top 5 numerical
                    })
                
                # Rolling window features
                if len(dt_data) > 30:
                    suggestions['rolling_features'].append({
                        'base_column': dt_col,
                        'windows': [3, 7, 14, 30],
                        'functions': ['mean', 'std', 'min', 'max'],
                        'description': 'Rolling window statistics for time series',
                        'applicable_columns': df.select_dtypes(include=[np.number]).columns.tolist()[:5]
                    })
                
                # Hour features (if time component exists)
                if hasattr(dt_data.dt, 'hour'):
                    hour_data = dt_data.dt.hour
                    if hour_data.nunique() > 1:
                        suggestions['temporal_features'][-1]['features'].extend([
                            f'{dt_col}_hour',
                            f'{dt_col}_minute',
                            f'{dt_col}_time_of_day'  # Morning, Afternoon, Evening, Night
                        ])
                
            except Exception as e:
                self._log(f"Error analyzing {dt_col}: {str(e)}")
                continue
        
        return suggestions
    
    def _suggest_numerical_features(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Suggest numerical feature engineering"""
        suggestions = {
            'polynomial_features': [],
            'binning_features': [],
            'log_transform': [],
            'sqrt_transform': [],
            'power_transform': [],
            'ratio_features': [],
            'difference_features': [],
            'normalization_suggestions': []
        }
        
        numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if not numerical_cols:
            suggestions['message'] = "No numerical columns found"
            return suggestions
        
        for col in numerical_cols:
            col_data = df[col].dropna()
            if len(col_data) == 0:
                continue
            
            # Check for skewness
            skewness = col_data.skew()
            if abs(skewness) > 1:
                suggestions['log_transform'].append({
                    'column': col,
                    'skewness': round(skewness, 3),
                    'reason': 'High skewness detected',
                    'transformation': f'log1p({col})' if col_data.min() >= 0 else f'log1p({col} + abs(min({col})))'
                })
            
            # Check for wide range
            if col_data.max() / col_data.min() > 1000 and col_data.min() > 0:
                suggestions['sqrt_transform'].append({
                    'column': col,
                    'range_ratio': round(col_data.max() / col_data.min(), 2),
                    'reason': 'Very wide value range',
                    'transformation': f'sqrt({col})'
                })
            
            # Binning suggestions
            if col_data.nunique() > 20:
                suggestions['binning_features'].append({
                    'column': col,
                    'unique_values': col_data.nunique(),
                    'bins': [5, 10, 20],
                    'method': 'quantile',  # or 'uniform'
                    'description': f'Convert {col} to categorical bins'
                })
            
            # Polynomial features (for highly correlated pairs)
            for other_col in numerical_cols:
                if col != other_col:
                    try:
                        corr = df[[col, other_col]].corr().iloc[0, 1]
                        if abs(corr) > 0.7:
                            suggestions['polynomial_features'].append({
                                'columns': [col, other_col],
                                'correlation': round(corr, 3),
                                'features': [
                                    f'{col}_x_{other_col}',
                                    f'{col}_squared',
                                    f'{other_col}_squared'
                                ],
                                'description': 'Polynomial features for highly correlated variables'
                            })
                            break  # Only suggest once per column
                    except:
                        continue
            
            # Ratio features
            for other_col in numerical_cols:
                if col != other_col:
                    # Avoid division by zero
                    if (df[other_col] != 0).any():
                        suggestions['ratio_features'].append({
                            'numerator': col,
                            'denominator': other_col,
                            'feature': f'{col}_div_{other_col}',
                            'description': f'Ratio of {col} to {other_col}'
                        })
                        break  # Limit suggestions
        
        # Normalization suggestions
        for col in numerical_cols[:10]:  # Top 10
            col_data = df[col].dropna()
            if len(col_data) > 0:
                std_dev = col_data.std()
                if std_dev > 0:
                    suggestions['normalization_suggestions'].append({
                        'column': col,
                        'std_dev': round(std_dev, 3),
                        'methods': ['standard_scaler', 'minmax_scaler', 'robust_scaler'],
                        'recommended': 'robust_scaler' if abs(col_data.skew()) > 1 else 'standard_scaler'
                    })
        
        return suggestions
    
    def _suggest_categorical_features(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Suggest categorical feature engineering"""
        suggestions = {
            'encoding_suggestions': [],
            'target_encoding': [],
            'frequency_encoding': [],
            'rare_category_handling': [],
            'category_combinations': []
        }
        
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        if not categorical_cols:
            suggestions['message'] = "No categorical columns found"
            return suggestions
        
        for col in categorical_cols:
            col_data = df[col].dropna()
            unique_count = col_data.nunique()
            total_count = len(col_data)
            
            # Encoding suggestions
            if unique_count <= 10:
                suggestions['encoding_suggestions'].append({
                    'column': col,
                    'unique_values': unique_count,
                    'recommended_encoding': 'one_hot',
                    'reason': 'Low cardinality - suitable for one-hot encoding'
                })
            elif unique_count <= 50:
                suggestions['encoding_suggestions'].append({
                    'column': col,
                    'unique_values': unique_count,
                    'recommended_encoding': 'target_encoding',
                    'alternative': 'ordinal_encoding',
                    'reason': 'Medium cardinality - consider target encoding or ordinal'
                })
            else:
                suggestions['encoding_suggestions'].append({
                    'column': col,
                    'unique_values': unique_count,
                    'recommended_encoding': 'target_encoding',
                    'alternative': 'frequency_encoding',
                    'reason': 'High cardinality - use target or frequency encoding'
                })
            
            # Frequency encoding
            if unique_count > 10:
                suggestions['frequency_encoding'].append({
                    'column': col,
                    'feature': f'{col}_frequency',
                    'description': 'Encode categories by their frequency in the dataset'
                })
            
            # Rare category handling
            value_counts = col_data.value_counts()
            rare_threshold = total_count * 0.01  # 1% threshold
            rare_categories = value_counts[value_counts < rare_threshold].index.tolist()
            
            if rare_categories:
                suggestions['rare_category_handling'].append({
                    'column': col,
                    'rare_categories_count': len(rare_categories),
                    'suggestion': 'Group rare categories into "Other" category',
                    'threshold': round(rare_threshold, 0)
                })
        
        return suggestions
    
    def _suggest_interaction_features(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Suggest interaction features between columns"""
        suggestions = {
            'numerical_interactions': [],
            'categorical_numerical_interactions': [],
            'categorical_interactions': []
        }
        
        numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        # Numerical interactions (multiplication, addition)
        if len(numerical_cols) >= 2:
            for i, col1 in enumerate(numerical_cols[:5]):  # Limit to top 5
                for col2 in numerical_cols[i+1:6]:
                    suggestions['numerical_interactions'].append({
                        'columns': [col1, col2],
                        'features': [
                            f'{col1}_x_{col2}',
                            f'{col1}_plus_{col2}',
                            f'{col1}_minus_{col2}'
                        ],
                        'description': 'Mathematical interactions between numerical features'
                    })
        
        # Categorical-Numerical interactions (group statistics)
        if categorical_cols and numerical_cols:
            for cat_col in categorical_cols[:3]:  # Top 3 categorical
                for num_col in numerical_cols[:3]:  # Top 3 numerical
                    suggestions['categorical_numerical_interactions'].append({
                        'categorical': cat_col,
                        'numerical': num_col,
                        'features': [
                            f'{num_col}_mean_by_{cat_col}',
                            f'{num_col}_std_by_{cat_col}',
                            f'{num_col}_min_by_{cat_col}',
                            f'{num_col}_max_by_{cat_col}'
                        ],
                        'description': f'Group statistics of {num_col} by {cat_col}'
                    })
        
        return suggestions
    
    def _suggest_aggregation_features(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Suggest aggregation features"""
        suggestions = {
            'row_level_aggregations': [],
            'group_aggregations': []
        }
        
        numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(numerical_cols) >= 2:
            suggestions['row_level_aggregations'].append({
                'columns': numerical_cols[:10],  # Top 10
                'features': [
                    'row_sum',
                    'row_mean',
                    'row_std',
                    'row_max',
                    'row_min',
                    'row_median'
                ],
                'description': 'Row-level aggregations across numerical columns'
            })
        
        return suggestions
    
    def _suggest_transformation_features(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Suggest transformation features"""
        suggestions = {
            'scaling_suggestions': [],
            'discretization': [],
            'clustering_features': []
        }
        
        numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        for col in numerical_cols[:10]:
            col_data = df[col].dropna()
            if len(col_data) == 0:
                continue
            
            # Discretization
            if col_data.nunique() > 20:
                suggestions['discretization'].append({
                    'column': col,
                    'method': 'KBinsDiscretizer',
                    'n_bins': 5,
                    'strategy': 'quantile',
                    'description': f'Discretize {col} into bins'
                })
        
        return suggestions
    
    def _suggest_time_series_features(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Suggest time series specific features"""
        suggestions = {
            'datetime_columns': [],
            'trend_features': [],
            'seasonality_features': [],
            'autocorrelation_features': []
        }
        
        datetime_cols = [col for col in df.columns 
                        if pd.api.types.is_datetime64_any_dtype(df[col])]
        
        if not datetime_cols:
            suggestions['message'] = "No datetime columns for time series analysis"
            return suggestions
        
        suggestions['datetime_columns'] = datetime_cols
        
        # If we have a datetime column and numerical columns, suggest time series features
        numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if datetime_cols and numerical_cols:
            dt_col = datetime_cols[0]
            suggestions['trend_features'].append({
                'datetime_column': dt_col,
                'numerical_columns': numerical_cols[:5],
                'features': [
                    'moving_average_7',
                    'moving_average_30',
                    'exponential_moving_average',
                    'trend_slope'
                ],
                'description': 'Trend detection features for time series'
            })
            
            suggestions['seasonality_features'].append({
                'datetime_column': dt_col,
                'features': [
                    'seasonal_decompose',
                    'fourier_features',
                    'lag_features'
                ],
                'description': 'Seasonality detection features'
            })
        
        return suggestions
    
    def _suggest_target_based_features(self, df: pd.DataFrame, target_column: str) -> Dict[str, Any]:
        """Suggest features based on target variable analysis"""
        if target_column not in df.columns:
            return {'error': f'Target column {target_column} not found'}
        
        suggestions = {
            'target_encoding': [],
            'correlation_based': [],
            'importance_based': []
        }
        
        # Target encoding for categoricals
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        for cat_col in categorical_cols:
            if cat_col != target_column:
                suggestions['target_encoding'].append({
                    'categorical_column': cat_col,
                    'target': target_column,
                    'feature': f'{cat_col}_target_encoded',
                    'description': f'Mean target value per category in {cat_col}'
                })
        
        # Correlation-based suggestions
        if pd.api.types.is_numeric_dtype(df[target_column]):
            numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            for num_col in numerical_cols:
                if num_col != target_column:
                    try:
                        corr = df[[num_col, target_column]].corr().iloc[0, 1]
                        if abs(corr) > 0.3:
                            suggestions['correlation_based'].append({
                                'column': num_col,
                                'correlation': round(corr, 3),
                                'suggestion': 'High correlation - consider polynomial features'
                            })
                    except:
                        pass
        
        return suggestions
    
    def _generate_summary(self, suggestions: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of all suggestions"""
        summary = {
            'total_suggestions': 0,
            'by_category': {},
            'priority_features': [],
            'quick_wins': []
        }
        
        # Count suggestions by category
        for category, content in suggestions.items():
            if category == 'summary':
                continue
            
            if isinstance(content, dict):
                count = sum(len(v) if isinstance(v, list) else 1 
                          for v in content.values() if v)
                summary['by_category'][category] = count
                summary['total_suggestions'] += count
        
        # Priority features (most impactful)
        priority = []
        
        # Time series features are high priority
        if suggestions.get('time_series_features', {}).get('datetime_columns'):
            priority.append({
                'type': 'time_series',
                'description': 'Time series features from datetime columns',
                'impact': 'high'
            })
        
        # Target encoding if target provided
        if suggestions.get('target_based_suggestions'):
            priority.append({
                'type': 'target_encoding',
                'description': 'Target-based encoding for categoricals',
                'impact': 'high'
            })
        
        # Log transforms for skewed data
        if suggestions.get('numerical_features', {}).get('log_transform'):
            priority.append({
                'type': 'log_transform',
                'description': 'Log transformation for skewed numerical features',
                'impact': 'medium'
            })
        
        summary['priority_features'] = priority[:5]
        
        # Quick wins (easy to implement, high impact)
        quick_wins = []
        
        if suggestions.get('datetime_features', {}).get('temporal_features'):
            quick_wins.append('Extract datetime components (year, month, day, etc.)')
        
        if suggestions.get('categorical_features', {}).get('frequency_encoding'):
            quick_wins.append('Frequency encoding for high-cardinality categoricals')
        
        if suggestions.get('numerical_features', {}).get('ratio_features'):
            quick_wins.append('Create ratio features between numerical columns')
        
        summary['quick_wins'] = quick_wins[:5]
        
        return summary
    
    def print_suggestions(self, suggestions: Optional[Dict[str, Any]] = None):
        """Pretty print suggestions"""
        if suggestions is None:
            suggestions = self.suggestions
        
        print("\n" + "=" * 70)
        print("🤖 AI-BASED FEATURE ENGINEERING SUGGESTIONS")
        print("=" * 70)
        
        # Summary
        summary = suggestions.get('summary', {})
        print(f"\n📊 Total Suggestions: {summary.get('total_suggestions', 0)}")
        
        # By category
        print("\n📋 Suggestions by Category:")
        for category, count in summary.get('by_category', {}).items():
            print(f"  • {category.replace('_', ' ').title()}: {count}")
        
        # Priority features
        print("\n⭐ Priority Features:")
        for feature in summary.get('priority_features', [])[:5]:
            print(f"  • [{feature['impact'].upper()}] {feature['description']}")
        
        # Quick wins
        print("\n⚡ Quick Wins (Easy to implement):")
        for win in summary.get('quick_wins', [])[:5]:
            print(f"  • {win}")
        
        # Detailed suggestions
        print("\n" + "=" * 70)
        print("📝 DETAILED SUGGESTIONS")
        print("=" * 70)
        
        # DateTime features
        dt_features = suggestions.get('datetime_features', {})
        if dt_features.get('datetime_columns'):
            print(f"\n📅 DateTime Features ({len(dt_features['datetime_columns'])} columns):")
            for feat in dt_features.get('temporal_features', [])[:3]:
                print(f"  • {feat['base_column']}: {len(feat['features'])} features suggested")
                print(f"    Examples: {', '.join(feat['features'][:5])}")
        
        # Numerical features
        num_features = suggestions.get('numerical_features', {})
        if num_features.get('log_transform'):
            print(f"\n🔢 Numerical Transformations:")
            print(f"  • Log transform: {len(num_features['log_transform'])} columns")
            for trans in num_features['log_transform'][:3]:
                print(f"    - {trans['column']} (skewness: {trans['skewness']})")
        
        # Categorical features
        cat_features = suggestions.get('categorical_features', {})
        if cat_features.get('encoding_suggestions'):
            print(f"\n🏷️  Categorical Encoding:")
            print(f"  • {len(cat_features['encoding_suggestions'])} columns analyzed")
            for enc in cat_features['encoding_suggestions'][:3]:
                print(f"    - {enc['column']}: {enc['recommended_encoding']} ({enc['unique_values']} unique values)")
        
        print("\n" + "=" * 70)


def suggest_features(df: pd.DataFrame, target_column: Optional[str] = None, 
                    verbose: bool = True) -> Dict[str, Any]:
    """
    Convenience function to get feature engineering suggestions
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input dataframe
    target_column : str, optional
        Target column for supervised learning
    verbose : bool
        Whether to print suggestions
        
    Returns:
    --------
    suggestions : dict
        Feature engineering suggestions
    """
    advisor = FeatureEngineeringAdvisor(verbose=verbose)
    suggestions = advisor.analyze_and_suggest(df, target_column)
    
    if verbose:
        advisor.print_suggestions(suggestions)
    
    return suggestions

