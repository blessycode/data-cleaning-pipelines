import os
import pandas as pd
import sqlalchemy
import chardet
import csv

def detect_encoding(file_path, sample_size=50000):
    """Automatically detects encoding for CSV files."""
    with open(file_path, "rb") as f:
        raw_data = f.read(sample_size)
    result = chardet.detect(raw_data)
    return result["encoding"]


def detect_delimiter(file_path):
    """Smart CSV delimiter detection."""
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        sample = f.read(2048)
    try:
        sniffer = csv.Sniffer()
        dialect = sniffer.sniff(sample)
        return dialect.delimiter
    except Exception:
        return ','   # fallback


def normalize_columns(df):
    """Clean up column names for consistency."""
    df.columns = (
        df.columns
        .str.strip()
        .str.replace(" ", "_")
        .str.replace(r"[^\w]", "", regex=True)
        .str.lower()
    )
    return df


def load_data(source, file_type=None, sheet_name=None, sql_query=None, sql_conn_str=None):
    """
    Enhanced ingestion pipeline:
    - Auto-detects file type when missing
    - Handles CSV, Excel, SQL
    - Detects encoding and delimiter
    - Produces detailed ingestion report
    """

    report = {
        "status": None,
        "source": source,
        "file_type": file_type,
        "info": {},
        "errors": None
    }

    try:
        # -------------------------
        # AUTO-DETECT FILE TYPE
        # -------------------------
        if file_type is None:
            extension = os.path.splitext(source)[1].lower()
            if extension in ['.csv']:
                file_type = 'csv'
            elif extension in ['.xls', '.xlsx']:
                file_type = 'excel'
            else:
                raise ValueError("Unable to auto-detect file type. Provide file_type manually.")

        # -------------------------
        # FILE EXISTENCE CHECK
        # -------------------------
        if file_type != "sql" and not os.path.exists(source):
            raise FileNotFoundError(f"File not found: {source}")

        # -------------------------
        # LOAD CSV
        # -------------------------
        if file_type == 'csv':
            encoding = detect_encoding(source)
            delimiter = detect_delimiter(source)
            df = pd.read_csv(source, encoding=encoding, delimiter=delimiter)

        # -------------------------
        # LOAD EXCEL
        # -------------------------
        elif file_type == 'excel':
            df = pd.read_excel(source, sheet_name=sheet_name)

        # -------------------------
        # LOAD SQL
        # -------------------------
        elif file_type == 'sql':
            if sql_query is None or sql_conn_str is None:
                raise ValueError("SQL ingestion requires sql_query and sql_conn_str.")
            engine = sqlalchemy.create_engine(sql_conn_str)
            df = pd.read_sql(sql_query, engine)

        else:
            raise ValueError("Unsupported file_type. Use csv, excel or sql.")

        # -------------------------
        # NORMALIZE COLUMNS
        # -------------------------
        df = normalize_columns(df)

        # -------------------------
        # INGESTION REPORT
        # -------------------------
        report["status"] = "success"
        report["info"] = {
            "rows": df.shape[0],
            "columns": df.shape[1],
            "column_names": df.columns.tolist(),
            "column_types": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "memory_usage_mb": round(df.memory_usage().sum() / (1024**2), 3),
            "file_size_mb": round(os.path.getsize(source) / (1024**2), 3)
                if file_type in ["csv", "excel"] else None
        }

        return df, report

    except Exception as e:
        report["status"] = "error"
        report["errors"] = str(e)
        return None, report
