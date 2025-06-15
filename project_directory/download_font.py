import os
import requests
import streamlit as st

UTILS_DIR = "utils"
FONT_FILENAME = "DejaVuSans.ttf"
FONT_PATH = os.path.join(UTILS_DIR, FONT_FILENAME)

def download_font():
    if not os.path.exists(FONT_PATH):
        url = "https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans.ttf"
        try:
            r = requests.get(url)
            r.raise_for_status()
            os.makedirs(UTILS_DIR, exist_ok=True)
            with open(FONT_PATH, "wb") as f:
                f.write(r.content)
            st.success("تم تحميل الخط بنجاح.")
        except Exception as e:
            st.error(f"فشل تحميل الخط: {e}")
