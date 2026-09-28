#import all your libraries you need
#recommend using aliases for NumPy and Pandas
#this code loads stock data for Apple stock and the S&P500 - try it with others

from matplotlib import dates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yf

raw = yf.download('SPY AAPL', start= '2010-01-01', end='2019-12-31')

print(raw)
