import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(layout="centered")
st.title("📆 مراحل المشروع")

DATA_PATH = "data/stages.csv"
os.makedirs("data", exist_ok=True)

# تحميل البيانات
def load_stages():
    if os.path.exists(DATA_PATH):
        return pd.read_csv(DATA_PATH)
    else:
        # ملف فارغ مبدئي إذا لم يوجد
        return pd.DataFrame(columns=["اسم المرحلة", "تاريخ البداية", "تاريخ النهاية", "المدة"])

# حفظ البيانات
def save_stages(df):
    df.to_csv(DATA_PATH, index=False, encoding="utf-8")

df = load_stages()

if df.empty:
    st.info("لا توجد مراحل مسجلة في الملف.")
else:
    st.subheader("📝 تعديل تواريخ المراحل")

    updated_rows = []
    for idx, row in df.iterrows():
        st.markdown(f"#### 🏗️ {row['اسم المرحلة']}")
        col1, col2, col3 = st.columns(3)

        # تحويل النصوص إلى تواريخ (أو تعيين قيم افتراضية)
        try:
            start_date = datetime.strptime(str(row["تاريخ البداية"]), "%Y-%m-%d").date()
        except:
            start_date = datetime.today().date()

        try:
            end_date = datetime.strptime(str(row["تاريخ النهاية"]), "%Y-%m-%d").date()
        except:
            end_date = datetime.today().date()

        with col1:
            new_start = st.date_input("تاريخ البداية", value=start_date, key=f"start_{idx}")
        with col2:
            new_end = st.date_input("تاريخ النهاية", value=end_date, key=f"end_{idx}")
        with col3:
            duration = (new_end - new_start).days
            st.write(f"📅 المدة: **{duration} يوم**")

        updated_rows.append({
            "اسم المرحلة": row["اسم المرحلة"],
            "تاريخ البداية": new_start.strftime("%Y-%m-%d"),
            "تاريخ النهاية": new_end.strftime("%Y-%m-%d"),
            "المدة": duration
        })

    if st.button("💾 حفظ التعديلات"):
        df_updated = pd.DataFrame(updated_rows)
        save_stages(df_updated)
        st.success("✅ تم حفظ التعديلات بنجاح.")
