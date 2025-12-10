"""
Final Data Validation Module
Performs comprehensive validation checks on cleaned data
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Callable
import warnings

warnings.filterwarnings('ignore')


class DataValidator:
    """
    Comprehensive data validation class for final quality checks
    """
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.validation_results = {}
        
    def _log(self, message: str):
        """Helper method for logging"""
        if self.verbose:
            print(f"  ✓ {message}")
    
    def validate_all(self, df: pd.DataFrame, 
                    schema: Optional[Dict[str, Any]] = None,
                    constraints: Optional[Dict[str, Callable]] = None) -> Dict[str, Any]:
        """
        Run all validation checks
        
        Parameters:
        -----------
        df : pd.DataFrame
            DataFrame to validate
        schema : dict, optional
            Expected schema: {'column_name': {'dtype': 'int64', 'nullable': False, ...}}
        constraints : dict, optional
            Custom validation functions: {'column_name': lambda x: x > 0}
            
        Returns:
        --------
        validation_report : dict
            Comprehensive validation report
        """
        self.validation_results = {
            'schema_validation': self.validate_schema(df, schema) if schema else {},
            'data_type_validation': self.validate_data_types(df),
            'null_validation': self.validate_null_values(df),
            'range_validation': self.validate_ranges(df),
            'uniqueness_validation': self.validate_uniqueness(df),
            'format_validation': self.validate_formats(df),
            'custom_constraints': self.validate_custom_constraints(df, constraints) if constraints else {},
            'data_quality_score': 0,
            'validation_status': 'unknown'
        }
        
        # Calculate overall quality score
        self.validation_results['data_quality_score'] = self._calculate_quality_score()
        self.validation_results['validation_status'] = self._determine_status()
        
        return self.validation_results
    
    def validate_schema(self, df: pd.DataFrame, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Validate DataFrame against expected schema"""
        results = {
            'columns_missing': [],
            'columns_extra': [],
            'type_mismatches': {},
            'nullable_violations': {},
            'status': 'passed'
        }
        
        expected_columns = set(schema.keys())
        actual_columns = set(df.columns)
        
        # Check missing columns
        results['columns_missing'] = list(expected_columns - actual_columns)
        
        # Check extra columns
        results['columns_extra'] = list(actual_columns - expected_columns)
        
        # Check data types and nullable constraints
        for col, col_schema in schema.items():
            if col not in df.columns:
                continue
                
            # Type validation
            expected_dtype = col_schema.get('dtype')
            if expected_dtype and not pd.api.types.is_dtype_equal(df[col].dtype, expected_dtype):
                results['type_mismatches'][col] = {
                    'expected': str(expected_dtype),
                    'actual': str(df[col].dtype)
                }
            
            # Nullable validation
            if col_schema.get('nullable', True) == False:
                null_count = df[col].isnull().sum()
                if null_count > 0:
                    results['nullable_violations'][col] = {
                        'null_count': int(null_count),
                        'null_percentage': float(null_count / len(df) * 100)
                    }
        
        # Determine status
        if (results['columns_missing'] or results['type_mismatches'] or 
            results['nullable_violations']):
            results['status'] = 'failed'
        else:
            results['status'] = 'passed'
            
        return results
    
    def validate_data_types(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate that data types are consistent and appropriate"""
        results = {
            'type_issues': {},
            'mixed_types': [],
            'inappropriate_types': {},
            'status': 'passed'
        }
        
        for col in df.columns:
            # Check for mixed types
            if df[col].dtype == 'object':
                unique_types = df[col].dropna().apply(type).unique()
                if len(unique_types) > 1:
                    results['mixed_types'].append({
                        'column': col,
                        'types': [str(t) for t in unique_types]
                    })
            
            # Check for inappropriate numeric types
            if pd.api.types.is_numeric_dtype(df[col]):
                if df[col].min() >= 0 and pd.api.types.is_signed_integer_dtype(df[col]):
                    # Could be unsigned
                    results['inappropriate_types'][col] = 'Consider unsigned integer type'
        
        if results['type_issues'] or results['mixed_types'] or results['inappropriate_types']:
            results['status'] = 'warning'
        else:
            results['status'] = 'passed'
            
        return results
    
    def validate_null_values(self, df: pd.DataFrame, 
                            max_null_percentage: float = 50.0) -> Dict[str, Any]:
        """Validate null value patterns"""
        results = {
            'high_null_columns': [],
            'null_patterns': {},
            'status': 'passed'
        }
        
        for col in df.columns:
            null_count = df[col].isnull().sum()
            null_pct = (null_count / len(df)) * 100
            
            if null_pct > max_null_percentage:
                results['high_null_columns'].append({
                    'column': col,
                    'null_count': int(null_count),
                    'null_percentage': round(null_pct, 2),
                    'recommendation': 'Consider dropping or extensive imputation'
                })
            
            results['null_patterns'][col] = {
                'null_count': int(null_count),
                'null_percentage': round(null_pct, 2)
            }
        
        if results['high_null_columns']:
            results['status'] = 'warning'
        else:
            results['status'] = 'passed'
            
        return results
    
    def validate_ranges(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate value ranges for numeric columns"""
        results = {
            'out_of_range': {},
            'negative_values': {},
            'zero_values': {},
            'status': 'passed'
        }
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            col_data = df[col].dropna()
            if len(col_data) == 0:
                continue
            
            # Check for negative values (might be invalid for certain columns)
            negative_count = (col_data < 0).sum()
            if negative_count > 0:
                results['negative_values'][col] = {
                    'count': int(negative_count),
                    'percentage': round(negative_count / len(col_data) * 100, 2)
                }
            
            # Check for zero values
            zero_count = (col_data == 0).sum()
            if zero_count > 0:
                results['zero_values'][col] = {
                    'count': int(zero_count),
                    'percentage': round(zero_count / len(col_data) * 100, 2)
                }
        
        if results['out_of_range'] or results['negative_values']:
            results['status'] = 'warning'
        else:
            results['status'] = 'passed'
            
        return results
    
    def validate_uniqueness(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate uniqueness constraints"""
        results = {
            'duplicate_rows': int(df.duplicated().sum()),
            'unique_columns': [],
            'low_cardinality_columns': [],
            'status': 'passed'
        }
        
        for col in df.columns:
            unique_count = df[col].nunique()
            total_count = len(df[col].dropna())
            
            if unique_count == total_count and total_count > 0:
                results['unique_columns'].append(col)
            elif unique_count < total_count * 0.01:  # Less than 1% unique values
                results['low_cardinality_columns'].append({
                    'column': col,
                    'unique_values': unique_count,
                    'total_values': total_count,
                    'cardinality_ratio': round(unique_count / total_count * 100, 2)
                })
        
        if results['duplicate_rows'] > 0:
            results['status'] = 'warning'
        else:
            results['status'] = 'passed'
            
        return results
    
    def validate_formats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate data formats (dates, emails, etc.)"""
        results = {
            'date_format_issues': [],
            'email_format_issues': [],
            'numeric_string_issues': [],
            'status': 'passed'
        }
        
        # Check for date-like columns that aren't datetime
        for col in df.select_dtypes(include=['object']).columns:
            sample = df[col].dropna().iloc[0] if len(df[col].dropna()) > 0 else None
            
            if sample and isinstance(sample, str):
                # Check if looks like date
                if any(x in sample.lower() for x in ['/', '-', ':', 'date']):
                    try:
                        pd.to_datetime(sample)
                        results['date_format_issues'].append({
                            'column': col,
                            'issue': 'Contains date-like strings, consider converting to datetime'
                        })
                    except:
                        pass
        
        if results['date_format_issues'] or results['email_format_issues']:
            results['status'] = 'warning'
        else:
            results['status'] = 'passed'
            
        return results
    
    def validate_custom_constraints(self, df: pd.DataFrame, 
                                   constraints: Dict[str, Callable]) -> Dict[str, Any]:
        """Validate custom constraints"""
        results = {
            'violations': {},
            'status': 'passed'
        }
        
        for col, constraint_func in constraints.items():
            if col not in df.columns:
                continue
            
            try:
                mask = ~df[col].apply(constraint_func)
                violation_count = mask.sum()
                
                if violation_count > 0:
                    results['violations'][col] = {
                        'violation_count': int(violation_count),
                        'violation_percentage': round(violation_count / len(df) * 100, 2),
                        'violation_indices': df[mask].index.tolist()[:10]  # First 10
                    }
            except Exception as e:
                results['violations'][col] = {
                    'error': str(e)
                }
        
        if results['violations']:
            results['status'] = 'failed'
        else:
            results['status'] = 'passed'
            
        return results
    
    def _calculate_quality_score(self) -> float:
        """Calculate overall data quality score (0-100)"""
        score = 100.0
        
        # Deduct points for each issue
        results = self.validation_results
        
        # Schema issues (-10 points each)
        if results.get('schema_validation', {}).get('columns_missing'):
            score -= len(results['schema_validation']['columns_missing']) * 10
        if results.get('schema_validation', {}).get('type_mismatches'):
            score -= len(results['schema_validation']['type_mismatches']) * 5
        
        # Data quality issues (-5 points each)
        if results.get('null_validation', {}).get('high_null_columns'):
            score -= len(results['null_validation']['high_null_columns']) * 5
        if results.get('uniqueness_validation', {}).get('duplicate_rows', 0) > 0:
            score -= min(10, results['uniqueness_validation']['duplicate_rows'] / 10)
        
        # Warning issues (-2 points each)
        if results.get('data_type_validation', {}).get('mixed_types'):
            score -= len(results['data_type_validation']['mixed_types']) * 2
        
        return max(0, round(score, 2))
    
    def _determine_status(self) -> str:
        """Determine overall validation status"""
        score = self.validation_results.get('data_quality_score', 0)
        
        if score >= 90:
            return 'excellent'
        elif score >= 75:
            return 'good'
        elif score >= 60:
            return 'acceptable'
        elif score >= 40:
            return 'poor'
        else:
            return 'critical'
    
    def print_validation_report(self, results: Optional[Dict[str, Any]] = None):
        """Pretty print validation report"""
        if results is None:
            results = self.validation_results
        
        print("\n" + "=" * 70)
        print("📋 FINAL DATA VALIDATION REPORT")
        print("=" * 70)
        
        score = results.get('data_quality_score', 0)
        status = results.get('validation_status', 'unknown')
        
        print(f"\n📊 Overall Quality Score: {score}/100")
        print(f"Status: {status.upper()}")
        
        # Schema validation
        schema = results.get('schema_validation', {})
        if schema:
            print(f"\n📐 Schema Validation: {schema.get('status', 'unknown').upper()}")
            if schema.get('columns_missing'):
                print(f"  ⚠️  Missing columns: {', '.join(schema['columns_missing'])}")
            if schema.get('type_mismatches'):
                print(f"  ⚠️  Type mismatches: {len(schema['type_mismatches'])} columns")
        
        # Null validation
        null_val = results.get('null_validation', {})
        if null_val.get('high_null_columns'):
            print(f"\n🔍 Null Value Validation: {null_val.get('status', 'unknown').upper()}")
            for col_info in null_val['high_null_columns'][:5]:
                print(f"  ⚠️  {col_info['column']}: {col_info['null_percentage']:.1f}% null")
        
        # Uniqueness
        uniqueness = results.get('uniqueness_validation', {})
        if uniqueness.get('duplicate_rows', 0) > 0:
            print(f"\n🔑 Uniqueness Validation: {uniqueness.get('status', 'unknown').upper()}")
            print(f"  ⚠️  Duplicate rows: {uniqueness['duplicate_rows']}")
        
        print("\n" + "=" * 70)


def validate_data(df: pd.DataFrame, 
                  schema: Optional[Dict[str, Any]] = None,
                  constraints: Optional[Dict[str, Callable]] = None,
                  verbose: bool = True) -> Dict[str, Any]:
    """
    Convenience function to validate data
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame to validate
    schema : dict, optional
        Expected schema
    constraints : dict, optional
        Custom validation functions
    verbose : bool
        Whether to print report
        
    Returns:
    --------
    validation_report : dict
        Validation results
    """
    validator = DataValidator(verbose=verbose)
    results = validator.validate_all(df, schema, constraints)
    
    if verbose:
        validator.print_validation_report(results)
    
    return results

