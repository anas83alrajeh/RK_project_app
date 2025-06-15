import streamlit as st
import pandas as pd
import os
from utils.helpers import save_df

st.title("🧮 صفحة حساب التكاليف")

DATA_PATH = "data/tasks.csv"
os.makedirs("data", exist_ok=True)

def load_data():
    if os.path.exists(DATA_PATH):
        return pd.read_csv(DATA_PATH)
    else:
        return pd.DataFrame(columns=["اسم المهمة", "العدد", "سعر الوحدة", "التكلفة"])

def save_data(df):
    save_df(df, DATA_PATH)

if "refresh" not in st.session_state:
    st.session_state.refresh = False

# تحميل البيانات
df = load_data()

st.subheader("➕ إضافة مهمة")

with st.form("task_form", clear_on_submit=True):
    name = st.text_input("اسم المهمة")
    count = st.number_input("العدد", min_value=1, value=1)
    unit_price = st.number_input("سعر الوحدة", min_value=0.0)
    submitted = st.form_submit_button("إضافة المهمة")

    if submitted:
        if name.strip() == "":
            st.error("يرجى إدخال اسم المهمة")
        else:
            cost = unit_price * count
            new_row = {"اسم المهمة": name, "العدد": count, "سعر الوحدة": unit_price, "التكلفة": cost}
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(df)
            st.success("تمت الإضافة")
            st.session_state.refresh = True  # علامة لتحديث البيانات بعد الإضافة

# إعادة تحميل البيانات عند الحاجة
if st.session_state.refresh:
    df = load_data()
    st.session_state.refresh = False

st.subheader("📋 قائمة المهام")

if df.empty:
    st.info("لا توجد مهام حالياً")
else:
    df = df.reset_index(drop=True)
    st.dataframe(df)

    st.markdown("---")
    st.write("**لحذف مهمة، اضغط على زر الحذف المقابل:**")
    for idx, row in df.iterrows():
        cols = st.columns([8, 1])
        with cols[0]:
            st.write(f"{row['اسم المهمة']} - العدد: {row['العدد']} - سعر الوحدة: {row['سعر الوحدة']} دولار - التكلفة: {row['التكلفة']:.2f} دولار")
        with cols[1]:
            if st.button("🗑️ حذف", key=f"delete_{idx}"):
                df = df.drop(idx).reset_index(drop=True)
                save_data(df)
                st.experimental_rerun()

if not df.empty:
    total = df["التكلفة"].sum()
    st.markdown(f"### 💰 المجموع الكلي: {total:,.2f} دولار")
    area = st.number_input("📐 المساحة الكلية بالمتر المربع", min_value=1.0)
    if area:
        cost_per_meter = total / area
        st.markdown(f"### 💸 تكلفة المتر المربع: {cost_per_meter:,.2f} دولار")
