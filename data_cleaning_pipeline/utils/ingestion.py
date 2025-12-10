import os
import pandas as pd
import sqlalchemy
import chardet
import csv
import numpy as np
import json
from pathlib import Path
from typing import Union, Optional, Dict, Any, Tuple


def detect_encoding(file_path: str, sample_size: int = 50000) -> str:
    """Detect file encoding with better error handling."""
    try:
        with open(file_path, "rb") as f:
            raw_data = f.read(sample_size)
        result = chardet.detect(raw_data)
        # Default to utf-8 if confidence is low
        if result['confidence'] < 0.7:
            return 'utf-8'
        return result["encoding"]
    except Exception:
        return 'utf-8'


def detect_delimiter(file_path: str, encoding: str = 'utf-8') -> str:
    """Detect CSV delimiter with better fallbacks."""
    try:
        with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
            sample = f.read(2048)

        # Try Sniffer first
        try:
            delimiter = csv.Sniffer().sniff(sample).delimiter
            if delimiter:
                return delimiter
        except:
            pass

        # Common delimiters to check
        delimiters = [',', ';', '\t', '|', ':', ' ']

        # Count occurrences of each delimiter
        delimiter_counts = {delim: sample.count(delim) for delim in delimiters}

        # Return delimiter with highest count, default to comma
        best_delimiter = max(delimiter_counts.items(), key=lambda x: x[1])[0]

        # If best delimiter has no occurrences, use comma
        if delimiter_counts[best_delimiter] == 0:
            return ','

        return best_delimiter
    except Exception:
        return ','


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize column names to be database-friendly."""
    if df is None or df.empty:
        return df

    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.replace(r"\s+", "_", regex=True)  # Replace spaces with underscore
        .str.replace(r"[^\w_]", "", regex=True)  # Keep underscores
        .str.lower()
    )

    # Handle duplicate column names
    cols = pd.Series(df.columns)
    for dup in cols[cols.duplicated()].unique():
        cols[cols == dup] = [f"{dup}_{i}" if i != 0 else dup
                             for i in range(sum(cols == dup))]

    df.columns = cols
    return df


def detect_file_type(file_path: str, provided_type: Optional[str] = None) -> str:
    """Detect file type from extension or content."""
    if provided_type and provided_type.lower() in ['csv', 'excel', 'parquet', 'json', 'sql']:
        return provided_type.lower()

    ext = Path(file_path).suffix.lower()

    file_type_mapping = {
        '.csv': 'csv',
        '.tsv': 'csv',
        '.txt': 'csv',
        '.dat': 'csv',  # Add .dat support
        '.xlsx': 'excel',
        '.xls': 'excel',
        '.xlsm': 'excel',
        '.parquet': 'parquet',
        '.pq': 'parquet',
        '.json': 'json',
        '.jsonl': 'json',
        '.feather': 'feather',
        '.ftr': 'feather',
        '.pkl': 'pickle',
        '.pickle': 'pickle',
        '.h5': 'hdf5',
        '.hdf5': 'hdf5',
    }

    if ext in file_type_mapping:
        return file_type_mapping[ext]

    # Try to infer from content for ambiguous extensions
    if ext in ['.txt', '.dat']:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                first_line = f.readline()
                # Check if it looks like CSV/TSV
                if ',' in first_line or '\t' in first_line or ';' in first_line:
                    return 'csv'
        except:
            pass

    raise ValueError(f"Unsupported file type: {ext}. Provide file_type parameter.")


def load_sql_data(sql_query: str, sql_conn_str: str, **kwargs) -> Tuple[pd.DataFrame, Dict]:
    """Load data from SQL database."""
    try:
        engine = sqlalchemy.create_engine(sql_conn_str)
        df = pd.read_sql(sql_query, engine, **kwargs)
        engine.dispose()
        return df, {}
    except Exception as e:
        raise ValueError(f"SQL loading failed: {str(e)}")


def load_csv_data(file_path: str, **kwargs) -> Tuple[pd.DataFrame, Dict]:
    """Load CSV data with auto-detection."""
    encoding = kwargs.get('encoding') or detect_encoding(file_path)
    delimiter = kwargs.get('delimiter') or detect_delimiter(file_path, encoding)

    read_kwargs = {
        'encoding': encoding,
        'sep': delimiter,
        'on_bad_lines': 'skip' if pd.__version__ >= '1.3.0' else 'error',
        'low_memory': False,
    }

    # Update with any additional kwargs
    read_kwargs.update({k: v for k, v in kwargs.items()
                        if k not in ['encoding', 'delimiter']})

    try:
        df = pd.read_csv(file_path, **read_kwargs)
        return df, {'encoding': encoding, 'delimiter': delimiter}
    except Exception as e:
        # Try with different parameters
        try:
            df = pd.read_csv(file_path, encoding='latin-1', sep=None, engine='python')
            return df, {'encoding': 'latin-1', 'delimiter': 'auto'}
        except:
            raise ValueError(f"Failed to load CSV: {str(e)}")


def load_excel_data(file_path: str, **kwargs) -> pd.DataFrame:
    """Load Excel data."""
    sheet_name = kwargs.get('sheet_name', 0)
    return pd.read_excel(file_path, sheet_name=sheet_name, **kwargs)


def load_parquet_data(file_path: str, **kwargs) -> pd.DataFrame:
    """Load Parquet data."""
    return pd.read_parquet(file_path, **kwargs)


def load_json_data(file_path: str, **kwargs) -> pd.DataFrame:
    """Load JSON data."""
    # Try to auto-detect JSON format
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            first_char = f.read(1)
            f.seek(0)

        if first_char == '[':
            return pd.read_json(file_path, **kwargs)
        else:
            # JSON Lines format
            return pd.read_json(file_path, lines=True, **kwargs)
    except:
        return pd.read_json(file_path, **kwargs)


def load_data(
        source: Optional[str] = None,
        file_type: Optional[str] = None,
        sql_query: Optional[str] = None,
        sql_conn_str: Optional[str] = None,
        **kwargs
) -> Tuple[Optional[pd.DataFrame], Dict[str, Any]]:
    """
    Enhanced data ingestion function supporting multiple formats.

    Parameters:
    -----------
    source : str, optional
        File path for file-based sources
    file_type : str, optional
        Type of file (csv, excel, parquet, json, etc.)
    sql_query : str, optional
        SQL query for database sources
    sql_conn_str : str, optional
        Database connection string
    **kwargs : additional arguments passed to the specific loader

    Returns:
    --------
    tuple : (DataFrame, report_dict)
    """

    report = {
        "status": None,
        "source_type": None,
        "source": source,
        "file_type": file_type,
        "info": {},
        "errors": None,
        "metadata": {}
    }

    df = None

    try:
        # 1) SQL DATABASE LOADING
        # ------------------------------------------------------------------
        if sql_query is not None:
            if sql_conn_str is None:
                raise ValueError("SQL loading requires sql_conn_str.")

            report["source_type"] = "sql"
            df, sql_metadata = load_sql_data(sql_query, sql_conn_str, **kwargs)
            report["metadata"].update(sql_metadata)

        # 2) FILE-BASED LOADING
        # ------------------------------------------------------------------
        elif source is not None:
            if not os.path.exists(source):
                raise FileNotFoundError(f"File not found: {source}")

            report["source_type"] = "file"
            file_type = detect_file_type(source, file_type)
            report["file_type"] = file_type

            # Load based on file type
            if file_type == "csv":
                df, csv_metadata = load_csv_data(source, **kwargs)
                report["metadata"].update(csv_metadata)

            elif file_type == "excel":
                df = load_excel_data(source, **kwargs)

            elif file_type == "parquet":
                df = load_parquet_data(source, **kwargs)

            elif file_type == "json":
                df = load_json_data(source, **kwargs)

            elif file_type == "feather":
                df = pd.read_feather(source, **kwargs)

            elif file_type == "pickle":
                df = pd.read_pickle(source, **kwargs)

            elif file_type == "hdf5":
                df = pd.read_hdf(source, **kwargs)

            else:
                raise ValueError(f"Unsupported file type: {file_type}")

        else:
            raise ValueError("Either source or sql_query must be provided.")

        # 3) POST-PROCESSING
        # ------------------------------------------------------------------
        if df is None or df.empty:
            raise ValueError("Loaded data is empty")

        # Normalize column names
        df = normalize_columns(df)

        # Reset index if it's a RangeIndex starting at 0
        if isinstance(df.index, pd.RangeIndex) and df.index[0] == 0:
            df = df.reset_index(drop=True)

        # 4) BUILD COMPREHENSIVE REPORT
        # ------------------------------------------------------------------
        numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(
            include=["object", "string", "category", "bool"]
        ).columns.tolist()
        datetime_cols = df.select_dtypes(
            include=["datetime64", "timedelta64"]
        ).columns.tolist()

        report["status"] = "success"
        report["info"] = {
            "rows": df.shape[0],
            "columns": df.shape[1],
            "column_names": df.columns.tolist(),
            "numerical_columns": numerical_cols,
            "categorical_columns": categorical_cols,
            "datetime_columns": datetime_cols,
            "column_types": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "memory_usage_mb": round(df.memory_usage(deep=True).sum() / (1024 ** 2), 3),
            "missing_values": int(df.isnull().sum().sum()),
            "missing_percentage": round(df.isnull().sum().sum() / (df.shape[0] * df.shape[1]) * 100, 2)
            if df.shape[0] * df.shape[1] > 0 else 0,
        }

        # Add file size for file-based sources
        if source and os.path.exists(source):
            report["info"]["file_size_mb"] = round(os.path.getsize(source) / (1024 ** 2), 3)

        # Add sample data preview
        report["info"]["sample_data"] = df.head(5).to_dict('records')

        return df, report

    except Exception as e:
        report["status"] = "error"
        report["errors"] = str(e)
        return None, report


