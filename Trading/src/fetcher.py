import os
import pandas as pd
import yfinance as yf
from pathlib import Path
from datetime import timedelta
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def cust_load(asset_name:str):
    p = r'C:\Users\ASUS\OneDrive\Desktop\code\serious_projects\Trading\data'+f'\{asset_name}.parquet'
    try:
        df = pd.read_parquet(p)
        return df
    except Exception as e:
        logger.info(e) 
        return False

def cust_save(asset_name:str,df:pd.DataFrame):
    p = r'C:\Users\ASUS\OneDrive\Desktop\code\serious_projects\Trading\data'+f'\{asset_name}.parquet'
    df.to_parquet(p,index=2)

def fetch_yf(asset_name,start = None,end = None,interval = '1d'):
    df = cust_load(asset_name)
    if df:
        last = df.index.max().date()
        if end is None:
            end = pd.Timestamp.today().date()
        if last >= pd.Timestamp(end).date():
            return df
        start = pd.Timestamp(last + timedelta(days=1)).strftime("%Y-%m-%d")
    new = yf.download(asset_name, start=start, end=end, interval=interval, progress=False,auto_adjust=True)
    'string (YYYY-MM-DD)'
    if df:
        df = pd.concat([df, new]).sort_index().drop_duplicates()
    else:
        df = new
    cust_save(asset_name=asset_name,df=df)
    

if __name__ != '__dick__':
    pass