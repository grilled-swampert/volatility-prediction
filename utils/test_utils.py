"""
Test script to verify all utility modules work correctly.
Run this after setting up the utils folder to ensure everything is configured properly.

Usage:
    python test_utils.py
"""

import os
import sys
import pandas as pd

# Test counters
tests_passed = 0
tests_failed = 0


def test_section(section_name: str) -> None:
    """Print a test section header."""
    print(f"\n{'='*60}")
    print(f"  Testing: {section_name}")
    print(f"{'='*60}")


def test_passed(test_name: str) -> None:
    """Mark test as passed."""
    global tests_passed
    tests_passed += 1
    print(f"✓ PASS: {test_name}")


def test_failed(test_name: str, error: str) -> None:
    """Mark test as failed."""
    global tests_failed
    tests_failed += 1
    print(f"✗ FAIL: {test_name}")
    print(f"  Error: {error}")


def test_io_module():
    """Test utils.io module."""
    test_section("I/O Module (io.py)")
    
    try:
        from utils.io import (
            create_output_directory,
            generate_filename,
            save_dataframe_to_csv,
            load_csv_data,
            get_data_file_info,
        )
        test_passed("Import io module functions")
    except ImportError as e:
        test_failed("Import io module", str(e))
        return
    
    try:
        # Test directory creation
        test_dir = create_output_directory("./test_data")
        assert os.path.exists(test_dir)
        test_passed("Create output directory")
    except Exception as e:
        test_failed("Create output directory", str(e))
    
    try:
        # Test filename generation
        filename = generate_filename("AAPL", "1y")
        assert filename.endswith(".csv")
        assert "AAPL" in filename
        test_passed("Generate filename")
    except Exception as e:
        test_failed("Generate filename", str(e))
    
    try:
        # Test CSV save/load
        test_df = pd.DataFrame({
            'Date': pd.date_range('2024-01-01', periods=5),
            'Open': [100.0, 101.0, 102.0, 103.0, 104.0],
            'Close': [101.0, 102.0, 103.0, 104.0, 105.0],
        })
        test_df.set_index('Date', inplace=True)
        
        filepath = save_dataframe_to_csv(
            test_df, 'TEST', '1mo',
            output_dir='./test_data'
        )
        assert os.path.exists(filepath)
        test_passed("Save DataFrame to CSV")
        
        # Load back
        loaded_df = load_csv_data(filepath)
        assert len(loaded_df) == 5
        test_passed("Load CSV data")
        
        # Get file info
        info = get_data_file_info(filepath)
        assert info['rows'] == 5
        test_passed("Get data file info")
        
    except Exception as e:
        test_failed("CSV operations", str(e))
    
    # Cleanup
    try:
        import shutil
        if os.path.exists("./test_data"):
            shutil.rmtree("./test_data")
    except:
        pass


def test_logging_module():
    """Test utils.logging module."""
    test_section("Logging Module (logger.py)")
    
    try:
        from utils.logger import DataLogger, DownloadLogger, setup_logging
        test_passed("Import logging module")
    except ImportError as e:
        test_failed("Import logging module", str(e))
        return
    
    try:
        logger = DataLogger()
        logger.info("Test message")
        logger.success("Success message")
        test_passed("Create DataLogger instance")
    except Exception as e:
        test_failed("Create DataLogger", str(e))
    
    try:
        download_logger = DownloadLogger()
        download_logger.log_download_start('TEST', 'max', '1d')
        test_passed("Use DownloadLogger methods")
    except Exception as e:
        test_failed("Use DownloadLogger", str(e))
    
    # Cleanup logs
    try:
        import shutil
        if os.path.exists("./logs"):
            shutil.rmtree("./logs")
    except:
        pass


def test_seeding_module():
    """Test utils.seeding module."""
    test_section("Seeding Module (seeding.py)")
    
    try:
        from utils.seeding import (
            set_random_seed,
            configure_environment,
            SeedManager,
            get_reproducible_config,
        )
        test_passed("Import seeding module functions")
    except ImportError as e:
        test_failed("Import seeding module", str(e))
        return
    
    try:
        set_random_seed(42)
        test_passed("Set random seed")
    except Exception as e:
        test_failed("Set random seed", str(e))
    
    try:
        config = configure_environment(seed=42, verbose=False)
        assert 'seed' in config
        test_passed("Configure environment")
    except Exception as e:
        test_failed("Configure environment", str(e))
    
    try:
        seed_mgr = SeedManager()
        seed_mgr.set_seed(42)
        current_seed = seed_mgr.get_seed()
        assert current_seed == 42
        test_passed("Use SeedManager")
    except Exception as e:
        test_failed("Use SeedManager", str(e))
    
    try:
        repro_config = get_reproducible_config()
        assert 'seed' in repro_config
        test_passed("Get reproducible config")
    except Exception as e:
        test_failed("Get reproducible config", str(e))


def test_download_module():
    """Test download_data module."""
    test_section("Download Module (download_data.py)")
    
    try:
        from download_data import (
            StockDataDownloader,
            download_stock_data,
            download_multiple_stocks,
        )
        test_passed("Import download module")
    except ImportError as e:
        test_failed("Import download module", str(e))
        return
    
    try:
        downloader = StockDataDownloader(use_logging=False)
        test_passed("Create StockDataDownloader instance")
    except Exception as e:
        test_failed("Create downloader instance", str(e))


def test_utils_package():
    """Test utils package __init__.py."""
    test_section("Utils Package (__init__.py)")
    
    try:
        import utils
        test_passed("Import utils package")
    except ImportError as e:
        test_failed("Import utils package", str(e))
        return
    
    try:
        # Test that exports are available
        from utils import (
            set_random_seed,
            DataLogger,
            save_dataframe_to_csv,
        )
        test_passed("Import from utils package")
    except ImportError as e:
        test_failed("Import from utils package", str(e))


def test_project_structure():
    """Test project structure."""
    test_section("Project Structure")
    
    required_files = [
        './utils/__init__.py',
        './utils/io.py',
        './utils/logger.py',
        './utils/seeding.py',
        './download_data.py',
    ]
    
    for filepath in required_files:
        if os.path.exists(filepath):
            test_passed(f"Found {filepath}")
        else:
            test_failed(f"Missing {filepath}", "File not found")


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("  Volatility Prediction Utils - Test Suite")
    print("="*60)
    
    test_project_structure()
    test_utils_package()
    test_io_module()
    test_logging_module()
    test_seeding_module()
    test_download_module()
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"  Test Summary")
    print(f"{'='*60}")
    print(f"✓ PASSED: {tests_passed}")
    print(f"✗ FAILED: {tests_failed}")
    total = tests_passed + tests_failed
    percentage = (tests_passed / total * 100) if total > 0 else 0
    print(f"Success Rate: {percentage:.1f}%")
    print("="*60 + "\n")
    
    return 0 if tests_failed == 0 else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
