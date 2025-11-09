"""
Input/Output utilities for downloading and saving financial data.
Handles file operations, directory management, and data persistence.
"""

import os
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Optional


def create_output_directory(output_dir: str = "../data/raw") -> str:
    """
    Create output directory if it doesn't exist.

    Parameters:
    -----------
    output_dir : str, default="../data/raw"
        Path to the output directory

    Returns:
    --------
    str
        Absolute path to the created directory
    """
    os.makedirs(output_dir, exist_ok=True)
    return os.path.abspath(output_dir)


def generate_filename(ticker: str, period: str,
                      custom_filename: Optional[str] = None) -> str:
    """
    Generate a filename for the downloaded stock data.

    Parameters:
    -----------
    ticker : str
        Stock ticker symbol
    period : str
        Data period (e.g., '1y', '5y', 'max')
    custom_filename : str, optional
        Custom filename. If provided, this is returned as-is

    Returns:
    --------
    str
        Generated or custom filename with .csv extension
    """
    if custom_filename is not None:
        return custom_filename if custom_filename.endswith('.csv') else f"{custom_filename}.csv"

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{ticker}_{period}_{timestamp}.csv"


def save_dataframe_to_csv(df: pd.DataFrame,
                          ticker: str,
                          period: str,
                          output_dir: str = "../data/raw",
                          filename: Optional[str] = None,
                          float_format: str = '%.6f',
                          date_format: str = '%Y-%m-%d %H:%M:%S') -> str:
    """
    Save DataFrame to CSV file with proper formatting.

    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame to save (typically stock OHLCV data)
    ticker : str
        Stock ticker symbol
    period : str
        Data period
    output_dir : str, default="../data/raw"
        Output directory path
    filename : str, optional
        Custom filename. Auto-generated if not provided
    float_format : str, default='%.6f'
        Float precision for price data
    date_format : str, default='%Y-%m-%d %H:%M:%S'
        Date format for index

    Returns:
    --------
    str
        Full filepath where data was saved
    """
    # Create directory
    output_path = create_output_directory(output_dir)

    # Generate filename
    csv_filename = generate_filename(ticker, period, filename)

    # Create full filepath
    filepath = os.path.join(output_path, csv_filename)

    # Reset index to make DateTime a column if it's in the index
    df_to_save = df.copy()
    if df_to_save.index.name:  # If index has a name (usually 'Date')
        df_to_save.reset_index(inplace=True)

    # Save with formatting options
    df_to_save.to_csv(filepath,
                      index=False,
                      float_format=float_format,
                      date_format=date_format)

    return filepath


def save_dataframe_to_excel(df: pd.DataFrame,
                            filepath: str,
                            sheet_name: str = "Sheet1",
                            include_index: bool = True) -> None:
    """
    Save DataFrame to Excel file.

    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame to save
    filepath : str
        Output Excel file path
    sheet_name : str, default="Sheet1"
        Excel sheet name
    include_index : bool, default=True
        Whether to include the index in the Excel file
    """
    os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
    df.to_excel(filepath, sheet_name=sheet_name, index=include_index)


def save_multiple_stocks_to_excel(stocks_dict: dict,
                                  output_filepath: str,
                                  output_dir: str = "../data/raw") -> str:
    """
    Save multiple stock DataFrames to different sheets in one Excel file.

    Parameters:
    -----------
    stocks_dict : dict
        Dictionary with ticker symbols as keys and DataFrames as values
        Example: {'AAPL': df1, 'MSFT': df2}
    output_filepath : str
        Output Excel filename
    output_dir : str, default="../data/raw"
        Output directory

    Returns:
    --------
    str
        Full path to the saved Excel file
    """
    output_path = create_output_directory(output_dir)
    full_filepath = os.path.join(output_path, output_filepath)

    with pd.ExcelWriter(full_filepath, engine='openpyxl') as writer:
        for ticker, df in stocks_dict.items():
            # Reset index for Excel export
            df_copy = df.copy()

            # Remove timezone from index
            if hasattr(df_copy.index, "tz") and df_copy.index.tz is not None:
                df_copy.index = df_copy.index.tz_localize(None)

            # Remove timezone from datetime columns
            for col in df_copy.columns:
                if pd.api.types.is_datetime64tz_dtype(df_copy[col]):
                    df_copy[col] = df_copy[col].dt.tz_localize(None)

            df_copy.to_excel(writer, sheet_name=ticker, index=False)

    return full_filepath


def load_csv_data(filepath: str, parse_dates: bool = True) -> pd.DataFrame:
    """
    Load stock data from CSV file.

    Parameters:
    -----------
    filepath : str
        Path to the CSV file
    parse_dates : bool, default=True
        Whether to parse date columns

    Returns:
    --------
    pd.DataFrame
        Loaded stock data
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    return pd.read_csv(filepath, parse_dates=parse_dates if parse_dates else None)


def get_data_file_info(filepath: str) -> dict:
    """
    Get information about a downloaded data file.

    Parameters:
    -----------
    filepath : str
        Path to the data file

    Returns:
    --------
    dict
        File information (size, creation time, rows, columns)
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    df = pd.read_csv(filepath)
    file_stat = os.stat(filepath)

    return {
        'filename': os.path.basename(filepath),
        'filepath': filepath,
        'size_mb': file_stat.st_size / (1024 * 1024),
        'created': datetime.fromtimestamp(file_stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S"),
        'rows': len(df),
        'columns': len(df.columns),
        'column_names': list(df.columns)
    }