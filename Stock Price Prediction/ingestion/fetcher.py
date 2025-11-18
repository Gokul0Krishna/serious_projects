import yfinance as yf
import pandas as pd

def Get_todays_data(ticker:str,):
    df = yf.download(ticker,interval='1d',progress=False,auto_adjust=False)

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = ["Open", "High", "Low", "Close", "Adj Close", "Volume"]
    
    df.index.name = "date"
    df.reset_index(inplace=True)
    df["ticker"] = ticker
    return df