import os
import sqlite3
import tempfile
import yfinance as yf
import pandas as pd


DEFAULT_CACHE_DIR: str = "${TMP}/cache"


def get_cache_sql_db(ticker: str, interval: str, cache_dir: str = DEFAULT_CACHE_DIR) -> str:
    """
    Returns the path to the SQLite database for the given ticker and interval.
    If the path does not exist, it will be created.

    NOTE: The database file itself is not created until the first time cache_ticker is called.
    """
    if "${TMP}" in cache_dir:
        cache_dir = cache_dir.replace(DEFAULT_CACHE_DIR, tempfile.gettempdir())

    cache_path = os.path.join(cache_dir, "yf", ticker, interval)
    os.makedirs(cache_path, exist_ok=True)

    return os.path.join(cache_path, "db.sql")


def exist_sql_db(
        ticker: str,
        interval: str,
        cache_dir: str = "${TMP}/cache") -> bool:
    """
    Returns True if the ticker data exists in the cache.

    How much data is never evaluated.
    """
    db_file = get_cache_sql_db(ticker, interval, cache_dir)

    return os.path.exists(db_file)


def cache_ticker(
        ticker: str,
        interval: str,
        start: str,
        end: str,
        cache_dir: str = DEFAULT_CACHE_DIR,
        clear: bool = False):
    """
    Downloads ticker data from Yahoo Finance and caches it in a SQLite database.

    Sample Usage: cache_ticker("AAPL", "1d", "2020-01-01", "2020-12-31")

    When clear is set to True, the database will be deleted before downloading the data.
    """

    # Download ticker data
    ticker_data = yf.download(
        tickers=[ticker], start=start, end=end, interval=interval)

    # Database file path
    db_file = get_cache_sql_db(ticker, interval, cache_dir)

    # Clear database if requested
    if clear and os.path.exists(db_file):
        os.remove(db_file)

    # Connect to the SQLite database
    with sqlite3.connect(db_file) as conn:
        # Create table with datetime as primary key
        conn.execute('''CREATE TABLE IF NOT EXISTS ticker_data (
                            "Date" TEXT PRIMARY KEY,
                            "Open" REAL, "High" REAL, "Low" REAL, 
                            "Close" REAL, "Adj Close" REAL, "Volume" REAL)''')

        # Prepare data for insertion
        records = ticker_data.reset_index().to_records(index=False)
        # Get the integer indexes of the columns to be used below
        ticker_data_columns = ticker_data.columns

        # Since Date is index
        date_index = 0
        open_index = ticker_data_columns.get_loc('Open') + 1
        high_index = ticker_data_columns.get_loc('High') + 1
        low_index = ticker_data_columns.get_loc('Low') + 1
        close_index = ticker_data_columns.get_loc('Close') + 1
        adj_close_index = ticker_data_columns.get_loc('Adj Close')
        volume_index = ticker_data_columns.get_loc('Volume') + 1

        if adj_close_index != -1:
            adj_close_index += 1

        data_to_insert = []

        # Convert each row to a tuple
        for r in records:
            if adj_close_index == -1:
                data_to_insert.append((str(r[date_index]), float(r[open_index]), float(r[high_index]), float(r[low_index]),
                                       float(r[close_index]), float(r[close_index]), int(r[volume_index])))
            else:
                data_to_insert.append((str(r[date_index]), float(r[open_index]), float(r[high_index]), float(r[low_index]),
                                       float(r[close_index]), float(r[adj_close_index]), int(r[volume_index])))

        # Perform batch upsert
        conn.executemany('''INSERT OR REPLACE INTO ticker_data 
                        ("Date", "Open", "High", "Low", "Close", "Adj Close", "Volume")
                        VALUES (?, ?, ?, ?, ?, ?, ?)''', data_to_insert)


def load_ticker(
        ticker: str,
        interval: str,
        start: str,
        end: str,
        cache_dir: str = DEFAULT_CACHE_DIR,
        strip_date_time_fractions: bool = True) -> pd.DataFrame:
    """
    Loads ticker data from the SQLite database.
    If the data is not in the database, it raises a ValueError.

    If strip_date_time_fractions is True, the time portion of the index will be stripped
    of their fraction of seconds.

    :param ticker: The ticker symbol to load
    :param interval: The interval of the data to load (15m, 1h, 1d, 1wk, 1mo)
    :param start: The start date of the data to load (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)
    :param end: The end date of the data to load (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)
    :param cache_dir: The directory where the SQLite database is stored (default: ${TMP}/cache)
    :param strip_date_time_fractions: If True, the time portion of the index will be stripped
                                        of their fraction of seconds (default: True)

    :return: A pandas DataFrame containing the ticker data with `Date` as the index.

    Sample Usage: load_ticker("AAPL", "1d", "2020-01-01", "2020-12-31")
    """

    # Database file path
    db_file = get_cache_sql_db(ticker, interval, cache_dir)

    # Connect to the SQLite database
    with sqlite3.connect(db_file) as conn:
        # Load data from database
        df = pd.read_sql_query(
            f"SELECT * FROM ticker_data WHERE Date BETWEEN '{start}' AND '{end}'", conn)

        # Strip date time fractions
        if strip_date_time_fractions:
            df['Date'] = df['Date'].astype(str).str[:19]

        # Make sure that the date time is a pd.DateTimeIndex
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)

    return df
