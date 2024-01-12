import pandas as pd

# This is when all the back_candles for EMA Fast are below EMA Slow
EMA_FAST_BELOW_EMA_SLOW:int = 1
# This is when all the back_candles for EMA Fast are above EMA Slow
EMA_FAST_ABOVE_EMA_SLOW:int = 2
# This is when all the back_candles are neither above or below EMA Slow & Fast
NO_CONCLUSIVE_SIGNAL:int = 0

def two_above_or_below(df:pd.DataFrame, current_candle:int, back_candles:int) -> int:
  """"
  This function will check up to back_candles candles before the current_candle
  if all of them are EMA Fast is are below EMA Slow. If so, it will return _EMA_FAST_BELOW_EMA_SLOW_.
  If all of them are above, it will return _EMA_FAST_ABOVE_EMA_SLOW_.

  Otherwise _NO_CONCLUSIVE_SIGNAL_ will be returned.

  NOTE: This function *REQUIRES* that column 'EMA Fast' and 'EMA Slow' are present,
        and that the dataframe is sorted by date (ascending). What 'EMA Fast' and
        'EMA Slow' are is up to you to decide.
  """
  # Copy the dataframe
  dfs = df.reset_index().copy()

  # Range of candles
  start = max(0, current_candle - back_candles)
  end = current_candle
  rows = dfs.iloc[start:end]

  # Check if all EMA Fast values are below EMA Slow
  if all(rows['EMA Fast'] < rows['EMA Slow']):
    return EMA_FAST_BELOW_EMA_SLOW
  elif all(rows['EMA Fast'] > rows['EMA Slow']):
    return EMA_FAST_ABOVE_EMA_SLOW
  else:
    return NO_CONCLUSIVE_SIGNAL