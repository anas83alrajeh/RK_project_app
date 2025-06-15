import streamlit as st
from PIL import Image
import os
import uuid
from utils.helpers import load_df, save_df

st.set_page_config(layout="centered")
st.title("📸 صفحة توثيق المشروع")

IMAGE_DIR = "data/documentation/"
os.makedirs(IMAGE_DIR, exist_ok=True)

DATA_SHEET_NAME = "app"
DOCS_WORKSHEET = "documentation"

def load_data():
    df = load_df(DATA_SHEET_NAME, DOCS_WORKSHEET)
    if df.empty:
        df = pd.DataFrame(columns=["الصورة", "الوصف", "التاريخ"])
    return df

def save_data(df):
    save_df(df, DATA_SHEET_NAME, DOCS_WORKSHEET)

df = load_data()

st.markdown("### إضافة صورة توثيق")

with st.form("doc_form"):
    img_file = st.file_uploader("صورة التوثيق", type=["jpg", "jpeg", "png"])
    description = st.text_input("الوصف")
    date = st.date_input("التاريخ")
    submitted = st.form_submit_button("إضافة")

    if submitted:
        if img_file is None:
            st.error("يرجى رفع صورة.")
        elif description.strip() == "":
            st.error("يرجى كتابة وصف.")
        else:
            img = Image.open(img_file)
            img_id = str(uuid.uuid4()) + ".jpg"
            img_path = os.path.join(IMAGE_DIR, img_id)
            if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
                img = img.convert("RGB")
            max_width = 600
            if img.width > max_width:
                ratio = max_width / img.width
                new_size = (max_width, int(img.height * ratio))
                img = img.resize(new_size)
            img.save(img_path)

            df.loc[len(df)] = [img_id, description, str(date)]
            save_data(df)
            st.success("✅ تمت إضافة الصورة")

# عرض الصور المضافة
st.subheader("📑 الصور الموثقة")
if df.empty:
    st.info("لا توجد صور مضافة بعد.")
else:
    for idx, row in df.iterrows():
        img_path = os.path.join(IMAGE_DIR, row["الصورة"])
        if os.path.exists(img_path):
            st.image(img_path, width=600)
        else:
            st.warning("❌ صورة غير موجودة")
        st.markdown(f"**الوصف:** {row['الوصف']}")
        st.markdown(f"**التاريخ:** {row['التاريخ']}")
        st.markdown("---")
