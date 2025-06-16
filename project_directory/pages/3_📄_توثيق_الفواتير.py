import streamlit as st
import pandas as pd
import os
from PIL import Image
import uuid
from utils.helpers import load_df, save_df
import logging
import streamlit.components.v1 as components
from fpdf import FPDF
import base64

st.set_page_config(layout="centered")
st.title("📄 صفحة توثيق الفواتير")

INVOICE_PATH = "data/invoices.csv"
IMAGE_DIR = "data/invoices/"
os.makedirs(IMAGE_DIR, exist_ok=True)

tasks_df = load_df("data/tasks.csv")
total_tasks_cost = tasks_df["التكلفة"].sum() if not tasks_df.empty else 0
st.markdown(f"### 💰 إجمالي تكاليف المهام: {total_tasks_cost:,.2f} دولار")

if "should_rerun" not in st.session_state:
    st.session_state.should_rerun = False

if "name_value" not in st.session_state:
    st.session_state.name_value = ""
if "value_amount" not in st.session_state:
    st.session_state.value_amount = 0.0
if "upload_key" not in st.session_state:
    st.session_state.upload_key = str(uuid.uuid4())

def add_invoice(date, name, value, image):
    img_id = str(uuid.uuid4()) + ".jpg"
    image_path = os.path.join(IMAGE_DIR, img_id)
    if image.mode in ("RGBA", "LA") or (image.mode == "P" and "transparency" in image.info):
        image = image.convert("RGB")
    max_width = 600
    if image.width > max_width:
        ratio = max_width / image.width
        new_size = (max_width, int(image.height * ratio))
        image = image.resize(new_size)
    image.save(image_path)

    df = load_df(INVOICE_PATH)
    if df.empty or not set(["التاريخ", "اسم الفاتورة", "القيمة", "الصورة"]).issubset(df.columns):
        df = pd.DataFrame(columns=["التاريخ", "اسم الفاتورة", "القيمة", "الصورة"])
    df.loc[len(df)] = [date, name, value, img_id]
    save_df(df, INVOICE_PATH)

def delete_invoice(idx):
    df = load_df(INVOICE_PATH)
    if df.empty:
        return
    img_file = df.loc[idx, "الصورة"]
    img_path = os.path.join(IMAGE_DIR, img_file)
    if os.path.exists(img_path):
        os.remove(img_path)
    df.drop(idx, inplace=True)
    df.reset_index(drop=True, inplace=True)
    save_df(df, INVOICE_PATH)
    st.session_state.should_rerun = True

with st.form("invoice_form"):
    date = st.date_input("تاريخ الفاتورة")
    name = st.text_input("اسم الفاتورة", value=st.session_state.name_value, key="name_input")
    value = st.number_input("القيمة", min_value=0.0, value=st.session_state.value_amount, key="value_input")
    img = st.file_uploader("صورة الفاتورة", type=["jpg", "jpeg", "png"], key=st.session_state.upload_key)
    submit = st.form_submit_button("إضافة الفاتورة")

    if submit:
        if not img:
            st.error("يرجى رفع صورة الفاتورة.")
        elif name.strip() == "":
            st.error("يرجى كتابة اسم الفاتورة.")
        elif value <= 0:
            st.error("القيمة يجب أن تكون أكبر من صفر.")
        else:
            img_obj = Image.open(img)
            add_invoice(date, name, value, img_obj)
            st.success("✅ تمت إضافة الفاتورة")
            st.session_state.name_value = ""
            st.session_state.value_amount = 0.0
            st.session_state.upload_key = str(uuid.uuid4())
            st.session_state.should_rerun = True

if st.session_state.should_rerun:
    st.session_state.should_rerun = False
    try:
        st.experimental_rerun()
    except Exception as e:
        logging.error(f"Error during rerun: {e}")
        components.html("<script>window.location.reload()</script>", height=0)

invoice_df = load_df(INVOICE_PATH)
if invoice_df.empty or not set(["التاريخ", "اسم الفاتورة", "القيمة", "الصورة"]).issubset(invoice_df.columns):
    invoice_df = pd.DataFrame(columns=["التاريخ", "اسم الفاتورة", "القيمة", "الصورة"])

st.subheader("📑 قائمة الفواتير")

if invoice_df.empty:
    st.info("لا توجد فواتير مضافة بعد.")
else:
    for idx, row in invoice_df.iterrows():
        cols = st.columns([1, 5, 1])
        with cols[0]:
            img_path = os.path.join(IMAGE_DIR, row["الصورة"])
            if os.path.exists(img_path):
                st.image(img_path, width=600)
            else:
                st.warning("❌ صورة غير موجودة")
        with cols[1]:
            st.markdown(
                f"""
                <div style="
                    direction: rtl; 
                    text-align: right; 
                    background-color: black; 
                    color: white; 
                    padding: 10px; 
                    border-radius: 8px;">
                    <strong>📅 التاريخ:</strong> {row['التاريخ']}<br>
                    <strong>📄 اسم الفاتورة:</strong> {row['اسم الفاتورة']}<br>
                    <strong>💵 القيمة:</strong> {row['القيمة']:,.2f} ريال
                </div>
                """,
                unsafe_allow_html=True
            )
        with cols[2]:
            if st.button("🗑️ حذف", key=f"delete_{idx}"):
                delete_invoice(idx)

total_invoices = invoice_df["القيمة"].sum()
st.markdown(f"### 💳 مجموع الفواتير: {total_invoices:,.2f} دولار")
st.markdown(f"### 🧾 المبلغ المتبقي: {total_tasks_cost - total_invoices:,.2f} دولار")

# --- هنا الإضافة: زر تحميل PDF أسفل الصفحة ---
def generate_pdf_from_images(df):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=15)
    df_sorted = df.sort_values(by="التاريخ")
    for _, row in df_sorted.iterrows():
        img_path = os.path.join(IMAGE_DIR, row["الصورة"])
        if os.path.exists(img_path):
            pdf.add_page()
            with Image.open(img_path) as img:
                width_px, height_px = img.size
            width_mm = width_px * 0.264583  # تحويل بيكسل إلى ملم
            height_mm = height_px * 0.264583
            max_width = pdf.w - 20  # هامش 10 ملم على كل جانب
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

if st.button("⬇️ تحميل جميع صور الفواتير كملف PDF"):
    if invoice_df.empty:
        st.warning("لا توجد فواتير لتحويلها إلى PDF.")
    else:
        pdf_bytes = generate_pdf_from_images(invoice_df)
        b64 = base64.b64encode(pdf_bytes).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="invoices_images.pdf">اضغط هنا لتحميل ملف PDF</a>'
        st.markdown(href, unsafe_allow_html=True)
