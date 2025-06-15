import pandas as pd
import os

def save_df(df, path):
    df.to_csv(path, index=False, encoding="utf-8")

def load_df(path, columns=None):
    if os.path.exists(path):
        return pd.read_csv(path)
    else:
        # إن لم توجد بيانات، يرجع DataFrame فارغ بالأعمدة المحددة
        return pd.DataFrame(columns=columns if columns else [])
