import pandas as pd
from .ema import two_above_or_below, EMA_FAST_ABOVE_EMA_SLOW, EMA_FAST_BELOW_EMA_SLOW

# Short signal is when a sell may be commenced -> we're going down
SHORT_SIGNAL = 1
# Long signal is when a buy may be commenced -> we're going up
LONG_SIGNAL = 2
# Inconclusive signal is when we're not sure if we're going up or down
INCONCLUSIVE_SHORT_LONG_SIGNAL = 0

def simple_signal(
    df: pd.DataFrame, 
    current_candle:int, 
    back_candles:int,
    close_column:str = 'Close',
    bollinger_bands_low_column:str = 'BBL_15_1.5',
    bollinger_bands_high_column:str = 'BBU_15_1.5'
    ) -> int:
  """
  Simple scalping signal is making sure that the trend is either up or down and when
  the current candle closes above or blow the upper or lower bollinger band respectively.

  :param df: DataFrame containing the ticker data
  :param current_candle: Current candle we're looking at
  :param back_candles: How many candles back we're looking at (used for trend analysis)

  :return: LONG_SIGNAL, SHORT_SIGNAL or INCONCLUSIVE_SHORT_LONG_SIGNAL
  """
  # Are we in an up trend? -yes-> Wait for current candle to close below lower bollinger band
  if (two_above_or_below(df, current_candle, back_candles) == EMA_FAST_ABOVE_EMA_SLOW
    and df[close_column][current_candle] <= df[bollinger_bands_low_column][current_candle]):
    return LONG_SIGNAL

  # Are we in a down trend? -yes-> Wait for current candle to close above upper bollinger band
  if (two_above_or_below(df, current_candle, back_candles) == EMA_FAST_BELOW_EMA_SLOW 
      and df[close_column][current_candle] >= df[bollinger_bands_high_column][current_candle]):
    return SHORT_SIGNAL
  
  return INCONCLUSIVE_SHORT_LONG_SIGNAL