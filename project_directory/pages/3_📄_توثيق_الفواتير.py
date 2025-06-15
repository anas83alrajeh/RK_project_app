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

# تحميل بيانات المهام وحساب مجموع التكلفة
tasks_df = load_df("data/tasks.csv")
total_tasks_cost = tasks_df["التكلفة"].sum() if not tasks_df.empty else 0
st.markdown(f"### 💰 إجمالي تكاليف المهام: {total_tasks_cost:,.2f} دولار")

# تعريف متغيرات الحالة لإعادة التشغيل
if "rerun_after_add" not in st.session_state:
    st.session_state.rerun_after_add = False
if "rerun_after_delete" not in st.session_state:
    st.session_state.rerun_after_delete = False

def add_invoice(date, name, value, image):
    img_id = str(uuid.uuid4()) + ".jpg"
    image_path = os.path.join(IMAGE_DIR, img_id)
    # تصغير الصورة إلى عرض 200 بكسل (يمكن تعديل الحجم حسب الحاجة)
    if image.mode in ("RGBA", "LA") or (image.mode == "P" and "transparency" in image.info):
        image = image.convert("RGB")
    max_width = 200
    if image.width > max_width:
        ratio = max_width / image.width
        new_size = (max_width, int(image.height * ratio))
        image = image.resize(new_size)
    image.save(image_path)

    # إعادة تحميل الفواتير قبل الإضافة لضمان عدم تعارض النسخ
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

# نموذج إضافة فاتورة
with st.form("invoice_form"):
    date = st.date_input("تاريخ الفاتورة")
    name = st.text_input("اسم الفاتورة")
    value = st.number_input("القيمة", min_value=0.0)
    img = st.file_uploader("صورة الفاتورة", type=["jpg", "jpeg", "png"])
    submit = st.form_submit_button("إضافة الفاتورة")

    if submit:
        if not img:
            st.error("يرجى رفع صورة الفاتورة.")
        else:
            img_obj = Image.open(img)
            add_invoice(date, name, value, img_obj)
            st.success("✅ تمت إضافة الفاتورة")
            # *** التغيير هنا: أزل st.experimental_rerun() الفوري ***
            st.session_state.rerun_after_add = True

# إعادة تشغيل الصفحة عند الإضافة أو الحذف
# هذا الجزء سيعالج إعادة التشغيل بشكل صحيح في الدورة التالية للتنفيذ
if st.session_state.rerun_after_add or st.session_state.rerun_after_delete:
    st.session_state.rerun_after_add = False
    st.session_state.rerun_after_delete = False
    st.experimental_rerun() # هذا الاستدعاء آمن هنا

# إعادة تحميل بيانات الفواتير للعرض
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
                st.image(img_path, width=100)
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
                # *** التغيير هنا: أزل st.experimental_rerun() الفوري ***
                st.session_state.rerun_after_delete = True

total_invoices = invoice_df["القيمة"].sum()
st.markdown(f"### 💳 مجموع الفواتير: {total_invoices:,.2f} ريال")
st.markdown(f"### 🧾 المبلغ المتبقي: {total_tasks_cost - total_invoices:,.2f} ريال")
