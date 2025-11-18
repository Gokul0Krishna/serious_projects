import pandas as pd

def Validate(df: pd.DataFrame, ticker: str):

    required_cols = ["date", "Open", "High", "Low", "Close", "Adj Close", "Volume", "ticker"]
    for col in required_cols:
        if col not in df.columns:
            print(f"[ERROR] Missing column: {col}")
            return False

    # Ensure ticker is correct
    if not all(df["ticker"] == ticker):
        print("[ERROR] Ticker mismatch in DataFrame")
        return False

    # Date validations
    try:
        df["date"] = pd.to_datetime(df["date"])
    except Exception:
        print("[ERROR] Could not parse 'date' column")
        return False

    return True

    # # Drop rows with NaN
    # if df.isna().sum().sum() > 0:
    #     print("[WARN] NaN rows removed")
    #     df.dropna(inplace=True)

    # # Remove invalid prices (zero or negative)
    # for c in ["Open", "High", "Low", "Close"]:
    #     df = df[df[c] > 0]

    # # Remove zero volume rows
    # df = df[df["Volume"] > 0]

    # # return df
