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
FONT_FILENAME = "Amiri-Regular.ttf"  # استبدال الخط إلى Amiri
FONT_PATH = os.path.join(UTILS_DIR, FONT_FILENAME)

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(UTILS_DIR, exist_ok=True)

# تحميل الخط العربي Amiri إذا لم يكن موجودًا
def download_font():
    if not os.path.exists(FONT_PATH):
        url = "https://github.com/aliftype/amiri-font/raw/master/ttf/Amiri-Regular.ttf"
        try:
            r = requests.get(url)
            r.raise_for_status()
            os.makedirs(UTILS_DIR, exist_ok=True)
            with open(FONT_PATH, "wb") as f:
                f.write(r.content)
            st.success("تم تحميل الخط العربي Amiri بنجاح.")
        except Exception as e:
            st.error(f"فشل تحميل الخط: {e}")

download_font()

# مفاتيح الجلسة
if "should_rerun" not in st.session_state:
    st.session_state.should_rerun = False
if "desc_val" not in st.session_state:
    st.session_state.desc_val = ""
if "upload_key" not in st.session_state:
    st.session_state.upload_key = str(uuid.uuid4())

if not os.path.exists(META_FILE):
    df = pd.DataFrame(columns=["الصورة", "الوصف", "التاريخ"])
    df.to_csv(META_FILE, index=False, encoding="utf-8")

def load_df():
    try:
        return pd.read_csv(META_FILE)
    except Exception as e:
        logging.error(f"Error reading metadata file: {e}")
        return pd.DataFrame(columns=["الصورة", "الوصف", "التاريخ"])

def save_df(df):
    df.to_csv(META_FILE, index=False, encoding="utf-8")

def add_entry(date, description, image):
    img_id = str(uuid.uuid4()) + ".jpg"
    img_path = os.path.join(DATA_DIR, img_id)

    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")
    image.save(img_path)

    df = load_df()
    df.loc[len(df)] = [img_id, description, date]
    save_df(df)

    st.session_state.desc_val = ""
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
    desc = st.text_input("الوصف", value=st.session_state.desc_val)
    img_file = st.file_uploader("تحميل الصورة", type=["jpg", "jpeg", "png"], key=st.session_state.upload_key)
    submitted = st.form_submit_button("إضافة")

    if submitted:
        if not img_file:
            st.error("يرجى رفع صورة.")
        elif desc.strip() == "":
            st.error("يرجى كتابة وصف.")
        else:
            img_obj = Image.open(img_file)
            add_entry(date, desc, img_obj)

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
                    <strong>📅 التاريخ:</strong> {row["التاريخ"]}<br>
                    <strong>📝 الوصف:</strong> {row["الوصف"]}
                </div>
                """,
                unsafe_allow_html=True
            )
        with cols[2]:
            if st.button("🗑️ حذف", key=f"delete_{idx}"):
                delete_entry(idx)

def reshape_arabic_text(text):
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    return bidi_text

def generate_pdf(df):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=15)

    if not os.path.exists(FONT_PATH):
        st.error("ملف الخط غير موجود، يرجى التأكد من تحميله.")
        return None

    pdf.add_font('Amiri', '', FONT_PATH, uni=True)
    pdf.set_font("Amiri", size=12)

    for idx, row in df.iterrows():
        pdf.add_page()

        # صياغة النص العربي لدعم RTL
        date_text = reshape_arabic_text(f"📅 التاريخ: {row['التاريخ']}")
        desc_text = reshape_arabic_text(f"📝 الوصف: {row['الوصف']}")

        # النص بمحاذاة يمين
        pdf.multi_cell(0, 10, f"{date_text}\n{desc_text}", align='R')
        pdf.ln(5)

        img_path = os.path.join(DATA_DIR, row["الصورة"])
        if os.path.exists(img_path):
            max_width = pdf.w - 20
            max_height = pdf.h - pdf.get_y() - 20

            with Image.open(img_path) as img:
                width_px, height_px = img.size

            width_mm = width_px * 0.264583
            height_mm = height_px * 0.264583

            scale = min(max_width / width_mm, max_height / height_mm, 1)
            disp_width = width_mm * scale
            disp_height = height_mm * scale

            pdf.image(img_path, x=10, y=pdf.get_y(), w=disp_width, h=disp_height)

    pdf_bytes = pdf.output(dest='S').encode('latin1')
    return pdf_bytes

st.markdown("---")
st.subheader("⬇️ تحميل جميع الصور مع التوثيق كـ PDF")
if st.button("📄 تنزيل PDF"):
    if df.empty:
        st.warning("لا توجد بيانات لتحويلها إلى PDF.")
    else:
        pdf_bytes = generate_pdf(df)
        if pdf_bytes:
            b64 = base64.b64encode(pdf_bytes).decode()
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="توثيق_المشروع.pdf">📥 اضغط هنا لتحميل الملف</a>'
            st.markdown(href, unsafe_allow_html=True)
