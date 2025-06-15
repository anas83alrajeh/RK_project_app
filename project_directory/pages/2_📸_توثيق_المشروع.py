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
import io

st.set_page_config(layout="centered")
st.title("📸 صفحة توثيق المشروع")

DATA_DIR = "data/documentation"
META_FILE = os.path.join(DATA_DIR, "metadata.csv")
os.makedirs(DATA_DIR, exist_ok=True)

# مفاتيح الجلسة
if "should_rerun" not in st.session_state:
    st.session_state.should_rerun = False
if "desc_val" not in st.session_state:
    st.session_state.desc_val = ""
if "upload_key" not in st.session_state:
    st.session_state.upload_key = str(uuid.uuid4())

# إنشاء الملف إن لم يكن موجود
if not os.path.exists(META_FILE):
    df = pd.DataFrame(columns=["الصورة", "الوصف", "التاريخ"])
    df.to_csv(META_FILE, index=False, encoding="utf-8")

# دالة التحميل
def load_df():
    try:
        return pd.read_csv(META_FILE)
    except Exception as e:
        logging.error(f"Error reading metadata file: {e}")
        return pd.DataFrame(columns=["الصورة", "الوصف", "التاريخ"])

# دالة الحفظ
def save_df(df):
    df.to_csv(META_FILE, index=False, encoding="utf-8")

# دالة الإضافة
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

# دالة الحذف
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

# النموذج لإضافة صورة جديدة
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

# إعادة التشغيل بعد الإضافة أو الحذف
if st.session_state.should_rerun:
    st.session_state.should_rerun = False
    try:
        st.experimental_rerun()
    except Exception as e:
        logging.error(f"Error during rerun: {e}")
        components.html("<script>window.location.reload()</script>", height=0)

# عرض الصور
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
                st.image(img_path)  # عرض الصورة بحجمها الأصلي
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

# دالة إنشاء ملف PDF مع دعم العربية
def generate_pdf(df):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_font('DejaVu', '', 'utils/DejaVuSans.ttf', uni=True)  # تأكد من وجود الخط في هذا المسار
    pdf.set_font("DejaVu", size=12)

    for idx, row in df.iterrows():
        pdf.add_page()
        img_path = os.path.join(DATA_DIR, row["الصورة"])
        if os.path.exists(img_path):
            # إعادة تحجيم الصورة لتناسب صفحة A4 مع هامش 10 مم
            pdf.image(img_path, x=10, y=30, w=pdf.w - 20)

        pdf.set_xy(10, 10)
        pdf.multi_cell(0, 10, f"📅 التاريخ: {row['التاريخ']}\n📝 الوصف: {row['الوصف']}", align='R')

    pdf_output = io.BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    return pdf_output.read()

# زر تحميل PDF
st.markdown("---")
st.subheader("⬇️ تحميل جميع الصور مع التوثيق كـ PDF")
if st.button("📄 تنزيل PDF"):
    if df.empty:
        st.warning("لا توجد بيانات لتحويلها إلى PDF.")
    else:
        pdf_bytes = generate_pdf(df)
        b64 = base64.b64encode(pdf_bytes).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="توثيق_المشروع.pdf">📥 اضغط هنا لتحميل الملف</a>'
        st.markdown(href, unsafe_allow_html=True)
