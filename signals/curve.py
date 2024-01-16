import pandas as pd
from enum import Enum

# This is when all the signal could not be concluded
INCONCLUSIVE:int = 0
# This is returned when the cure/candle(s) are above the curve
ABOVE_CURVE:int = 1
# This is returned when the curve/candle(s) are below the curve
BELOW_CURVE:int = 2

class WindowUsage(Enum):
    """
    This is used to specify how the window is used.
    """
    BACKWARD_ONLY = 1
    """This will only use the window to look back in history."""
    FORWARD_ONLY = 2
    """This will only use the window to look forward in history."""
    BOTH_DIRECTIONS = 3
    """This will use the window to look back and forward in history."""

def above_or_below_curve(
    df:pd.DataFrame,
    current_pos:int,
    window:int,
    usage:WindowUsage = WindowUsage.BACKWARD_ONLY,
    curve:str = 'Close',
    compare:str = 'EMA'
    ) -> int:
  """
  This function will check from the _curve_ within the _window_ is
  above or below the _curve_to_check_.

  If using  'Close' as _curve_ you will effectively check if the candles(s)
  are above or below the _curve_to_check_ e.g. EMA or bollinger.

  :param df: DataFrame containing the ticker data
  :param current_pos: Current position (usually a candle) we're looking at
  :param window: How many candles back we're looking at (used for trend analysis)
  :param usage: How the window is used (back, forward or both)
  :param curve: The curve to check if it's above or below the _compare_.
  :param compare: The comparison curve curve that the _curve_ will match.

  :return: Returns a signal ABOVE_CURVE, BELOW_CURVE or INCONCLUSIVE.
  """
  # Copy the dataframe
  dfs = df.copy().reset_index()

  # Range of candles
  if usage == WindowUsage.BACKWARD_ONLY:
    start = max(0, current_pos - window)
    end = current_pos
  elif usage == WindowUsage.FORWARD_ONLY:
    start = current_pos
    end = current_pos + window
  elif usage == WindowUsage.BOTH_DIRECTIONS:
    length = window // 2
    start = max(0, current_pos - length)
    end = current_pos + length

  # Get the rows
  if end > len(dfs):
    end = len(dfs)

  rows = dfs.iloc[start:end]

  if all(rows[curve] > rows[compare]):
    return ABOVE_CURVE
  elif all(rows[curve] < rows[compare]):
    return BELOW_CURVE
  else:
    return INCONCLUSIVE
