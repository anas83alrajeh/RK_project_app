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

# تحميل البيانات مرة واحدة وتخزينها في session_state
if "df" not in st.session_state:
    st.session_state.df = load_data()

df = st.session_state.df.copy()

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
            st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(st.session_state.df)
            st.success("تمت الإضافة")

st.subheader("📋 قائمة المهام")

if st.session_state.df.empty:
    st.info("لا توجد مهام حالياً")
else:
    df_display = st.session_state.df.reset_index(drop=True)

    # استخدم جدول عادي مع زر حذف لكل صف
    for idx, row in df_display.iterrows():
        cols = st.columns([8, 1])
        with cols[0]:
            st.write(f"{row['اسم المهمة']} - العدد: {row['العدد']} - سعر الوحدة: {row['سعر الوحدة']} دولار - التكلفة: {row['التكلفة']:.2f} دولار")
        with cols[1]:
            if st.button("🗑️ حذف", key=f"delete_{idx}"):
                # حذف المهمة من DataFrame في session_state
                st.session_state.df = st.session_state.df.drop(idx).reset_index(drop=True)
                save_data(st.session_state.df)
                st.experimental_rerun_flag = True  # علم لإعادة تحميل بعد الحلقة

# إعادة تحميل الصفحة بعد الحلقة إذا علمت بالضرورة
if "st.experimental_rerun_flag" in st.session_state and st.session_state.st.experimental_rerun_flag:
    st.session_state.st.experimental_rerun_flag = False
    st.experimental_rerun()

total = st.session_state.df["التكلفة"].sum() if not st.session_state.df.empty else 0
st.markdown(f"### 💰 المجموع الكلي: {total:,.2f} دولار")

area = st.number_input("📐 المساحة الكلية بالمتر المربع", min_value=1.0)
if area and total > 0:
    cost_per_meter = total / area
    st.markdown(f"### 💸 تكلفة المتر المربع: {cost_per_meter:,.2f} دولار")
