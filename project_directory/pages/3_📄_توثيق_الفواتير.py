import streamlit as st
import pandas as pd
import os
from PIL import Image
import uuid
from utils.helpers import load_df, save_df

st.title("📄 صفحة توثيق الفواتير")
INVOICE_PATH = "data/invoices.csv"
IMAGE_DIR = "data/invoices/"
os.makedirs(IMAGE_DIR, exist_ok=True)

tasks_df = load_df("data/tasks.csv")
total_tasks_cost = tasks_df["التكلفة"].sum() if not tasks_df.empty else 0
st.markdown(f"### 💰 إجمالي تكاليف المهام: {total_tasks_cost:,.2f} دولار")    

invoice_df = load_df(INVOICE_PATH)

def add_invoice(date, name, value, image):
    img_id = str(uuid.uuid4()) + ".jpg"
    image_path = os.path.join(IMAGE_DIR, img_id)
    image.save(image_path)
    invoice_df.loc[len(invoice_df)] = [date, name, value, img_id]
    save_df(invoice_df, INVOICE_PATH)

with st.form("invoice_form"):
    date = st.date_input("تاريخ الفاتورة")
    name = st.text_input("اسم الفاتورة")
    value = st.number_input("القيمة", min_value=0.0)
    img = st.file_uploader("صورة الفاتورة", type=["jpg", "jpeg", "png"])
    submit = st.form_submit_button("إضافة الفاتورة")
    if submit and img:
        img = Image.open(img)
        add_invoice(date, name, value, img)
        st.success("✅ تمت إضافة الفاتورة")

st.subheader("📑 قائمة الفواتير")
st.dataframe(invoice_df)

if not invoice_df.empty:
    total_invoices = invoice_df["القيمة"].sum()
    st.markdown(f"### 💳 مجموع الفواتير: {total_invoices:,.2f} ريال")
    st.markdown(f"### 🧾 المبلغ المتبقي: {total_tasks_cost - total_invoices:,.2f} ريال")
