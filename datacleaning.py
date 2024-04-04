import pandas as pd
from auxiliary import *
from dbhandler import *
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import mplfinance as mpf

db = DBHandler()
in_df = pd.read_sql(sql='SELECT * FROM SPY',con=db.conn)

df = in_df[['time', 'open', 'high', 'low', 'close', 'vwap', 'count', 'volume', 'bidVolume', 'askVolume', 'impVolatility']]
df.dropna(axis=0, how='any', subset=['open','high','low','close','volume'], inplace=True)
df.loc[:,'time'] = df['time'].apply(lambda x : unix_to_time(x, granularity='s', scaled=True))
#items from candle come in reverse chronological order
df = df[::-1]
df = df[1::] # idk why the fking df dropna cant drop a row with all NaN values
df = df.set_index('time')

print(df.head())

#8000 candles is unplottable

mpf.plot(df, type='candle', volume=True, title='test')
plt.show()