import pandas as pd
from .curve import above_or_below_curve, ABOVE_CURVE, BELOW_CURVE

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
    ema_slow:str = 'EMA_Slow',
    ema_fast:str = 'EMA_Fast',
    bollinger_low:str = 'BBL_15_1.5',
    bollinger_high:str = 'BBU_15_1.5'
    ) -> int:
  """
  Simple scalping signal is making sure that the trend is either up or down and when
  the current candle closes above or blow the upper or lower bollinger band respectively.
  """
  # Are we in an up trend? -yes-> Wait for current candle to close below lower bollinger band
  if (above_or_below_curve(df, current_candle, back_candles, 
                           curve=ema_fast, 
                           compare=ema_slow
    ) == ABOVE_CURVE
    and df[close_column][current_candle] <= df[bollinger_low][current_candle]):
    return LONG_SIGNAL

  # Are we in a down trend? -yes-> Wait for current candle to close above upper bollinger band
  if (above_or_below_curve(df, current_candle, back_candles, 
                           curve= ema_fast, 
                           compare=ema_slow
    ) == BELOW_CURVE 
      and df[close_column][current_candle] >= df[bollinger_high][current_candle]):
    return SHORT_SIGNAL
  
  return INCONCLUSIVE_SHORT_LONG_SIGNAL