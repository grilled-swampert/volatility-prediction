"""
Stock data downloader using Yahoo Finance.
Refactored to use modular utility functions.

Usage:
    python download_data.py
    
    # Or programmatically:
    from download_data import download_stock_data, download_multiple_stocks
    df = download_stock_data('AAPL', period='1y')
"""

import yfinance as yf
import pandas as pd
from typing import List, Optional, Dict
from utils.io import save_dataframe_to_csv
from utils.logger import DownloadLogger
from utils.seeding import set_random_seed


class StockDataDownloader:
    """
    Main class for downloading and saving stock data from Yahoo Finance.
    """
    
    def __init__(self, output_dir: str = "./data/raw", use_logging: bool = True):
        """
        Initialize the stock data downloader.
        
        Parameters:
        -----------
        output_dir : str, default="./data/raw"
            Directory to save downloaded data
        use_logging : bool, default=True
            Whether to use logging for operations
        """
        self.output_dir = output_dir
        self.logger = DownloadLogger() if use_logging else None
    
    def download_single_stock(self,
                            ticker: str,
                            period: str = "1y",
                            interval: str = "1d",
                            filename: Optional[str] = None) -> Optional[pd.DataFrame]:
        """
        Download stock data for a single ticker and save to CSV.
        
        Parameters:
        -----------
        ticker : str
            Stock ticker symbol (e.g., 'AAPL', '^VIX')
        period : str, default="1y"
            Data period - valid values: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
        interval : str, default="1d"
            Data interval - valid values: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
        filename : str, optional
            Custom output filename. Auto-generated if not provided
        
        Returns:
        --------
        pd.DataFrame or None
            Downloaded stock data, or None if download failed
        """
        try:
            if self.logger:
                self.logger.log_download_start(ticker, period, interval)
            
            # Download data using yfinance
            stock = yf.Ticker(ticker)
            df = stock.history(period=period, interval=interval)
            
            if df.empty:
                if self.logger:
                    self.logger.warning(f"No data found for {ticker}")
                return None
            
            # Save to CSV
            filepath = save_dataframe_to_csv(
                df, ticker, period,
                output_dir=self.output_dir,
                filename=filename
            )
            
            if self.logger:
                self.logger.log_download_complete(ticker, len(df), filepath)
                self.logger.log_data_stats(ticker, len(df), list(df.columns))
            
            return df
        
        except Exception as e:
            if self.logger:
                self.logger.log_download_error(ticker, str(e))
            else:
                print(f"Error downloading {ticker}: {e}")
            return None
    
    def download_multiple_stocks(self,
                               tickers: List[str],
                               period: str = "1y",
                               interval: str = "1d",
                               save_individual: bool = True,
                               save_combined_excel: bool = False) -> Dict[str, pd.DataFrame]:
        """
        Download data for multiple stocks.
        
        Parameters:
        -----------
        tickers : list
            List of stock ticker symbols
        period : str, default="1y"
            Data period
        interval : str, default="1d"
            Data interval
        save_individual : bool, default=True
            Save each stock in individual CSV files
        save_combined_excel : bool, default=False
            Save all stocks in a single Excel file with multiple sheets
        
        Returns:
        --------
        dict
            Dictionary with ticker symbols as keys and DataFrames as values
        """
        results = {}
        
        for ticker in tickers:
            df = self.download_single_stock(ticker, period, interval)
            if df is not None:
                results[ticker] = df
            
            if self.logger:
                self.logger.separator()
        
        # Save combined Excel if requested
        if save_combined_excel and results:
            try:
                from utils.io import save_multiple_stocks_to_excel
                filename = f"combined_stocks_{period}.xlsx"
                excel_path = save_multiple_stocks_to_excel(
                    results, filename, self.output_dir
                )
                if self.logger:
                    self.logger.success(f"Combined Excel saved to {excel_path}")
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Failed to save combined Excel: {e}")
        
        return results


def download_stock_data(ticker: str,
                       period: str = "1y",
                       interval: str = "1d",
                       filename: Optional[str] = None,
                       output_dir: str = "./data/raw") -> Optional[pd.DataFrame]:
    """
    Convenience function to download a single stock.
    
    Parameters:
    -----------
    ticker : str
        Stock ticker symbol
    period : str, default="1y"
        Data period
    interval : str, default="1d"
        Data interval
    filename : str, optional
        Custom filename
    output_dir : str, default="./data/raw"
        Output directory
    
    Returns:
    --------
    pd.DataFrame or None
        Downloaded data or None
    """
    downloader = StockDataDownloader(output_dir=output_dir)
    return downloader.download_single_stock(ticker, period, interval, filename)


def download_multiple_stocks(tickers: List[str],
                           period: str = "1y",
                           interval: str = "1d",
                           output_dir: str = "./data/raw",
                           save_combined_excel: bool = False) -> Dict[str, pd.DataFrame]:
    """
    Convenience function to download multiple stocks.
    
    Parameters:
    -----------
    tickers : list
        List of ticker symbols
    period : str, default="1y"
        Data period
    interval : str, default="1d"
        Data interval
    output_dir : str, default="./data/raw"
        Output directory
    save_combined_excel : bool, default=False
        Save combined Excel file
    
    Returns:
    --------
    dict
        Dictionary of downloaded DataFrames
    """
    downloader = StockDataDownloader(output_dir=output_dir)
    return downloader.download_multiple_stocks(
        tickers, period, interval,
        save_combined_excel=save_combined_excel
    )


if __name__ == "__main__":
    # Set seed for reproducibility
    set_random_seed(42)
    
    # Volatility research tickers
    volatility_tickers = [
        "^GSPC",  # S&P 500
        "^VIX",   # CBOE Volatility Index
        "^IXIC",  # NASDAQ
        "^DJI"    # Dow Jones
    ]
    
    print("=" * 50)
    print("Stock Data Downloader - Volatility Research")
    print("=" * 50)
    print()
    
    # Download volatility data with maximum available history
    print("Downloading volatility research data (max history)...\n")
    downloader = StockDataDownloader()
    results = downloader.download_multiple_stocks(
        volatility_tickers,
        period="max",
        interval="1d",
        save_combined_excel=True
    )
    
    print("\n" + "=" * 50)
    print("Download Summary")
    print("=" * 50)
    print(f"Successfully downloaded: {len(results)} out of {len(volatility_tickers)} tickers")
    
    # Alternative examples (commented out):
    # Download specific period with different interval
    # downloader.download_multiple_stocks(
    #     volatility_tickers,
    #     period="5y",
    #     interval="1d"
    # )
    
    # Download hourly data for recent period
    # downloader.download_multiple_stocks(
    #     volatility_tickers,
    #     period="1mo",
    #     interval="1h"
    # )
