import pandas as pd
import os

def save_df(df, path):
    df.to_csv(path, index=False, encoding="utf-8")

def load_df(path):
    if os.path.exists(path):
        return pd.read_csv(path)
    else:
        return pd.DataFrame()
