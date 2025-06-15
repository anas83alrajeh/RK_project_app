import streamlit as st
import pandas as pd
import os
from PIL import Image
import uuid
from utils.helpers import load_df, save_df

st.set_page_config(layout="centered")
st.title("📄 صفحة توثيق الفواتير")

INVOICE_PATH = "data/invoices.csv"
IMAGE_DIR = "data/invoices/"
os.makedirs(IMAGE_DIR, exist_ok=True)

# تحميل بيانات المهام وحساب مجموع تكلفتها
tasks_df = load_df("data/tasks.csv")
total_tasks_cost = tasks_df["التكلفة"].sum() if not tasks_df.empty else 0
st.markdown(f"### 💰 إجمالي تكاليف المهام: {total_tasks_cost:,.2f} دولار")

# تحميل الفواتير أو إنشاء DataFrame فارغ
invoice_df = load_df(INVOICE_PATH)
if invoice_df.empty or set(invoice_df.columns) != {"التاريخ", "اسم الفاتورة", "القيمة", "الصورة"}:
    invoice_df = pd.DataFrame(columns=["التاريخ", "اسم الفاتورة", "القيمة", "الصورة"])

# دالة إضافة فاتورة جديدة
def add_invoice(date, name, value, image):
    img_id = str(uuid.uuid4()) + ".jpg"
    image_path = os.path.join(IMAGE_DIR, img_id)
    image.save(image_path)
    invoice_df.loc[len(invoice_df)] = [date, name, value, img_id]
    save_df(invoice_df, INVOICE_PATH)

# دالة حذف فاتورة
def delete_invoice(index):
    img_file = invoice_df.loc[index, "الصورة"]
    img_path = os.path.join(IMAGE_DIR, img_file)
    if os.path.exists(img_path):
        os.remove(img_path)
    invoice_df.drop(index, inplace=True)
    invoice_df.reset_index(drop=True, inplace=True)
    save_df(invoice_df, INVOICE_PATH)
    st.rerun()

# نموذج إضافة فاتورة
with st.form("invoice_form"):
    date = st.date_input("تاريخ الفاتورة")
    name = st.text_input("اسم الفاتورة")
    value = st.number_input("القيمة", min_value=0.0)
    img = st.file_uploader("صورة الفاتورة", type=["jpg", "jpeg", "png"])
    submit = st.form_submit_button("إضافة الفاتورة")

    if submit:
        if not img:
            st.error("يرجى رفع صورة للفاتورة.")
        else:
            img = Image.open(img)
            add_invoice(date, name, value, img)
            st.success("✅ تمت إضافة الفاتورة")
            st.rerun()

# عرض الفواتير الحالية
st.subheader("📑 قائمة الفواتير")

if invoice_df.empty:
    st.info("لا توجد فواتير مضافة بعد.")
else:
    for idx, row in invoice_df.iterrows():
        cols = st.columns([1, 5, 1])
        with cols[0]:
            img_path = os.path.join(IMAGE_DIR, row["الصورة"])
            if os.path.exists(img_path):
                st.image(img_path, width=100)
            else:
                st.warning("❌ صورة غير موجودة")
        with cols[1]:
            st.markdown(
                f"""
                <div style="direction: rtl; text-align: right; background-color: #f8f8f8; padding: 10px; border-radius: 8px;">
                    <strong>📅 التاريخ:</strong> {row['التاريخ']}<br>
                    <strong>📄 الاسم:</strong> {row['اسم الفاتورة']}<br>
                    <strong>💵 القيمة:</strong> {row['القيمة']:,.2f} ريال
                </div>
                """,
                unsafe_allow_html=True
            )
        with cols[2]:
            if st.button("🗑️ حذف", key=f"delete_{idx}"):
                delete_invoice(idx)

    # إجمالي الفواتير والمبلغ المتبقي
    total_invoices = invoice_df["القيمة"].sum()
    st.markdown(f"### 💳 مجموع الفواتير: {total_invoices:,.2f} ريال")
    st.markdown(f"### 🧾 المبلغ المتبقي: {total_tasks_cost - total_invoices:,.2f} ريال")
