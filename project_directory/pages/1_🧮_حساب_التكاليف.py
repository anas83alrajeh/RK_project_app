import streamlit as st
import pandas as pd
import os
from utils.helpers import save_df

st.set_page_config(layout="centered")
st.title("🧮 صفحة حساب التكاليف")

DATA_PATH = "data/tasks.csv"
os.makedirs("data", exist_ok=True)

# دالة تحميل البيانات
def load_data():
    if os.path.exists(DATA_PATH):
        return pd.read_csv(DATA_PATH)
    return pd.DataFrame(columns=["اسم المهمة", "العدد", "سعر الوحدة", "التكلفة"])

# دالة حفظ البيانات
def save_data(df):
    save_df(df, DATA_PATH)

# تحميل البيانات عند بدء الصفحة
if "df" not in st.session_state:
    st.session_state.df = load_data()

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
            new_row = {
                "اسم المهمة": name,
                "العدد": count,
                "سعر الوحدة": unit_price,
                "التكلفة": cost
            }
            st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(st.session_state.df)
            st.rerun()  # إعادة تحميل الصفحة مباشرة بدون خطأ

st.subheader("📋 قائمة المهام")

box_bg_color = "#f0f0f0"  # خلفية رمادية فاتحة
text_color = "#000000"    # نص أسود

if st.session_state.df.empty:
    st.info("لا توجد مهام حالياً")
else:
    df_display = st.session_state.df.reset_index(drop=True)

    for idx, row in df_display.iterrows():
        cols = st.columns([9, 1])
        with cols[0]:
            st.markdown(
                f"""
                <div style="background-color: {box_bg_color}; color: {text_color}; padding: 15px; margin-bottom: 10px; border-radius: 8px; direction: rtl; text-align: right;">
                    <div><strong>اسم المهمة:</strong> {row['اسم المهمة']}</div>
                    <div><strong>العدد:</strong> {row['العدد']}</div>
                    <div><strong>سعر الوحدة:</strong> {row['سعر الوحدة']} دولار</div>
                    <div><strong>التكلفة:</strong> {row['التكلفة']:.2f} دولار</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with cols[1]:
            if st.button("🗑️ حذف", key=f"delete_{idx}"):
                st.session_state.df = st.session_state.df.drop(idx).reset_index(drop=True)
                save_data(st.session_state.df)
                st.rerun()  # الحل الآمن لإعادة تحميل الصفحة

# 💰 إجمالي التكلفة
total = st.session_state.df["التكلفة"].sum() if not st.session_state.df.empty else 0
st.markdown(f"### 💰 المجموع الكلي: {total:,.2f} دولار")

# 📐 تكلفة المتر المربع
area = st.number_input("📐 المساحة الكلية بالمتر المربع", min_value=1.0)
if area and total > 0:
    cost_per_meter = total / area
    st.markdown(f"### 💸 تكلفة المتر المربع: {cost_per_meter:,.2f} دولار")
