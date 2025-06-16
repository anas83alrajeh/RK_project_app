import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="centered")

DATA_PATH = "data/project_phases.csv"
os.makedirs("data", exist_ok=True)

# المراحل العشر المطلوبة
phase_names = [
    "تحديد الأرض",
    "استخراج التراخيص",
    "التصميم الهندسي والمعماري",
    "أعمال الحفر",
    "صب القواعد والأساسات",
    "صب الأعمدة والأسقف والجدران الحاملة",
    "إغلاق الهيكل بالجدران الداخلية والخارجية",
    "كهرباء وسباكة",
    "تركيب المصعد والتأكد من الجاهزية",
    "إعداد تقرير التسليم"
]

default_phases = [
    {
        "رقم المرحلة": i + 1,
        "اسم المرحلة": name,
        "تاريخ البدء": "",
        "تاريخ النهاية": "",
        "المدة الزمنية": "",
        "تم التنفيذ": False
    } for i, name in enumerate(phase_names)
]

def load_data():
    if os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH)
        # ✅ إذا كانت البيانات أقل من 10 مراحل، إعادة تعيين الملف
        if len(df) < 10:
            return pd.DataFrame(default_phases)
        return df
    else:
        return pd.DataFrame(default_phases)

def save_data(df):
    df.to_csv(DATA_PATH, index=False, encoding="utf-8")

def safe_to_date(value):
    try:
        if pd.isna(value) or value == "" or value is None:
            return None
        dt = pd.to_datetime(value)
        return dt.date()
    except Exception:
        return None

df = load_data()

# RTL CSS
st.markdown("""
<style>
    body, div, input, label, textarea, select, button {
        direction: rtl !important;
        text-align: right !important;
    }
    .phase-box {
        background-color: #f0f0f0;
        color: #000000;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 12px;
        font-size: 14px;
        direction: rtl;
        text-align: right;
    }
    .phase-title {
        font-weight: bold;
        font-size: 16px;
        margin-bottom: 6px;
    }
</style>
""", unsafe_allow_html=True)

# عرض المراحل
completed_count = 0

for idx, row in df.iterrows():
    st.markdown(f'<div class="phase-box">', unsafe_allow_html=True)
    st.markdown(f'<div class="phase-title">المرحلة {row["رقم المرحلة"]}: {row["اسم المرحلة"]}</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        df.at[idx, "تاريخ البدء"] = st.date_input(
            f"تاريخ البدء للمرحلة {row['رقم المرحلة']}",
            value=safe_to_date(row["تاريخ البدء"]),
            key=f"start_{idx}"
        )
    with col2:
        df.at[idx, "تاريخ النهاية"] = st.date_input(
            f"تاريخ النهاية للمرحلة {row['رقم المرحلة']}",
            value=safe_to_date(row["تاريخ النهاية"]),
            key=f"end_{idx}"
        )
    with col3:
        try:
            start = pd.to_datetime(df.at[idx, "تاريخ البدء"])
            end = pd.to_datetime(df.at[idx, "تاريخ النهاية"])
            if pd.notnull(start) and pd.notnull(end) and end >= start:
                duration = (end - start).days
                df.at[idx, "المدة الزمنية"] = duration
            else:
                df.at[idx, "المدة الزمنية"] = ""
        except Exception:
            df.at[idx, "المدة الزمنية"] = ""

        st.text_input(
            "المدة الزمنية (بالأيام)",
            value=str(df.at[idx, "المدة الزمنية"]),
            disabled=True,
            key=f"duration_{idx}"
        )

    done = st.checkbox("✅ تم التنفيذ", value=bool(row.get("تم التنفيذ", False)), key=f"done_{idx}")
    df.at[idx, "تم التنفيذ"] = done
    if done:
        completed_count += 1

    st.markdown("</div>", unsafe_allow_html=True)

# ✅ عرض نسبة الإنجاز
progress_percent = completed_count * 10
st.progress(progress_percent / 100)
st.markdown(f"<h4 style='text-align: right; direction: rtl;'>🚀 نسبة إنجاز المشروع: {progress_percent}%</h4>", unsafe_allow_html=True)

# زر الحفظ
if st.button("💾 حفظ المراحل"):
    save_data(df)
    st.success("✅ تم حفظ البيانات وتحديث نسبة الإنجاز.")
