"""
Final Data Validation Module
Comprehensive validation checks for cleaned data before export
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
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
            print(f"🔍 {message}")
    
    def validate_all(self, df: pd.DataFrame, 
                    schema: Optional[Dict[str, Any]] = None,
                    constraints: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Run all validation checks
        
        Parameters:
        -----------
        df : pd.DataFrame
            DataFrame to validate
        schema : dict, optional
            Expected schema with column types and constraints
        constraints : dict, optional
            Business rules and constraints
            
        Returns:
        --------
        validation_report : dict
            Comprehensive validation report
        """
        self._log("Starting comprehensive data validation...")
        
        validation_report = {
            'basic_checks': self.validate_basic_quality(df),
            'data_types': self.validate_data_types(df, schema),
            'missing_values': self.validate_missing_values(df),
            'duplicates': self.validate_duplicates(df),
            'value_ranges': self.validate_value_ranges(df, constraints),
            'data_integrity': self.validate_data_integrity(df),
            'business_rules': self.validate_business_rules(df, constraints),
            'summary': {}
        }
        
        # Generate summary
        validation_report['summary'] = self._generate_validation_summary(validation_report)
        
        self.validation_results = validation_report
        return validation_report
    
    def validate_basic_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Basic data quality checks"""
        checks = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'empty_dataframe': len(df) == 0,
            'empty_columns': [],
            'all_null_columns': [],
            'issues': []
        }
        
        # Check for empty columns
        for col in df.columns:
            if len(df[col].dropna()) == 0:
                checks['empty_columns'].append(col)
                checks['issues'].append(f"Column '{col}' is completely empty")
            
            if df[col].isna().all():
                checks['all_null_columns'].append(col)
                checks['issues'].append(f"Column '{col}' contains only null values")
        
        checks['has_issues'] = len(checks['issues']) > 0
        checks['quality_score'] = 100 - (len(checks['issues']) * 10)
        checks['quality_score'] = max(0, checks['quality_score'])
        
        return checks
    
    def validate_data_types(self, df: pd.DataFrame, schema: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Validate data types match expected schema"""
        checks = {
            'type_mismatches': [],
            'unexpected_types': [],
            'all_valid': True
        }
        
        if schema and 'columns' in schema:
            expected_types = schema['columns']
            
            for col, expected_type in expected_types.items():
                if col not in df.columns:
                    checks['type_mismatches'].append({
                        'column': col,
                        'issue': 'Column missing from dataframe'
                    })
                    checks['all_valid'] = False
                    continue
                
                actual_type = str(df[col].dtype)
                expected_type_str = str(expected_type)
                
                # Check if types match
                if not self._types_match(actual_type, expected_type_str):
                    checks['type_mismatches'].append({
                        'column': col,
                        'expected': expected_type_str,
                        'actual': actual_type
                    })
                    checks['all_valid'] = False
        
        return checks
    
    def _types_match(self, actual: str, expected: str) -> bool:
        """Check if data types match (with some flexibility)"""
        type_mapping = {
            'int': ['int64', 'int32', 'int16', 'int8', 'Int64'],
            'float': ['float64', 'float32', 'Float64'],
            'object': ['object', 'string'],
            'datetime': ['datetime64[ns]', 'datetime64'],
            'bool': ['bool', 'boolean']
        }
        
        for base_type, variants in type_mapping.items():
            if base_type in expected.lower():
                return any(v in actual.lower() for v in variants)
        
        return actual.lower() == expected.lower()
    
    def validate_missing_values(self, df: pd.DataFrame, 
                               max_missing_percent: float = 50.0) -> Dict[str, Any]:
        """Validate missing values are within acceptable limits"""
        checks = {
            'total_missing': int(df.isnull().sum().sum()),
            'missing_percentage': float((df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100),
            'high_missing_columns': [],
            'acceptable': True
        }
        
        for col in df.columns:
            missing_pct = (df[col].isnull().sum() / len(df)) * 100
            if missing_pct > max_missing_percent:
                checks['high_missing_columns'].append({
                    'column': col,
                    'missing_percentage': round(missing_pct, 2)
                })
                checks['acceptable'] = False
        
        if checks['missing_percentage'] > max_missing_percent:
            checks['acceptable'] = False
        
        return checks
    
    def validate_duplicates(self, df: pd.DataFrame, 
                           max_duplicate_percent: float = 10.0) -> Dict[str, Any]:
        """Validate duplicate rows are within acceptable limits"""
        duplicate_count = df.duplicated().sum()
        duplicate_percent = (duplicate_count / len(df)) * 100 if len(df) > 0 else 0
        
        checks = {
            'duplicate_count': int(duplicate_count),
            'duplicate_percentage': round(duplicate_percent, 2),
            'acceptable': duplicate_percent <= max_duplicate_percent,
            'max_allowed_percent': max_duplicate_percent
        }
        
        return checks
    
    def validate_value_ranges(self, df: pd.DataFrame, 
                             constraints: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Validate values are within expected ranges"""
        checks = {
            'range_violations': [],
            'all_valid': True
        }
        
        if not constraints or 'ranges' not in constraints:
            return checks
        
        ranges = constraints['ranges']
        
        for col, range_def in ranges.items():
            if col not in df.columns:
                continue
            
            if not pd.api.types.is_numeric_dtype(df[col]):
                continue
            
            col_data = df[col].dropna()
            if len(col_data) == 0:
                continue
            
            min_val = range_def.get('min')
            max_val = range_def.get('max')
            
            violations = []
            
            if min_val is not None:
                below_min = col_data[col_data < min_val]
                if len(below_min) > 0:
                    violations.append(f"{len(below_min)} values below minimum ({min_val})")
            
            if max_val is not None:
                above_max = col_data[col_data > max_val]
                if len(above_max) > 0:
                    violations.append(f"{len(above_max)} values above maximum ({max_val})")
            
            if violations:
                checks['range_violations'].append({
                    'column': col,
                    'violations': violations
                })
                checks['all_valid'] = False
        
        return checks
    
    def validate_data_integrity(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate data integrity (referential, consistency)"""
        checks = {
            'infinite_values': [],
            'negative_counts': [],
            'date_consistency': [],
            'all_valid': True
        }
        
        # Check for infinite values
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if np.isinf(df[col]).any():
                checks['infinite_values'].append(col)
                checks['all_valid'] = False
        
        # Check for negative values in count/positive-only columns
        count_like_cols = [col for col in numeric_cols 
                          if any(keyword in col.lower() for keyword in ['count', 'quantity', 'amount', 'age'])]
        for col in count_like_cols:
            if (df[col] < 0).any():
                negative_count = (df[col] < 0).sum()
                checks['negative_counts'].append({
                    'column': col,
                    'count': int(negative_count)
                })
                checks['all_valid'] = False
        
        # Check date consistency
        datetime_cols = [col for col in df.columns 
                        if pd.api.types.is_datetime64_any_dtype(df[col])]
        for col in datetime_cols:
            # Check for future dates (if not expected)
            future_dates = df[col] > pd.Timestamp.now()
            if future_dates.any():
                checks['date_consistency'].append({
                    'column': col,
                    'issue': f"{future_dates.sum()} future dates found"
                })
        
        return checks
    
    def validate_business_rules(self, df: pd.DataFrame, 
                               constraints: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Validate business rules and constraints"""
        checks = {
            'rule_violations': [],
            'all_valid': True
        }
        
        if not constraints or 'business_rules' not in constraints:
            return checks
        
        rules = constraints['business_rules']
        
        for rule_name, rule_def in rules.items():
            rule_type = rule_def.get('type')
            columns = rule_def.get('columns', [])
            condition = rule_def.get('condition')
            
            if rule_type == 'unique_combination':
                # Check if combination of columns should be unique
                if all(col in df.columns for col in columns):
                    duplicates = df[columns].duplicated().sum()
                    if duplicates > 0:
                        checks['rule_violations'].append({
                            'rule': rule_name,
                            'type': rule_type,
                            'violations': int(duplicates),
                            'columns': columns
                        })
                        checks['all_valid'] = False
            
            elif rule_type == 'conditional':
                # Check conditional rules
                if condition and all(col in df.columns for col in columns):
                    try:
                        # Evaluate condition (simplified - in production, use safer evaluation)
                        violations = df.query(condition)
                        if len(violations) > 0:
                            checks['rule_violations'].append({
                                'rule': rule_name,
                                'type': rule_type,
                                'violations': len(violations),
                                'condition': condition
                            })
                            checks['all_valid'] = False
                    except:
                        pass
        
        return checks
    
    def _generate_validation_summary(self, validation_report: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of validation results"""
        summary = {
            'overall_status': 'PASS',
            'total_issues': 0,
            'critical_issues': [],
            'warnings': [],
            'validation_score': 100
        }
        
        # Collect all issues
        issues = []
        
        # Basic quality issues
        basic = validation_report.get('basic_checks', {})
        if basic.get('has_issues'):
            issues.extend(basic.get('issues', []))
            summary['validation_score'] = min(summary['validation_score'], basic.get('quality_score', 100))
        
        # Type mismatches
        types = validation_report.get('data_types', {})
        if types.get('type_mismatches'):
            issues.extend([f"Type mismatch in {m['column']}" for m in types['type_mismatches']])
            summary['validation_score'] -= len(types['type_mismatches']) * 5
        
        # Missing values
        missing = validation_report.get('missing_values', {})
        if not missing.get('acceptable'):
            issues.append(f"High missing values: {missing.get('missing_percentage', 0):.1f}%")
            summary['validation_score'] -= 10
        
        # Duplicates
        duplicates = validation_report.get('duplicates', {})
        if not duplicates.get('acceptable'):
            issues.append(f"High duplicate percentage: {duplicates.get('duplicate_percentage', 0):.1f}%")
            summary['validation_score'] -= 10
        
        # Range violations
        ranges = validation_report.get('value_ranges', {})
        if not ranges.get('all_valid'):
            issues.append(f"{len(ranges.get('range_violations', []))} range violations found")
            summary['validation_score'] -= len(ranges.get('range_violations', [])) * 5
        
        # Data integrity
        integrity = validation_report.get('data_integrity', {})
        if not integrity.get('all_valid'):
            if integrity.get('infinite_values'):
                issues.append(f"Infinite values in: {', '.join(integrity['infinite_values'])}")
            if integrity.get('negative_counts'):
                issues.append(f"Negative values in count columns")
            summary['validation_score'] -= 15
        
        # Business rules
        business = validation_report.get('business_rules', {})
        if not business.get('all_valid'):
            issues.append(f"{len(business.get('rule_violations', []))} business rule violations")
            summary['validation_score'] -= len(business.get('rule_violations', [])) * 10
        
        summary['total_issues'] = len(issues)
        summary['critical_issues'] = [i for i in issues if 'critical' in i.lower() or 'violation' in i.lower()]
        summary['warnings'] = [i for i in issues if i not in summary['critical_issues']]
        
        summary['validation_score'] = max(0, summary['validation_score'])
        
        if summary['total_issues'] > 0:
            summary['overall_status'] = 'FAIL' if summary['validation_score'] < 70 else 'WARNING'
        
        return summary
    
    def print_validation_report(self, validation_report: Optional[Dict[str, Any]] = None):
        """Pretty print validation report"""
        if validation_report is None:
            validation_report = self.validation_results
        
        summary = validation_report.get('summary', {})
        
        print("\n" + "=" * 70)
        print("🔍 FINAL DATA VALIDATION REPORT")
        print("=" * 70)
        
        print(f"\n📊 Overall Status: {summary.get('overall_status', 'UNKNOWN')}")
        print(f"📈 Validation Score: {summary.get('validation_score', 0)}/100")
        print(f"⚠️  Total Issues: {summary.get('total_issues', 0)}")
        
        if summary.get('critical_issues'):
            print(f"\n❌ Critical Issues ({len(summary['critical_issues'])}):")
            for issue in summary['critical_issues'][:5]:
                print(f"  • {issue}")
        
        if summary.get('warnings'):
            print(f"\n⚠️  Warnings ({len(summary['warnings'])}):")
            for warning in summary['warnings'][:5]:
                print(f"  • {warning}")
        
        # Detailed checks
        print("\n" + "-" * 70)
        print("📋 DETAILED CHECKS:")
        print("-" * 70)
        
        basic = validation_report.get('basic_checks', {})
        print(f"\n✓ Basic Quality: {basic.get('total_rows', 0):,} rows × {basic.get('total_columns', 0)} columns")
        if basic.get('empty_columns'):
            print(f"  ⚠️  Empty columns: {', '.join(basic['empty_columns'][:3])}")
        
        missing = validation_report.get('missing_values', {})
        print(f"\n✓ Missing Values: {missing.get('missing_percentage', 0):.1f}%")
        if not missing.get('acceptable'):
            print(f"  ⚠️  High missing values detected")
        
        duplicates = validation_report.get('duplicates', {})
        print(f"\n✓ Duplicates: {duplicates.get('duplicate_percentage', 0):.1f}%")
        if not duplicates.get('acceptable'):
            print(f"  ⚠️  High duplicate percentage")
        
        integrity = validation_report.get('data_integrity', {})
        if integrity.get('all_valid'):
            print(f"\n✓ Data Integrity: All checks passed")
        else:
            print(f"\n⚠️  Data Integrity: Issues detected")
        
        print("\n" + "=" * 70)


def validate_data(df: pd.DataFrame, 
                 schema: Optional[Dict[str, Any]] = None,
                 constraints: Optional[Dict[str, Any]] = None,
                 verbose: bool = True) -> Dict[str, Any]:
    """
    Convenience function for data validation
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame to validate
    schema : dict, optional
        Expected schema
    constraints : dict, optional
        Business rules and constraints
    verbose : bool
        Whether to print report
        
    Returns:
    --------
    validation_report : dict
        Validation report
    """
    validator = DataValidator(verbose=verbose)
    report = validator.validate_all(df, schema, constraints)
    
    if verbose:
        validator.print_validation_report(report)
    
    return report

