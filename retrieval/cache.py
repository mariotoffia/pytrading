import os
import sqlite3
import tempfile
import yfinance as yf
import pandas as pd


def get_cache_sql_db(ticker: str, interval: str, cache_dir: str = "${TMP}/cache") -> str:
    """
    Returns the path to the SQLite database for the given ticker and interval.
    If the path does not exist, it will be created.

    NOTE: The database file itself is not created until the first time cache_ticker is called.
    """
    if "${TMP}" in cache_dir:
        cache_dir = cache_dir.replace("${TMP}", tempfile.gettempdir())

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
    db_file = get_cache_sql_db(ticker, interval,cache_dir)

    return os.path.exists(db_file)

def cache_ticker(
        ticker: str, 
        interval: str, 
        start: str, 
        end: str, 
        cache_dir: str = "${TMP}/cache",
        clear: bool = False):
    """
    Downloads ticker data from Yahoo Finance and caches it in a SQLite database.

    Sample Usage: cache_ticker("AAPL", "1d", "2020-01-01", "2020-12-31")

    When clear is set to True, the database will be deleted before downloading the data.
    """

    # Download ticker data
    ticker_data = yf.download(tickers=[ticker], start=start, end=end, interval=interval)

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
                            "Close" REAL, "Adj Close" REAL, "Volume" INTEGER)''')

        # Prepare data for insertion
        records = ticker_data.reset_index().to_records(index=False)
        
        # Date Open High Low Close "Adj Close" Volume
        data_to_insert = [(str(r[0]), float(r[1]), float(r[2]), float(r[3]),
                           float(r[4]), float(r[5]), int(r[6])) for r in records]

        # Perform batch upsert
        conn.executemany('''INSERT OR REPLACE INTO ticker_data 
                        ("Date", "Open", "High", "Low", "Close", "Adj Close", "Volume")
                        VALUES (?, ?, ?, ?, ?, ?, ?)''', data_to_insert)

def load_ticker(
        ticker: str, 
        interval: str, 
        start: str, 
        end: str, 
        cache_dir: str = "${TMP}/cache", 
        index_column:str = "", 
        strip_date_time_fractions: bool = True) -> pd.DataFrame:
    """
    Loads ticker data from the SQLite database.
    If the data is not in the database, it raises a ValueError.
    
    If the index_column is specified, it will be used as the index of the DataFrame.
    If strip_date_time_fractions is True, the time portion of the index will be stripped
    of their fraction of seconds.
    """

    # Database file path
    db_file = get_cache_sql_db(ticker, interval, cache_dir)

    # Connect to the SQLite database
    with sqlite3.connect(db_file) as conn:
        # Load data from database
        df = pd.read_sql_query(f"SELECT * FROM ticker_data WHERE Date BETWEEN '{start}' AND '{end}'", conn)

        # Strip date time fractions
        if strip_date_time_fractions:
            df['Date'] = df['Date'].astype(str).str[:19]

        # Make sure that the date time is a pd.DateTimeIndex
        # (but only if we set the 'Date' as index, otherwise just a indication)
        df['Date'] = pd.to_datetime(df['Date'])

        # Set index to specific column
        if index_column:
            df.set_index(index_column, inplace=True)
        else:
            df.set_index('Date', inplace=True)

    return df
