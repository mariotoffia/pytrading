import pandas as pd

# This is when all the back_candles for EMA Fast are below EMA Slow
EMA_FAST_BELOW_EMA_SLOW:int = 1
# This is when all the back_candles for EMA Fast are above EMA Slow
EMA_FAST_ABOVE_EMA_SLOW:int = 2
# This is when all the back_candles are neither above or below EMA Slow & Fast
NO_CONCLUSIVE_SIGNAL:int = 0

def two_above_or_below(
    df:pd.DataFrame, 
    current_candle:int, 
    back_candles:int,
    ema_fast_column:str = 'EMA Fast',
    ema_slow_column:str = 'EMA Slow'
    ) -> int:
  """"
  This function will check up to back_candles candles before the current_candle
  if all of them are EMA Fast is are above or below EMA Slow.
  
  :param df: DataFrame containing the ticker data
  :param current_candle: Current candle we're looking at
  :param back_candles: How many candles back we're looking at (used for trend analysis)

  :return: Returns a signal EMA_FAST_BELOW_EMA_SLOW, EMA_FAST_ABOVE_EMA_SLOW or NO_CONCLUSIVE_SIGNAL.
  """
  # Copy the dataframe
  dfs = df.reset_index().copy()

  # Range of candles
  start = max(0, current_candle - back_candles)
  end = current_candle
  rows = dfs.iloc[start:end]

  # Check if all EMA Fast values are below EMA Slow
  if all(rows[ema_fast_column] < rows[ema_slow_column]):
    return EMA_FAST_BELOW_EMA_SLOW
  elif all(rows[ema_fast_column] > rows[ema_slow_column]):
    return EMA_FAST_ABOVE_EMA_SLOW
  else:
    return NO_CONCLUSIVE_SIGNAL