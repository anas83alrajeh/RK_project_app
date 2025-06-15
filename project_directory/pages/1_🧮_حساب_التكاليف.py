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

st.subheader("➕ إضافة مهمة")
with st.form("task_form"):
    name = st.text_input("اسم المهمة")
    count = st.number_input("العدد", min_value=1, value=1)
    unit_price = st.number_input("سعر الوحدة", min_value=0.0)
    submitted = st.form_submit_button("إضافة المهمة")

    if submitted:
        df = load_data()
        cost = unit_price * count
        df.loc[len(df)] = [name, count, unit_price, cost]
        save_df(df, DATA_PATH)
        st.success("تمت الإضافة")

# عرض المهام
st.subheader("📋 قائمة المهام")
df = load_data()
st.dataframe(df)

# الحسابات النهائية
if not df.empty:
    total = df["التكلفة"].sum()
    st.markdown(f"### 💰 المجموع الكلي: {total:,.2f} دولار")
    area = st.number_input("📐 المساحة الكلية بالمتر المربع", min_value=1.0)
    if area:
        cost_per_meter = total / area
        st.markdown(f"### 💸 تكلفة المتر المربع: {cost_per_meter:,.2f} دولار")
