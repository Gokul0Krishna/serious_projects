from datetime import date
import os
from fetcher import Get_todays_data
from validation import Validate
from feeder import Insert


if __name__ == '__main__':
    data = Get_todays_data(ticker='BTC-USD')
    print(data)

    if Validate(data,ticker='BTC-USD'):
        print('Data is getting cleaned')
        if data.isna().sum().sum() > 0:
            data.dropna(inplace=True)
        for c in ["Open", "High", "Low", "Close"]:
            data = data[data[c] > 0]
        data = data[data["Volume"] > 0]
        Insert(data)
