import streamlit as st
import os
import pandas as pd
from PIL import Image
import uuid
from datetime import datetime
import logging
import streamlit.components.v1 as components
from fpdf import FPDF
import base64
import requests
import arabic_reshaper
from bidi.algorithm import get_display

st.set_page_config(layout="centered")
st.title("📸 صفحة توثيق المشروع")

DATA_DIR = "data/documentation"
META_FILE = os.path.join(DATA_DIR, "metadata.csv")
UTILS_DIR = "utils"
FONT_FILENAME = "Amiri-Regular.ttf"
FONT_PATH = os.path.join(UTILS_DIR, FONT_FILENAME)

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(UTILS_DIR, exist_ok=True)

KNOWN_FONT_SIZE_BYTES = 4500000

def download_font():
    if not os.path.exists(FONT_PATH) or os.path.getsize(FONT_PATH) < KNOWN_FONT_SIZE_BYTES * 0.9:
        st.info("جاري تحميل الخط العربي Amiri...")
        url = "https://github.com/anas83alrajeh/RK_project_app/raw/master/project_directory/utils/Amiri-Regular.ttf"
        try:
            r = requests.get(url, stream=True)
            r.raise_for_status()
            with open(FONT_PATH, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            if os.path.getsize(FONT_PATH) >= KNOWN_FONT_SIZE_BYTES * 0.9:
                st.success("تم تحميل الخط العربي Amiri بنجاح.")
            else:
                st.error("فشل تحميل الخط: الملف صغير أو غير مكتمل.")
                if os.path.exists(FONT_PATH):
                    os.remove(FONT_PATH)
        except Exception as e:
            st.error(f"خطأ أثناء تحميل الخط: {e}")
            if os.path.exists(FONT_PATH):
                os.remove(FONT_PATH)

download_font()

if "should_rerun" not in st.session_state:
    st.session_state.should_rerun = False
if "upload_key" not in st.session_state:
    st.session_state.upload_key = str(uuid.uuid4())

# إنشاء ملف الميتاداتا إذا غير موجود
if not os.path.exists(META_FILE):
    pd.DataFrame(columns=["الصورة", "التاريخ"]).to_csv(META_FILE, index=False, encoding="utf-8")

def load_df():
    try:
        df = pd.read_csv(META_FILE, encoding="utf-8")
        expected_cols = ["الصورة", "التاريخ"]
        if list(df.columns) != expected_cols:
            df = pd.DataFrame(columns=expected_cols)
        return df
    except Exception as e:
        logging.error(f"Error reading metadata file: {e}")
        return pd.DataFrame(columns=["الصورة", "التاريخ"])

def save_df(df):
    df.to_csv(META_FILE, index=False, encoding="utf-8")

def add_entry(date, image):
    img_id = str(uuid.uuid4()) + ".jpg"
    img_path = os.path.join(DATA_DIR, img_id)
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")
    image.save(img_path)
    df = load_df()
    date_str = pd.to_datetime(date).strftime("%Y-%m-%d")
    new_row = {"الصورة": img_id, "التاريخ": date_str}
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    save_df(df)
    st.session_state.upload_key = str(uuid.uuid4())
    st.session_state.should_rerun = True

def delete_entry(idx):
    df = load_df()
    if df.empty:
        return
    img_file = df.loc[idx, "الصورة"]
    img_path = os.path.join(DATA_DIR, img_file)
    if os.path.exists(img_path):
        os.remove(img_path)
    df.drop(idx, inplace=True)
    df.reset_index(drop=True, inplace=True)
    save_df(df)
    st.session_state.should_rerun = True

st.subheader("➕ إضافة صورة جديدة")
with st.form("image_form"):
    date = st.date_input("تاريخ الإضافة", value=datetime.today())
    img_file = st.file_uploader("تحميل الصورة", type=["jpg", "jpeg", "png"], key=st.session_state.upload_key)
    submitted = st.form_submit_button("إضافة")
    if submitted:
        if not img_file:
            st.error("يرجى رفع صورة.")
        else:
            img_obj = Image.open(img_file)
            add_entry(date, img_obj)

if st.session_state.should_rerun:
    st.session_state.should_rerun = False
    try:
        st.experimental_rerun()
    except Exception as e:
        logging.error(f"Error during rerun: {e}")
        components.html("<script>window.location.reload()</script>", height=0)

st.subheader("📑 الصور المضافة")
df = load_df()

if df.empty:
    st.info("لا توجد صور حتى الآن.")
else:
    for idx, row in df.iterrows():
        cols = st.columns([1, 5, 1])
        img_path = os.path.join(DATA_DIR, row["الصورة"])
        with cols[0]:
            if os.path.exists(img_path):
                st.image(img_path)
            else:
                st.warning("❌ الصورة غير موجودة")
        with cols[1]:
            st.markdown(
                f"""
                <div style="direction: rtl; text-align: right; background-color: #000; color: #fff; padding: 10px; border-radius: 8px;">
                    <strong>📅 التاريخ:</strong> {row["التاريخ"]}
                </div>
                """,
                unsafe_allow_html=True
            )
        with cols[2]:
            if st.button("🗑️ حذف", key=f"delete_{idx}"):
                delete_entry(idx)

def generate_pdf_only_images(df):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=15)
    df_sorted = df.sort_values(by="التاريخ")
    for _, row in df_sorted.iterrows():
        pdf.add_page()
        img_path = os.path.join(DATA_DIR, row["الصورة"])
        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                width_px, height_px = img.size
            width_mm = width_px * 0.264583
            height_mm = height_px * 0.264583
            max_width = pdf.w - 20
            max_height = pdf.h - 20
            scale = min(max_width / width_mm, max_height / height_mm, 1)
            disp_width = width_mm * scale
            disp_height = height_mm * scale
            x = (pdf.w - disp_width) / 2
            y = (pdf.h - disp_height) / 2
            pdf.image(img_path, x=x, y=y, w=disp_width, h=disp_height)
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    return pdf_bytes

st.markdown("---")
st.subheader("⬇️ تحميل الملفات")

col1 = st.columns(1)[0]

with col1:
    if st.button("⬇️ تنزيل PDF بالصور فقط (مرتبة حسب التاريخ)"):
        if df.empty:
            st.warning("لا توجد صور للتحميل.")
        else:
            pdf_bytes = generate_pdf_only_images(df)
            b64 = base64.b64encode(pdf_bytes).decode()
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="project_images.pdf">اضغط هنا لتحميل ملف PDF</a>'
            st.markdown(href, unsafe_allow_html=True)
