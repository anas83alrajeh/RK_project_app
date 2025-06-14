import streamlit as st
import os
from PIL import Image
import uuid
from datetime import datetime
from fpdf import FPDF

st.title("📸 صفحة توثيق المشروع")
BASE_PATH = "data/documentation"
os.makedirs(BASE_PATH, exist_ok=True)

st.subheader("➕ إضافة مرحلة")
stage = st.text_input("اسم المرحلة")

if stage:
    stage_path = os.path.join(BASE_PATH, stage)
    os.makedirs(stage_path, exist_ok=True)

    st.subheader("📷 إضافة صورة")
    with st.form("image_form"):
        description = st.text_input("الوصف")
        date = st.date_input("تاريخ الإضافة")
        img_file = st.file_uploader("تحميل الصورة", type=["jpg", "jpeg", "png"])
        submit = st.form_submit_button("إضافة الصورة")

        if submit and img_file:
            img_id = str(uuid.uuid4()) + ".jpg"
            img_path = os.path.join(stage_path, img_id)
            image = Image.open(img_file)
            image.save(img_path)

            meta_path = os.path.join(stage_path, "metadata.csv")
            with open(meta_path, "a", encoding="utf-8") as f:
                f.write(f"{img_id},{description},{date}\n")
            st.success("✅ تم حفظ الصورة")

# توليد ملف PDF
st.subheader("📄 إنشاء ملف توثيق PDF")
stages = os.listdir(BASE_PATH)
selected_stage = st.selectbox("اختر المرحلة", stages)

if st.button("إنشاء PDF"):
    stage_dir = os.path.join(BASE_PATH, selected_stage)
    meta_file = os.path.join(stage_dir, "metadata.csv")
    if os.path.exists(meta_file):
        pdf = FPDF()
        with open(meta_file, encoding="utf-8") as f:
            for line in f:
                img_id, desc, date = line.strip().split(",")
                img_path = os.path.join(stage_dir, img_id)
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                pdf.cell(200, 10, txt=f"الوصف: {desc} | التاريخ: {date}", ln=True)
                pdf.image(img_path, x=10, y=30, w=180)
        pdf_file = f"{selected_stage}_توثيق.pdf"
        pdf.output(pdf_file)
        st.success(f"✅ تم إنشاء ملف {pdf_file}")
        with open(pdf_file, "rb") as f:
            st.download_button("📥 تحميل الملف", f, file_name=pdf_file)
