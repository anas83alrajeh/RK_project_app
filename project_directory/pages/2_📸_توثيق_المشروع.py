import streamlit as st
import os
from PIL import Image
import uuid
import pandas as pd
from datetime import datetime

st.set_page_config(layout="centered")
st.title("📸 صفحة توثيق المشروع")

DATA_DIR = "data/documentation"
os.makedirs(DATA_DIR, exist_ok=True)
META_FILE = os.path.join(DATA_DIR, "metadata.csv")

# إنشاء ملف البيانات إذا لم يكن موجودًا
if not os.path.exists(META_FILE):
    df = pd.DataFrame(columns=["الصورة", "الوصف", "التاريخ"])
    df.to_csv(META_FILE, index=False, encoding="utf-8")

# تحميل البيانات
df = pd.read_csv(META_FILE)

# --- النموذج العلوي لإضافة صورة
st.subheader("➕ إضافة صورة جديدة")

with st.form("image_form"):
    description = st.text_input("الوصف")
    date = st.date_input("تاريخ الإضافة", value=datetime.today())
    img_file = st.file_uploader("تحميل الصورة", type=["jpg", "jpeg", "png"])
    submit = st.form_submit_button("➕ إضافة")

    if submit:
        if not img_file:
            st.error("❗ يرجى تحميل صورة.")
        elif description.strip() == "":
            st.error("❗ يرجى إدخال وصف للصورة.")
        else:
            img_id = str(uuid.uuid4()) + ".jpg"
            img_path = os.path.join(DATA_DIR, img_id)

            image = Image.open(img_file)
            if image.mode in ("RGBA", "P"):
                image = image.convert("RGB")

            # تغيير حجم الصورة إن لزم
            max_width = 600
            if image.width > max_width:
                ratio = max_width / image.width
                image = image.resize((max_width, int(image.height * ratio)))

            image.save(img_path)

            df.loc[len(df)] = [img_id, description, date]
            df.to_csv(META_FILE, index=False, encoding="utf-8")
            st.success("✅ تم حفظ الصورة")
            st.experimental_rerun()

# --- عرض الصور كما في صفحة الفواتير
st.subheader("📑 قائمة الصور المضافة")

if df.empty:
    st.info("لا توجد صور مضافة بعد.")
else:
    for idx, row in df.iterrows():
        cols = st.columns([1, 5, 1])
        img_path = os.path.join(DATA_DIR, row["الصورة"])

        with cols[0]:
            if os.path.exists(img_path):
                st.image(img_path, width=600)
            else:
                st.warning("❌ الصورة غير موجودة")

        with cols[1]:
            st.markdown(
                f"""
                <div style="
                    direction: rtl;
                    text-align: right;
                    background-color: #000;
                    color: #fff;
                    padding: 10px;
                    border-radius: 8px;">
                    <strong>📅 التاريخ:</strong> {row["التاريخ"]}<br>
                    <strong>📝 الوصف:</strong> {row["الوصف"]}
                </div>
                """,
                unsafe_allow_html=True
            )

        with cols[2]:
            if st.button("🗑️ حذف", key=f"delete_{idx}"):
                # حذف الصورة من القرص
                if os.path.exists(img_path):
                    os.remove(img_path)
                # حذف السطر من الجدول
                df.drop(idx, inplace=True)
                df.to_csv(META_FILE, index=False, encoding="utf-8")
                st.experimental_rerun()
