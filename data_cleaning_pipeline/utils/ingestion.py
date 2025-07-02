import pandas as pd
import sqlalchemy

def load_data(source, file_type='csv', sheet_name=None, sql_query=None, sql_conn_str=None):
    """
    This function loads data from csv, excel and sql sources into pandas DataFrame.
    :source: str, filepath for csv and excel sources ignoring sql:
    :param file_type: csv, excel or sql.
    :param sheet_name: str/int for Excel sheet
    :param sql_query: str, sql select query (only for sql file types)
    :param sql_conn_str: str, SQLAlchemy connection string
    :return:
    df: pandas DataFrame or None on error
    reports: dictionary with loading info or error details
    """
    report = {}
    try:
        if file_type == 'csv':
            try:
                df = pd.read_csv(source, encoding='utf-8')
            except UnicodeDecodeError:
                df = pd.read_csv(source, encoding='latin-1')
        elif file_type == 'excel':
            df = pd.read_excel(source, sheet_name=sheet_name)

        elif file_type == 'sql':
            if sql_query is None or sql_conn_str is None:
                raise ValueError("sql_query and sql_conn_str are required for SQL data loading")
            engine = sqlalchemy.create_engine(sql_conn_str)
            df = pd.read_sql(sql_query, engine)

        else:
            raise ValueError("file_type must be csv, excel or sql")

        report['status'] = 'successfully loaded'
        report['rows'] = df.shape[0]
        report['columns'] = df.shape[1]
        report['columns_names'] = df.columns.tolist()
        report['columns_types'] = df.dtypes.tolist()

        return df, report

    except Exception as e:
        report['status'] = 'error'
        report['error_message'] = str(e)
        return None, report
