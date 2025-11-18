import pandas as pd

def Validate(df:pd):
    if df.empty:
        return False
    required = {"date","Open","High","Low","Close","Volume","ticker"}
    if not required.issubset(set(df.columns)):
        return False
    numeric_cols = ["Open","High","Low","Close","Volume"]
    if not all(pd.to_numeric(df[c], errors="coerce").notna().all() for c in numeric_cols):
        return False
    return True