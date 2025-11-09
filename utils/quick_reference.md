# Utils Modules Quick Reference

## io.py - File Operations

```python
from utils.io import (
    save_dataframe_to_csv,
    load_csv_data,
    save_multiple_stocks_to_excel,
    get_data_file_info
)

# Save single dataset
filepath = save_dataframe_to_csv(df, 'AAPL', '1y', 
                                 output_dir='../data/raw')

# Load dataset
df = load_csv_data(filepath)

# Save multiple stocks to Excel
stocks_dict = {'AAPL': df1, 'MSFT': df2}
excel_path = save_multiple_stocks_to_excel(
    stocks_dict, 
    'portfolio.xlsx'
)

# Get file info
info = get_data_file_info('./data/raw/AAPL_1y.csv')
print(f"Rows: {info['rows']}, Size: {info['size_mb']} MB")
```

---

## logging.py - Logging Operations

```python
from utils.logging import DownloadLogger

logger = DownloadLogger()

# Log different message types
logger.info("Processing started")           # ✓ Green
logger.success("Task completed")             # ✓ Green
logger.warning("Check this")                 # ⚠ Yellow
logger.error("Something went wrong")         # ✗ Red
logger.debug("Debugging info")               # ⚙ Cyan

# Special methods for downloads
logger.log_download_start('AAPL', 'max', '1d')
logger.log_download_complete('AAPL', 2000, './data/AAPL.csv')
logger.log_download_error('AAPL', 'Network timeout')
logger.log_data_stats('AAPL', 2000, ['Open', 'Close', 'Volume'])

# Visual separator
logger.separator()  # Prints: --------------------------------------------------
```

---

## seeding.py - Reproducibility

```python
from utils.seeding import (
    set_random_seed,
    configure_environment,
    SeedManager,
    get_reproducible_config
)

# Simple seed setting (recommended)
set_random_seed(42)

# Full environment setup with verbosity
config = configure_environment(
    seed=42,
    gpu_memory_fraction=0.5,
    verbose=True
)

# Using SeedManager for multiple experiments
seed_mgr = SeedManager()
seed_mgr.set_seed(42)

exp1_seed = seed_mgr.create_experiment_seed('experiment_1')
exp2_seed = seed_mgr.create_experiment_seed('experiment_2')

# Get reproducibility config
repro_config = get_reproducible_config()
```

---

## download_data.py - Download Operations

### Quick Usage (Functions)

```python
from download_data import download_stock_data, download_multiple_stocks

# Single stock
df = download_stock_data('AAPL', period='1y', interval='1d')

# Multiple stocks
tickers = ['^GSPC', '^VIX']
results = download_multiple_stocks(
    tickers,
    period='max',
    save_combined_excel=True
)
```

### Advanced Usage (Class)

```python
from download_data import StockDataDownloader

downloader = StockDataDownloader(
    output_dir='./data/raw',
    use_logging=True
)

# Single download
df = downloader.download_single_stock(
    'AAPL',
    period='1y',
    interval='1d',
    filename='apple_stock.csv'
)

# Batch download
results = downloader.download_multiple_stocks(
    ['^GSPC', '^VIX', '^IXIC'],
    period='5y',
    interval='1d',
    save_combined_excel=True
)
```

---

## Complete Minimal Example

```python
"""Minimal working example with all utilities"""

from utils.seeding import set_random_seed
from utils.logging import DownloadLogger
from utils.io import save_dataframe_to_csv, load_csv_data
from download_data import download_stock_data

# 1. Set seed for reproducibility
set_random_seed(42)

# 2. Create logger
logger = DownloadLogger()

# 3. Download data
logger.info("Starting data download...")
df = download_stock_data('AAPL', period='1y')

if df is not None:
    logger.success(f"Downloaded {len(df)} rows")
else:
    logger.error("Download failed")

logger.separator()
```

---

## Common Patterns

### Pattern 1: Download and Analyze

```python
from download_data import StockDataDownloader
from utils.io import load_csv_data
from utils.logging import DownloadLogger

logger = DownloadLogger()
downloader = StockDataDownloader()

# Download
df = downloader.download_single_stock('^VIX', period='max')

# Analyze
if df is not None:
    logger.info(f"Volatility stats for VIX:")
    logger.debug(f"Mean: {df['Close'].mean():.2f}")
    logger.debug(f"Std: {df['Close'].std():.2f}")
```

### Pattern 2: Multi-stock Processing

```python
from download_data import download_multiple_stocks
from utils.io import get_data_file_info

tickers = ['^GSPC', '^VIX', '^DJI']
results = download_multiple_stocks(tickers, period='5y')

for ticker, df in results.items():
    print(f"{ticker}: {len(df)} rows, {df['Close'].std():.2f} volatility")
```

### Pattern 3: Export to Excel

```python
from download_data import StockDataDownloader
from utils.io import save_multiple_stocks_to_excel

downloader = StockDataDownloader()
results = downloader.download_multiple_stocks(
    ['^GSPC', '^VIX'],
    period='1y'
)

# Already saved as Excel during download
# Or manually save later:
save_multiple_stocks_to_excel(results, 'volatility_data.xlsx')
```

---

## Parameter Reference

### Yfinance Periods
- `1d` - 1 day
- `5d` - 5 days
- `1mo` - 1 month
- `3mo` - 3 months
- `6mo` - 6 months
- `1y` - 1 year
- `2y` - 2 years
- `5y` - 5 years
- `10y` - 10 years
- `ytd` - Year to date
- `max` - Maximum available

### Yfinance Intervals
- `1m` - 1 minute
- `5m` - 5 minutes
- `15m` - 15 minutes
- `30m` - 30 minutes
- `60m` - 60 minutes (1 hour)
- `1h` - 1 hour
- `1d` - 1 day
- `1wk` - 1 week
- `1mo` - 1 month
- `3mo` - 3 months

---

## Troubleshooting

**Issue: No data found**
```python
# Try with different period/interval
df = download_stock_data('AAPL', period='max', interval='1d')
```

**Issue: Logs not appearing**
```python
# Enable file logging
logger = DownloadLogger()
# Check ../logs/ directory for log files
```

**Issue: File not found**
```python
# Check output directory
from utils.io import get_data_file_info
info = get_data_file_info('./data/raw/AAPL_1y.csv')
```

**Issue: Memory error with large downloads**
```python
# Download in smaller batches
for ticker in tickers:
    df = download_stock_data(ticker, period='1y')  # Smaller period
```
